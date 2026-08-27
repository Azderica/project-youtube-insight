from unittest.mock import MagicMock, patch
from youtube_insight import transcript


class FakeSnippet:
    def __init__(self, text):
        self.text = text


def test_fetch_transcript_성공하면_텍스트_반환():
    fake_api = MagicMock()
    fake_api.fetch.return_value = [FakeSnippet("안녕하세요"), FakeSnippet("반갑습니다")]
    with patch("youtube_insight.transcript.YouTubeTranscriptApi", return_value=fake_api):
        result = transcript.fetch_transcript("vid1")
    assert result == "안녕하세요 반갑습니다"
    fake_api.fetch.assert_called_once_with("vid1", languages=["ko", "en"])


def test_fetch_transcript_자막없으면_None_반환():
    fake_api = MagicMock()
    fake_api.fetch.side_effect = Exception("no transcript")
    with patch("youtube_insight.transcript.YouTubeTranscriptApi", return_value=fake_api):
        result = transcript.fetch_transcript("vid1")
    assert result is None
