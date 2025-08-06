"""Utilities for generating media from text prompts.

This module provides a :class:`GenerativeMediaManager` capable of creating
images, videos and audio clips.  Real models such as Stable Diffusion, Stable
Video Diffusion and Bark are used when the corresponding libraries are
available.  Model paths and generation parameters are configurable so different
pipelines can easily be swapped in.

The implementations are intentionally lightweight – imports happen lazily and
model loading is deferred until the first generation call.  This keeps the
module usable even in environments where the heavy model dependencies are not
installed.  In such cases an informative ``RuntimeError`` is raised.
"""

from __future__ import annotations

import logging
import os
import wave
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import numpy as np
from PIL import Image

# Optional third‑party libraries.  These are imported lazily to avoid mandatory
# heavy dependencies at import time.  They are set to ``None`` when unavailable
# so tests can patch them.
try:  # pragma: no cover - simply testing availability
    from diffusers import StableDiffusionPipeline, StableVideoDiffusionPipeline  # type: ignore
except Exception:  # pragma: no cover - module not installed
    StableDiffusionPipeline = None  # type: ignore
    StableVideoDiffusionPipeline = None  # type: ignore

try:  # pragma: no cover
    from bark import generate_audio as bark_generate_audio, SAMPLE_RATE as BARK_SAMPLE_RATE  # type: ignore
except Exception:  # pragma: no cover - module not installed
    bark_generate_audio = None  # type: ignore
    BARK_SAMPLE_RATE = 22050

try:  # pragma: no cover
    import imageio.v2 as imageio
except Exception:  # pragma: no cover - module not installed
    imageio = None  # type: ignore


@dataclass
class ModelConfig:
    """Configuration for a generative model."""

    model_path: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)


class GenerativeMediaManager:
    """Generate images, videos and audio from text prompts."""

    def __init__(
        self,
        output_dir: str = "outputs",
        logger: Optional[logging.Logger] = None,
        *,
        image: Optional[ModelConfig] = None,
        video: Optional[ModelConfig] = None,
        audio: Optional[ModelConfig] = None,
    ) -> None:
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        self.logger = logger or logging.getLogger("GenerativeMediaManager")

        self.image_cfg = image or ModelConfig()
        self.video_cfg = video or ModelConfig()
        self.audio_cfg = audio or ModelConfig()

        # Model instances are loaded lazily
        self._image_pipe = None
        self._video_pipe = None

    # ------------------------------------------------------------------ utils
    def _load_image_pipe(self) -> Any:
        if self._image_pipe is None:
            if StableDiffusionPipeline is None:
                raise RuntimeError("diffusers is not installed")
            if not self.image_cfg.model_path:
                raise ValueError("image model path not configured")
            self.logger.debug("Loading image model: %s", self.image_cfg.model_path)
            self._image_pipe = StableDiffusionPipeline.from_pretrained(
                self.image_cfg.model_path, **self.image_cfg.params
            )
        return self._image_pipe

    def _load_video_pipe(self) -> Any:
        if self._video_pipe is None:
            if StableVideoDiffusionPipeline is None:
                raise RuntimeError("diffusers is not installed")
            if not self.video_cfg.model_path:
                raise ValueError("video model path not configured")
            self.logger.debug("Loading video model: %s", self.video_cfg.model_path)
            self._video_pipe = StableVideoDiffusionPipeline.from_pretrained(
                self.video_cfg.model_path, **self.video_cfg.params
            )
        return self._video_pipe

    # ---------------------------------------------------------------- generation
    def generate_image(self, prompt: str, **kwargs: Any) -> str:
        """Generate an image using a Stable Diffusion compatible pipeline."""

        pipe = self._load_image_pipe()
        self.logger.info("Generating image for prompt: %s", prompt)
        result = pipe(prompt, **{**self.image_cfg.params, **kwargs})
        # Result object from diffusers has an ``images`` attribute
        image: Image.Image = result.images[0]
        image_path = os.path.join(self.output_dir, "image_result.png")
        image.save(image_path)
        return image_path

    def generate_video(self, prompt: str, num_frames: int = 8, fps: int = 8, **kwargs: Any) -> str:
        """Generate a short video clip using a Stable Video Diffusion pipeline."""

        if imageio is None:
            raise RuntimeError("imageio is not installed")
        pipe = self._load_video_pipe()
        self.logger.info("Generating video for prompt: %s", prompt)
        result = pipe(prompt, num_frames=num_frames, **{**self.video_cfg.params, **kwargs})
        frames = result.frames[0]
        video_path = os.path.join(self.output_dir, "video_result.mp4")
        imageio.mimwrite(video_path, frames, fps=fps)
        return video_path

    def generate_audio(self, prompt: str, **kwargs: Any) -> str:
        """Generate an audio clip using the Bark model."""

        if bark_generate_audio is None:
            raise RuntimeError("bark is not installed")
        if self.audio_cfg.model_path:
            # Bark uses the ``history_prompt`` parameter to select pre-trained
            # voices; we pass the model path through here if provided.
            kwargs.setdefault("history_prompt", self.audio_cfg.model_path)

        self.logger.info("Generating audio for prompt: %s", prompt)
        audio_array = bark_generate_audio(prompt, **{**self.audio_cfg.params, **kwargs})

        audio_path = os.path.join(self.output_dir, "audio_result.wav")
        self._write_wav(audio_path, audio_array, BARK_SAMPLE_RATE)
        return audio_path

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _write_wav(path: str, audio_array: np.ndarray, sample_rate: int) -> None:
        """Write a numpy array of floats to a 16‑bit PCM WAV file."""

        audio = np.clip(audio_array, -1.0, 1.0)
        audio_int16 = (audio * 32767).astype(np.int16)
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_int16.tobytes())


__all__ = ["GenerativeMediaManager", "ModelConfig"]

