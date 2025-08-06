import os
import shutil
import subprocess
import threading
import time
import hashlib
from typing import Optional, Dict


class UpdateError(Exception):
    """Custom exception for update failures."""


class UpdateManager:
    """Fetch and apply updates for model checkpoints or plugins.

    Supports local filesystem paths or git repositories as sources.
    Provides version checking, optional SHA256 signature validation,
    and automatic rollback on failure. Updates can be triggered
    manually or scheduled periodically.
    """

    def __init__(self, rollback_dir: str = "rollback", logger=None):
        self.rollback_dir = rollback_dir
        self.logger = logger
        self.installed_versions: Dict[str, str] = {}
        os.makedirs(self.rollback_dir, exist_ok=True)

    # ----------------------------- Utilities -----------------------------
    def _log(self, msg: str):
        if self.logger:
            self.logger.info(msg)

    def _parse_version(self, v: str):
        try:
            return tuple(int(x) for x in v.split('.'))
        except Exception:
            return (0,)

    def _compute_signature(self, path: str) -> str:
        h = hashlib.sha256()
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                for fname in sorted(files):
                    fpath = os.path.join(root, fname)
                    with open(fpath, 'rb') as f:
                        for chunk in iter(lambda: f.read(8192), b''):
                            h.update(chunk)
        else:
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    h.update(chunk)
        return h.hexdigest()

    def _backup(self, target: str) -> Optional[str]:
        if not os.path.exists(target):
            return None
        ts = time.strftime("%Y%m%d%H%M%S")
        backup_path = os.path.join(self.rollback_dir, f"{os.path.basename(target)}_{ts}")
        if os.path.isdir(target):
            shutil.copytree(target, backup_path)
        else:
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(target, backup_path)
        return backup_path

    def _rollback(self, backup: Optional[str], target: str):
        if not backup:
            return
        if os.path.isdir(backup):
            if os.path.exists(target):
                shutil.rmtree(target)
            shutil.copytree(backup, target)
        else:
            shutil.copy2(backup, target)
        self._log(f"Rolled back update for {target}")

    # ----------------------------- Fetchers -----------------------------
    def _fetch_from_git(self, url: str, dest: str):
        if os.path.exists(dest):
            shutil.rmtree(dest)
        subprocess.check_call(["git", "clone", url, dest])

    def _fetch_from_path(self, src: str, dest: str):
        if os.path.isdir(src):
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
        else:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(src, dest)

    # ----------------------------- Public API -----------------------------
    def update(
        self,
        name: str,
        source: str,
        dest: str,
        version: str,
        signature: Optional[str] = None,
        from_git: bool = False,
    ):
        """Fetch and apply an update from ``source`` to ``dest``.

        Args:
            name: Unique identifier for the artifact.
            source: Local path or git URL.
            dest: Destination path.
            version: Version string for the new artifact.
            signature: Optional SHA256 hash to validate integrity.
            from_git: Treat ``source`` as a git repository if True.
        """
        current = self.installed_versions.get(name)
        if current and self._parse_version(version) <= self._parse_version(current):
            raise UpdateError("New version must be greater than installed version")

        backup = self._backup(dest)
        try:
            if from_git:
                self._fetch_from_git(source, dest)
            else:
                self._fetch_from_path(source, dest)

            if signature:
                actual_sig = self._compute_signature(dest)
                if actual_sig != signature:
                    raise UpdateError("Signature mismatch")

            self.installed_versions[name] = version
            self._log(f"Updated {name} to version {version}")
        except Exception as e:
            self._rollback(backup, dest)
            raise UpdateError(str(e))

    def schedule_update(
        self,
        name: str,
        interval: int,
        source: str,
        dest: str,
        version: str,
        signature: Optional[str] = None,
        from_git: bool = False,
    ) -> threading.Timer:
        """Schedule recurring updates every ``interval`` seconds."""

        def task():
            try:
                self.update(name, source, dest, version, signature, from_git)
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Scheduled update failed for {name}: {e}")
            else:
                # reschedule on success or failure for continuous checks
                self.schedule_update(name, interval, source, dest, version, signature, from_git)

        timer = threading.Timer(interval, task)
        timer.daemon = True
        timer.start()
        return timer


__all__ = ["UpdateManager", "UpdateError"]

