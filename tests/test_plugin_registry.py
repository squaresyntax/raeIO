import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from plugin_registry import PluginRegistry


def test_example_plugin_execution():
    plugin_dir = os.path.join(os.path.dirname(__file__), "..", "plugins")
    registry = PluginRegistry(plugin_dir=plugin_dir)
    plugins = registry.list_plugins()
    assert any(p["name"] == "example_plugin" for p in plugins)
    result = registry.execute_plugin("example_plugin", prompt="hello", context={})
    assert result == "Echo: hello"

