from youtube_insight import publish


def test_render_index_영상없으면_빈목록_안내():
    html = publish.render_index([])
    assert "아직 정리된 영상이 없습니다" in html


def test_render_index_영상목록_링크_포함하고_자막전문은_제외():
    videos = [{
        "title": "테스트 영상", "url": "https://youtu.be/vid1", "channel_name": "테스트채널",
        "published_at": "2026-08-01", "summary": "요약 내용", "insight": "인사이트 내용",
        "transcript_full": "이 자막 전문은 공개 페이지에 노출되면 안 된다",
    }]
    html = publish.render_index(videos)
    assert "테스트 영상" in html
    assert "https://youtu.be/vid1" in html
    assert "요약 내용" in html
    assert "인사이트 내용" in html
    assert "이 자막 전문은 공개 페이지에 노출되면 안 된다" not in html
