import os
import time
from task_memory import TaskMemory
from cache_manager import CacheManager
from plugin_system import PluginRegistry
from tts_manager import TTSManager
from browser_automation import BrowserAutomation

class RAEIOAgent:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.fuckery_mode = config.get("fuckery_mode", False)
        self.memory = TaskMemory(
            path=config.get("memory_path", "task_memory.jsonl"),
            fuckery_mode=self.fuckery_mode,
        )
        self.cache_manager = CacheManager(
            temp_dir=config.get("temp_dir", "temp"),
            cache_dir=config.get("cache_dir", "cache"),
            max_temp_mb=config.get("max_temp_mb", 500),
            max_cache_mb=config.get("max_cache_mb", 500),
            check_interval=config.get("cache_check_interval", 300),
            logger=logger,
            fuckery_mode=self.fuckery_mode,
        )
        self.cache_manager.start_auto_clean()
        self.plugin_registry = PluginRegistry(
            plugin_dir=config.get("plugin_dir", "plugins"),
            logger=logger,
            fuckery_mode=self.fuckery_mode,
        )
        self.tts_manager = TTSManager(
            voice=config.get("tts_voice", "tts_models/en/vctk/vits"),
            cache_dir=config.get("tts_cache_dir", "tts_cache"),
            logger=logger,
            fuckery_mode=self.fuckery_mode,
        )
        self.browser_automation = BrowserAutomation(
            user_agent=config.get("browser_user_agent"),
            proxy=config.get("browser_proxy"),
            headless=config.get("browser_headless", True),
            logger=logger,
            fuckery_mode=self.fuckery_mode,
        )

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

    def set_fuckery_mode(self, enabled: bool):
        self.fuckery_mode = enabled
        self.memory.fuckery_mode = enabled
        self.cache_manager.secure_delete = enabled
        self.plugin_registry.fuckery_mode = enabled
        self.tts_manager.fuckery_mode = enabled
        self.browser_automation.set_fuckery_mode(enabled)
