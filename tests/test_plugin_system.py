from plugin_system import PluginRegistry


def test_list_and_execute_plugin(tmp_path):
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    plugin_file = plugin_dir / "sample.py"
    plugin_file.write_text(
        "PLUGIN_META = {'description': 'demo'}\n"
        "def run(value):\n    return value * 2\n"
    )

    registry = PluginRegistry(plugin_dir=str(plugin_dir))
    plugins = registry.list_plugins()
    assert plugins[0]["name"] == "sample"
    assert plugins[0]["meta"] == {"description": "demo"}
    result = registry.execute_plugin("sample", value=3)
    assert result == 6
