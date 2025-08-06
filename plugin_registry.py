import importlib
import os

class PluginRegistry:
    """Dynamically discover and load plugins of various types."""
    def __init__(self, plugin_dirs):
        self.plugin_dirs = plugin_dirs
        self.plugins = {}
        self.discover_plugins()

    def discover_plugins(self):
        for d in self.plugin_dirs:
            for fname in os.listdir(d):
                if fname.endswith(".py") and not fname.startswith("__"):
                    mod_name = fname[:-3]
                    try:
                        mod = importlib.import_module(f"{d.replace('/', '.')}.{mod_name}")
                        if hasattr(mod, "register"):
                            plugin = mod.register()
                            self.plugins[plugin["name"]] = plugin
                    except Exception as e:
                        print(f"Plugin load error ({fname}): {e}")

    def call(self, name, *args, **kwargs):
        if name in self.plugins:
            return self.plugins[name]["func"](*args, **kwargs)
        raise ValueError(f"Plugin {name} not found")