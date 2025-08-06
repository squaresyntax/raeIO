import logging
import os
import sys
from types import SimpleNamespace

import json
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import types

class _DummyBrowserAutomation:
    def __init__(self, *args, **kwargs):
        pass

    def run_script(self, url, actions):  # pragma: no cover - not used
        return ""

sys.modules['browser_automation'] = types.SimpleNamespace(BrowserAutomation=_DummyBrowserAutomation)

import safety_enforcement
from raeio_agent import RAEIOAgent, EmergencyStop


def make_agent(tmp_path, config_dict):
    cfg_path = tmp_path / "policy.json"
    with open(cfg_path, "w") as f:
        json.dump(config_dict, f)
    logger = logging.getLogger("test")
    logger.setLevel(logging.DEBUG)
    return RAEIOAgent({"policy_config_path": str(cfg_path), "memory_path": str(tmp_path / "memory.jsonl")}, logger)


class _FakePsutil:
    @staticmethod
    def virtual_memory():
        return SimpleNamespace(used=2 * 1024 * 1024)

    @staticmethod
    def cpu_percent(interval=None):
        return 100


def test_resource_limit_violation(tmp_path, caplog, monkeypatch):
    monkeypatch.setattr(safety_enforcement, "psutil", _FakePsutil())
    config = {
        "resource_limits": {"memory_mb": 0, "cpu_percent": 0},
        "privacy_settings": {},
        "security": {"action_whitelist": ["test"]},
    }
    agent = make_agent(tmp_path, config)
    with caplog.at_level(logging.ERROR, logger="SafetyManager"):
        with pytest.raises(MemoryError):
            agent.run_task("test", "hello", {})
    assert any("Memory usage exceeded" in r.message for r in caplog.records)


def test_pii_scrubbing(tmp_path, caplog):
    config = {
        "resource_limits": {},
        "privacy_settings": {"redact_pii": True},
        "security": {"action_whitelist": ["test"]},
    }
    agent = make_agent(tmp_path, config)
    with caplog.at_level(logging.WARNING, logger="SafetyManager"):
        output = agent.run_task("test", "contact me at test@example.com", {})
    assert "[REDACTED]" in output
    assert any("PII detected" in r.message for r in caplog.records)


def test_emergency_stop(tmp_path, caplog):
    config = {
        "resource_limits": {},
        "privacy_settings": {},
        "security": {"action_whitelist": ["test"]},
    }
    agent = make_agent(tmp_path, config)
    with caplog.at_level(logging.CRITICAL, logger="PolicyManager"):
        # Trigger stop and ignore the initial exception
        with pytest.raises(EmergencyStop):
            try:
                agent.policy_manager.emergency_stop()
            except EmergencyStop:
                pass
            agent.run_task("test", "hi", {})
    assert any("Emergency stop triggered" in r.message for r in caplog.records)

