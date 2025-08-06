from raeio_core import RAEIOAgent


def test_fuckery_mode_sets_flags():
    agent = RAEIOAgent()
    agent.set_mode("Fuckery", feature_focus="Art")
    assert agent.fuckery_mode
    assert agent.stealth_mode
    assert agent.prioritized_store == "art"
    assert agent.get_fuckery_encryption_key() is not None


def test_training_mode_resets_fuckery():
    agent = RAEIOAgent()
    agent.set_mode("Fuckery", feature_focus="Art")
    agent.set_mode("Training")
    assert agent.training_mode
    assert not agent.fuckery_mode
    assert not agent.stealth_mode
    assert agent.prioritized_store == "general"
