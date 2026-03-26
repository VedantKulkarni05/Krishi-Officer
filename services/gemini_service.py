import os
import google.generativeai as genai
from PIL import Image, UnidentifiedImageError
from dotenv import load_dotenv

load_dotenv()

_model = None


class GeminiInputError(ValueError):
    """Raised when inputs are missing or malformed for Gemini requests."""


class GeminiConfigurationError(RuntimeError):
    """Raised when Gemini client configuration is invalid."""


class GeminiResponseError(RuntimeError):
    """Raised when Gemini responds without usable content."""


class GeminiServiceError(RuntimeError):
    """Raised when Gemini request execution fails."""


def _get_model():
    """Lazily initialize the Gemini model to avoid import-time failures."""
    global _model
    if _model is not None:
        return _model

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise GeminiConfigurationError("GEMINI_API_KEY or GOOGLE_API_KEY is required.")

    genai.configure(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    _model = genai.GenerativeModel(model_name)
    return _model


def _prepare_image_for_model(image_file):
    """Validate and normalize an uploaded image for Gemini."""
    file_obj = image_file.stream if hasattr(image_file, "stream") else image_file
    try:
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
        with Image.open(file_obj) as img:
            img.verify()
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
        with Image.open(file_obj) as img:
            normalized = img.convert("RGB") if img.mode != "RGB" else img
            result = normalized.copy()
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
        return result
    except (UnidentifiedImageError, OSError) as exc:
        raise GeminiInputError(f"Failed to process image: {str(exc)}") from exc


def _extract_response_text(response):
    """Extract text defensively across Gemini response variants."""
    text = getattr(response, "text", None)
    if isinstance(text, str) and text.strip():
        return text.strip()

    candidates = getattr(response, "candidates", None) or []
    parts_text = []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None) or []
        for part in parts:
            part_text = getattr(part, "text", None)
            if isinstance(part_text, str) and part_text.strip():
                parts_text.append(part_text.strip())

    if parts_text:
        return "\n".join(parts_text)

    raise GeminiResponseError("AI returned an empty response.")


def get_gemini_analysis(image_file=None, prompt=None):
    """
    Centralized function to get AI analysis.
    Supports Image + Text, Text only, or Image only (with default prompt).
    """
    if not image_file and not prompt:
        raise GeminiInputError("Either an image or a prompt must be provided.")

    contents = []
    
    if prompt:
        contents.append(prompt)
    
    if image_file:
        contents.append(_prepare_image_for_model(image_file))

    try:
        model = _get_model()
        response = model.generate_content(contents)
        return _extract_response_text(response)
    except (GeminiInputError, GeminiConfigurationError, GeminiResponseError):
        raise
    except Exception as exc:
        raise GeminiServiceError(f"AI Generation Error: {str(exc)}") from exc