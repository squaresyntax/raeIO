"""Simple file-based plugin discovery and execution."""

import os
import importlib.util


class PluginRegistry:
    """Discover and run plugins from a directory."""

    def __init__(self, plugin_dir: str = "plugins", logger=None):
        self.plugin_dir = plugin_dir
        self.logger = logger
        self.plugins = {}
        os.makedirs(plugin_dir, exist_ok=True)
        self.scan_plugins()

    def scan_plugins(self):
        self.plugins = {}
        for fname in os.listdir(self.plugin_dir):
            if fname.endswith(".py") and not fname.startswith("_"):
                plugin_name = fname[:-3]
                self.plugins[plugin_name] = os.path.join(self.plugin_dir, fname)

    def load_plugin(self, plugin_name):
        path = self.plugins.get(plugin_name)
        if not path:
            raise ImportError(f"Plugin {plugin_name} not found.")
        spec = importlib.util.spec_from_file_location(plugin_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def get_metadata(self, plugin_name):
        try:
            mod = self.load_plugin(plugin_name)
            return getattr(mod, "PLUGIN_META", {})
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to load plugin {plugin_name}: {e}")
            return {}

    def list_plugins(self):
        self.scan_plugins()
        result = []
        for pname in self.plugins:
            meta = self.get_metadata(pname)
            result.append({"name": pname, "meta": meta})
        return result

    def execute_plugin(self, plugin_name, **kwargs):
        plugin = self.load_plugin(plugin_name)
        if hasattr(plugin, "run"):
            return plugin.run(**kwargs)
        raise AttributeError(f"Plugin {plugin_name} has no run()")
