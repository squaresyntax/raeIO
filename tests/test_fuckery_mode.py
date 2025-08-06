import json
import os

import pytest


from generative_media_manager import GenerativeMediaManager
from tts_manager import TTSManager
from plugin_system import PluginRegistry
from task_memory import TaskMemory
from browser_automation import BrowserAutomation
from raeio_agent import RAEIOAgent


def test_generative_media_manager_encrypts(tmp_path):
    mgr = GenerativeMediaManager(output_dir=tmp_path, fuckery_mode=True)
    path = mgr.generate_image("cat")
    assert path.endswith(".enc")
    assert (tmp_path / "image_result.png.enc").read_bytes() == b"ENCRYPTED"
    mgr2 = GenerativeMediaManager(output_dir=tmp_path, fuckery_mode=False)
    path2 = mgr2.generate_image("dog")
    assert not path2.endswith(".enc")
    assert (tmp_path / "image_result.png").read_bytes() == b""


def test_tts_manager_encrypts(tmp_path):
    mgr = TTSManager(cache_dir=str(tmp_path), fuckery_mode=True)
    path = mgr.synthesize("hello")
    assert path.endswith(".enc")
    assert (tmp_path / os.path.basename(path)).read_bytes() == b"ENCRYPTED"
    mgr2 = TTSManager(cache_dir=str(tmp_path), fuckery_mode=False)
    path2 = mgr2.synthesize("hello")
    assert not path2.endswith(".enc")
    assert (tmp_path / os.path.basename(path2)).read_bytes() == b"FAKEAUDIO"


def test_plugin_registry_limits(tmp_path):
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    (plugin_dir / "echo.py").write_text("def run(prompt=None, context=None):\n    return 'ok'\n")
    reg = PluginRegistry(plugin_dir=str(plugin_dir), fuckery_mode=False)
    assert reg.execute_plugin("echo") == "ok"
    reg2 = PluginRegistry(plugin_dir=str(plugin_dir), fuckery_mode=True)
    with pytest.raises(RuntimeError):
        reg2.execute_plugin("echo")


def test_task_memory_redacts(tmp_path):
    mem_path = tmp_path / "mem.jsonl"
    mem = TaskMemory(path=str(mem_path), fuckery_mode=True)
    mem.log_task("type", "prompt", {"a": 1}, "/tmp/out", True, 0.1)
    entry = json.loads(mem_path.read_text().strip())
    assert entry["prompt"] == "REDACTED"
    assert entry["context"] == "REDACTED"
    assert entry["output_path"] is None
    mem2_path = tmp_path / "mem2.jsonl"
    mem2 = TaskMemory(path=str(mem2_path), fuckery_mode=False)
    mem2.log_task("type", "prompt", {"a": 1}, "/tmp/out", True, 0.1)
    entry2 = json.loads(mem2_path.read_text().strip())
    assert entry2["prompt"] == "prompt"
    assert entry2["context"] == {"a": 1}
    assert entry2["output_path"] == "/tmp/out"


def test_browser_automation_stealth():
    b1 = BrowserAutomation(headless=False, user_agent=None, fuckery_mode=True)
    assert b1.headless is True
    assert b1.user_agent is not None
    b2 = BrowserAutomation(headless=False, user_agent=None, fuckery_mode=False)
    assert b2.headless is False
    assert b2.user_agent is None


def test_agent_propagates_flag(tmp_path):
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    config = {
        "fuckery_mode": True,
        "memory_path": str(tmp_path / "mem.jsonl"),
        "plugin_dir": str(plugin_dir),
        "tts_cache_dir": str(tmp_path / "tts"),
        "media_output_dir": str(tmp_path / "media"),
    }
    agent = RAEIOAgent(config, logger=None)
    assert agent.fuckery_mode is True
    assert agent.memory.fuckery_mode is True
    assert agent.plugin_registry.fuckery_mode is True
    assert agent.tts_manager.fuckery_mode is True
    assert agent.browser_automation.fuckery_mode is True
    assert agent.media_manager.fuckery_mode is True

