from unittest.mock import patch, MagicMock
from youtube_insight import summarizer


def test_summarize_claude_print_호출하고_결과_파싱():
    fake_result = MagicMock()
    fake_result.stdout = "SUMMARY: 요약 내용입니다\nINSIGHT: 인사이트 내용입니다\nTAGS: 재테크,절약"
    fake_result.returncode = 0
    with patch("youtube_insight.summarizer.subprocess.run", return_value=fake_result) as mock_run:
        result = summarizer.summarize("영상 제목", "자막 전문 텍스트")
    assert result == {
        "summary": "요약 내용입니다",
        "insight": "인사이트 내용입니다",
        "tags": "재테크,절약",
    }
    args, kwargs = mock_run.call_args
    assert args[0] == ["claude", "--print", "--tools", ""]
    assert "자막 전문 텍스트" in kwargs["input"]


def test_summarize_claude_실패하면_None_반환():
    fake_result = MagicMock()
    fake_result.returncode = 1
    fake_result.stdout = ""
    with patch("youtube_insight.summarizer.subprocess.run", return_value=fake_result):
        result = summarizer.summarize("영상 제목", "자막 전문 텍스트")
    assert result is None


def test_parse_summary_output_형식_어긋나면_None():
    assert summarizer.parse_summary_output("형식이 안 맞는 응답") is None
