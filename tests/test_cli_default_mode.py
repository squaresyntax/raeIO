import subprocess
import sys
import tempfile
import shutil
import os


def test_default_mode_uses_text():
    script = os.path.abspath('raeio_cli_Version2.py')
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy('config.yaml', tmp)
        result = subprocess.run(
            [sys.executable, script, '--prompt', 'hi'],
            input='\n',
            text=True,
            capture_output=True,
            check=True,
            cwd=tmp,
        )
        assert 'Stub output for text: hi' in result.stdout

