import json
from unittest.mock import patch, MagicMock
from youtube_insight import notion_sync


def test_sync_video_to_notion_토큰없으면_스킵():
    result = notion_sync.sync_video_to_notion(
        {"title": "제목", "url": "u", "channel_name": "채널", "published_at": "2026-08-01",
         "insight": "인사이트", "tags": "태그", "status": "success"},
        token="", database_id="",
    )
    assert result is False


def test_sync_video_to_notion_토큰있으면_page_생성_요청():
    mock_response = MagicMock()
    mock_response.__enter__.return_value.status = 200
    with patch("youtube_insight.notion_sync.urlopen", return_value=mock_response) as mock_urlopen:
        result = notion_sync.sync_video_to_notion(
            {"title": "제목", "url": "https://youtu.be/vid1", "channel_name": "채널",
             "published_at": "2026-08-01", "insight": "인사이트", "tags": "태그,재테크", "status": "success"},
            token="secret_abc", database_id="db123",
        )
    assert result is True
    request = mock_urlopen.call_args[0][0]
    assert request.full_url == "https://api.notion.com/v1/pages"
    assert request.headers["Authorization"] == "Bearer secret_abc"
    body = json.loads(request.data.decode())
    assert body["parent"]["database_id"] == "db123"
    assert body["properties"]["제목"]["title"][0]["text"]["content"] == "제목"
