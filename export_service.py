import json
import os
from datetime import datetime
from PIL import Image


def make_safe_filename(name):
    safe = ""
    for c in name:
        if c.isalpha() or c.isdigit() or c in " _-":
            safe = safe + c
    safe = safe.rstrip()
    if not safe:
        safe = "album"
    return safe


def get_unique_path(folder, base_name, ext):
    candidate = os.path.join(folder, base_name + ext)
    if not os.path.exists(candidate):
        return candidate

    version = 2
    while True:
        candidate = os.path.join(folder, base_name + "_v" + str(version) + ext)
        if not os.path.exists(candidate):
            return candidate
        version = version + 1


def _notify(status_callback, message):
    if status_callback:
        try:
            status_callback(message)
        except Exception:
            pass


def export_album_data(folder_path, album_name, metadata, tracklist, cover_image, status_callback=None):
    if not os.path.exists(folder_path):
        raise FileNotFoundError("Selected folder does not exist: " + folder_path)

    if not (cover_image and isinstance(cover_image, Image.Image)):
        raise ValueError("Provided cover_image is not a valid PIL Image instance.")

    safe_name = make_safe_filename(album_name)

    json_path = get_unique_path(folder_path, safe_name + "_metadata", ".json")
    png_path = get_unique_path(folder_path, safe_name + "_cover", ".png")
    thumb_path = get_unique_path(folder_path, safe_name + "_cover_thumb", ".png")

    track_count = 0
    if isinstance(tracklist, list):
        track_count = len(tracklist)

    export_payload = {
        "export_version": "1.0",
        "exported_at": datetime.now().isoformat(),
        "track_count": track_count,
        "metadata": metadata,
        "tracklist": tracklist,
    }

    _notify(status_callback, "Writing metadata JSON...")
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(export_payload, json_file, indent=4, ensure_ascii=False)

    _notify(status_callback, "Saving cover artwork (PNG)...")
    cover_image.save(png_path, "PNG", optimize=True)

    _notify(status_callback, "Saving cover thumbnail...")
    thumb = cover_image.copy()
    thumb.thumbnail((200, 200), Image.LANCZOS)
    thumb.save(thumb_path, "PNG", optimize=True)

    _notify(status_callback, "Export complete.")
    return json_path, png_path
