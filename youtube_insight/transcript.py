from youtube_transcript_api import YouTubeTranscriptApi


def fetch_transcript(video_id: str) -> str | None:
    try:
        api = YouTubeTranscriptApi()
        snippets = api.fetch(video_id, languages=["ko", "en"])
    except Exception:
        return None
    return " ".join(snippet.text for snippet in snippets)
