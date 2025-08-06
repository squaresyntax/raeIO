import os
import json
import time
from datetime import datetime

class TaskMemory:
    def __init__(self, path="task_memory.jsonl", max_entries=10000):
        self.path = path
        self.max_entries = max_entries
        self._create_file()
        self.flags = None

    def update_mode_flags(self, flags) -> None:
        self.flags = flags

    def _create_file(self):
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                pass

    def log_task(self, task_type, prompt, context, output_path, success, duration, extra_metrics=None):
        if self.flags and self.flags.stealth_mode:
            return
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "task_type": task_type,
            "prompt": prompt,
            "context": context,
            "output_path": output_path,
            "success": success,
            "duration": duration,
            "metrics": extra_metrics or {},
        }
        line = json.dumps(entry)
        if self.flags and self.flags.fuckery_mode:
            line = self.flags.encrypt(line.encode()).decode()
        with open(self.path, "a") as f:
            f.write(line + "\n")
        self._prune()

    def _prune(self):
        with open(self.path, "r") as f:
            lines = f.readlines()
        if len(lines) > self.max_entries:
            with open(self.path, "w") as f:
                f.writelines(lines[-self.max_entries:])

    def get_recent(self, n=50):
        with open(self.path, "r") as f:
            lines = f.readlines()
        result = []
        for line in lines[-n:]:
            line = line.strip()
            if not line:
                continue
            if self.flags and self.flags.fuckery_mode:
                line = self.flags.decrypt(line.encode()).decode()
            result.append(json.loads(line))
        return result

    def analyze_performance(self, n=100):
        entries = self.get_recent(n)
        if not entries:
            return {}
        durations = [e["duration"] for e in entries if "duration" in e]
        success_rate = sum(1 for e in entries if e["success"]) / len(entries)
        avg_duration = sum(durations) / len(durations) if durations else None
        return {
            "task_count": len(entries),
            "success_rate": success_rate,
            "avg_duration": avg_duration,
        }