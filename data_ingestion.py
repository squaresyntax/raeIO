import os
from urllib.parse import urlparse
from yt_dlp import YoutubeDL
import requests
from cache_manager import CacheManager

def download_and_extract(link_or_file, cache_manager=None):
    """
    Downloads and extracts data from a URL or uploaded file.
    - For YouTube/SoundCloud/Spotify: downloads audio or video.
    - For other links: downloads the file and infers type by extension.
    - For file uploads: saves to temp and infers type.
    Returns: (temp_file_path, detected_type, metadata)
    """
    def guess_type(ext):
        ext = ext.lower()
        if ext in [".jpg", ".jpeg", ".png", ".webp"]:
            return "image"
        elif ext in [".wav", ".mp3", ".aac", ".opus", ".flac", ".ogg"]:
            return "audio"
        elif ext in [".mp4", ".webm", ".avi", ".mov", ".mkv"]:
            return "video"
        elif ext in [".txt", ".pdf", ".md"]:
            return "text"
        else:
            return "unknown"

    if cache_manager is None:
        cache_manager = CacheManager()

    if isinstance(link_or_file, str):
        url = link_or_file
        if "youtube.com" in url or "youtu.be" in url or "soundcloud.com" in url or "spotify.com" in url:
            # Use yt_dlp for all major streaming sites
            with YoutubeDL({"outtmpl": "%(id)s.%(ext)s", "format": "bestaudio/best"}) as ydl:
                info = ydl.extract_info(url, download=False)
                ext = "." + info["ext"]
                temp_path = cache_manager.create_temp_file(suffix=ext)
                ydl.download([url])
                os.rename(f"{info['id']}{ext}", temp_path)
                detected_type = "audio" if info.get('vcodec') == 'none' else "video"
                return temp_path, detected_type, info
        elif url.startswith("http"):
            # Download direct file
            resp = requests.get(url, timeout=10)
            ext = os.path.splitext(urlparse(url).path)[-1]
            temp_path = cache_manager.create_temp_file(suffix=ext)
            with open(temp_path, "wb") as temp_file:
                temp_file.write(resp.content)
            dtype = guess_type(ext)
            return temp_path, dtype, {}
    else:
        # File-like object (upload)
        ext = os.path.splitext(getattr(link_or_file, 'name', ''))[-1]
        temp_path = cache_manager.create_temp_file(suffix=ext)
        with open(temp_path, "wb") as temp_file:
            temp_file.write(link_or_file.read())
        dtype = guess_type(ext)
        return temp_path, dtype, {}
