class ModelAdapter:
    """Simple placeholder for external model adapters."""
    def __init__(self, logger=None, fuckery_mode=False):
        self.logger = logger
        self.fuckery_mode = fuckery_mode
        self.encryption_enabled = False
        if fuckery_mode:
            self.enable_encryption()

    def enable_encryption(self):
        self.encryption_enabled = True

    def disable_encryption(self):
        self.encryption_enabled = False

    def set_fuckery_mode(self, enabled: bool):
        self.fuckery_mode = enabled
        if enabled:
            self.enable_encryption()
        else:
            self.disable_encryption()
