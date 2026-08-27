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
