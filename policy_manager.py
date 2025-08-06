import os
import re
import signal
import threading
import logging
import yaml

try:  # pragma: no cover - optional dependency
    import psutil
except ImportError:
    psutil = None


class EmergencyStop(Exception):
    """Raised when an emergency stop is triggered."""


class PolicyManager:
    """Simple policy and privacy enforcement helper."""

    def __init__(self, config_path: str = "config.yaml"):
        self.load_config(config_path)
        self.stopped = threading.Event()
        self.logger = logging.getLogger("PolicyManager")
        self.logger.setLevel(logging.INFO)

    # ------------------------------------------------------------------
    # Configuration and policy checks
    # ------------------------------------------------------------------
    def load_config(self, path: str) -> None:
        with open(path, "r") as f:
            self.config = yaml.safe_load(f) or {}

    def check_action(self, action: str) -> None:
        allowed = self.config.get("security", {}).get("action_whitelist", [])
        if allowed and action not in allowed:
            self.logger.warning(f"Action '{action}' not permitted.")
            raise PermissionError(f"Action '{action}' is not allowed by policy.")

    # ------------------------------------------------------------------
    # Resource and privacy enforcement
    # ------------------------------------------------------------------
    def enforce_resource_limits(self) -> None:
        """Check CPU and memory usage against configured limits."""

        limits = self.config.get("resource_limits", {})
        if not psutil:
            self.logger.warning("psutil not available; resource limits not enforced")
            return

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

    def apply_privacy(self, data):
        """Apply PII redaction to data if configured."""

        privacy = self.config.get("privacy_settings", {})
        if privacy.get("redact_pii"):
            return self.redact_pii(data)
        return data

    def redact_pii(self, data):
        """Redact simple PII such as emails and phone numbers."""

        if isinstance(data, str):
            email_re = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
            phone_re = r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
            data = re.sub(email_re, "[REDACTED_EMAIL]", data)
            data = re.sub(phone_re, "[REDACTED_PHONE]", data)
            return data
        if isinstance(data, dict):
            return {k: self.redact_pii(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self.redact_pii(v) for v in data]
        return data

    def enforce_anonymity(self) -> None:
        """Configure proxy settings to anonymise network access."""

        privacy = self.config.get("privacy_settings", {})
        if not privacy.get("use_proxy"):
            return
        proxy = privacy.get("proxy")
        if proxy:
            os.environ["http_proxy"] = proxy
            os.environ["https_proxy"] = proxy
            os.environ["HTTP_PROXY"] = proxy
            os.environ["HTTPS_PROXY"] = proxy
            self.logger.info(f"Proxy enabled via {proxy}")

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def audit_log(self, event: str) -> None:
        self.logger.info(f"Audit: {event}")

    def emergency_stop(self, signum=None, frame=None) -> None:
        self.logger.critical("Emergency stop triggered! Halting all processes.")
        self.stopped.set()
        raise EmergencyStop("Emergency stop activated.")

    def register_signal_handlers(self) -> None:
        signal.signal(signal.SIGINT, self.emergency_stop)
        signal.signal(signal.SIGTERM, self.emergency_stop)

