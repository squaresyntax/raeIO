from policy_manager import PolicyManager, EmergencyStop

def main():
    policy = PolicyManager(config_path='config.yaml')
    policy.register_signal_handlers()

    try:
        # Example task loop
        while not policy.stopped.is_set():
            # Example: check resource usage
            policy.enforce_resource_limits()
            # Example: enforce action
            action = "read"  # Replace with real action
            policy.check_action(action)
            # ... do work ...
    except EmergencyStop:
        print("Program halted by emergency stop.")
    except Exception as e:
        policy.audit_log(f"Unhandled exception: {e}")
        # Optionally restart or clean up

if __name__ == '__main__':
    main()