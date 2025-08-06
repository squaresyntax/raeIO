import subprocess
import sys
from pathlib import Path


def test_cli_uses_default_text_mode():
    script = Path(__file__).resolve().parent.parent / 'raeio_cli_Version2.py'
    result = subprocess.run(
        [sys.executable, str(script), '--prompt', 'hello'],
        capture_output=True,
        text=True,
        check=True,
    )
    assert 'Stub output for text: hello' in result.stdout
