import os
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from cache_manager import CacheManager
from raeio_agent import RAEIOAgent


def test_agent_clear_cache_removes_temp_files(tmp_path):
    config = {
        "temp_dir": str(tmp_path / "temp"),
        "cache_dir": str(tmp_path / "cache"),
        "cache_check_interval": 1,
        "cache_file_ttl": 1,
    }
    agent = RAEIOAgent(config, logger=None)
    temp_path = agent.cache_manager.create_temp_file(suffix=".txt")
    assert os.path.exists(temp_path)
    agent.clear_cache()
    assert not os.path.exists(temp_path)


def test_delete_old_files_removes_expired_files(tmp_path):
    cm = CacheManager(
        temp_dir=str(tmp_path / "temp"),
        cache_dir=str(tmp_path / "cache"),
        file_ttl=1,
        check_interval=1,
    )
    path = cm.create_temp_file(suffix=".tmp")
    old = time.time() - 5
    os.utime(path, (old, old))
    cm.delete_old_files()
    assert not os.path.exists(path)

