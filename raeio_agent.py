import os
import time

from task_memory import TaskMemory
from cache_manager import CacheManager
from plugin_system import PluginRegistry
from tts_manager import TTSManager

# dispatchable helper functions for core task types
from art_generator import generate_art
from audio_composer import compose_audio
from text_summarizer import summarize_text

try:  # optional dependency
    from browser_automation import BrowserAutomation
except ImportError:  # pragma: no cover
    BrowserAutomation = None


# map task types to their handler functions for easy extensibility
TASK_HANDLERS = {
    "art": generate_art,
    "audio": compose_audio,
    "text": summarize_text,
}


class RAEIOAgent:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.memory = TaskMemory(path=config.get("memory_path", "task_memory.jsonl"))
        self.cache_manager = CacheManager(
            temp_dir=config.get("temp_dir", "temp"),
            cache_dir=config.get("cache_dir", "cache"),
            max_temp_mb=config.get("max_temp_mb", 500),
            max_cache_mb=config.get("max_cache_mb", 500),
            check_interval=config.get("cache_check_interval", 300),
            logger=logger,
        )
        self.cache_manager.start_auto_clean()
        self.plugin_registry = PluginRegistry(
            plugin_dir=config.get("plugin_dir", "plugins"),
            logger=logger,
        )
        self.tts_manager = TTSManager(
            voice=config.get("tts_voice", "tts_models/en/vctk/vits"),
            cache_dir=config.get("tts_cache_dir", "tts_cache"),
            logger=logger,
        )
        if BrowserAutomation:
            self.browser_automation = BrowserAutomation(
                user_agent=config.get("browser_user_agent"),
                proxy=config.get("browser_proxy"),
                headless=config.get("browser_headless", True),
                logger=logger,
            )
        else:
            self.browser_automation = None

    def run_task(self, task_type, prompt, context=None, plugin=None):
        """Execute a task and record it in memory.

        Parameters
        ----------
        task_type: str
            Type of task to perform (e.g. "art", "audio", "text").
        prompt: str
            Input prompt for the task.
        context: Optional[dict]
            Additional data for the task. Defaults to an empty dict.
        plugin: Optional[str]
            Name of a plugin to execute instead of built-in tasks.
        """

        context = context or {}
        t0 = time.time()
        try:
            if plugin:
                output = self.plugin_registry.execute_plugin(
                    plugin, prompt=prompt, context=context
                )
            elif task_type == "browser":
                if not self.browser_automation:
                    raise RuntimeError("Browser automation dependencies not installed")
                output = self.browser_automation.run_script(
                    context["url"], context["actions"]
                )
            elif task_type in TASK_HANDLERS:
                output = TASK_HANDLERS[task_type](prompt)
            else:
                raise ValueError(f"Unsupported task type: {task_type}")

            duration = time.time() - t0
            self.memory.log_task(task_type, prompt, context, output, True, duration)
            return output
        except Exception as e:
            duration = time.time() - t0
            self.memory.log_task(
                task_type,
                prompt,
                context,
                None,
                False,
                duration,
                extra_metrics={"error": str(e)},
            )
            raise RuntimeError(f"Task '{task_type}' failed: {e}") from e

    def analyze_self(self):
        perf = self.memory.analyze_performance()
        if self.logger:
            self.logger.info(f"Performance summary: {perf}")
        return perf

    def speak(self, text, voice=None, emotion=None, speaker_wav=None):
        return self.tts_manager.synthesize(
            text, voice=voice, emotion=emotion, speaker_wav=speaker_wav
        )
