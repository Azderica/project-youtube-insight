import json
from urllib.request import Request, urlopen

NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_VERSION = "2022-06-28"


def _build_page_body(video: dict, database_id: str) -> dict:
    return {
        "parent": {"database_id": database_id},
        "properties": {
            "제목": {"title": [{"text": {"content": video["title"]}}]},
            "채널명": {"rich_text": [{"text": {"content": video["channel_name"]}}]},
            "링크": {"url": video["url"]},
            "업로드일": {"date": {"start": video["published_at"]}},
            "한줄인사이트": {"rich_text": [{"text": {"content": video.get("insight") or ""}}]},
            "태그": {"multi_select": [{"name": t.strip()} for t in (video.get("tags") or "").split(",") if t.strip()]},
            "처리상태": {"select": {"name": "성공" if video["status"] == "success" else "실패"}},
        },
    }


def sync_video_to_notion(video: dict, token: str, database_id: str) -> bool:
    if not token or not database_id:
        return False
    body = json.dumps(_build_page_body(video, database_id)).encode()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }
    request = Request(NOTION_API_URL, data=body, headers=headers, method="POST")
    try:
        with urlopen(request, timeout=15) as response:
            return response.status in (200, 201)
    except Exception:
        return False
