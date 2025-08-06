import os
import sys
import tempfile
import wave
from pathlib import Path

from PIL import Image

# Ensure repository root is on sys.path when tests run from a subdirectory.
sys.path.append(str(Path(__file__).resolve().parent.parent))

from model_trainer import (
    train_audio_model,
    train_image_model,
    train_video_model,
    train_voice_model,
)


def _create_temp_wav() -> str:
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(8000)
        wf.writeframes(b"\x00\x00" * 800)
    return path


def _create_temp_image() -> str:
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    Image.new("RGB", (2, 2), color=(123, 222, 64)).save(path)
    return path


def _create_temp_video() -> str:
    fd, path = tempfile.mkstemp(suffix=".bin")
    os.close(fd)
    with open(path, "wb") as fh:
        fh.write(os.urandom(1024))
    return path


def test_train_voice_model():
    path = _create_temp_wav()
    message = train_voice_model(path)
    assert message.startswith("Voice model")
    assert not os.path.exists(path)


def test_train_image_model():
    path = _create_temp_image()
    message = train_image_model(path)
    assert message.startswith("Image generation")
    assert not os.path.exists(path)


def test_train_video_model():
    path = _create_temp_video()
    message = train_video_model(path)
    assert message.startswith("Video generation")
    assert not os.path.exists(path)


def test_train_audio_model():
    path = _create_temp_wav()
    message = train_audio_model(path)
    assert message.startswith("Audio/music")
    assert not os.path.exists(path)

