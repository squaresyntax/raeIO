import time
from task_memory import TaskMemory
from cache_manager import CacheManager
from plugin_system import PluginRegistry
from tts_manager import TTSManager
from browser_automation import BrowserAutomation
from generative_media_manager import GenerativeMediaManager
from text_analyzers import summarize_text, sentiment_analysis


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
        self.browser_automation = BrowserAutomation(
            user_agent=config.get("browser_user_agent"),
            proxy=config.get("browser_proxy"),
            headless=config.get("browser_headless", True),
            logger=logger,
        )
        self.media_manager = GenerativeMediaManager(
            output_dir=config.get("output_dir", "outputs"),
            logger=logger,
        )

    def run_task(self, task_type, prompt, context=None, plugin=None):
        context = context or {}
        if not isinstance(context, dict):
            raise ValueError("context must be a dict")
        t0 = time.time()
        try:
            if plugin:
                output = self.plugin_registry.execute_plugin(plugin, prompt=prompt, context=context)
            elif task_type == "browser":
                if "url" not in context or "actions" not in context:
                    raise ValueError("Browser task requires 'url' and 'actions' in context")
                output = self.browser_automation.run_script(context["url"], context["actions"])
            elif task_type == "image":
                if not prompt:
                    raise ValueError("Image generation requires a prompt")
                output = self.media_manager.generate_image(prompt)
            elif task_type == "video":
                if not prompt:
                    raise ValueError("Video generation requires a prompt")
                duration_arg = context.get("duration", 5)
                output = self.media_manager.generate_video(prompt, duration=duration_arg)
            elif task_type == "audio":
                if not prompt:
                    raise ValueError("Audio generation requires a prompt")
                duration_arg = context.get("duration", 5)
                output = self.media_manager.generate_audio(prompt, duration=duration_arg)
            elif task_type == "summarize":
                output = summarize_text(prompt)
            elif task_type == "sentiment":
                output = sentiment_analysis(prompt)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
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
            raise

    def analyze_self(self):
        perf = self.memory.analyze_performance()
        if self.logger:
            self.logger.info(f"Performance summary: {perf}")
        return perf

    def speak(self, text, voice=None, emotion=None, speaker_wav=None):
        return self.tts_manager.synthesize(
            text, voice=voice, emotion=emotion, speaker_wav=speaker_wav
        )

