import json
from unittest.mock import patch, MagicMock
from youtube_insight import notify


def test_send_notification_urlopen에_올바른_body_전달():
    mock_response = MagicMock()
    mock_response.__enter__.return_value.status = 200
    with patch("youtube_insight.notify.urlopen", return_value=mock_response) as mock_urlopen:
        notify.send_notification("새 영상: 제목", url="http://localhost:8080/internal/notify", token="tok123")
    request = mock_urlopen.call_args[0][0]
    body = json.loads(request.data.decode())
    assert body["msg"] == "새 영상: 제목"
    assert body["level"] == "info"
    assert request.headers["X-internal-token"] == "tok123"


def test_send_notification_실패하면_False_반환():
    with patch("youtube_insight.notify.urlopen", side_effect=Exception("연결 실패")):
        result = notify.send_notification("메시지", url="http://localhost:8080/internal/notify", token="tok123")
    assert result is False
