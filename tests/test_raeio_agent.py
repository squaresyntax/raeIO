import logging
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from raeio_agent import RAEIOAgent


def make_agent(tmp_path):
    config = {
        "memory_path": str(tmp_path / "mem.jsonl"),
        "temp_dir": str(tmp_path / "temp"),
        "cache_dir": str(tmp_path / "cache"),
        "plugin_dir": str(tmp_path / "plugins"),
        "tts_cache_dir": str(tmp_path / "tts_cache"),
    }
    return RAEIOAgent(config, logger=logging.getLogger("test"))


def test_run_task_art(tmp_path):
    agent = make_agent(tmp_path)
    result = agent.run_task("art", "sunset", {})
    assert "Art generated" in result


def test_run_task_audio(tmp_path):
    agent = make_agent(tmp_path)
    result = agent.run_task("audio", "melody", {})
    assert "Audio composed" in result


def test_run_task_text(tmp_path):
    agent = make_agent(tmp_path)
    result = agent.run_task("text", "This is a long passage", {})
    assert result.startswith("Summary:")


def test_run_task_unsupported(tmp_path):
    agent = make_agent(tmp_path)
    with pytest.raises(RuntimeError) as exc:
        agent.run_task("video", "prompt", {})
    assert "Unsupported task type" in str(exc.value)
