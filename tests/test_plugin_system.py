import importlib.util
from pathlib import Path


PLUGIN_SYSTEM_PATH = Path(__file__).resolve().parent.parent / "plugin_system.py"
spec = importlib.util.spec_from_file_location("plugin_system", PLUGIN_SYSTEM_PATH)
plugin_system = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(plugin_system)
PluginRegistry = plugin_system.PluginRegistry


def test_example_plugin_discovery_and_execution():
    plugin_dir = Path(__file__).resolve().parent.parent / "plugins"
    registry = PluginRegistry(plugin_dir=plugin_dir)
    plugins = registry.list_plugins()
    assert any(p["name"] == "example_plugin" for p in plugins)
    meta = next(p["meta"] for p in plugins if p["name"] == "example_plugin")
    assert meta.get("description") == "Adds two numbers"
    result = registry.execute_plugin("example_plugin", x=1, y=2)
    assert result == 3

