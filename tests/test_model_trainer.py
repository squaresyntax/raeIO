import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from model_trainer import rollback_checkpoint, train_voice_model


def test_train_voice_model_and_rollback(tmp_path, monkeypatch):
    """Minimal training cycle: checkpoint -> train -> rollback."""

    # Redirect checkpoints to a temporary directory
    checkpoints = tmp_path / "ckpts"
    monkeypatch.setattr("model_trainer.CHECKPOINT_DIR", str(checkpoints))

    # Prepare dummy model and audio sample
    model_path = tmp_path / "voice_model.bin"
    model_path.write_text("base-model", encoding="utf-8")
    audio_path = tmp_path / "sample.wav"
    audio_path.write_text("audio-data", encoding="utf-8")

    # Train and create checkpoint
    train_voice_model(str(audio_path), str(model_path), checkpoint_name="cp1")

    # Check that checkpoint was created and temporary audio deleted
    checkpoint_file = checkpoints / "cp1_voice_model.bin"
    assert checkpoint_file.exists()
    assert not audio_path.exists()

    # Model should have new contents after training
    assert model_path.read_text(encoding="utf-8") != "base-model"

    # Rollback to checkpoint
    rollback_checkpoint(str(model_path), checkpoint_file.name)
    assert model_path.read_text(encoding="utf-8") == "base-model"

