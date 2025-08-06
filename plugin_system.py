"""Simple file based plugin registry.

The registry scans a directory for ``.py`` files and treats each module as a
plugin.  Plugins may expose a ``PLUGIN_META`` dictionary for metadata and must
implement a ``run`` function to be executed.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Dict, List


class PluginRegistry:
    """Discover and execute Python based plugins."""

    def __init__(self, plugin_dir: str | Path = "plugins", logger=None) -> None:
        self.plugin_dir = Path(plugin_dir)
        self.logger = logger
        self.plugins: Dict[str, Path] = {}
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        self.scan_plugins()

    def scan_plugins(self) -> None:
        """Scan the plugin directory for available plugins."""
        self.plugins = {}
        for file in self.plugin_dir.iterdir():
            if file.suffix == ".py" and not file.name.startswith("_"):
                self.plugins[file.stem] = file

    def load_plugin(self, plugin_name: str):
        """Load the named plugin module."""
        path = self.plugins.get(plugin_name)
        if not path:
            # Rescan in case a new plugin was added after initialization
            self.scan_plugins()
            path = self.plugins.get(plugin_name)
            if not path:
                raise ImportError(f"Plugin {plugin_name} not found.")
        spec = importlib.util.spec_from_file_location(plugin_name, str(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def get_metadata(self, plugin_name: str) -> Dict[str, object]:
        try:
            mod = self.load_plugin(plugin_name)
            return getattr(mod, "PLUGIN_META", {})
        except Exception as e:  # pragma: no cover - defensive logging
            if self.logger:
                self.logger.warning(f"Failed to load plugin {plugin_name}: {e}")
            return {}

    def list_plugins(self) -> List[Dict[str, object]]:
        self.scan_plugins()
        result: List[Dict[str, object]] = []
        for pname in self.plugins:
            meta = self.get_metadata(pname)
            result.append({"name": pname, "meta": meta})
        return result

    def execute_plugin(self, plugin_name: str, **kwargs):
        plugin = self.load_plugin(plugin_name)
        if hasattr(plugin, "run"):
            return plugin.run(**kwargs)
        else:
            raise AttributeError(f"Plugin {plugin_name} has no run()")
