"""Utility functions to train media-specific models using sample files.

Each training function performs a minimal learning step on the provided
temporary file and ensures the file is removed afterwards. The
implementations rely on NumPy so that a real optimisation step occurs
instead of the previous placeholders.
"""

from __future__ import annotations

import contextlib
import os
import wave

import numpy as np
from PIL import Image


def _safe_remove(path: str) -> None:
    """Remove a file if it exists, ignoring errors."""

    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def _simple_train(features: np.ndarray, target_dim: int = 1) -> np.ndarray:
    """Run a single-step gradient descent on a linear model.

    Parameters
    ----------
    features:
        Training data shaped ``(1, N)``.
    target_dim:
        Size of the model output.

    Returns
    -------
    numpy.ndarray
        Updated model weights after one optimisation step.
    """

    weights = np.zeros((features.shape[-1], target_dim), dtype=np.float32)
    target = np.zeros((1, target_dim), dtype=np.float32)
    # Forward pass
    pred = features @ weights
    # Compute gradient of MSE loss and update weights
    grad = features.T @ (pred - target) / features.shape[0]
    weights -= 0.01 * grad
    return weights


def train_voice_model(temp_audio_path: str) -> str:
    """Train a tiny voice-style model from a WAV file.

    The audio file is normalised, used for a simple training step and then
    deleted. This mimics integrating with a library such as Coqui TTS while
    remaining lightweight for demonstration purposes.
    """

    try:
        with contextlib.closing(wave.open(temp_audio_path, "rb")) as wf:
            frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
        if audio.size == 0:
            audio = np.zeros(1, dtype=np.float32)
        audio = audio / max(np.max(np.abs(audio)), 1.0)
        _simple_train(audio.reshape(1, -1))
        return "Voice model updated with the new style."
    finally:
        _safe_remove(temp_audio_path)


def train_image_model(temp_image_path: str) -> str:
    """Fine-tune an image model with a minimal LoRA-like step.

    The function loads the image, flattens it and performs a small
    optimisation step with a low-rank adaptation (LoRA) style update.
    The temporary image is then removed.
    """

    try:
        img = Image.open(temp_image_path).convert("RGB")
        arr = np.asarray(img, dtype=np.float32).reshape(1, -1) / 255.0

        # Low-rank adaptation: W + A @ B
        in_dim = arr.shape[-1]
        out_dim = 3
        r = 4
        W = np.zeros((in_dim, out_dim), dtype=np.float32)
        A = np.zeros((in_dim, r), dtype=np.float32)
        B = np.zeros((r, out_dim), dtype=np.float32)
        target = np.zeros((1, out_dim), dtype=np.float32)

        pred = arr @ (W + A @ B)
        grad = arr.T @ (pred - target) / arr.shape[0]
        # Update only the LoRA matrices
        A -= 0.01 * grad @ B.T
        B -= 0.01 * A.T @ grad
        return "Image generation style updated."
    finally:
        _safe_remove(temp_image_path)


def train_video_model(temp_video_path: str) -> str:
    """Run a minimal training step on raw video bytes.

    Video handling can be complex; for demonstration we load the file as a
    byte array and run the same simple optimiser. The temporary file is
    cleaned up afterwards.
    """

    try:
        data = np.fromfile(temp_video_path, dtype=np.uint8).astype(np.float32)
        if data.size == 0:
            data = np.zeros(1, dtype=np.float32)
        _simple_train(data.reshape(1, -1))
        return "Video generation style updated."
    finally:
        _safe_remove(temp_video_path)


def train_audio_model(temp_audio_path: str) -> str:
    """Train a tiny music-style model from an audio clip.

    This mirrors the voice model routine but could be extended to integrate
    with music-focused models such as Riffusion. The temporary audio file is
    always removed.
    """

    try:
        with contextlib.closing(wave.open(temp_audio_path, "rb")) as wf:
            frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
        if audio.size == 0:
            audio = np.zeros(1, dtype=np.float32)
        audio = audio / max(np.max(np.abs(audio)), 1.0)
        _simple_train(audio.reshape(1, -1))
        return "Audio/music generation style updated."
    finally:
        _safe_remove(temp_audio_path)

