from unittest.mock import patch
from youtube_insight import feed

SAMPLE_FEED_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns="http://www.w3.org/2005/Atom">
 <yt:channelId>UC123</yt:channelId>
 <title>테스트채널</title>
 <entry>
  <yt:videoId>vid1</yt:videoId>
  <yt:channelId>UC123</yt:channelId>
  <title>첫번째 영상</title>
  <link rel="alternate" href="https://www.youtube.com/watch?v=vid1"/>
  <published>2026-08-01T00:00:00+00:00</published>
 </entry>
 <entry>
  <yt:videoId>vid2</yt:videoId>
  <yt:channelId>UC123</yt:channelId>
  <title>두번째 영상</title>
  <link rel="alternate" href="https://www.youtube.com/watch?v=vid2"/>
  <published>2026-08-02T00:00:00+00:00</published>
 </entry>
</feed>
"""


def test_parse_feed_엔트리_2개_파싱():
    entries = feed.parse_feed(SAMPLE_FEED_XML)
    assert len(entries) == 2
    assert entries[0] == {
        "video_id": "vid1",
        "channel_id": "UC123",
        "title": "첫번째 영상",
        "url": "https://www.youtube.com/watch?v=vid1",
        "published_at": "2026-08-01T00:00:00+00:00",
    }


def test_fetch_feed_entries_urlopen_호출():
    with patch("youtube_insight.feed.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value.read.return_value = SAMPLE_FEED_XML.encode()
        entries = feed.fetch_feed_entries("UC123")
    assert len(entries) == 2
    called_url = mock_urlopen.call_args[0][0]
    assert called_url == "https://www.youtube.com/feeds/videos.xml?channel_id=UC123"


def test_find_new_entries_이미_처리된_video_id는_제외():
    entries = [
        {"video_id": "vid1", "channel_id": "UC123", "title": "a", "url": "u1", "published_at": "p1"},
        {"video_id": "vid2", "channel_id": "UC123", "title": "b", "url": "u2", "published_at": "p2"},
    ]
    known_ids = {"vid1"}
    new_entries = feed.find_new_entries(entries, known_ids)
    assert len(new_entries) == 1
    assert new_entries[0]["video_id"] == "vid2"
