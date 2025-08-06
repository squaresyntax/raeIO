import os
import time
import tempfile
import shutil
import unittest

from cache_manager import CacheManager


class CacheManagerTest(unittest.TestCase):
    def test_delete_old_files(self):
        temp_dir = tempfile.mkdtemp()
        cache_dir = tempfile.mkdtemp()
        try:
            new_file = os.path.join(temp_dir, "new.txt")
            with open(new_file, "w") as f:
                f.write("new")

            old_file = os.path.join(temp_dir, "old.txt")
            with open(old_file, "w") as f:
                f.write("old")
            old_time = time.time() - 10
            os.utime(old_file, (old_time, old_time))

            manager = CacheManager(temp_dir=temp_dir, cache_dir=cache_dir, max_file_age=5)
            manager.delete_old_files(temp_dir)

            self.assertFalse(os.path.exists(old_file))
            self.assertTrue(os.path.exists(new_file))
        finally:
            shutil.rmtree(temp_dir)
            shutil.rmtree(cache_dir)


if __name__ == "__main__":
    unittest.main()
