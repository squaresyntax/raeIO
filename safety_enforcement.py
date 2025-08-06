import logging
import os
import re
import threading

try:  # pragma: no cover - optional dependency
    import psutil
except ImportError:
    psutil = None


class SafetyManager:
    """Runtime safety enforcement for tasks."""

    def __init__(self, resource_limits=None, privacy_settings=None, action_whitelist=None):
        self.resource_limits = resource_limits or {}
        self.privacy_settings = privacy_settings or {}
        self.action_whitelist = action_whitelist or []
        self.stopped = threading.Event()
        self.logger = logging.getLogger("SafetyManager")
        self.logger.setLevel(logging.INFO)

    # ------------------------------------------------------------------
    # Policy checks
    # ------------------------------------------------------------------
    def check_action(self, action: str) -> None:
        if self.action_whitelist and action not in self.action_whitelist:
            raise PermissionError(f"Action {action} not allowed.")

    # ------------------------------------------------------------------
    # Resource and privacy enforcement
    # ------------------------------------------------------------------
    def enforce_resource_limits(self) -> None:
        """Ensure the running process does not exceed CPU or memory limits."""

        if not psutil:
            self.logger.warning("psutil not available; resource limits not enforced")
            return

        limits = self.resource_limits
        mem_limit = limits.get("memory_mb")
        if mem_limit is not None:
            mem_used = psutil.Process().memory_info().rss / (1024 * 1024)
            if mem_used > mem_limit:
                msg = f"Memory usage exceeded: {mem_used:.1f}MB > {mem_limit}MB"
                self.audit_log(msg)
                raise MemoryError(msg)

        cpu_limit = limits.get("cpu_percent")
        if cpu_limit is not None:
            cpu = psutil.cpu_percent(interval=0.1)
            if cpu > cpu_limit:
                msg = f"CPU usage exceeded: {cpu:.1f}% > {cpu_limit}%"
                self.audit_log(msg)
                raise RuntimeError(msg)

    def scrub_data(self, data):
        """Scrub simple PII such as emails and phone numbers from data."""

        if not self.privacy_settings.get("redact_pii"):
            return data

        if isinstance(data, str):
            email_re = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
            phone_re = r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
            data = re.sub(email_re, "[REDACTED_EMAIL]", data)
            data = re.sub(phone_re, "[REDACTED_PHONE]", data)
            return data
        if isinstance(data, dict):
            return {k: self.scrub_data(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self.scrub_data(v) for v in data]
        return data

    def emergency_stop(self) -> None:
        """Immediately halt processing by setting an event and raising SystemExit."""

        self.logger.critical("Emergency stop triggered! Halting all processes.")
        self.stopped.set()
        raise SystemExit("Emergency stop activated")

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def audit_log(self, event: str) -> None:
        self.logger.info(f"Audit: {event}")

