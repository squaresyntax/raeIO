"""Entry point demonstrating policy and safety enforcement."""

import time
from policy_manager import PolicyManager, EmergencyStop
from safety_enforcement import SafetyManager


def main() -> None:
    policy = PolicyManager(config_path="config.yaml")
    safety = SafetyManager(
        resource_limits=policy.config.get("resource_limits"),
        privacy_settings=policy.config.get("privacy_settings"),
        action_whitelist=policy.config.get("security", {}).get("action_whitelist"),
    )
    policy.register_signal_handlers()

    try:
        # Example task loop – in real usage replace with actual work
        for _ in range(3):
            # Enforce resource limits; any exception halts execution
            policy.enforce_resource_limits()
            safety.enforce_resource_limits()

            action = "read"  # Replace with real action
            policy.check_action(action)
            safety.check_action(action)

            # Example data handling
            data = "Contact me at test@example.com or 555-123-4567"
            data = policy.apply_privacy(data)
            data = safety.scrub_data(data)
            print(data)

            time.sleep(0.1)

    except (EmergencyStop, SystemExit, MemoryError, RuntimeError, PermissionError) as err:
        policy.audit_log(str(err))
        safety.audit_log(str(err))
        print(f"Execution halted: {err}")


if __name__ == "__main__":
    main()

