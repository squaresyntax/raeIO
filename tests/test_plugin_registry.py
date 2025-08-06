import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from plugin_registry import PluginRegistry


def test_example_plugin_discovery_and_execution():
    plugin_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "plugins")
    )
    registry = PluginRegistry(plugin_dir=plugin_dir)
    plugins = registry.list_plugins()
    names = [p["name"] for p in plugins]
    assert "example_plugin" in names
    result = registry.execute_plugin("example_plugin", prompt="hello")
    assert result == "Echo: hello"

