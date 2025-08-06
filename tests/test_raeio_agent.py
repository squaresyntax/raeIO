import os
import sys
import textwrap

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from raeio_agent import RAEIOAgent


class DummyLogger:
    def info(self, *_args, **_kwargs):
        pass


def make_agent(tmp_path, extra_config=None):
    config = {}
    if tmp_path is not None:
        config["output_dir"] = str(tmp_path / "out")
    if extra_config:
        config.update(extra_config)
    return RAEIOAgent(config, logger=DummyLogger())


def test_image_generation(tmp_path):
    agent = make_agent(tmp_path)
    result = agent.run_task("image", "a cat", {})
    assert result.endswith("image_result.png")


def test_video_generation(tmp_path):
    agent = make_agent(tmp_path)
    result = agent.run_task("video", "a dog", {})
    assert result.endswith("video_result.mp4")


def test_audio_generation(tmp_path):
    agent = make_agent(tmp_path)
    result = agent.run_task("audio", "a song", {})
    assert result.endswith("audio_result.wav")


def test_text_summarization():
    agent = make_agent(tmp_path=None)  # output_dir not needed
    summary = agent.run_task("summarize", "This is a long text that should be shortened for testing purposes.", {})
    assert "..." in summary or len(summary.split()) <= 20


def test_plugin_execution(tmp_path):
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    plugin_code = textwrap.dedent(
        """
        PLUGIN_META = {"name": "echo", "desc": "Echo plugin"}

        def run(prompt, context):
            return f"echo:{prompt}"
        """
    )
    (plugin_dir / "echo.py").write_text(plugin_code)
    agent = make_agent(tmp_path, {"plugin_dir": str(plugin_dir)})
    result = agent.run_task("anything", "hello", {}, plugin="echo")
    assert result == "echo:hello"


def test_browser_mode(monkeypatch):
    agent = make_agent(tmp_path=None)

    def fake_run_script(url, actions):
        return f"visited {url}"

    monkeypatch.setattr(agent.browser_automation, "run_script", fake_run_script)
    result = agent.run_task("browser", "", {"url": "http://example.com", "actions": []})
    assert "example.com" in result


def test_unknown_mode_raises():
    agent = make_agent(tmp_path=None)
    with pytest.raises(ValueError):
        agent.run_task("unknown", "prompt", {})

