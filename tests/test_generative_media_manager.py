import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from generative_media_manager import GenerativeMediaManager


def test_generate_image(tmp_path):
    manager = GenerativeMediaManager(output_dir=tmp_path)
    path = manager.generate_image("a test image")
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0


def test_generate_audio(tmp_path):
    manager = GenerativeMediaManager(output_dir=tmp_path)
    path = manager.generate_audio("hello world")
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0


def test_generate_video(tmp_path):
    manager = GenerativeMediaManager(output_dir=tmp_path)
    path = manager.generate_video("a video", duration=1)
    assert os.path.exists(path)
    assert os.path.getsize(path) > 0

