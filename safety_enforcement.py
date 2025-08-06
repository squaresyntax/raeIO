import logging
import re


class EmergencyStop(Exception):
    """Raised when an emergency stop is triggered."""


class SafetyManager:
    """Centralised safety and policy enforcement."""

    def __init__(self, resource_limits=None, privacy_settings=None, action_whitelist=None):
        self.resource_limits = resource_limits or {}
        self.privacy_settings = privacy_settings or {}
        self.action_whitelist = action_whitelist or []
        self.logger = logging.getLogger("SafetyManager")

    # ------------------------------------------------------------------
    # Action Validation
    # ------------------------------------------------------------------
    def check_action(self, action: str) -> None:
        """Ensure the requested action is permitted."""
        if action not in self.action_whitelist:
            self.logger.warning("Action '%s' not permitted.", action)
            raise PermissionError(f"Action '{action}' is not allowed by policy.")

    # ------------------------------------------------------------------
    # Resource Limits
    # ------------------------------------------------------------------
    def enforce_resource_limits(self) -> None:
        """Validate resource usage against configured limits."""
        usage = self._get_resource_usage()

        mem_limit = self.resource_limits.get("memory_mb")
        if mem_limit is not None and usage.get("memory_mb", 0) > mem_limit:
            self.logger.error(
                "Memory usage exceeded: %sMB > %sMB", usage["memory_mb"], mem_limit
            )
            raise MemoryError("Memory limit exceeded")

        cpu_limit = self.resource_limits.get("cpu_percent")
        if cpu_limit is not None and usage.get("cpu_percent", 0) > cpu_limit:
            self.logger.error(
                "CPU usage exceeded: %s%% > %s%%", usage["cpu_percent"], cpu_limit
            )
            raise RuntimeError("CPU limit exceeded")

    def _get_resource_usage(self):
        """Return current resource usage.

        Values are returned as a dictionary with ``memory_mb`` and ``cpu_percent``
        keys.  ``psutil`` is used if available; otherwise zeros are returned so
        tests can monkeypatch this method.
        """
        try:  # pragma: no cover - executed only when psutil is available
            import psutil

            mem_mb = psutil.virtual_memory().used // (1024 * 1024)
            cpu_percent = psutil.cpu_percent(interval=0)
            return {"memory_mb": mem_mb, "cpu_percent": cpu_percent}
        except Exception:
            self.logger.debug("psutil not available; resource usage defaulted to 0")
            return {"memory_mb": 0, "cpu_percent": 0}

    # ------------------------------------------------------------------
    # Privacy Enforcement
    # ------------------------------------------------------------------
    def scrub_data(self, data: str) -> str:
        """Redact basic PII from the provided string."""
        if not isinstance(data, str):
            return data

        if not self.privacy_settings.get("redact_pii", False):
            return data

        # Simple email and phone regexes – sufficient for tests
        email_regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
        phone_regex = r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
        data = re.sub(email_regex, "[REDACTED]", data)
        data = re.sub(phone_regex, "[REDACTED]", data)
        return data

    # ------------------------------------------------------------------
    # Emergency Stop / Auditing
    # ------------------------------------------------------------------
    def emergency_stop(self) -> None:
        """Immediately halt execution."""
        self.logger.critical("Emergency stop triggered! Halting all processes.")
        raise EmergencyStop("Emergency stop activated.")

    def audit_log(self, event: str) -> None:
        """Log sensitive events for later review."""
        self.logger.info("AUDIT: %s", event)

