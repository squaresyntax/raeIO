import logging
import json
import pytest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from policy_manager import PolicyManager


def write_config(tmp_path, config):
    path = tmp_path / "config.yaml"
    with open(path, "w") as fh:
        json.dump(config, fh)
    return str(path)


def base_config():
    return {
        "security": {"action_whitelist": ["read"]},
        "resource_limits": {"memory_mb": 100, "cpu_percent": 90},
        "privacy_settings": {"redact_pii": True},
    }


def test_action_blocked_logs_warning(tmp_path, caplog):
    config_path = write_config(tmp_path, base_config())
    pm = PolicyManager(config_path=config_path)

    with caplog.at_level(logging.WARNING):
        with pytest.raises(PermissionError):
            pm.execute("write", lambda: "data")

    assert "not permitted" in caplog.text


def test_resource_limit_exceeded_logs_error(tmp_path, caplog):
    config_path = write_config(tmp_path, base_config())
    pm = PolicyManager(config_path=config_path)

    # Force resource usage over the configured memory limit
    pm.safety._get_resource_usage = lambda: {"memory_mb": 200, "cpu_percent": 10}

    with caplog.at_level(logging.ERROR):
        with pytest.raises(MemoryError):
            pm.enforce_resource_limits()

    assert "Memory usage exceeded" in caplog.text

