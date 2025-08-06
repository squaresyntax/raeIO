import os
import sys

sys.path.append(os.getcwd())

from raeio_agent import RAEIOAgent
from model_adapter import ModelAdapter


class DummyLogger:
    def __init__(self):
        self.anonymized = False

    def info(self, msg):
        pass


def create_plugin(dir_path):
    os.makedirs(dir_path, exist_ok=True)
    with open(os.path.join(dir_path, "sample_plugin.py"), "w") as f:
        f.write(
            "def run(prompt=None, context=None, fuckery_mode=False):\n"
            "    return fuckery_mode\n"
        )


def test_fuckery_mode_propagates(tmp_path):
    plugin_dir = tmp_path / "plugins"
    create_plugin(plugin_dir)
    logger = DummyLogger()
    adapter = ModelAdapter()
    config = {
        "plugin_dir": str(plugin_dir),
        "browser_headless": False,
    }
    agent = RAEIOAgent(config, logger, model_adapter=adapter)

    assert agent.fuckery_mode is False
    assert agent.browser_automation.headless is False
    assert adapter.fuckery_mode is False
    assert logger.anonymized is False

    # Plugin should see current fuckery_mode state
    res = agent.plugin_registry.execute_plugin("sample_plugin", prompt="p", context={})
    assert res is False

    agent.set_fuckery_mode(True)
    assert agent.fuckery_mode is True
    assert agent.browser_automation.headless is True
    assert adapter.fuckery_mode is True
    assert logger.anonymized is True
    assert agent.encryption_key is not None

    res = agent.plugin_registry.execute_plugin("sample_plugin", prompt="p", context={})
    assert res is True

    agent.set_fuckery_mode(False)
    assert agent.fuckery_mode is False
    assert agent.browser_automation.headless is False
    assert adapter.fuckery_mode is False
    assert logger.anonymized is False
    assert agent.encryption_key is None
