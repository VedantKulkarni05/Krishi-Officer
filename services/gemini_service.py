import os
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

# Explicitly tell it to look one level up if it still can't find it
load_dotenv() 

# Try to get the key from either common name
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("API Key not found. Please ensure .env is in the root folder.")

genai.configure(api_key=api_key)

def get_gemini_analysis(image_file, prompt):
    img = Image.open(image_file)
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content([prompt, img])
    return response.text