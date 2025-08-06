"""Client for interacting with a VST analysis server.

This module exposes :class:`VSTClient` which communicates with a
minimal VST-style analysis server over HTTP.  The client supports
configurable retries and timeout handling and returns structured
results so callers can easily determine success or failure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class VSTClient:
    """HTTP client for the VST analysis server.

    Parameters
    ----------
    base_url:
        Base URL of the VST server.
    timeout:
        Request timeout in seconds.
    retries:
        Number of retries for failed requests.
    """

    base_url: str = "http://localhost:5005"
    timeout: int = 5
    retries: int = 3
    session: requests.Session = field(init=False, repr=False)

    def __post_init__(self) -> None:
        # Configure a session with retry logic for robust communication.
        self.session = requests.Session()
        retry = Retry(
            total=self.retries,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def analyze_media(self, file_path: str, analysis_type: str = "audio") -> Dict[str, Any]:
        """Send media to the VST server for analysis.

        Parameters
        ----------
        file_path:
            Path to the media file on disk.
        analysis_type:
            Type of analysis to perform (e.g., ``"audio"``, ``"video"`` or
            ``"image"``).

        Returns
        -------
        dict
            Structured result containing either the server response under
            ``"result"`` when successful or an ``"error"`` message when
            the request fails.
        """

        url = f"{self.base_url}/analyze"
        files = {"file": open(file_path, "rb")}
        params = {"type": analysis_type}

        try:
            resp = self.session.post(url, files=files, data=params, timeout=self.timeout)
            resp.raise_for_status()
            return {"success": True, "result": resp.json()}
        except requests.RequestException as exc:  # pragma: no cover - network failures
            return {"success": False, "error": str(exc)}
        finally:
            files["file"].close()


__all__ = ["VSTClient"]

