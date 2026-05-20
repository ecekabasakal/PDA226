import requests
from PIL import Image, ImageEnhance
import io
import time
from urllib.parse import quote


def clean_prompt(text):
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    while "  " in text:
        text = text.replace("  ", " ")
    text = text.strip()
    if len(text) > 500:
        text = text[:500]
    return text


def enhance_cover(pil_image, contrast=1.10, saturation=1.15):
    img = ImageEnhance.Contrast(pil_image).enhance(contrast)
    img = ImageEnhance.Color(img).enhance(saturation)
    return img


def _notify(status_callback, message):
    if status_callback:
        try:
            status_callback(message)
        except Exception:
            pass


def generate_cover(prompt, genre_style=None, status_callback=None):
    prompt = clean_prompt(prompt)

    full_prompt = prompt
    if genre_style:
        full_prompt = prompt + ", " + genre_style + " album art style, professional graphic design, crisp details, high resolution"

    encoded_prompt = quote(full_prompt)
    url = "https://image.pollinations.ai/prompt/" + encoded_prompt + "?width=600&height=600&referrer=AlbumCoverStudio"

    last_error = None
    max_tries = 3

    for attempt in range(max_tries):
        try:
            _notify(status_callback, "Connecting to Pollinations.ai (attempt " + str(attempt + 1) + "/" + str(max_tries) + ")...")
            print("Pollinations attempt " + str(attempt + 1) + "/" + str(max_tries))
            response = requests.get(url, timeout=60)
            response.raise_for_status()

            _notify(status_callback, "Decoding image bytes...")
            image_bytes = response.content
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            _notify(status_callback, "Enhancing cover artwork...")
            img = enhance_cover(img)
            return img

        except requests.exceptions.RequestException as e:
            print("Request failed: " + str(e))
            last_error = e
            if attempt < max_tries - 1:
                time.sleep(16)

    raise Exception("Failed to fetch image from Pollinations.ai after " + str(max_tries) + " tries: " + str(last_error))


def resize_for_display(pil_image, size=(160, 160)):
    return pil_image.resize(size, Image.LANCZOS)
