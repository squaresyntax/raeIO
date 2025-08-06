import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from raeio_agent import RAEIOAgent


@pytest.fixture(scope="module")
def agent():
    return RAEIOAgent(config={}, logger=None)


def test_art_mode(agent):
    path = agent.run_task("art", "test", {})
    assert os.path.exists(path)


def test_sound_mode(agent):
    path = agent.run_task("sound", "test", {})
    assert os.path.exists(path)


def test_video_mode(agent):
    path = agent.run_task("video", "test", {})
    assert os.path.exists(path)


def test_energy_mode(agent):
    result = agent.run_task("energy", "test", {})
    assert "Energy transformed" in result

