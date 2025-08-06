import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from plugin_system import PluginRegistry


def test_example_plugin_discovery_and_execution():
    plugin_dir = Path(__file__).resolve().parent.parent / "plugins"
    registry = PluginRegistry(plugin_dir=plugin_dir)
    plugins = registry.list_plugins()
    assert any(p["name"] == "example_plugin" for p in plugins)
    meta = next(p["meta"] for p in plugins if p["name"] == "example_plugin")
    assert meta.get("description") == "Adds two numbers"
    result = registry.execute_plugin("example_plugin", x=1, y=2)
    assert result == 3

