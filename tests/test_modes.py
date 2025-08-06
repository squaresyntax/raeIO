import io
import io
import json
import logging
import os
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

import browser_automation as ba_module
from raeio_agent import ModeFlags
from task_memory import TaskMemory
from cache_manager import CacheManager
from plugin_system import PluginRegistry
from tts_manager import TTSManager
from browser_automation import BrowserAutomation


def test_task_memory_modes(tmp_path):
    path = tmp_path / "mem.jsonl"
    mem = TaskMemory(path=str(path))
    flags = ModeFlags()
    mem.update_mode_flags(flags)

    flags.stealth_mode = True
    mem.log_task("t", "p", {}, "out", True, 1.0)
    assert path.read_text() == ""

    flags.stealth_mode = False
    flags.enable_fuckery()
    flags.stealth_mode = False
    mem.log_task("t", "p", {}, "out", True, 1.0)
    line = path.read_text().strip().splitlines()[0]
    decoded = flags.decrypt(line.encode()).decode()
    entry = json.loads(decoded)
    assert entry["task_type"] == "t"


def test_cache_manager_modes(tmp_path):
    log_stream = io.StringIO()
    logger = logging.getLogger("cachetest")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(log_stream)
    logger.addHandler(handler)

    cm = CacheManager(temp_dir=str(tmp_path / "temp"), cache_dir=str(tmp_path / "cache"), max_temp_mb=0, max_cache_mb=0, logger=logger)
    flags = ModeFlags()
    cm.update_mode_flags(flags)

    os.makedirs(cm.temp_dir, exist_ok=True)
    with open(os.path.join(cm.temp_dir, "file.txt"), "w") as f:
        f.write("data")
    cm.enforce_thresholds()
    assert "cleaning" in log_stream.getvalue()

    log_stream.truncate(0)
    log_stream.seek(0)
    flags.stealth_mode = True
    with open(os.path.join(cm.temp_dir, "file2.txt"), "w") as f:
        f.write("data")
    cm.enforce_thresholds()
    assert log_stream.getvalue() == ""

    flags.enable_fuckery()
    with pytest.raises(RuntimeError):
        cm.manual_clean()


def test_plugin_registry_modes(tmp_path):
    plugdir = tmp_path / "plugins"
    plugdir.mkdir()
    (plugdir / "simple.py").write_text("def run(**kwargs):\n    return 'ok'\n")
    registry = PluginRegistry(plugin_dir=str(plugdir))
    flags = ModeFlags()
    registry.update_mode_flags(flags)
    assert registry.execute_plugin("simple") == "ok"
    flags.stealth_mode = True
    with pytest.raises(RuntimeError):
        registry.execute_plugin("simple")


def test_tts_manager_stealth_mode():
    tts = TTSManager()
    flags = ModeFlags()
    tts.update_mode_flags(flags)
    flags.stealth_mode = True
    with pytest.raises(RuntimeError):
        tts.synthesize("hello")


def test_browser_automation_modes(monkeypatch):
    flags = ModeFlags()
    ba = BrowserAutomation(headless=False)
    ba.update_mode_flags(flags)

    class DummyPage:
        def goto(self, url):
            pass

        def click(self, selector):
            pass

        def fill(self, selector, value):
            pass

        def wait_for_timeout(self, timeout):
            pass

        def content(self):
            return "data"

    class DummyContext:
        def new_page(self):
            return DummyPage()

    class DummyBrowser:
        def new_context(self, **kwargs):
            return DummyContext()

        def close(self):
            pass

    class DummyPlaywright:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        class chromium:
            @staticmethod
            def launch(headless=True):
                return DummyBrowser()

    def dummy_sync_playwright():
        return DummyPlaywright()

    monkeypatch.setattr(ba_module, "sync_playwright", dummy_sync_playwright)

    flags.enable_fuckery()
    content = ba.run_script('http://example.com', [])
    assert content != 'data'
    assert flags.decrypt(content.encode()).decode() == 'data'
    assert ba.headless is True

