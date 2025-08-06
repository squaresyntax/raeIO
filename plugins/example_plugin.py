"""Example plugin used for tests."""

PLUGIN_META = {
    "description": "Adds two numbers",
}


def run(x: int, y: int) -> int:
    """Return the sum of ``x`` and ``y``."""
    return x + y

