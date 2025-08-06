# Pseudocode for VST plugin communication (using REST API as example)
import requests

def analyze_media_with_vst(file_path, analysis_type="audio"):
    """
    Sends file to VST plugin REST server for analysis.
    analysis_type: "audio", "video", "image"
    """
    url = f"http://localhost:5005/analyze"
    files = {"file": open(file_path, "rb")}
    params = {"type": analysis_type}
    resp = requests.post(url, files=files, data=params)
    if resp.status_code == 200:
        return resp.json()
    else:
        return {"error": "VST analysis failed"}