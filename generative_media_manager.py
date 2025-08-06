"""Utilities for generating images, audio and simple videos.

This module provides a small abstraction layer ("adapters") around
third‑party generative libraries so that the rest of the codebase can work
with a unified interface.  Each adapter implements three methods:

``load``
    Prepare the underlying model.  This is typically called lazily the first
    time ``infer`` is executed so that importing the module does not trigger
    heavyweight initialisation.

``infer``
    Run inference and return the generated object.  For image and audio
    generation the result is saved to a file whose path is returned.

``train``
    Optional method; most adapters in this repository raise
    ``NotImplementedError``.

The concrete adapters use the following libraries:

* :mod:`diffusers` – a tiny Stable Diffusion pipeline for image generation.
* :mod:`TTS` – the Coqui TTS library for speech synthesis.
* :mod:`imageio` – for assembling a simple video from generated frames.

The goal of these implementations is not to provide state‑of‑the-art
generation, but to exercise the interaction with real libraries so that the
manager can be extended later on.
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


LOGGER = logging.getLogger("GenerativeMediaManager")


class GeneratorAdapter(ABC):
    """Base class for generator adapters."""

    def __init__(self) -> None:
        self._is_loaded = False

    @abstractmethod
    def load(self) -> None:
        """Load model weights or perform other heavy initialisation."""

    @abstractmethod
    def infer(self, prompt: str, **kwargs):  # pragma: no cover - interface
        """Generate output for ``prompt``."""

    def train(self, *args, **kwargs) -> None:  # pragma: no cover - optional
        """Optional training hook."""
        raise NotImplementedError("Training not implemented for this adapter")


class StableDiffusionAdapter(GeneratorAdapter):
    """Image generation via a tiny Stable Diffusion pipeline."""

    def __init__(self) -> None:
        super().__init__()
        self.pipeline = None  # populated lazily

    def load(self) -> None:
        from diffusers import StableDiffusionPipeline
        import torch

        model_id = "hf-internal-testing/tiny-stable-diffusion-torch"
        self.pipeline = StableDiffusionPipeline.from_pretrained(
            model_id, safety_checker=None, torch_dtype=torch.float32
        )
        self.pipeline.to("cpu")
        self._is_loaded = True

    def infer(self, prompt: str, num_inference_steps: int = 1):
        if not self._is_loaded:
            self.load()
        result = self.pipeline(prompt, num_inference_steps=num_inference_steps)
        return result.images[0]


class CoquiTTSAdapter(GeneratorAdapter):
    """Text to speech generation using Coqui TTS."""

    def __init__(self, model_name: str = "tts_models/en/ljspeech/tacotron2-DDC") -> None:
        super().__init__()
        self.tts = None
        self.model_name = model_name

    def load(self) -> None:
        from TTS.api import TTS

        self.tts = TTS(model_name=self.model_name)
        self._is_loaded = True

    def infer(self, prompt: str, file_path: str) -> str:
        if not self._is_loaded:
            self.load()
        # The library writes directly to ``file_path``
        self.tts.tts_to_file(text=prompt, file_path=file_path)
        return file_path


class SimpleVideoAdapter(GeneratorAdapter):
    """Create a video by duplicating a generated frame."""

    def __init__(self, image_adapter: Optional[StableDiffusionAdapter] = None) -> None:
        super().__init__()
        self.image_adapter = image_adapter or StableDiffusionAdapter()

    def load(self) -> None:
        # Loading is delegated to the image adapter
        if not self.image_adapter._is_loaded:
            self.image_adapter.load()
        self._is_loaded = True

    def infer(self, prompt: str, duration: int, file_path: str, fps: int = 1) -> str:
        if not self._is_loaded:
            self.load()
        frame = self.image_adapter.infer(prompt)
        import numpy as np
        import imageio

        frames = [np.array(frame)] * max(1, duration * fps)
        imageio.mimsave(file_path, frames, fps=fps)
        return file_path


@dataclass
class GenerativeMediaManager:
    """High level helper exposing simple generation methods."""

    output_dir: str = "outputs"
    logger: logging.Logger = LOGGER

    def __post_init__(self) -> None:
        os.makedirs(self.output_dir, exist_ok=True)
        self.image_adapter = StableDiffusionAdapter()
        self.audio_adapter = CoquiTTSAdapter()
        self.video_adapter = SimpleVideoAdapter(self.image_adapter)

    # Public API ---------------------------------------------------------
    def generate_image(self, prompt: str) -> str:
        self.logger.info("Generating image for prompt: %s", prompt)
        image = self.image_adapter.infer(prompt)
        path = os.path.join(self.output_dir, "image_result.png")
        image.save(path)
        return path

    def generate_audio(self, prompt: str) -> str:
        self.logger.info("Generating audio for prompt: %s", prompt)
        path = os.path.join(self.output_dir, "audio_result.wav")
        self.audio_adapter.infer(prompt, file_path=path)
        return path

    def generate_video(self, prompt: str, duration: int = 5) -> str:
        self.logger.info("Generating video for prompt: %s", prompt)
        path = os.path.join(self.output_dir, "video_result.mp4")
        self.video_adapter.infer(prompt, duration=duration, file_path=path)
        return path

