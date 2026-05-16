"""
image_service.py - AI Image Generation System
Handles API requests to Pollinations.ai and processes images using PIL.
"""
import requests
from PIL import Image
import io
from urllib.parse import quote

def generate_cover(prompt, genre_style=None):
    """
    Gemini'den gelen promptu kullanarak Pollinations.ai üzerinden albüm kapağı üretir.
    Görsel byte dizisini PIL Image nesnesine dönüştürerek döndürür.
    """
    full_prompt = prompt
    if genre_style:
        full_prompt = f"{prompt}, {genre_style} album art style, professional graphic design, crisp details, high resolution"
        
    encoded_prompt = quote(full_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=600&height=600&nologo=true"
    
    try:
        response = requests.get(url, timeout=45)
        response.raise_for_status()
        
        image_bytes = response.content
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return img
    except requests.exceptions.RequestException as e:
        print(f"Pollinations.ai API bağlantı hatası: {e}")
        raise Exception(f"Failed to fetch image from Pollinations.ai: {e}")
