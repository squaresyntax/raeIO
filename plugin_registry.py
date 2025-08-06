import os
import importlib.util
import ast


class PluginRegistry:
    """Simple filesystem-based plugin registry."""

    def __init__(self, plugin_dir="plugins", logger=None, fuckery_mode=False):
        self.plugin_dir = plugin_dir
        self.logger = logger
        self.fuckery_mode = fuckery_mode
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
        # Ensure the plugin list is up to date in case new plugins were
        # added after the registry was initialized. This helps avoid
        # integration issues where freshly created plugins cannot be
        # located until `scan_plugins` or `list_plugins` is called
        # manually.
        self.scan_plugins()
        path = self.plugins.get(plugin_name)
        if not path:
            raise ImportError(f"Plugin {plugin_name} not found.")
        spec = importlib.util.spec_from_file_location(plugin_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def get_metadata(self, plugin_name):
        """Return plugin metadata without importing the plugin code."""
        path = self.plugins.get(plugin_name)
        if not path:
            raise ImportError(f"Plugin {plugin_name} not found.")
        try:
            with open(path, "r") as f:
                src = f.read()
            tree = ast.parse(src, filename=path)
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "PLUGIN_META":
                            return ast.literal_eval(node.value)
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to parse metadata for {plugin_name}: {e}")
        return {}

    def list_plugins(self):
        self.scan_plugins()
        result = []
        for pname in self.plugins:
            meta = self.get_metadata(pname)
            result.append({"name": pname, "meta": meta})
        return result

    def execute_plugin(self, plugin_name, **kwargs):
        """Execute a plugin if permitted.

        When fuckery mode is active, only plugins declaring
        ``allow_fuckery=True`` in their metadata may run.
        """
        meta = self.get_metadata(plugin_name)
        if self.fuckery_mode and not meta.get("allow_fuckery"):
            raise PermissionError(f"Plugin {plugin_name} is not allowed in fuckery mode")
        plugin = self.load_plugin(plugin_name)
        if hasattr(plugin, "run"):
            return plugin.run(**kwargs)
        raise AttributeError(f"Plugin {plugin_name} has no run()")

    def set_fuckery_mode(self, enabled: bool):
        """Toggle fuckery mode for the registry.

        This allows the owning agent to enable or disable the runtime
        restriction logic without needing to recreate the registry.
        """
        self.fuckery_mode = enabled
