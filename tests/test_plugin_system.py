import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from plugin_system import PluginRegistry


def test_example_plugin_discovery_and_execution():
    plugin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plugins"))
    registry = PluginRegistry(plugin_dir=plugin_dir)
    plugins = registry.list_plugins()
    assert any(p["name"] == "example_plugin" for p in plugins)
    result = registry.execute_plugin("example_plugin", x=1, y=2)
    assert result == 3

