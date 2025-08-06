import subprocess
import sys
from pathlib import Path

def test_cli_defaults_to_text():
    script = Path(__file__).resolve().parents[1] / 'raeio_cli_Version2.py'
    result = subprocess.run(
        [sys.executable, str(script), '--prompt', 'Hello world'],
        input='\n',
        capture_output=True,
        text=True,
        check=True,
    )
    assert 'Stub output for text: Hello world' in result.stdout
