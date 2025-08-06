import os
import importlib.util
from update_manager import UpdateManager

class PluginRegistry:
    def __init__(self, plugin_dir="plugins", logger=None, update_manager=None):
        self.plugin_dir = plugin_dir
        self.logger = logger
        self.plugins = {}
        self.update_manager = update_manager or UpdateManager(logger=logger)
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
        else:
            raise AttributeError(f"Plugin {plugin_name} has no run()")

    def update_plugin(
        self,
        plugin_name,
        source,
        version,
        signature=None,
        from_git=False,
        schedule_interval=None,
    ):
        """Update a plugin from a local path or git repository.

        Args:
            plugin_name: Name of the plugin file (without .py).
            source: Path or git URL for the updated plugin code.
            version: Version string for the update.
            signature: Optional SHA256 signature for verification.
            from_git: If True, treat ``source`` as a git repository.
            schedule_interval: If set, schedule periodic updates every
                ``schedule_interval`` seconds instead of applying immediately.
        """
        dest = os.path.join(self.plugin_dir, f"{plugin_name}.py")
        if schedule_interval:
            return self.update_manager.schedule_update(
                plugin_name,
                schedule_interval,
                source,
                dest,
                version,
                signature,
                from_git,
            )
        self.update_manager.update(
            plugin_name,
            source,
            dest,
            version,
            signature,
            from_git,
        )
        self.scan_plugins()
        return None

