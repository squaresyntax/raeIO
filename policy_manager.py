"""Central policy management for RAEIO.

This module loads policy configuration and provides helpers for enforcing
resource limits, privacy rules and emergency stop handling.  The original
implementation only contained placeholders which made it difficult to test
the agent's safety features.  The new implementation adds concrete CPU and
memory limit checks using ``psutil`` as well as very small PII scrubbing
utilities.  These are intentionally lightweight but sufficient for unit tests
and serve as an example of how a real system could plug in more advanced
solutions.

The ``PolicyManager`` exposes an ``EmergencyStop`` exception and a
``stopped`` event that can be checked by callers.  When ``emergency_stop`` is
invoked (either directly or via a signal handler) the event is set and the
exception is raised so that callers can immediately terminate execution.
"""

import threading
import signal
import logging
import re
from typing import Any

import json

try:  # yaml is optional; fall back to json if unavailable
    import yaml  # type: ignore
except Exception:  # pragma: no cover - handled gracefully when missing
    yaml = None

try:  # psutil is optional but used for resource checks
    import psutil
except Exception:  # pragma: no cover - handled gracefully in tests
    psutil = None

class EmergencyStop(Exception):
    pass

class PolicyManager:
    def __init__(self, config_path='config.yaml'):
        self.load_config(config_path)
        self.stopped = threading.Event()
        self.logger = logging.getLogger("PolicyManager")
        self.logger.setLevel(logging.INFO)

    def load_config(self, path):
        with open(path, "r") as f:
            data = f.read()
        if yaml is not None:
            self.config = yaml.safe_load(data)
        else:  # Fallback to JSON
            self.config = json.loads(data)

    def check_action(self, action: str):
        allowed = self.config.get('security', {}).get('action_whitelist', [])
        if action not in allowed:
            self.logger.warning(f"Action '{action}' not permitted.")
            raise PermissionError(f"Action '{action}' is not allowed by policy.")

    def enforce_resource_limits(self) -> None:
        """Enforce basic CPU and memory limits.

        The limits are specified under ``resource_limits`` in the configuration
        as ``memory_mb`` and ``cpu_percent``.  The function raises ``MemoryError``
        or ``RuntimeError`` if the current usage exceeds the configured values.
        """

        limits = self.config.get("resource_limits", {}) or {}

        if not limits:
            return  # Nothing to enforce

        if psutil is None:
            self.logger.warning("psutil not installed; resource limits not enforced.")
            return

        # Memory check
        if "memory_mb" in limits:
            mem_used_mb = psutil.virtual_memory().used // (1024 * 1024)
            if mem_used_mb > limits["memory_mb"]:
                msg = (
                    f"Memory usage exceeded: {mem_used_mb}MB > {limits['memory_mb']}MB"
                )
                self.logger.error(msg)
                raise MemoryError(msg)

        # CPU check – a short interval keeps tests snappy
        if "cpu_percent" in limits:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if cpu_percent > limits["cpu_percent"]:
                msg = (
                    f"CPU usage exceeded: {cpu_percent}% > {limits['cpu_percent']}%"
                )
                self.logger.error(msg)
                raise RuntimeError(msg)

    def apply_privacy(self, data: Any) -> Any:
        """Apply privacy rules to ``data``.

        Currently this only performs simple PII redaction when enabled in the
        configuration.  Non-string data is returned unchanged.
        """

        if not isinstance(data, str):
            return data

        if self.config.get("privacy_settings", {}).get("redact_pii", False):
            return self.redact_pii(data)
        return data

    def redact_pii(self, data: str) -> str:
        """Redact very simple PII such as email addresses or phone numbers."""

        pii_pattern = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)|(\b\d{3}[-.]?\d{3}[-.]?\d{4}\b)"

        def _repl(match: re.Match) -> str:
            self.logger.warning("PII detected and redacted.")
            return "[REDACTED]"

        return re.sub(pii_pattern, _repl, data)

    def enforce_anonymity(self):
        if self.config['privacy_settings'].get('use_proxy', False):
            # Route traffic via proxy (see networking code)
            pass

    def audit_log(self, event):
        # Log all sensitive events for review
        self.logger.info(f"Audit: {event}")

    def emergency_stop(self, signum=None, frame=None):
        self.logger.critical("Emergency stop triggered! Halting all processes.")
        self.stopped.set()
        raise EmergencyStop("Emergency stop activated.")

    def register_signal_handlers(self):
        signal.signal(signal.SIGINT, self.emergency_stop)
        signal.signal(signal.SIGTERM, self.emergency_stop)