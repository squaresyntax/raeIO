import os
import logging
import yaml
from model_registry import ModelRegistry


class GenerativeMediaManager:
    def __init__(self, output_dir="outputs", config=None, config_path="config.yaml", logger=None):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger = logger or logging.getLogger("GenerativeMediaManager")
        if config is None:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        self.models_config = config.get("models", {})

    def _get_model(self, modality: str):
        cfg = self.models_config.get(modality, {})
        if not cfg.get("enabled", True):
            raise RuntimeError(f"{modality.capitalize()} generation disabled")
        name = cfg.get("name")
        if not name:
            raise RuntimeError(f"No model configured for {modality}")
        return ModelRegistry.get_model(name)

    def generate_image(self, prompt: str) -> str:
        self.logger.info(f"Generating image for prompt: {prompt}")
        model = self._get_model("image")
        return model.generate(prompt, self.output_dir)

    def generate_video(self, prompt: str, duration=5) -> str:
        self.logger.info(f"Generating video for prompt: {prompt}, duration: {duration}s")
        model = self._get_model("video")
        return model.generate(prompt, self.output_dir, duration=duration)

    def generate_audio(self, prompt: str, duration=5) -> str:
        self.logger.info(f"Generating audio for prompt: {prompt}, duration: {duration}s")
        model = self._get_model("audio")
        return model.generate(prompt, self.output_dir, duration=duration)
