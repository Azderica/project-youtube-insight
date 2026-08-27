import json
from urllib.request import Request, urlopen
from youtube_insight.config import PROJECT_ROOT


def send_notification(msg: str, url: str, token: str) -> bool:
    body = json.dumps({"dir": str(PROJECT_ROOT), "level": "info", "msg": msg}).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Internal-Token"] = token
    request = Request(url, data=body, headers=headers)
    try:
        with urlopen(request, timeout=15) as response:
            return response.status == 200
    except Exception:
        return False
