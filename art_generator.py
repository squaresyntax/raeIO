"""Simple art generation placeholder."""


def generate_art(prompt: str) -> str:
    """Return a mock art generation result.

    Args:
        prompt: Description of the desired artwork.
    Returns:
        A string describing the generated art.
    Raises:
        ValueError: If prompt is empty.
    """
    if not prompt:
        raise ValueError("Prompt cannot be empty for art generation")
    return f"Art generated for: {prompt}"
