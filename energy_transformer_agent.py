import threading
import signal
import logging
import yaml
import time
import sys
import os
import traceback
import queue

try:
    import psutil
except ImportError:
    psutil = None

import re
import subprocess

# --- Utility Functions ---
def is_pii(text):
    # Simple regex for email/phone. Use libraries for production (e.g., presidio)
    email_regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    phone_regex = r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
    if re.search(email_regex, text) or re.search(phone_regex, text):
        return True
    return False

def moderate_content(text):
    # Basic NSFW filter; use OpenAI/Google APIs or open-source NSFW models for production
    nsfw_words = ["nsfw", "nude", "violence", "gore", "sex"]
    return any(word in text.lower() for word in nsfw_words)

# --- Policy/Resource Manager ---
class EmergencyStop(Exception):
    pass

class PolicyManager:
    def __init__(self, config_path='config.yaml'):
        self.stopped = threading.Event()
        self.logger = logging.getLogger("PolicyManager")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)
        self.load_config(config_path)

    def load_config(self, path):
        if not os.path.exists(path):
            self.logger.error(f"Config file not found: {path}")
            sys.exit(1)
        with open(path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.logger.info(f"Configuration loaded from {path}")

    def check_action(self, action: str):
        allowed = self.config.get('security', {}).get('action_whitelist', [])
        if action not in allowed:
            self.logger.warning(f"Action '{action}' not permitted.")
            raise PermissionError(f"Action '{action}' is not allowed by policy.")
        self.logger.info(f"Action '{action}' permitted.")

    def enforce_resource_limits(self):
        limits = self.config.get('resource_limits', {})
        if psutil:
            # RAM
            mem_used_mb = psutil.virtual_memory().used // (1024 * 1024)
            if mem_used_mb > limits.get('memory_mb', 2048):
                self.logger.error(f"Memory usage exceeded: {mem_used_mb}MB > {limits.get('memory_mb', 2048)}MB")
                raise MemoryError("Memory limit exceeded")
            # CPU (over 10s window)
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > limits.get('cpu_percent', 90):
                self.logger.error(f"CPU usage exceeded: {cpu_percent}% > {limits.get('cpu_percent', 90)}%")
                raise RuntimeError("CPU limit exceeded")
        else:
            self.logger.warning("psutil not installed; resource limits not enforced.")

    def audit_log(self, event):
        self.logger.info(f"AUDIT: {event}")

    def emergency_stop(self, signum=None, frame=None):
        self.logger.critical("Emergency stop triggered! Halting all processes.")
        self.stopped.set()
        raise EmergencyStop("Emergency stop activated.")

    def register_signal_handlers(self):
        signal.signal(signal.SIGINT, self.emergency_stop)
        signal.signal(signal.SIGTERM, self.emergency_stop)

    def auto_test(self):
        if self.config.get('robustness', {}).get('auto_test', False):
            self.logger.info("Running self-tests.")
            try:
                assert 'security' in self.config, "Missing security config"
                assert 'resource_limits' in self.config, "Missing resource_limits config"
                self.logger.info("Basic config self-test passed.")
            except Exception as e:
                self.logger.error(f"Self-test failed: {e}")
                if self.config.get('robustness', {}).get('auto_restart_on_failure', False):
                    self.logger.info("Restarting due to failed self-test.")
                    os.execv(sys.executable, ['python'] + sys.argv)

    def enforce_anonymity(self):
        # STUB: Add proxy to requests if used
        if self.config['privacy_settings'].get('use_proxy', False):
            proxy = self.config['privacy_settings'].get('proxy_url')
            self.logger.info(f"Proxy enabled: {proxy}")
        else:
            self.logger.info("Proxy not enabled.")

    def redact_and_moderate(self, text):
        # Redact PII
        if self.config['privacy_settings'].get('redact_pii', False) and is_pii(text):
            self.logger.warning("PII detected and redacted.")
            return "[REDACTED]"
        # Moderate NSFW
        if moderate_content(text):
            self.logger.warning("NSFW content detected and blocked.")
            return "[CONTENT MODERATION BLOCKED]"
        return text

    def checkpoint_state(self, state, path='agent_checkpoint.yaml'):
        try:
            with open(path, 'w') as f:
                yaml.dump(state, f)
            self.logger.info(f"Checkpointed agent state to {path}")
        except Exception as e:
            self.logger.error(f"Failed to checkpoint state: {e}")

    def recover_state(self, path='agent_checkpoint.yaml'):
        if os.path.exists(path):
            with open(path, 'r') as f:
                state = yaml.safe_load(f)
            self.logger.info(f"Recovered agent state from {path}")
            return state
        return {}

# --- Generative Media Modules with Timeouts & Sandboxing ---
class GenerationTimeout(Exception):
    pass

class GenerativeMediaManager:
    def __init__(self, output_dir="outputs", logger=None, timeout=30,
                 consistency_threshold: float = 0.8, raise_on_mismatch: bool = True):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger = logger or logging.getLogger("GenerativeMediaManager")
        self.timeout = timeout
        self.consistency_threshold = consistency_threshold
        self.raise_on_mismatch = raise_on_mismatch

    def _embed_text(self, text: str):
        tokens = re.findall(r"\w+", text.lower())
        return set(tokens)

    def _similarity(self, a, b):
        if not a or not b:
            return 0.0
        return len(a & b) / len(a | b)

    def _run_with_timeout(self, func, *args, **kwargs):
        result_queue = queue.Queue()
        def wrapper():
            try:
                result_queue.put(func(*args, **kwargs))
            except Exception as e:
                result_queue.put(e)
        t = threading.Thread(target=wrapper)
        t.daemon = True
        t.start()
        t.join(self.timeout)
        if t.is_alive():
            self.logger.error("Generation timeout")
            raise GenerationTimeout("Generation timed out.")
        res = result_queue.get()
        if isinstance(res, Exception):
            raise res
        return res

    def generate_image(self, prompt: str):
        return self._run_with_timeout(self._safe_generate_image, prompt)

    def _safe_generate_image(self, prompt: str):
        # Sandbox demo: use subprocess for real model inference if unsafe
        self.logger.info(f"Generating image for prompt: {prompt}")
        if moderate_content(prompt) or is_pii(prompt):
            raise ValueError("Unsafe prompt blocked.")
        image_path = os.path.join(self.output_dir, "image_result.png")
        # Replace with actual model inference code
        with open(image_path, "wb") as f:
            f.write(b'')
        return image_path, prompt

    def generate_video(self, prompt: str, duration=5):
        return self._run_with_timeout(self._safe_generate_video, prompt, duration)

    def _safe_generate_video(self, prompt: str, duration=5):
        self.logger.info(f"Generating video for prompt: {prompt}, duration: {duration}s")
        if moderate_content(prompt) or is_pii(prompt):
            raise ValueError("Unsafe prompt blocked.")
        video_path = os.path.join(self.output_dir, "video_result.mp4")
        with open(video_path, "wb") as f:
            f.write(b'')
        return video_path, prompt

    def generate_audio(self, prompt: str, duration=5):
        return self._run_with_timeout(self._safe_generate_audio, prompt, duration)

    def _safe_generate_audio(self, prompt: str, duration=5):
        self.logger.info(f"Generating audio for prompt: {prompt}, duration: {duration}s")
        if moderate_content(prompt) or is_pii(prompt):
            raise ValueError("Unsafe prompt blocked.")
        audio_path = os.path.join(self.output_dir, "audio_result.wav")
        with open(audio_path, "wb") as f:
            f.write(b'')
        return audio_path, prompt

    # Modal consistency using simple token overlap embedding
    def check_modal_consistency(self, prompt_text: str, output_text: str):
        prompt_emb = self._embed_text(prompt_text)
        output_emb = self._embed_text(output_text)
        similarity = self._similarity(prompt_emb, output_emb)
        if similarity < self.consistency_threshold:
            self.logger.error(
                f"Modal inconsistency detected: similarity {similarity:.2f} below {self.consistency_threshold}"
            )
            if self.raise_on_mismatch:
                raise ValueError("Modal inconsistency detected")
            return False
        self.logger.info(
            f"Modal consistency verified: similarity {similarity:.2f}"
        )
        return True

# --- Main Agent ---
class EnergyTransformerAgent:
    def __init__(self, config_path='config.yaml'):
        self.policy = PolicyManager(config_path)
        self.policy.register_signal_handlers()
        self.policy.enforce_anonymity()
        self.media_manager = GenerativeMediaManager(logger=self.policy.logger)
        self.last_state = self.policy.recover_state()
        self.run_count = self.last_state.get("run_count", 0)
        self.error_count = self.last_state.get("error_count", 0)

    def contextual_analysis(self):
        self.policy.logger.info("Performing contextual analysis...")
        return "A futuristic city skyline at sunset"

    def determine_generation_type(self):
        # Alternate between modalities for demo
        ts = (self.run_count) % 3
        if ts == 0:
            return "image"
        elif ts == 1:
            return "video"
        else:
            return "audio"

    def run(self):
        self.policy.auto_test()
        try:
            while not self.policy.stopped.is_set():
                self.policy.enforce_resource_limits()
                action = "analyze"
                try:
                    self.policy.check_action(action)
                except PermissionError as e:
                    self.policy.audit_log(f"Blocked action: {e}")
                    continue

                prompt = self.contextual_analysis()
                prompt = self.policy.redact_and_moderate(prompt)
                gen_type = self.determine_generation_type()
                output_info = None

                try:
                    if gen_type == "image":
                        output_info = self.media_manager.generate_image(prompt)
                    elif gen_type == "video":
                        output_info = self.media_manager.generate_video(prompt)
                    elif gen_type == "audio":
                        output_info = self.media_manager.generate_audio(prompt)
                    else:
                        self.policy.audit_log("Unknown generation type")
                        continue

                    if output_info:
                        output_path, output_desc = output_info
                        self.policy.audit_log(f"Generated {gen_type} saved at: {output_path}")

                        # Consistency check
                        self.media_manager.check_modal_consistency(prompt, output_desc)
                except (GenerationTimeout, ValueError) as e:
                    self.policy.audit_log(f"Generation failed: {e}")
                    self.error_count += 1
                except Exception as e:
                    self.policy.audit_log(f"Unhandled exception: {e}\n{traceback.format_exc()}")
                    self.error_count += 1
                    if self.policy.config.get('robustness', {}).get('auto_restart_on_failure', False):
                        self.policy.logger.info("Restarting agent due to exception.")
                        # Checkpoint state before restart
                        self.policy.checkpoint_state({"run_count": self.run_count, "error_count": self.error_count})
                        os.execv(sys.executable, ['python'] + sys.argv)

                self.run_count += 1
                # Checkpoint after each run
                self.policy.checkpoint_state({"run_count": self.run_count, "error_count": self.error_count})

                time.sleep(2)
        except EmergencyStop:
            self.policy.logger.info("Agent terminated by emergency stop.")
        except Exception as e:
            self.policy.audit_log(f"Agent crashed: {e}\n{traceback.format_exc()}")
            self.policy.checkpoint_state({"run_count": self.run_count, "error_count": self.error_count})

if __name__ == '__main__':
    agent = EnergyTransformerAgent(config_path='config.yaml')
    agent.run()