import subprocess

PROMPT_TEMPLATE = """다음은 유튜브 영상 "{title}"의 자막 전문이다. 아래 형식을 정확히 지켜서 응답하라. 다른 말은 하지 마라.

SUMMARY: <5줄 이내 한국어 요약>
INSIGHT: <이 영상에서 가장 핵심적인 통찰 1~2문장>
TAGS: <쉼표로 구분한 태그 2~5개>

자막 전문:
{transcript}
"""


def parse_summary_output(text: str) -> dict | None:
    lines = {"summary": None, "insight": None, "tags": None}
    for line in text.splitlines():
        if line.startswith("SUMMARY:"):
            lines["summary"] = line[len("SUMMARY:"):].strip()
        elif line.startswith("INSIGHT:"):
            lines["insight"] = line[len("INSIGHT:"):].strip()
        elif line.startswith("TAGS:"):
            lines["tags"] = line[len("TAGS:"):].strip()
    if not all(lines.values()):
        return None
    return lines


def summarize(title: str, transcript_text: str) -> dict | None:
    prompt = PROMPT_TEMPLATE.format(title=title, transcript=transcript_text[:15000])
    result = subprocess.run(
        ["claude", "--print", "--permission-mode", "bypassPermissions"],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode != 0:
        return None
    return parse_summary_output(result.stdout)
