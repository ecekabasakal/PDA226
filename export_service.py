"""
export_service.py - Export Subsystem
Saves album metadata as JSON and cover artwork as PNG.
"""
import json
import os
from PIL import Image

def export_album_data(folder_path, album_name, metadata, tracklist, cover_image):
    """
    Albüm meta verilerini ve Last.fm şarkı listesini tek bir JSON dosyası; 
    albüm kapağını ise PNG görseli olarak kullanıcının seçtiği klasöre kaydeder.
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Selected directory does not exist: {folder_path}")
        
    safe_name = "".join([c for c in album_name if c.isalpha() or c.isdigit() or c in ' _-']).rstrip()
    if not safe_name:
        safe_name = "album"
        
    json_filename = f"{safe_name}_metadata.json"
    png_filename = f"{safe_name}_cover.png"
    
    json_path = os.path.join(folder_path, json_filename)
    png_path = os.path.join(folder_path, png_filename)
    
    export_payload = {
        "metadata": metadata,  
        "tracklist": tracklist  
    }
    
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(export_payload, json_file, indent=4, ensure_ascii=False)
        
    
    if cover_image and isinstance(cover_image, Image.Image):
        cover_image.save(png_path, "PNG")
    else:
        
        raise ValueError("Provided cover_image is not a valid PIL Image instance.")
        
    return json_path, png_path
