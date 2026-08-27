import html as html_escape

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>유튜브 인사이트</title>
</head>
<body>
<h1>유튜브 인사이트</h1>
{body}
</body>
</html>
"""

ITEM_TEMPLATE = """<article>
<h2><a href="{url}">{title}</a></h2>
<p>{channel_name} · {published_at}</p>
<p>{summary}</p>
<p><strong>인사이트:</strong> {insight}</p>
</article>
"""


def render_index(videos: list[dict]) -> str:
    if not videos:
        return PAGE_TEMPLATE.format(body="<p>아직 정리된 영상이 없습니다.</p>")
    items = []
    for video in videos:
        items.append(ITEM_TEMPLATE.format(
            url=html_escape.escape(video["url"]),
            title=html_escape.escape(video["title"]),
            channel_name=html_escape.escape(video["channel_name"]),
            published_at=html_escape.escape(video["published_at"]),
            summary=html_escape.escape(video.get("summary") or ""),
            insight=html_escape.escape(video.get("insight") or ""),
        ))
    return PAGE_TEMPLATE.format(body="\n".join(items))
