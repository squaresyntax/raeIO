import re

try:  # pragma: no cover - psutil may not be available in all environments
    import psutil
except Exception:  # pragma: no cover
    psutil = None


class EmergencyStop(Exception):
    """Raised when an emergency stop is requested."""


class SafetyManager:
    def __init__(self, resource_limits, privacy_settings, action_whitelist):
        self.resource_limits = resource_limits or {}
        self.privacy_settings = privacy_settings or {}
        self.action_whitelist = action_whitelist or []
        self.audit_trail = []
        self.stopped = False

    def check_action(self, action):
        # Enforce action whitelist/blacklist
        if action not in self.action_whitelist:
            raise PermissionError(f"Action {action} not allowed.")

    def enforce_resource_limits(self):
        """Check CPU and memory usage against configured limits."""

        cpu_limit = self.resource_limits.get("cpu_percent")
        mem_limit = self.resource_limits.get("memory_percent")

        if cpu_limit is not None:
            cpu_usage = (
                psutil.cpu_percent(interval=0.1) if psutil else 100.0
            )
            if cpu_usage > cpu_limit:
                raise ResourceWarning("CPU limit exceeded")

        if mem_limit is not None:
            mem_usage = (
                psutil.virtual_memory().percent if psutil else 100.0
            )
            if mem_usage > mem_limit:
                raise ResourceWarning("Memory limit exceeded")

    def scrub_data(self, data):
        """Remove simple PII such as emails and phone numbers."""

        if not self.privacy_settings.get("redact_pii"):
            return data

        patterns = [
            r"[\w.\-]+@[\w.\-]+",
            r"\b\d{3}[\-\.]?\d{3}[\-\.]?\d{4}\b",
        ]
        redacted = data
        for pat in patterns:
            redacted = re.sub(pat, "[REDACTED]", redacted)
        return redacted

    def emergency_stop(self):
        """Immediately halt all processes by raising ``EmergencyStop``."""

        self.stopped = True
        raise EmergencyStop("Emergency stop activated")

    def audit_log(self, event):
        """Store ``event`` in the audit trail for later review."""

        self.audit_trail.append(event)
