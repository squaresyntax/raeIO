from policy_manager import PolicyManager, EmergencyStop
from safety_enforcement import SafetyManager


def example_task(data):
    # Placeholder for real work; returns processed data
    return data

def main():
    policy = PolicyManager(config_path='config.yaml')
    policy.register_signal_handlers()
    safety = SafetyManager(policy)

    try:
        # Example task loop
        while not policy.stopped.is_set():
            # Run a task under safety enforcement. Replace with real tasks.
            safety.execute("read", "user@example.com", example_task)
    except EmergencyStop:
        print("Program halted by emergency stop.")
    except Exception as e:
        policy.audit_log(f"Unhandled exception: {e}")
        # Optionally restart or clean up

if __name__ == '__main__':
    main()

