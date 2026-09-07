from youtube_insight import publish


def test_render_index_영상없으면_빈목록_안내():
    html = publish.render_index([])
    assert "아직 정리된 영상이 없습니다" in html


def test_render_index_영상목록_링크_포함하고_자막전문은_제외():
    videos = [{
        "video_id": "vid1", "title": "테스트 영상", "url": "https://youtu.be/vid1", "channel_name": "테스트채널",
        "published_at": "2026-08-01", "summary": "요약 내용", "insight": "인사이트 내용",
        "transcript_full": "이 자막 전문은 공개 페이지에 노출되면 안 된다",
    }]
    html = publish.render_index(videos)
    assert "테스트 영상" in html
    assert "https://youtu.be/vid1" in html
    assert "요약 내용" in html
    assert "인사이트 내용" in html
    assert "이 자막 전문은 공개 페이지에 노출되면 안 된다" not in html


def test_render_index_첫번째_썸네일만_preload와_high_priority():
    videos = [
        {"video_id": "vid1", "title": "영상1", "url": "https://youtu.be/vid1", "channel_name": "채널",
         "published_at": "2026-08-01", "summary": "", "insight": ""},
        {"video_id": "vid2", "title": "영상2", "url": "https://youtu.be/vid2", "channel_name": "채널",
         "published_at": "2026-08-02", "summary": "", "insight": ""},
    ]
    html = publish.render_index(videos)
    assert '<link rel="preload" as="image" fetchpriority="high" href="https://i.ytimg.com/vi/vid1/hqdefault.jpg">' in html
    assert 'src="https://i.ytimg.com/vi/vid1/hqdefault.jpg" alt="" loading="eager" fetchpriority="high"' in html
    assert 'src="https://i.ytimg.com/vi/vid2/hqdefault.jpg" alt="" loading="lazy" fetchpriority="auto"' in html
