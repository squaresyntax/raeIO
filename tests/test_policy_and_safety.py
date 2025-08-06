import os
import tempfile

import json
import os
import sys

import pytest

sys.path.append(os.getcwd())

from policy_manager import PolicyManager
from safety_enforcement import SafetyManager, EmergencyStop


def _write_config(data):
    tmp = tempfile.NamedTemporaryFile("w", delete=False)
    json.dump(data, tmp)
    tmp.close()
    return tmp.name


def test_policy_manager_resource_limits():
    cfg = {
        "resource_limits": {"cpu_percent": 0, "memory_percent": 0},
        "privacy_settings": {},
    }
    path = _write_config(cfg)
    pm = PolicyManager(config_path=path)
    try:
        with pytest.raises(ResourceWarning):
            pm.enforce_resource_limits()
    finally:
        os.unlink(path)


def test_policy_manager_pii_redaction():
    cfg = {"privacy_settings": {"redact_pii": True}}
    path = _write_config(cfg)
    pm = PolicyManager(config_path=path)
    try:
        text = "Email me at user@example.com or call 123-456-7890."
        assert "[REDACTED]" in pm.apply_privacy(text)
    finally:
        os.unlink(path)


def test_policy_manager_proxy_handling(monkeypatch):
    cfg = {
        "privacy_settings": {
            "use_proxy": True,
            "proxy_url": "http://proxy.example",
        }
    }
    path = _write_config(cfg)
    try:
        with monkeypatch.context() as m:
            m.delenv("HTTP_PROXY", raising=False)
            m.delenv("HTTPS_PROXY", raising=False)
            pm = PolicyManager(config_path=path)
            pm.enforce_anonymity()
            assert os.environ["HTTP_PROXY"] == "http://proxy.example"
            assert os.environ["HTTPS_PROXY"] == "http://proxy.example"
    finally:
        os.unlink(path)


def test_safety_manager_resource_limits():
    sm = SafetyManager({"cpu_percent": 0, "memory_percent": 0}, {}, [])
    with pytest.raises(ResourceWarning):
        sm.enforce_resource_limits()


def test_safety_manager_scrub_data():
    sm = SafetyManager({}, {"redact_pii": True}, [])
    data = "Contact user@example.com or 555-555-5555."
    assert "[REDACTED]" in sm.scrub_data(data)


def test_safety_manager_emergency_stop():
    sm = SafetyManager({}, {}, [])
    with pytest.raises(EmergencyStop):
        sm.emergency_stop()
    assert sm.stopped is True


def test_safety_manager_audit_log():
    sm = SafetyManager({}, {}, [])
    sm.audit_log("event1")
    assert sm.audit_trail == ["event1"]

