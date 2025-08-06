import threading
import signal
import logging
import json

from safety_enforcement import SafetyManager, EmergencyStop


class PolicyManager:
    """High-level wrapper around :class:`SafetyManager`.

    The policy manager loads configuration, delegates checks to the safety
    manager and exposes a small helper API for validating and executing
    actions.  It also handles signal-based emergency stops via an internal
    ``threading.Event``.
    """

    def __init__(self, config_path: str = 'config.yaml'):
        self.load_config(config_path)
        self.stopped = threading.Event()
        self.logger = logging.getLogger("PolicyManager")
        self.logger.setLevel(logging.INFO)
        self.safety = SafetyManager(
            resource_limits=self.config.get('resource_limits', {}),
            privacy_settings=self.config.get('privacy_settings', {}),
            action_whitelist=self.config.get('security', {}).get('action_whitelist', []),
        )

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------
    def load_config(self, path: str) -> None:
        with open(path, 'r') as f:
            self.config = json.load(f)

    # ------------------------------------------------------------------
    # Delegated Safety Methods
    # ------------------------------------------------------------------
    def check_action(self, action: str) -> None:
        self.safety.check_action(action)

    def enforce_resource_limits(self) -> None:
        self.safety.enforce_resource_limits()

    def apply_privacy(self, data):
        return self.safety.scrub_data(data)

    def audit_log(self, event: str) -> None:
        self.safety.audit_log(event)

    # ------------------------------------------------------------------
    # Emergency Stop & Signal Handling
    # ------------------------------------------------------------------
    def emergency_stop(self, signum=None, frame=None) -> None:
        self.stopped.set()
        self.safety.emergency_stop()

    def register_signal_handlers(self) -> None:
        signal.signal(signal.SIGINT, self.emergency_stop)
        signal.signal(signal.SIGTERM, self.emergency_stop)

    # ------------------------------------------------------------------
    # Action Execution
    # ------------------------------------------------------------------
    def execute(self, action: str, func, *args, **kwargs):
        """Validate and execute ``func`` labelled by ``action``.

        The action is checked against the whitelist and resource limits before
        ``func`` is invoked.  If the function returns a string, it is passed
        through the privacy scrubber before being returned.
        """
        self.check_action(action)
        self.enforce_resource_limits()
        result = func(*args, **kwargs)
        if isinstance(result, str):
            result = self.apply_privacy(result)
        return result

