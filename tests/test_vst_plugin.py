"""Integration test for the VST client and example server."""

import threading
import tempfile
import os
import time
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from vst_plugin_interface import VSTClient
from vst_server_example import create_server


def _run_server() -> tuple:
    server = create_server()
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server, thread


def test_vst_integration() -> None:
    server, thread = _run_server()
    time.sleep(0.5)  # give the server a moment to start

    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"dummy data")
            tmp_path = tmp.name

        client = VSTClient()
        result = client.analyze_media(tmp_path, analysis_type="audio")
        assert result["success"] is True
        assert result["result"]["analysis_type"] == "audio"
    finally:
        os.unlink(tmp_path)
        server.shutdown()
        thread.join()

