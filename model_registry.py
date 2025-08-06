class ModelRegistry:
    """Simple registry to lazily load model adapters."""
    def __init__(self, config, logger=None):
        self.config = config or {}
        self.logger = logger
        self.loaders = {
            "stable_diffusion": self._load_stable_diffusion,
            "whisper": self._load_whisper,
        }
        self.adapters = {}

    def get_adapter(self, key):
        if key not in self.adapters:
            cfg = self.config.get(key, {})
            if not cfg.get("enabled"):
                raise ValueError(f"Model {key} is disabled")
            loader = self.loaders.get(key)
            if not loader:
                raise ValueError(f"Unknown model key: {key}")
            self.adapters[key] = loader(cfg)
        return self.adapters[key]

    def _load_stable_diffusion(self, cfg):
        checkpoint = cfg.get("checkpoint")
        def generate(prompt, context=None):
            return f"Stable Diffusion model at {checkpoint} generated: {prompt}"
        return generate

    def _load_whisper(self, cfg):
        checkpoint = cfg.get("checkpoint")
        def transcribe(prompt, context=None):
            return f"Whisper model at {checkpoint} transcribed: {prompt}"
        return transcribe
