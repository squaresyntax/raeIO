import threading
import signal
import logging
import json
try:
    import yaml
except ImportError:  # pragma: no cover - fallback when PyYAML isn't installed
    yaml = None
import resource
import re

class EmergencyStop(Exception):
    """Raised when an emergency stop is triggered."""
    pass


class ResourceLimitExceeded(Exception):
    """Raised when a resource limit defined in the configuration is exceeded."""
    pass

class PolicyManager:
    def __init__(self, config_path='config.yaml'):
        self.load_config(config_path)
        self.stopped = threading.Event()
        self.logger = logging.getLogger("PolicyManager")
        self.logger.setLevel(logging.INFO)

    def load_config(self, path):
        with open(path, "r") as f:
            if yaml is not None:
                self.config = yaml.safe_load(f)
            else:
                self.config = json.load(f)

    def check_action(self, action: str):
        allowed = self.config.get('security', {}).get('action_whitelist', [])
        if action not in allowed:
            self.logger.warning(f"Action '{action}' not permitted.")
            raise PermissionError(f"Action '{action}' is not allowed by policy.")

    def enforce_resource_limits(self):
        """Check CPU time and memory usage against configured limits.

        This implementation relies on the ``resource`` module which is
        available on Unix platforms.  The limits are expressed in bytes for
        memory and seconds for CPU time.
        """
        limits = self.config.get('resource_limits', {})

        # Memory limit enforcement
        memory_limit = limits.get('memory')
        if memory_limit is not None:
            # ``ru_maxrss`` is in kilobytes on Linux, convert to bytes
            usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
            if usage > memory_limit:
                self.logger.error(
                    f"Memory usage {usage} exceeds limit {memory_limit}."
                )
                raise ResourceLimitExceeded(
                    f"Memory usage {usage} exceeds limit {memory_limit}"
                )

        # CPU time limit enforcement
        cpu_time_limit = limits.get('cpu_time')
        if cpu_time_limit is not None:
            usage_time = (
                resource.getrusage(resource.RUSAGE_SELF).ru_utime
                + resource.getrusage(resource.RUSAGE_SELF).ru_stime
            )
            if usage_time > cpu_time_limit:
                self.logger.error(
                    f"CPU time {usage_time} exceeds limit {cpu_time_limit}."
                )
                raise ResourceLimitExceeded(
                    f"CPU time {usage_time} exceeds limit {cpu_time_limit}"
                )

    def apply_privacy(self, data):
        if self.config['privacy_settings'].get('redact_pii', False):
            return self.redact_pii(data)
        return data

    def redact_pii(self, data):
        """Naively redact email addresses and phone numbers from text."""
        if not isinstance(data, str):
            return data

        email_pattern = r"\b[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}\b"
        phone_pattern = r"\b\d{3}[-. ]?\d{3}[-. ]?\d{4}\b"

        data = re.sub(email_pattern, "[REDACTED_EMAIL]", data)
        data = re.sub(phone_pattern, "[REDACTED_PHONE]", data)
        return data

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
