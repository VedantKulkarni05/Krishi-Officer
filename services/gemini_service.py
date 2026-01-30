import os
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# Configuration
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("API Key not found. Please ensure .env is in the root folder.")

genai.configure(api_key=api_key)

# Initialize Model (at module level for efficiency)
model = genai.GenerativeModel('gemini-2.5-flash')

def get_gemini_analysis(image_file=None, prompt=None):
    """
    Centralized function to get AI analysis.
    Supports Image + Text, Text only, or Image only (with default prompt).
    """
    if not image_file and not prompt:
        raise ValueError("Either an image or a prompt must be provided.")

    contents = []
    
    if prompt:
        contents.append(prompt)
    
    if image_file:
        try:
            img = Image.open(image_file)
            contents.append(img)
        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")

    try:
        response = model.generate_content(contents)
        return response.text
    except Exception as e:
        raise Exception(f"AI Generation Error: {str(e)}")