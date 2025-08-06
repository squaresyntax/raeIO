import os
import time
from dataclasses import dataclass, field
from cryptography.fernet import Fernet

from task_memory import TaskMemory
from cache_manager import CacheManager
from plugin_system import PluginRegistry
from tts_manager import TTSManager
from browser_automation import BrowserAutomation


@dataclass
class ModeFlags:
    """Holds runtime mode toggles for the agent."""
    fuckery_mode: bool = False
    stealth_mode: bool = False
    training_mode: bool = False
    fuckery_key: bytes | None = field(default=None, repr=False)

    def enable_fuckery(self) -> None:
        self.fuckery_mode = True
        self.stealth_mode = True
        if not self.fuckery_key:
            self.fuckery_key = Fernet.generate_key()

    def disable_fuckery(self) -> None:
        self.fuckery_mode = False
        self.stealth_mode = False

    def encrypt(self, data: bytes) -> bytes:
        if not self.fuckery_key:
            raise ValueError("No encryption key set for fuckery mode")
        return Fernet(self.fuckery_key).encrypt(data)

    def decrypt(self, data: bytes) -> bytes:
        if not self.fuckery_key:
            raise ValueError("No encryption key set for fuckery mode")
        return Fernet(self.fuckery_key).decrypt(data)

class RAEIOAgent:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.flags = ModeFlags()
        self.memory = TaskMemory(path=config.get("memory_path", "task_memory.jsonl"))
        self.cache_manager = CacheManager(
            temp_dir=config.get("temp_dir", "temp"),
            cache_dir=config.get("cache_dir", "cache"),
            max_temp_mb=config.get("max_temp_mb", 500),
            max_cache_mb=config.get("max_cache_mb", 500),
            check_interval=config.get("cache_check_interval", 300),
            logger=logger
        )
        self.cache_manager.start_auto_clean()
        self.plugin_registry = PluginRegistry(plugin_dir=config.get("plugin_dir", "plugins"), logger=logger)
        self.tts_manager = TTSManager(
            voice=config.get("tts_voice", "tts_models/en/vctk/vits"),
            cache_dir=config.get("tts_cache_dir", "tts_cache"),
            logger=logger
        )
        self.browser_automation = BrowserAutomation(
            user_agent=config.get("browser_user_agent"),
            proxy=config.get("browser_proxy"),
            headless=config.get("browser_headless", True),
            logger=logger
        )
        self._propagate_flags()

    def _propagate_flags(self) -> None:
        for subsystem in (
            self.memory,
            self.cache_manager,
            self.plugin_registry,
            self.tts_manager,
            self.browser_automation,
        ):
            if hasattr(subsystem, "update_mode_flags"):
                subsystem.update_mode_flags(self.flags)

    def set_mode(self, mode: str, feature_focus: str | None = None) -> None:
        self.flags.training_mode = False
        self.flags.disable_fuckery()
        if mode == "Fuckery":
            self.flags.enable_fuckery()
        elif mode == "Training":
            self.flags.training_mode = True
        self._propagate_flags()

    def run_task(self, task_type, prompt, context, plugin=None):
        t0 = time.time()
        try:
            if plugin:
                output = self.plugin_registry.execute_plugin(plugin, prompt=prompt, context=context)
            elif task_type == "browser":
                output = self.browser_automation.run_script(context["url"], context["actions"])
            else:
                output = f"Stub output for {task_type}: {prompt}"
            duration = time.time() - t0
            self.memory.log_task(task_type, prompt, context, output, True, duration)
            return output
        except Exception as e:
            duration = time.time() - t0
            self.memory.log_task(task_type, prompt, context, None, False, duration, extra_metrics={"error": str(e)})
            raise

    def analyze_self(self):
        perf = self.memory.analyze_performance()
        if self.logger:
            self.logger.info(f"Performance summary: {perf}")
        return perf

    def speak(self, text, voice=None, emotion=None, speaker_wav=None):
        return self.tts_manager.synthesize(text, voice=voice, emotion=emotion, speaker_wav=speaker_wav)