import logging
from raeio_agent import RAEIOAgent


class DummyBrowser:
    def run_script(self, url, actions):
        return "dummy"


def test_run_task_default(tmp_path):
    plugin_dir = tmp_path / "plugins"
    config = {
        "memory_path": str(tmp_path / "mem.jsonl"),
        "plugin_dir": str(plugin_dir),
    }
    agent = RAEIOAgent(config=config, logger=logging.getLogger("test"))
    agent.browser_automation = DummyBrowser()
    result = agent.run_task("general", "hello", {})
    assert result == "Stub output for general: hello"


def test_run_task_plugin(tmp_path):
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    plugin_file = plugin_dir / "p.py"
    plugin_file.write_text(
        "def run(prompt, context):\n    return prompt + context['suf']\n"
    )
    config = {
        "memory_path": str(tmp_path / "mem.jsonl"),
        "plugin_dir": str(plugin_dir),
    }
    agent = RAEIOAgent(config=config, logger=None)
    agent.browser_automation = DummyBrowser()
    result = agent.run_task("task", "hi", {"suf": "!"}, plugin="p")
    assert result == "hi!"


def test_run_task_browser(tmp_path):
    plugin_dir = tmp_path / "plugins"
    config = {
        "memory_path": str(tmp_path / "mem.jsonl"),
        "plugin_dir": str(plugin_dir),
    }
    agent = RAEIOAgent(config=config, logger=None)
    agent.browser_automation = DummyBrowser()
    result = agent.run_task("browser", "", {"url": "http://example.com", "actions": []})
    assert result == "dummy"
