import logging
from typing import Callable, Any

from policy_manager import (
    PolicyManager,
    EmergencyStop,
    ResourceLimitExceeded,
)


class SafetyManager:
    """High-level interface that runs tasks under policy enforcement.

    The safety manager delegates the actual policy checks to ``PolicyManager``
    but is responsible for orchestrating the checks and ensuring that any
    violation halts execution and is logged for audit purposes.
    """

    def __init__(self, policy: PolicyManager):
        self.policy = policy
        self.logger = logging.getLogger("SafetyManager")

    def execute(
        self, action: str, data: Any, task: Callable[[Any], Any], *args, **kwargs
    ) -> Any:
        """Run ``task`` after enforcing policy checks.

        Parameters
        ----------
        action:
            Name of the action the task intends to perform.  Must appear in the
            policy's action whitelist.
        data:
            Data that may need to be scrubbed for privacy before being passed to
            the task.
        task:
            Callable representing the work to be executed.
        """
        try:
            self.policy.check_action(action)
            self.policy.enforce_resource_limits()
            safe_data = self.policy.apply_privacy(data)
            return task(safe_data, *args, **kwargs)
        except (PermissionError, ResourceLimitExceeded) as exc:
            self.logger.error(f"Policy violation: {exc}")
            self.policy.audit_log(f"Policy violation: {exc}")
            self.policy.stopped.set()
            raise
        except EmergencyStop:
            # Emergency stop already logs via PolicyManager
            self.logger.critical("Emergency stop invoked during task execution")
            self.policy.stopped.set()
            self.policy.audit_log("Emergency stop invoked during task execution")
            raise

    def emergency_stop(self):
        """Trigger an emergency stop manually."""
        self.policy.emergency_stop()

