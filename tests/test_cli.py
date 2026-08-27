import sqlite3
from unittest.mock import patch
from youtube_insight import cli, db


def make_conn():
    conn = sqlite3.connect(":memory:")
    db.init_db(conn)
    return conn


def test_cmd_channels_add_채널_추가():
    conn = make_conn()
    cli.cmd_channels_add(conn, channel_id="UC123", channel_name="테스트채널")
    channels = db.list_channels(conn)
    assert len(channels) == 1
    assert channels[0]["source"] == "manual"


def test_cmd_process_자막없으면_no_transcript_상태로_저장():
    conn = make_conn()
    db.add_channel(conn, "UC123", "테스트채널", source="manual")
    with patch("youtube_insight.cli.fetch_transcript", return_value=None):
        result = cli.cmd_process(
            conn,
            video_id="vid1",
            channel_id="UC123",
            title="영상 제목",
            url="https://youtu.be/vid1",
            published_at="2026-08-01T00:00:00+00:00",
        )
    assert result["status"] == "no_transcript"
    stored = db.search_videos(conn, "영상")
    assert stored == []  # 자막 없으면 FTS에 남길 요약이 없음


def test_cmd_process_성공하면_success_상태로_저장():
    conn = make_conn()
    db.add_channel(conn, "UC123", "테스트채널", source="manual")
    with patch("youtube_insight.cli.fetch_transcript", return_value="자막 전문"), \
         patch("youtube_insight.cli.summarize", return_value={"summary": "요약", "insight": "인사이트", "tags": "재테크"}):
        result = cli.cmd_process(
            conn,
            video_id="vid1",
            channel_id="UC123",
            title="영상 제목",
            url="https://youtu.be/vid1",
            published_at="2026-08-01T00:00:00+00:00",
        )
    assert result["status"] == "success"
    assert db.has_video(conn, "vid1") is True


def test_cmd_watch_신규영상_있으면_process_호출하고_알림전송():
    conn = make_conn()
    db.add_channel(conn, "UC123", "테스트채널", source="manual")
    fake_entries = [{
        "video_id": "vid1", "channel_id": "UC123", "title": "새 영상",
        "url": "https://youtu.be/vid1", "published_at": "2026-08-01T00:00:00+00:00",
    }]
    with patch("youtube_insight.cli.fetch_feed_entries", return_value=fake_entries), \
         patch("youtube_insight.cli.fetch_transcript", return_value="자막"), \
         patch("youtube_insight.cli.summarize", return_value={"summary": "요약", "insight": "인사이트", "tags": "태그"}), \
         patch("youtube_insight.cli.send_notification", return_value=True) as mock_notify:
        processed = cli.cmd_watch(conn, notify_url="http://x", notify_token="tok")
    assert len(processed) == 1
    assert processed[0]["status"] == "success"
    mock_notify.assert_called_once()
    assert "새 영상" in mock_notify.call_args[0][0]


def test_cmd_watch_이미_처리된_영상은_건너뜀():
    conn = make_conn()
    db.add_channel(conn, "UC123", "테스트채널", source="manual")
    db.upsert_video(conn, {
        "video_id": "vid1", "channel_id": "UC123", "title": "기존 영상", "url": "u",
        "published_at": "p", "transcript_full": "t", "summary": "s", "insight": "i",
        "tags": "tag", "status": "success",
    })
    fake_entries = [{
        "video_id": "vid1", "channel_id": "UC123", "title": "기존 영상",
        "url": "u", "published_at": "p",
    }]
    with patch("youtube_insight.cli.fetch_feed_entries", return_value=fake_entries), \
         patch("youtube_insight.cli.send_notification") as mock_notify:
        processed = cli.cmd_watch(conn, notify_url="http://x", notify_token="tok")
    assert processed == []
    mock_notify.assert_not_called()


def test_cmd_watch_한_영상_처리중_예외나도_나머지_영상은_처리됨():
    conn = make_conn()
    db.add_channel(conn, "UC123", "테스트채널", source="manual")
    fake_entries = [
        {
            "video_id": "vid1", "channel_id": "UC123", "title": "실패할 영상",
            "url": "https://youtu.be/vid1", "published_at": "2026-08-01T00:00:00+00:00",
        },
        {
            "video_id": "vid2", "channel_id": "UC123", "title": "성공할 영상",
            "url": "https://youtu.be/vid2", "published_at": "2026-08-02T00:00:00+00:00",
        },
    ]
    with patch("youtube_insight.cli.fetch_feed_entries", return_value=fake_entries), \
         patch("youtube_insight.cli.cmd_process", side_effect=[
             sqlite3.OperationalError("database is locked"),
             {"video_id": "vid2", "status": "success", "title": "성공할 영상",
              "insight": "인사이트", "url": "https://youtu.be/vid2"},
         ]) as mock_process, \
         patch("youtube_insight.cli.send_notification", return_value=True) as mock_notify:
        processed = cli.cmd_watch(conn, notify_url="http://x", notify_token="tok")
    assert mock_process.call_count == 2
    assert len(processed) == 1
    assert processed[0]["video_id"] == "vid2"
    mock_notify.assert_called_once()
