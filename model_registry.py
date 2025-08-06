MODEL_REGISTRY = {
    # Text-focused models
    "gpt-4": {"text_generation", "text_editing"},
    # Image generation model
    "stable-diffusion": {"image_generation"},
    # Browser automation pseudo-model
    "browser-automation": {"browser"},
}

def all_features():
    """Return a sorted list of all available features."""
    feats = set()
    for fset in MODEL_REGISTRY.values():
        feats.update(fset)
    return sorted(feats)


def model_for_feature(feature: str) -> str | None:
    """Return the first model that supports the given feature."""
    for model, features in MODEL_REGISTRY.items():
        if feature in features:
            return model
    return None
