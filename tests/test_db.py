import sqlite3
import pytest
from youtube_insight import db


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    db.init_db(connection)
    yield connection
    connection.close()


def test_add_channel_후_list_channels에_나타남(conn):
    db.add_channel(conn, "UC123", "테스트채널", source="manual")
    channels = db.list_channels(conn)
    assert len(channels) == 1
    assert channels[0]["channel_id"] == "UC123"
    assert channels[0]["channel_name"] == "테스트채널"
    assert channels[0]["source"] == "manual"


def test_remove_channel_후_list에서_사라짐(conn):
    db.add_channel(conn, "UC123", "테스트채널", source="manual")
    db.remove_channel(conn, "UC123")
    assert db.list_channels(conn) == []


def test_add_channel_중복_추가시_에러없이_무시(conn):
    db.add_channel(conn, "UC123", "테스트채널", source="manual")
    db.add_channel(conn, "UC123", "테스트채널", source="manual")
    assert len(db.list_channels(conn)) == 1


def test_has_video_없으면_False(conn):
    assert db.has_video(conn, "vid1") is False


def test_upsert_video_후_has_video_True(conn):
    db.add_channel(conn, "UC123", "테스트채널", source="manual")
    db.upsert_video(conn, {
        "video_id": "vid1",
        "channel_id": "UC123",
        "title": "테스트 영상",
        "url": "https://youtu.be/vid1",
        "published_at": "2026-08-01T00:00:00+00:00",
        "transcript_full": "이것은 자막 전문입니다",
        "summary": "요약입니다",
        "insight": "인사이트입니다",
        "tags": "재테크,절약",
        "status": "success",
    })
    assert db.has_video(conn, "vid1") is True


def test_search_videos_키워드로_찾음(conn):
    db.add_channel(conn, "UC123", "테스트채널", source="manual")
    db.upsert_video(conn, {
        "video_id": "vid1",
        "channel_id": "UC123",
        "title": "순자산 4층 모델",
        "url": "https://youtu.be/vid1",
        "published_at": "2026-08-01T00:00:00+00:00",
        "transcript_full": "레버리지를 써야 하는 시점에 대한 이야기",
        "summary": "레버리지 전환 시점 요약",
        "insight": "3층에서 4층으로",
        "tags": "재테크",
        "status": "success",
    })
    results = db.search_videos(conn, "레버리지")
    assert len(results) == 1
    assert results[0]["video_id"] == "vid1"


def test_search_videos_결과없으면_빈리스트(conn):
    assert db.search_videos(conn, "존재하지않는단어") == []
