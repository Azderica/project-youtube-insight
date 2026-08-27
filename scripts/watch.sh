#!/usr/bin/env bash
# 매일 1회: 구독/등록 채널의 신규 영상을 감지해 요약하고 Discord로 알린다.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ -f "/Users/mh97888/business/backend/.env" ]]; then
  export INTERNAL_API_TOKEN="$(grep -m1 '^INTERNAL_API_TOKEN=' /Users/mh97888/business/backend/.env | cut -d= -f2- | tr -d '"'\''\r')"
  export CLAUDE_CODE_OAUTH_TOKEN="$(grep -m1 '^CLAUDE_CODE_OAUTH_TOKEN=' /Users/mh97888/business/backend/.env | cut -d= -f2- | tr -d '"'\''\r')"
fi

"$REPO_ROOT/.venv/bin/python" -m youtube_insight.cli watch
