import subprocess
import os

def compress_image(input_path, output_path):
    # Try WebP lossless, fallback to original if larger or fails
    try:
        result = subprocess.run(["cwebp", "-lossless", "-z", "9", input_path, "-o", output_path], check=False)
        if os.path.exists(output_path) and os.path.getsize(output_path) < os.path.getsize(input_path):
            return
        # fallback: just copy original
        with open(input_path, "rb") as src, open(output_path, "wb") as dst:
            dst.write(src.read())
    except Exception:
        with open(input_path, "rb") as src, open(output_path, "wb") as dst:
            dst.write(src.read())

def compress_audio(input_path, output_path):
    # Opus at high quality
    try:
        result = subprocess.run(["ffmpeg", "-y", "-i", input_path, "-c:a", "libopus", "-b:a", "96k", output_path], check=False, capture_output=True)
        if os.path.exists(output_path) and os.path.getsize(output_path) < os.path.getsize(input_path):
            return
        with open(input_path, "rb") as src, open(output_path, "wb") as dst:
            dst.write(src.read())
    except Exception:
        with open(input_path, "rb") as src, open(output_path, "wb") as dst:
            dst.write(src.read())

def compress_video(input_path, output_path):
    # AV1 or H.264 (CRF 18-28)
    try:
        result = subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-c:v", "libaom-av1", "-crf", "28", "-b:v", "0",
            "-c:a", "libopus", "-b:a", "96k",
            output_path
        ], check=False, capture_output=True)
        if os.path.exists(output_path) and os.path.getsize(output_path) < os.path.getsize(input_path):
            return
        with open(input_path, "rb") as src, open(output_path, "wb") as dst:
            dst.write(src.read())
    except Exception:
        with open(input_path, "rb") as src, open(output_path, "wb") as dst:
            dst.write(src.read())