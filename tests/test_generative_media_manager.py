import os
import pathlib
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import numpy as np
from PIL import Image

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from generative_media_manager import GenerativeMediaManager, ModelConfig


class DummyImagePipeline:
    @staticmethod
    def from_pretrained(path, **kwargs):
        return DummyImagePipeline()

    def __call__(self, prompt, **kwargs):  # pragma: no cover - trivial
        img = Image.new("RGB", (4, 4), color="white")
        return MagicMock(images=[img])


class DummyVideoPipeline:
    @staticmethod
    def from_pretrained(path, **kwargs):
        return DummyVideoPipeline()

    def __call__(self, prompt, num_frames=4, **kwargs):  # pragma: no cover
        frames = np.zeros((num_frames, 4, 4, 3), dtype=np.uint8)
        return MagicMock(frames=[frames])


def dummy_generate_audio(prompt, **kwargs):  # pragma: no cover - simple stub
    return np.ones(1000, dtype=np.float32) * 0.1


def dummy_mimwrite(path, frames, fps=8):  # pragma: no cover - simple stub
    with open(path, "wb") as f:
        f.write(b"video")


@patch("generative_media_manager.StableDiffusionPipeline", DummyImagePipeline)
@patch("generative_media_manager.StableVideoDiffusionPipeline", DummyVideoPipeline)
@patch("generative_media_manager.bark_generate_audio", dummy_generate_audio)
@patch("generative_media_manager.BARK_SAMPLE_RATE", 1000)
@patch("generative_media_manager.imageio", SimpleNamespace(mimwrite=dummy_mimwrite))
def test_generate_media(tmp_path):
    manager = GenerativeMediaManager(
        output_dir=str(tmp_path),
        image=ModelConfig(model_path="dummy"),
        video=ModelConfig(model_path="dummy"),
        audio=ModelConfig(model_path="dummy"),
    )

    image_path = manager.generate_image("test image")
    assert os.path.exists(image_path)
    assert os.path.getsize(image_path) > 0

    video_path = manager.generate_video("test video")
    assert os.path.exists(video_path)
    assert os.path.getsize(video_path) > 0

    audio_path = manager.generate_audio("test audio")
    assert os.path.exists(audio_path)
    assert os.path.getsize(audio_path) > 0

