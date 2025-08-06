import json
import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from policy_manager import PolicyManager, EmergencyStop, ResourceLimitExceeded
from safety_enforcement import SafetyManager


def make_policy(tmp_path, config):
    config_path = tmp_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f)
    return PolicyManager(config_path=str(config_path))


def test_check_action_violation(tmp_path):
    config = {
        "security": {"action_whitelist": ["read"]},
        "resource_limits": {},
        "privacy_settings": {"redact_pii": False},
    }
    policy = make_policy(tmp_path, config)
    with pytest.raises(PermissionError):
        policy.check_action("write")


def test_resource_limit_violation(tmp_path):
    config = {
        "security": {"action_whitelist": ["read"]},
        "resource_limits": {"memory": 0},
        "privacy_settings": {"redact_pii": False},
    }
    policy = make_policy(tmp_path, config)
    with pytest.raises(ResourceLimitExceeded):
        policy.enforce_resource_limits()


def test_privacy_redaction(tmp_path):
    config = {
        "security": {"action_whitelist": ["read"]},
        "resource_limits": {},
        "privacy_settings": {"redact_pii": True},
    }
    policy = make_policy(tmp_path, config)
    redacted = policy.apply_privacy("Email me at test@example.com or 123-456-7890")
    assert "[REDACTED_EMAIL]" in redacted
    assert "[REDACTED_PHONE]" in redacted


def test_safety_manager_stops_on_violation(tmp_path):
    config = {
        "security": {"action_whitelist": ["read"]},
        "resource_limits": {"memory": 0},
        "privacy_settings": {"redact_pii": False},
    }
    policy = make_policy(tmp_path, config)
    safety = SafetyManager(policy)

    def dummy_task(data):
        return data

    with pytest.raises(ResourceLimitExceeded):
        safety.execute("read", "data", dummy_task)
    assert policy.stopped.is_set()


def test_emergency_stop(tmp_path):
    config = {
        "security": {"action_whitelist": ["read"]},
        "resource_limits": {},
        "privacy_settings": {"redact_pii": False},
    }
    policy = make_policy(tmp_path, config)
    safety = SafetyManager(policy)

    def stop_task(data):
        policy.emergency_stop()

    with pytest.raises(EmergencyStop):
        safety.execute("read", "data", stop_task)
    assert policy.stopped.is_set()

