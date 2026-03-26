# Image + Gemini orchestration
# Accepts images and user queries, triggers Gemini analysis using prompt registry.
import difflib
import json
import re
import uuid
from services.gemini_service import (
    get_gemini_analysis,
    GeminiInputError,
    GeminiConfigurationError,
    GeminiResponseError,
    GeminiServiceError,
)
from services.prompt_registry import PROMPTS
from database.db import get_db_connection, release_db_connection
from flask import Blueprint, request, jsonify, g
from middleware.auth_middleware import token_required

analyze_bp = Blueprint("analyze", __name__)

# Allowed MIME types for uploaded images
ALLOWED_MIMETYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}

# Language mapping for precise AI instruction
LANG_MAP = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu"
}

SUMMARY_KEYS = {"summary", "सारांश", "சுருக்கம்", "సారాంశం"}
ROLE_TOKENS = {"crop_health_advisory", "pest_detection_analysis", "reject"}

ALTERNATIVE_KEYWORDS = {
    "alternative", "alternatives", "similar", "lookalike", "look-alike", "could also be",
    "what else", "another pest", "differential",
    "alternative pest", "similar pest",
    "वैकल्पिक", "दूसरे कीट", "और कौन", "और कौन सा",
    "पर्यायी", "इतर किड", "आणखी कोणता",
    "மாற்று", "ஒத்த பூச்சி", "வேறு பூச்சி",
    "ప్రత్యామ్నాయ", "ఇంకా ఏ పురుగు", "సమాన పురుగు",
}

CLARIFICATION_KEYWORDS = {
    "why", "how", "explain", "difference", "clarify", "what does it mean",
    "क्यों", "कैसे", "अंतर", "समझाओ",
    "का", "कसा", "फरक", "समजावून",
    "ஏன்", "எப்படி", "வேறுபாடு", "விளக்கம்",
    "ఎందుకు", "ఎలా", "తేడా", "వివరించు",
}

PROGRESSION_KEYWORDS = {
    "worse", "better", "spread", "spreading", "increased", "reduced", "after spray", "after treatment",
    "बढ़", "घट", "फैल", "स्प्रे के बाद", "उपचार के बाद",
    "वाढ", "कमी", "पसर", "फवारणीनंतर", "उपचारानंतर",
    "அதிகம்", "குறைந்த", "பரவ", "தெளித்த பிறகு", "சிகிச்சைக்கு பிறகு",
    "పెరిగింది", "తగ్గింది", "వ్యాప", "స్ప్రే తర్వాత", "చికిత్స తర్వాత",
}

TREATMENT_KEYWORDS = {
    "dose", "dosage", "frequency", "how often", "mix", "mixing", "spray schedule",
    "मात्रा", "कितनी बार", "मिश्रण", "स्प्रे",
    "डोस", "किती वेळा", "मिश्रण", "फवारणी",
    "அளவு", "எத்தனை முறை", "கலவை", "தெளிப்பு",
    "మోతాదు", "ఎంతసార్లు", "మిశ్రమం", "స్ప్రే",
}

SWITCH_TO_GENERAL_KEYWORDS = {
    "overall crop health", "general advisory", "nutrient", "nutrition", "soil issue", "irrigation",
    "सामान्य सलाह", "कुल फसल स्वास्थ्य", "पोषक", "मिट्टी", "सिंचाई",
    "सामान्य सल्ला", "एकूण पीक आरोग्य", "पोषण", "माती", "सिंचन",
    "பொது ஆலோசனை", "மண்", "நீர்ப்பாசனம்", "ஊட்டச்சத்து",
    "సాధారణ సలహా", "మట్టి", "పొలానికి నీరు", "పోషకాలు",
}

TEXT_LABELS = {
    "en": {
        "analysis_role": "Analysis Role",
        "status": "Status",
        "confidence": "Confidence",
        "summary": "Summary",
        "evidence": "Evidence",
        "actions": "Immediate Actions (24-48h)",
        "organic": "Organic Treatments",
        "note": "Note",
    },
    "hi": {
        "analysis_role": "विश्लेषण प्रकार",
        "status": "स्थिति",
        "confidence": "विश्वास स्तर",
        "summary": "सारांश",
        "evidence": "साक्ष्य",
        "actions": "तुरंत कदम (24-48 घंटे)",
        "organic": "जैविक उपचार",
        "note": "नोट",
    },
    "mr": {
        "analysis_role": "विश्लेषण प्रकार",
        "status": "स्थिती",
        "confidence": "विश्वास पातळी",
        "summary": "सारांश",
        "evidence": "पुरावे",
        "actions": "त्वरित उपाय (24-48 तास)",
        "organic": "सेंद्रिय उपाय",
        "note": "टीप",
    },
    "ta": {
        "analysis_role": "பகுப்பாய்வு வகை",
        "status": "நிலை",
        "confidence": "நம்பகத்தன்மை",
        "summary": "சுருக்கம்",
        "evidence": "ஆதாரங்கள்",
        "actions": "உடனடி நடவடிக்கைகள் (24-48 மணி)",
        "organic": "இயற்கை சிகிச்சைகள்",
        "note": "குறிப்பு",
    },
    "te": {
        "analysis_role": "విశ్లేషణ రకం",
        "status": "స్థితి",
        "confidence": "నమ్మక స్థాయి",
        "summary": "సారాంశం",
        "evidence": "ఆధారాలు",
        "actions": "తక్షణ చర్యలు (24-48 గంటలు)",
        "organic": "సేంద్రియ చికిత్సలు",
        "note": "గమనిక",
    },
}


def _normalize_language_code(language_code):
    code = (language_code or "en").strip().lower()
    return code if code in LANG_MAP else "en"


def _resolve_payload_language(payload, fallback_code):
    language_value = str(payload.get("language", "")).strip().lower()
    if language_value in LANG_MAP:
        return language_value
    for code, name in LANG_MAP.items():
        if language_value == name.lower():
            return code
    return fallback_code


def _clip_text(value, max_len=280):
    text = str(value or "").replace("\n", " ").strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "..."


def _extract_summary_from_model_content(content):
    """Extract summary-like sentence from previously rendered model content."""
    for line in str(content or "").splitlines():
        line = line.strip().lstrip("-").strip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key.strip().lower() in SUMMARY_KEYS:
            cleaned = value.strip().strip("*")
            if cleaned:
                return cleaned
    return _clip_text(content, 180)


def _extract_last_analysis_role(content):
    text = str(content or "")
    for role in ROLE_TOKENS:
        if role in text:
            return role
    return "unknown"


def _extract_last_detection_name(content):
    summary = _extract_summary_from_model_content(content)
    patterns = [
        r"appears to be\s+(?:a|an|the|type of)?\s*([A-Za-z\- ]{3,80})",
        r"identified\s+(?:as|is)\s+([A-Za-z\- ]{3,80})",
        r"likely\s+([A-Za-z\- ]{3,80})",
    ]
    for pattern in patterns:
        m = re.search(pattern, summary, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip(" .,:;")
    return "unknown"


def _extract_last_detection_category(content):
    text = str(content or "").lower()
    if "fung" in text:
        return "fungal"
    if "bacter" in text:
        return "bacterial"
    if "viral" in text or "virus" in text:
        return "viral"
    if "insect" in text or "beetle" in text or "larva" in text or "worm" in text:
        return "insect"
    return "unknown"


def _has_any_keyword(query, keywords):
    q = str(query or "").lower()
    return any(k in q for k in keywords)


def _detect_follow_up_intent(query, follow_up_mode):
    if not follow_up_mode:
        return "new_issue"
    if _has_any_keyword(query, ALTERNATIVE_KEYWORDS):
        return "alternatives"
    if _has_any_keyword(query, TREATMENT_KEYWORDS):
        return "treatment_adjustment"
    if _has_any_keyword(query, PROGRESSION_KEYWORDS):
        return "progression"
    if _has_any_keyword(query, CLARIFICATION_KEYWORDS):
        return "clarification"
    return "general_followup"


def _should_lock_role(last_role, follow_up_intent, query):
    if last_role != "pest_detection_analysis":
        return False
    if _has_any_keyword(query, SWITCH_TO_GENERAL_KEYWORDS):
        return False
    return follow_up_intent in {
        "alternatives", "clarification", "progression", "treatment_adjustment", "general_followup"
    }


def _similarity_score(a, b):
    """Return normalized text similarity in [0, 1]."""
    clean = lambda s: re.sub(r"\s+", " ", str(s or "").strip().lower())
    return difflib.SequenceMatcher(None, clean(a), clean(b)).ratio()


def _build_recent_messages_block(messages):
    if not messages:
        return "None"
    lines = []
    for msg in messages:
        role = msg.get("role", "unknown")
        content = _clip_text(msg.get("content", ""), 220)
        lines.append(f"- {role}: {content}")
    return "\n".join(lines)


def _build_session_summary(messages):
    """Create a compact session memory summary for follow-up continuity."""
    last_user_query = ""
    last_model_summary = ""

    for msg in reversed(messages):
        if not last_user_query and msg.get("role") == "user":
            val = msg.get("content", "")
            if val and val != "[Image Uploaded]":
                last_user_query = _clip_text(val, 180)
        if not last_model_summary and msg.get("role") == "model":
            last_model_summary = _extract_summary_from_model_content(msg.get("content", ""))
        if last_user_query and last_model_summary:
            break

    parts = []
    if last_user_query:
        parts.append(f"Last user concern: {last_user_query}")
    if last_model_summary:
        parts.append(f"Last model summary: {last_model_summary}")
    return " | ".join(parts) if parts else "No prior summary available."


def _create_or_validate_session(cur, session_id, user_id):
    """Create a new session if none provided. Returns a UUID."""
    if not session_id:
        cur.execute("INSERT INTO sessions (user_id) VALUES (%s) RETURNING id", (user_id,))
        return cur.fetchone()[0]
    # Validate that the provided session_id is a valid UUID format
    try:
        return uuid.UUID(str(session_id))
    except (ValueError, AttributeError):
        raise ValueError(f"Invalid session_id format: {session_id}")


def _parse_analysis_json(raw_text):
    """Parse and validate Gemini JSON response contract."""
    payload = json.loads(raw_text)
    required = {"prompt_version", "language", "role", "status", "summary"}
    if not isinstance(payload, dict) or not required.issubset(payload.keys()):
        raise ValueError("AI response JSON missing required keys.")
    return payload


def _analysis_to_text(payload, fallback_language="en"):
    """Build a compact text response for current frontend chat rendering."""
    language_code = _resolve_payload_language(payload, fallback_language)
    labels = TEXT_LABELS.get(language_code, TEXT_LABELS["en"])

    lines = []
    role = payload.get("role", "unknown")
    status = payload.get("status", "unknown")
    summary = payload.get("summary", "")
    confidence = payload.get("confidence", "unknown")

    lines.append(f"### {labels['analysis_role']}: {role}")
    lines.append(f"- {labels['status']}: **{status}**")
    lines.append(f"- {labels['confidence']}: **{confidence}**")
    if summary:
        lines.append(f"- {labels['summary']}: {summary}")

    evidence = payload.get("evidence") or []
    if evidence:
        lines.append(f"### {labels['evidence']}")
        lines.extend([f"- {item}" for item in evidence if item])

    advisory = payload.get("advisory") or {}
    immediate = advisory.get("immediate_actions_24_48h") or []
    if immediate:
        lines.append(f"### {labels['actions']}")
        lines.extend([f"- {item}" for item in immediate if item])

    organic = advisory.get("organic_treatments") or []
    if organic:
        lines.append(f"### {labels['organic']}")
        lines.extend([f"- {item}" for item in organic if item])

    rejection = payload.get("rejection") or {}
    rejection_message = rejection.get("message")
    if rejection_message:
        lines.append(f"### {labels['note']}")
        lines.append(f"- {rejection_message}")

    return "\n".join(lines)


@analyze_bp.route("/analyze-crop", methods=["POST"])
@token_required
def analyze_crop():
    """Route for general crop advisory analysis (multimodal)."""
    image_file = request.files.get("crop_image")
    user_query = request.form.get("query", "")
    session_id = request.form.get("session_id")
    language_code = _normalize_language_code(request.form.get("language", "en"))

    if not image_file and not user_query:
        return jsonify({"error": "Please provide an image or a description."}), 400

    # --- File upload validation ---
    if image_file:
        if image_file.mimetype not in ALLOWED_MIMETYPES:
            return jsonify({"error": "Only JPEG, PNG, WebP, or GIF images are supported."}), 415

    # --- Build the AI prompt ---
    target_language = LANG_MAP[language_code]
    base_prompt = PROMPTS.get("crop_pest")
    query_context = user_query if user_query else "[No text query provided]"

    recent_messages = []
    follow_up_mode = False
    previous_image_available = False
    previous_model_content = ""
    last_analysis_role = "unknown"
    last_detection_name = "unknown"
    last_detection_category = "unknown"
    follow_up_intent = "new_issue"
    role_continuity_required = False
    role_lock_target = "none"

    # --- Phase 1: Open a DB connection, create/validate session, store user message, release ---
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        validated_session_id = _create_or_validate_session(cur, session_id, g.user.id)

        cur.execute(
            "SELECT role, content FROM messages WHERE session_id = %s ORDER BY created_at DESC LIMIT 8",
            (str(validated_session_id),)
        )
        prev_rows = cur.fetchall()
        prev_rows.reverse()
        recent_messages = [{"role": row[0], "content": row[1]} for row in prev_rows]
        follow_up_mode = any(m["role"] == "model" for m in recent_messages) and bool(user_query.strip())
        previous_image_available = any(
            m["role"] == "user" and m["content"] == "[Image Uploaded]"
            for m in recent_messages
        )
        for msg in reversed(recent_messages):
            if msg["role"] == "model":
                previous_model_content = msg.get("content", "")
                last_analysis_role = _extract_last_analysis_role(previous_model_content)
                if last_analysis_role == "pest_detection_analysis":
                    last_detection_name = _extract_last_detection_name(previous_model_content)
                    last_detection_category = _extract_last_detection_category(previous_model_content)
                break

        follow_up_intent = _detect_follow_up_intent(user_query, follow_up_mode)
        role_continuity_required = _should_lock_role(last_analysis_role, follow_up_intent, user_query)
        role_lock_target = "pest_detection_analysis" if role_continuity_required else "none"

        msg_content = user_query if user_query else "[Image Uploaded]"
        cur.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)",
            (str(validated_session_id), 'user', msg_content)
        )

        recent_for_context = (recent_messages + [{"role": "user", "content": msg_content}])[-8:]
        session_summary = _build_session_summary(recent_messages)
        full_prompt = (
            f"{base_prompt}\n\n"
            f"INPUT CONTEXT:\n"
            f"USER_LANGUAGE_CODE: {language_code}\n"
            f"USER_LANGUAGE_NAME: {target_language}\n"
            f"USER_QUERY: {query_context}\n"
            f"FOLLOW_UP_MODE: {'true' if follow_up_mode else 'false'}\n"
            f"FOLLOW_UP_INTENT: {follow_up_intent}\n"
            f"LAST_ANALYSIS_ROLE: {last_analysis_role}\n"
            f"ROLE_CONTINUITY_REQUIRED: {'true' if role_continuity_required else 'false'}\n"
            f"ROLE_LOCK_TARGET: {role_lock_target}\n"
            f"LAST_DETECTION_NAME: {last_detection_name}\n"
            f"LAST_DETECTION_CATEGORY: {last_detection_category}\n"
            f"HAS_NEW_IMAGE: {'true' if bool(image_file) else 'false'}\n"
            f"PREVIOUS_IMAGE_AVAILABLE: {'true' if previous_image_available else 'false'}\n"
            f"SESSION_SUMMARY: {session_summary}\n"
            f"RECENT_MESSAGES:\n{_build_recent_messages_block(recent_for_context)}"
        )

        if not image_file and previous_image_available:
            full_prompt += (
                "\nIMAGE CONTINUITY NOTE: No new image was uploaded in this turn. "
                "Use prior visual observations for continuity, and ask for a new close-up image "
                "if confidence is low or condition may have changed."
            )

        conn.commit()
    except ValueError as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception:
        conn.rollback()
        return jsonify({"error": "Failed to create or update session."}), 500
    finally:
        cur.close()
        # CRITICAL: Release the connection back to the pool BEFORE calling Gemini.
        # Gemini can take 5-15 seconds. Holding the connection during that time would
        # starve other requests of DB connections under any meaningful load.
        release_db_connection(conn)

    # --- Phase 2: Call Gemini AI (no DB connection held) ---
    try:
        ai_advice = get_gemini_analysis(image_file, full_prompt)
        analysis_payload = _parse_analysis_json(ai_advice)
        analysis_payload["language"] = _resolve_payload_language(analysis_payload, language_code)
        advice_text = _analysis_to_text(analysis_payload, fallback_language=language_code)

        if role_continuity_required and analysis_payload.get("role") != role_lock_target:
            role_lock_prompt = (
                f"{full_prompt}\n\n"
                "ROLE_LOCK_CORRECTION:\n"
                f"- You must return role exactly: {role_lock_target}.\n"
                "- Do not switch to crop_health_advisory for this follow-up.\n"
                "- Answer the user query within the locked role."
            )
            ai_advice = get_gemini_analysis(image_file, role_lock_prompt)
            analysis_payload = _parse_analysis_json(ai_advice)
            analysis_payload["language"] = _resolve_payload_language(analysis_payload, language_code)
            advice_text = _analysis_to_text(analysis_payload, fallback_language=language_code)

        if follow_up_mode and previous_model_content:
            previous_summary = _extract_summary_from_model_content(previous_model_content)
            current_summary = analysis_payload.get("summary", "")
            repeat_score = _similarity_score(current_summary or advice_text, previous_summary or previous_model_content)
            if repeat_score >= 0.86:
                anti_repeat_prompt = (
                    f"{full_prompt}\n\n"
                    "ANTI_REPEAT_GUARD:\n"
                    "- Your previous answer was too similar to the prior response.\n"
                    "- Do not repeat previous advice text.\n"
                    "- Focus only on what is new, changed, or uncertain in this follow-up.\n"
                    f"- Keep role as {role_lock_target} if ROLE_CONTINUITY_REQUIRED=true.\n"
                    "- If no new signal exists, ask one clarifying question and give minimal interim guidance."
                )
                ai_advice = get_gemini_analysis(image_file, anti_repeat_prompt)
                analysis_payload = _parse_analysis_json(ai_advice)
                analysis_payload["language"] = _resolve_payload_language(analysis_payload, language_code)
                advice_text = _analysis_to_text(analysis_payload, fallback_language=language_code)
    except GeminiInputError as e:
        return jsonify({"error": str(e)}), 400
    except GeminiConfigurationError as e:
        return jsonify({"error": str(e)}), 500
    except GeminiResponseError as e:
        return jsonify({"error": str(e)}), 502
    except GeminiServiceError as e:
        return jsonify({"error": str(e)}), 502
    except (json.JSONDecodeError, ValueError) as e:
        return jsonify({"error": f"AI response format error: {str(e)}"}), 502
    except Exception:
        return jsonify({"error": "AI analysis failed."}), 502

    # --- Phase 3: Re-acquire a DB connection to store the AI response ---
    conn2 = get_db_connection()
    cur2 = conn2.cursor()
    try:
        cur2.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)",
            (str(validated_session_id), 'model', advice_text)
        )
        conn2.commit()
    except Exception as e:
        conn2.rollback()
        # We still have a valid AI response, so we return it even if storing fails.
        # The session_id is returned for the client to keep using.
        return jsonify({
            "advice": advice_text,
            "analysis": analysis_payload,
            "session_id": str(validated_session_id)
        }), 200
    finally:
        cur2.close()
        release_db_connection(conn2)

    return jsonify({
        "advice": advice_text,
        "analysis": analysis_payload,
        "session_id": str(validated_session_id)
    })
