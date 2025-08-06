"""Example plugin used for tests."""

PLUGIN_META = {"version": "1.0", "description": "Echo plugin"}


def run(prompt: str, **kwargs):
    return f"Echo: {prompt}"

