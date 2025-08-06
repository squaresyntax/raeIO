import os
import shutil
import tempfile
import time

class CacheManager:
    def __init__(
        self,
        temp_dir="temp",
        cache_dir="cache",
        max_temp_mb=500,
        max_cache_mb=500,
        check_interval=300,
        file_ttl=60 * 60,
        logger=None,
    ):
        self.temp_dir = temp_dir
        self.cache_dir = cache_dir
        self.max_temp_mb = max_temp_mb
        self.max_cache_mb = max_cache_mb
        self.check_interval = check_interval
        self.file_ttl = file_ttl
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

    def create_temp_file(self, suffix=""):
        temp_file = tempfile.NamedTemporaryFile(delete=False, dir=self.temp_dir, suffix=suffix)
        temp_file.close()
        return temp_file.name

    def delete_old_files(self):
        now = time.time()
        for d in [self.temp_dir, self.cache_dir]:
            for fname in os.listdir(d):
                fpath = os.path.join(d, fname)
                try:
                    mtime = os.path.getmtime(fpath)
                    if now - mtime > self.file_ttl:
                        if os.path.isfile(fpath) or os.path.islink(fpath):
                            os.unlink(fpath)
                        elif os.path.isdir(fpath):
                            shutil.rmtree(fpath)
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"Failed to remove {fpath}: {e}")

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
                self.delete_old_files()
                self.enforce_thresholds()
                time.sleep(self.check_interval)

        t = threading.Thread(target=loop, daemon=True)
        t.start()

    def clear_cache(self):
        self.clean_dir(self.temp_dir)
        self.clean_dir(self.cache_dir)
        if self.logger:
            self.logger.info("Manual cache/temp clean triggered.")
