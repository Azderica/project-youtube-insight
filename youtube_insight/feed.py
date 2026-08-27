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
        video_id_el = entry.find("yt:videoId", NS)
        channel_id_el = entry.find("yt:channelId", NS)
        title_el = entry.find("atom:title", NS)
        link_el = entry.find("atom:link[@rel='alternate']", NS)
        published_el = entry.find("atom:published", NS)
        if None in (video_id_el, channel_id_el, title_el, link_el, published_el):
            continue
        entries.append({
            "video_id": video_id_el.text,
            "channel_id": channel_id_el.text,
            "title": title_el.text,
            "url": link_el.get("href"),
            "published_at": published_el.text,
        })
    return entries


def fetch_feed_entries(channel_id: str) -> list[dict]:
    url = FEED_URL_TEMPLATE.format(channel_id=channel_id)
    with urlopen(url, timeout=15) as response:
        xml_text = response.read().decode("utf-8")
    return parse_feed(xml_text)


def find_new_entries(entries: list[dict], known_video_ids: set[str]) -> list[dict]:
    return [entry for entry in entries if entry["video_id"] not in known_video_ids]
