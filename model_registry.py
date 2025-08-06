import logging
import os
import uuid
from types import SimpleNamespace
from typing import Callable, Dict


class PlaceholderModel:
    """Simple generator that creates placeholder files."""

    def __init__(self, extension: str):
        self.extension = extension

    def generate(self, prompt: str, output_dir: str, **kwargs) -> str:
        os.makedirs(output_dir, exist_ok=True)
        fname = f"placeholder_{uuid.uuid4().hex}{self.extension}"
        path = os.path.join(output_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"Generated placeholder for prompt: {prompt}\n")
        return path


class ModelRegistry:
    """Registry mapping model names to loader functions."""

    _loaders: Dict[str, Callable[[], object]] = {}
    _models: Dict[str, object] = {}
    logger = logging.getLogger("ModelRegistry")

    @classmethod
    def register(cls, name: str, loader: Callable[[], object]) -> None:
        cls._loaders[name] = loader

    @classmethod
    def get_model(cls, name: str):
        if name not in cls._models:
            if name not in cls._loaders:
                raise KeyError(f"Model '{name}' not registered")
            cls._models[name] = cls._loaders[name]()
        return cls._models[name]


# --- Default loader functions -------------------------------------------------

def load_stable_diffusion():
    try:
        from diffusers import StableDiffusionPipeline  # type: ignore
    except Exception as e:  # pragma: no cover - optional dependency
        ModelRegistry.logger.warning("Stable Diffusion unavailable: %s", e)
        return PlaceholderModel(".png")

    def generate(prompt: str, output_dir: str, **kwargs) -> str:
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5"
        )
        image = pipe(prompt).images[0]
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"sd_{uuid.uuid4().hex}.png")
        image.save(path)
        return path

    return SimpleNamespace(generate=generate)


def load_bark():
    try:
        from bark import generate_audio, SAMPLE_RATE  # type: ignore
        from scipy.io.wavfile import write  # type: ignore
    except Exception as e:  # pragma: no cover - optional dependency
        ModelRegistry.logger.warning("Bark unavailable: %s", e)
        return PlaceholderModel(".wav")

    def generate(prompt: str, output_dir: str, **kwargs) -> str:
        audio_array = generate_audio(prompt)
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"bark_{uuid.uuid4().hex}.wav")
        write(path, SAMPLE_RATE, audio_array)
        return path

    return SimpleNamespace(generate=generate)


def load_stable_video_diffusion():
    try:
        import torch  # type: ignore
    except Exception as e:  # pragma: no cover - optional dependency
        ModelRegistry.logger.warning("Stable Video Diffusion unavailable: %s", e)
        return PlaceholderModel(".mp4")

    def generate(prompt: str, output_dir: str, duration: int = 5, **kwargs) -> str:
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"svd_{uuid.uuid4().hex}.mp4")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"Placeholder video for prompt: {prompt}, duration: {duration}\n")
        return path

    return SimpleNamespace(generate=generate)


ModelRegistry.register("stable_diffusion", load_stable_diffusion)
ModelRegistry.register("bark", load_bark)
ModelRegistry.register("stable_video_diffusion", load_stable_video_diffusion)
