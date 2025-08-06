"""Runtime safety enforcement utilities.

This module complements :mod:`policy_manager` by providing a light‑weight
``SafetyManager`` class that can be embedded in agents.  It offers basic
resource limit checks, PII scrubbing and an emergency stop mechanism.  The
implementation is intentionally minimal but fully functional so that the unit
tests can exercise the different enforcement paths.
"""

import logging
import re
from typing import Any, List, Optional

try:  # psutil is optional and only used for resource checks
    import psutil
except Exception:  # pragma: no cover
    psutil = None


class EmergencyStop(Exception):
    """Raised when an emergency stop is requested."""


class SafetyManager:
    def __init__(
        self,
        resource_limits: Optional[dict] = None,
        privacy_settings: Optional[dict] = None,
        action_whitelist: Optional[List[str]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.resource_limits = resource_limits or {}
        self.privacy_settings = privacy_settings or {}
        self.action_whitelist = action_whitelist or []
        self.logger = logger or logging.getLogger("SafetyManager")
        self.stopped = False

    # ------------------------------------------------------------------
    # Action enforcement
    def check_action(self, action: str) -> None:
        if self.action_whitelist and action not in self.action_whitelist:
            self.logger.warning("Action '%s' not allowed.", action)
            raise PermissionError(f"Action {action} not allowed.")

    # ------------------------------------------------------------------
    # Resource enforcement
    def enforce_resource_limits(self) -> None:
        if not self.resource_limits:
            return

        if psutil is None:
            self.logger.warning("psutil not installed; resource limits not enforced.")
            return

        if "memory_mb" in self.resource_limits:
            mem_used_mb = psutil.virtual_memory().used // (1024 * 1024)
            if mem_used_mb > self.resource_limits["memory_mb"]:
                msg = (
                    f"Memory usage exceeded: {mem_used_mb}MB > {self.resource_limits['memory_mb']}MB"
                )
                self.logger.error(msg)
                raise MemoryError(msg)

        if "cpu_percent" in self.resource_limits:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if cpu_percent > self.resource_limits["cpu_percent"]:
                msg = (
                    f"CPU usage exceeded: {cpu_percent}% > {self.resource_limits['cpu_percent']}%"
                )
                self.logger.error(msg)
                raise RuntimeError(msg)

    # ------------------------------------------------------------------
    # Privacy enforcement
    def scrub_data(self, data: Any) -> Any:
        if not isinstance(data, str):
            return data

        if not self.privacy_settings.get("redact_pii", False):
            return data

        pii_pattern = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)|(\b\d{3}[-.]?\d{3}[-.]?\d{4}\b)"

        def _repl(match: re.Match) -> str:
            self.logger.warning("PII detected and redacted.")
            return "[REDACTED]"

        return re.sub(pii_pattern, _repl, data)

    # ------------------------------------------------------------------
    def emergency_stop(self) -> None:
        self.logger.critical("Emergency stop triggered! Halting all processes.")
        self.stopped = True
        raise EmergencyStop("Emergency stop activated.")

    # ------------------------------------------------------------------
    def audit_log(self, event: str) -> None:
        self.logger.info("Audit: %s", event)

