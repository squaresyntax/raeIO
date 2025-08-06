"""Simple audio composition placeholder."""


def compose_audio(prompt: str) -> str:
    """Return a mock audio composition result.

    Args:
        prompt: Description of the desired audio piece.
    Returns:
        A string describing the composed audio.
    Raises:
        ValueError: If prompt is empty.
    """
    if not prompt:
        raise ValueError("Prompt cannot be empty for audio composition")
    return f"Audio composed for: {prompt}"
