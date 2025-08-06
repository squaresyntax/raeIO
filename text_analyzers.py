def summarize_text(text: str, max_words: int = 20) -> str:
    """Naive summarization by truncating to `max_words` words."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text must be a non-empty string")
    words = text.strip().split()
    if len(words) <= max_words:
        return text.strip()
    return " ".join(words[:max_words]) + "..."


def sentiment_analysis(text: str) -> str:
    """Very small heuristic sentiment analyzer."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text must be a non-empty string")
    positive = {"good", "great", "excellent", "happy", "awesome"}
    negative = {"bad", "terrible", "sad", "poor", "awful"}
    score = 0
    for word in text.lower().split():
        if word in positive:
            score += 1
        elif word in negative:
            score -= 1
    if score > 0:
        return "positive"
    if score < 0:
        return "negative"
    return "neutral"

