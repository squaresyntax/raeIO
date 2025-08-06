import threading
import signal
import logging
import os
import re

try:  # pragma: no cover - yaml is optional in minimal environments
    import yaml
except Exception:  # pragma: no cover
    yaml = None
import json

try:  # pragma: no cover - fallback when psutil is unavailable
    import psutil
except Exception:  # pragma: no cover
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
        with open(path, 'r') as f:
            content = f.read()
            if yaml:
                self.config = yaml.safe_load(content)
            else:
                self.config = json.loads(content)

    def check_action(self, action: str):
        allowed = self.config.get('security', {}).get('action_whitelist', [])
        if action not in allowed:
            self.logger.warning(f"Action '{action}' not permitted.")
            raise PermissionError(f"Action '{action}' is not allowed by policy.")

    def enforce_resource_limits(self):
        """Check basic CPU and memory usage against configured limits.

        This implementation relies on the ``psutil`` package which provides
        cross-platform utilities for retrieving system utilisation metrics.
        If the current process exceeds any configured limit a ``ResourceWarning``
        is raised. Limits are expressed as percentages.
        """

        limits = self.config.get('resource_limits', {})
        cpu_limit = limits.get('cpu_percent')
        mem_limit = limits.get('memory_percent')

        if cpu_limit is not None:
            cpu_usage = (
                psutil.cpu_percent(interval=0.1) if psutil else 100.0
            )
            if cpu_usage > cpu_limit:
                raise ResourceWarning(
                    f"CPU usage {cpu_usage}% exceeds limit of {cpu_limit}%"
                )

        if mem_limit is not None:
            mem_usage = (
                psutil.virtual_memory().percent if psutil else 100.0
            )
            if mem_usage > mem_limit:
                raise ResourceWarning(
                    f"Memory usage {mem_usage}% exceeds limit of {mem_limit}%"
                )

    def apply_privacy(self, data):
        if self.config['privacy_settings'].get('redact_pii', False):
            return self.redact_pii(data)
        return data

    def redact_pii(self, data):
        """Naively redact email addresses and phone numbers from ``data``."""

        patterns = [
            r"[\w.\-]+@[\w.\-]+",  # email addresses
            r"\b\d{3}[\-\.]?\d{3}[\-\.]?\d{4}\b",  # phone numbers
        ]
        redacted = data
        for pat in patterns:
            redacted = re.sub(pat, "[REDACTED]", redacted)
        return redacted

    def enforce_anonymity(self):
        """Configure proxy settings if anonymity is requested."""

        settings = self.config.get("privacy_settings", {})
        if settings.get("use_proxy"):
            proxy = settings.get("proxy_url")
            if proxy:
                os.environ["HTTP_PROXY"] = proxy
                os.environ["HTTPS_PROXY"] = proxy

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
