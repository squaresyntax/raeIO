import os
import shutil
import time


class CacheManager:
    def __init__(
        self,
        temp_dir="temp",
        cache_dir="cache",
        max_temp_mb=500,
        max_cache_mb=500,
        check_interval=300,
        max_file_age=24 * 60 * 60,
        logger=None,
    ):
        self.temp_dir = temp_dir
        self.cache_dir = cache_dir
        self.max_temp_mb = max_temp_mb
        self.max_cache_mb = max_cache_mb
        self.check_interval = check_interval
        self.max_file_age = max_file_age
        self.logger = logger
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_dir_size_mb(self, path):
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.isfile(fp):
                    total += os.path.getsize(fp)
        return total / (1024 * 1024)

    def clean_dir(self, path):
        for fname in os.listdir(path):
            fpath = os.path.join(path, fname)
            try:
                if os.path.isfile(fpath) or os.path.islink(fpath):
                    os.unlink(fpath)
                elif os.path.isdir(fpath):
                    shutil.rmtree(fpath)
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Failed to remove {fpath}: {e}")

    def delete_old_files(self, path):
        now = time.time()
        for root, dirs, files in os.walk(path):
            for name in files:
                fpath = os.path.join(root, name)
                try:
                    if now - os.path.getmtime(fpath) > self.max_file_age:
                        if os.path.isfile(fpath) or os.path.islink(fpath):
                            os.unlink(fpath)
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"Failed to remove old file {fpath}: {e}")
            for name in dirs:
                dpath = os.path.join(root, name)
                try:
                    if now - os.path.getmtime(dpath) > self.max_file_age:
                        shutil.rmtree(dpath)
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"Failed to remove old directory {dpath}: {e}")

    def enforce_thresholds(self):
        temp_size = self.get_dir_size_mb(self.temp_dir)
        cache_size = self.get_dir_size_mb(self.cache_dir)
        if temp_size > self.max_temp_mb:
            if self.logger:
                self.logger.info(f"Temp dir exceeds threshold ({temp_size:.2f}MB > {self.max_temp_mb}MB), cleaning...")
            self.clean_dir(self.temp_dir)
        if cache_size > self.max_cache_mb:
            if self.logger:
                self.logger.info(f"Cache dir exceeds threshold ({cache_size:.2f}MB > {self.max_cache_mb}MB), cleaning...")
            self.clean_dir(self.cache_dir)

    def start_auto_clean(self):
        import threading
        def loop():
            while True:
                self.enforce_thresholds()
                self.delete_old_files(self.temp_dir)
                self.delete_old_files(self.cache_dir)
                time.sleep(self.check_interval)
        t = threading.Thread(target=loop, daemon=True)
        t.start()

    def manual_clean(self):
        self.clean_dir(self.temp_dir)
        self.clean_dir(self.cache_dir)
        if self.logger:
            self.logger.info("Manual cache/temp clean triggered.")
