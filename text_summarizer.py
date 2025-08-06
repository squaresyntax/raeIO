"""Simple text summarization placeholder."""


def summarize_text(prompt: str) -> str:
    """Return a mock text summary.

    Args:
        prompt: Text to summarize.
    Returns:
        A short summary string.
    Raises:
        ValueError: If prompt is empty.
    """
    if not prompt:
        raise ValueError("Prompt cannot be empty for text summarization")
    return f"Summary: {prompt[:10]}..."
