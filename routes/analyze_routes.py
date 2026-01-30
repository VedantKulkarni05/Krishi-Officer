# Image + Gemini orchestration
# Accepts images and user queries, triggers Gemini analysis using prompt registry.
from flask import Blueprint, request, jsonify
from services.gemini_service import get_gemini_analysis
from services.prompt_registry import PROMPTS

analyze_bp = Blueprint("analyze", __name__)

@analyze_bp.route("/analyze-crop", methods=["POST"])
def analyze_crop():
    """Route for general crop advisory analysis (multimodal)."""
    image_file = request.files.get("crop_image")
    user_query = request.form.get("query")
    
    if not image_file and not user_query:
        return jsonify({"error": "Please provide an image or a description."}), 400

    # For crop advisory, we combine the system prompt with user input
    base_prompt = PROMPTS.get("crop_pest")
    full_prompt = f"{base_prompt}\n\nUSER QUERY: {user_query}" if user_query else base_prompt

    try:
        ai_advice = get_gemini_analysis(image_file, full_prompt)
        return jsonify({"advice": ai_advice})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analyze_bp.route("/analyze-soil", methods=["POST"])
def analyze_soil():
    """Specific route for soil analysis."""
    image_file = request.files.get("soil_image")
    if not image_file:
        return jsonify({"error": "No soil image uploaded"}), 400
    
    try:
        ai_advice = get_gemini_analysis(image_file, PROMPTS["soil"])
        return jsonify({"advice": ai_advice})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analyze_bp.route("/analyze-water", methods=["POST"])
def analyze_water():
    """Specific route for water analysis."""
    image_file = request.files.get("water_image")
    if not image_file:
        return jsonify({"error": "No water image uploaded"}), 400
    
    try:
        ai_advice = get_gemini_analysis(image_file, PROMPTS["water"])
        return jsonify({"advice": ai_advice})
    except Exception as e:
        return jsonify({"error": str(e)}), 500