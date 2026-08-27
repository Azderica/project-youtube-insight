import xml.etree.ElementTree as ET
from urllib.request import urlopen

FEED_URL_TEMPLATE = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
}


def parse_feed(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    entries = []
    for entry in root.findall("atom:entry", NS):
        video_id = entry.find("yt:videoId", NS).text
        channel_id = entry.find("yt:channelId", NS).text
        title = entry.find("atom:title", NS).text
        link = entry.find("atom:link[@rel='alternate']", NS).get("href")
        published = entry.find("atom:published", NS).text
        entries.append({
            "video_id": video_id,
            "channel_id": channel_id,
            "title": title,
            "url": link,
            "published_at": published,
        })
    return entries


def fetch_feed_entries(channel_id: str) -> list[dict]:
    url = FEED_URL_TEMPLATE.format(channel_id=channel_id)
    with urlopen(url, timeout=15) as response:
        xml_text = response.read().decode("utf-8")
    return parse_feed(xml_text)


def find_new_entries(entries: list[dict], known_video_ids: set[str]) -> list[dict]:
    return [entry for entry in entries if entry["video_id"] not in known_video_ids]
