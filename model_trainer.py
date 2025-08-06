"""Utilities for training or fine-tuning different models.

This module provides lightweight adapter hooks that call per-model trainer
implementations. The heavy model code is intentionally not bundled; instead we
dispatch to thin wrappers that save checkpoints and metadata for later use.
"""

import os
from sd_trainer import train_sd
from llama_trainer import train_llama

DEFAULT_CHECKPOINT_DIR = "checkpoints"


def train_model(model: str, dataset_path: str, output_dir: str = DEFAULT_CHECKPOINT_DIR):
    """Route training to the appropriate per-model adapter.

    Args:
        model: Identifier for the model to train (e.g., ``"sd"`` or ``"llama"``).
        dataset_path: Path to the local dataset used for fine-tuning.
        output_dir: Directory where checkpoints and metadata will be stored.

    Returns:
        Dictionary describing the generated checkpoint and metadata files.
    """
    model = model.lower()
    target_dir = os.path.join(output_dir, model)
    if model == "sd":
        return train_sd(dataset_path, target_dir)
    if model == "llama":
        return train_llama(dataset_path, target_dir)
    raise ValueError(f"Unsupported model type: {model}")


# Legacy placeholder functions kept for compatibility with earlier code. They
# still remove temporary files but do not produce checkpoints.
def train_voice_model(temp_audio_path):
    os.remove(temp_audio_path)
    return "Voice model updated with the new style."


def train_image_model(temp_image_path):
    os.remove(temp_image_path)
    return "Image generation style updated."


def train_video_model(temp_video_path):
    os.remove(temp_video_path)
    return "Video generation style updated."


def train_audio_model(temp_audio_path):
    os.remove(temp_audio_path)
    return "Audio/music generation style updated."