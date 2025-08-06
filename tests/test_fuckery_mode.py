import os
import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from raeio_agent import RAEIOAgent


class DummyTTS:
    def tts(self, text, speaker_wav=None, emotion=None):
        return b"0"

    def save_wav(self, wav, fpath):
        with open(fpath, "wb") as f:
            f.write(wav)

    def list_voices(self):
        return []


def test_fuckery_mode_affects_subsystems(tmp_path):
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    (plugin_dir / "echo.py").write_text(
        "def run(fuckery_mode=False, **kwargs):\n    return fuckery_mode\n"
    )
    config = {
        "plugin_dir": str(plugin_dir),
        "memory_path": str(tmp_path / "mem.jsonl"),
        "temp_dir": str(tmp_path / "temp"),
        "cache_dir": str(tmp_path / "cache"),
        "tts_cache_dir": str(tmp_path / "tts"),
        "browser_headless": False,
    }
    agent = RAEIOAgent(config, logger=None)

    # Mode off by default
    assert agent.plugin_registry.execute_plugin("echo") is False
    agent.memory.log_task("a", "b", {}, None, True, 0.1)
    with open(config["memory_path"]) as f:
        first_line = f.readline().strip()
    assert first_line.startswith("{")
    assert agent.cache_manager.secure_delete is False
    assert agent.browser_automation.headless is False

    # Enable fuckery mode
    agent.set_fuckery_mode(True)
    assert agent.plugin_registry.execute_plugin("echo") is True
    agent.memory.log_task("a", "b", {}, None, True, 0.1)
    with open(config["memory_path"]) as f:
        lines = [l.strip() for l in f.readlines()]
    assert lines[-1].startswith("ENC:")
    assert agent.cache_manager.secure_delete is True
    assert agent.browser_automation.headless is True
    assert agent.browser_automation.user_agent.startswith("Mozilla")
    agent.tts_manager.tts = DummyTTS()
    path = agent.speak("hi")
    assert os.path.basename(path).startswith("enc_")

    # Disable again
    agent.set_fuckery_mode(False)
    assert agent.plugin_registry.execute_plugin("echo") is False
    agent.memory.log_task("a", "b", {}, None, True, 0.1)
    with open(config["memory_path"]) as f:
        last_line = f.readlines()[-1].strip()
    assert last_line.startswith("{")
    assert agent.cache_manager.secure_delete is False
    agent.tts_manager.tts = DummyTTS()
    path2 = agent.speak("hi")
    assert not os.path.basename(path2).startswith("enc_")
    assert agent.browser_automation.headless is False

