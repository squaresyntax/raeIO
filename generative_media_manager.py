import os
import logging


class GenerativeMediaManager:
    def __init__(self, output_dir="outputs", logger=None, fuckery_mode=False):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger = logger or logging.getLogger("GenerativeMediaManager")
        self.fuckery_mode = fuckery_mode

    def _save(self, path):
        if self.fuckery_mode:
            path = f"{path}.enc"
            with open(path, "wb") as f:
                f.write(b"ENCRYPTED")
        else:
            with open(path, "wb") as f:
                f.write(b"")
        return path

    def generate_image(self, prompt: str) -> str:
        self.logger.info(f"Generating image for prompt: {prompt}")
        image_path = os.path.join(self.output_dir, "image_result.png")
        return self._save(image_path)

    def generate_video(self, prompt: str, duration=5) -> str:
        self.logger.info(f"Generating video for prompt: {prompt}, duration: {duration}s")
        video_path = os.path.join(self.output_dir, "video_result.mp4")
        return self._save(video_path)

    def generate_audio(self, prompt: str, duration=5) -> str:
        self.logger.info(f"Generating audio for prompt: {prompt}, duration: {duration}s")
        audio_path = os.path.join(self.output_dir, "audio_result.wav")
        return self._save(audio_path)
