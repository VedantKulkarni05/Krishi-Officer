 # Image + Gemini orchestration
#  Accepts crop images and user queries, triggers Gemini analysis, and returns remedies and suggestions.
from flask import Blueprint, request, jsonify
from services.gemini_service import get_gemini_analysis # Updated function name

analyze_bp = Blueprint('analyze', __name__)

@analyze_bp.route('/analyze-crop', methods=['POST'])
def analyze_crop():
    # 1. Get the image and text from the request
    image_file = request.files.get('crop_image')
    user_query = request.form.get('query', 'Identify any pests or diseases in this image.')

    if not image_file:
        return jsonify({"error": "No image uploaded"}), 400

    # 2. Call the service with BOTH image and text
    try:
        # We pass the file stream directly to the service
        ai_advice = get_gemini_analysis(image_file, user_query)
        return jsonify({"advice": ai_advice})
    except Exception as e:
        return jsonify({"error": str(e)}), 500