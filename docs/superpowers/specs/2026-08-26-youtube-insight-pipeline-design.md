# 유튜브 인사이트 파이프라인 — 설계

## 목적

구독 중인 유튜브 채널에 새 영상이 올라오면, 영상을 직접 보지 않고도 요약과 핵심 인사이트를 먼저 받아본 뒤 시청 여부를 판단할 수 있게 한다. 쌓인 요약은 검색 가능한 지식 베이스가 되어 "그 채널에서 A 얘기한 거 뭐였지?" 같은 질문에 답할 수 있다.

## 범위

- 대상: 사용자가 지정/구독한 유튜브 채널의 신규 영상
- 비대상: 실시간 스트리밍, 자막이 아예 없는 영상의 STT 전사(자막 없으면 스킵)

## 아키텍처

```
[신규 감지]           [자막 추출]        [요약 생성]        [저장]                [알림/퍼블리시]
RSS 폴링(1일 1회)  →  youtube_        →  Claude로       →  SQLite(전문+메타)  →  Discord 자동 알림
+ 수동(Discord 링크)   transcript_api     압축요약+인사이트    Notion DB(뷰)         GitHub Pages(공개 요약)
```

### 1. 채널 소스

- 기본값: 사용자의 유튜브 구독 목록을 Google OAuth로 가져와 자동 반영
- 추가 수단: Discord 명령 `/addchannel <링크>`, `/removechannel <링크>` — 구독 여부와 무관하게 개별 채널 추가/제외
- 채널 목록은 SQLite `channels` 테이블에 보관 (channel_id, source: subscription|manual, added_at)

### 2. 신규 영상 감지

- 채널별 YouTube RSS 피드(`https://www.youtube.com/feeds/videos.xml?channel_id=`)를 기본 1일 1회 폴링. API 쿼터 소모 없음.
- 이미 처리한 `video_id`는 SQLite에 기록해 중복 처리 방지.
- 수동 요청: Discord에 유튜브 링크를 보내면 동일 파이프라인을 즉시 실행 (구독 목록에 없는 채널의 영상도 1회성으로 처리 가능).

### 3. 자막 추출

- `youtube_transcript_api`로 자막 텍스트 추출 (한국어 우선, 없으면 영어).
- 자막이 없는 영상은 실패로 기록하고 스킵 — 재시도나 Whisper STT 폴백은 두지 않는다(범위 밖).
- 실패는 SQLite에 상태로 남기고, Notion 처리상태를 "실패"로 표시.

### 4. 요약/인사이트 생성

- 추출한 자막 전문을 Claude에 넘겨 요약 + 핵심 인사이트를 생성.
- 출력은 Discord 응답 규약(15줄 이내)에 맞게 압축된 형태와, 지식베이스에 남길 조금 더 상세한 형태 두 가지를 만든다.

### 5. 저장 (이중화)

**SQLite** (`youtube_insight.db`) — 검색 가능한 지식 베이스, 원문 보관:
- `videos`: video_id, channel_id, title, url, published_at, transcript_full, summary, insight, tags, status, processed_at
- FTS5 가상 테이블로 `transcript_full` + `summary` 키워드 검색 지원

**Notion DB** — 훑어보기용 뷰, 원문 전문은 넣지 않음:
- 필드: 채널명 / 제목(링크) / 업로드일 / 한줄 인사이트 / 태그 / 처리상태(성공·실패) / 처리일시

### 6. 퍼블리시 (GitHub Pages)

- 이 프로젝트 전용 공개 레포: `Azderica/project-youtube-insight` (public)
- **저작권 원칙**: 공개 페이지에는 요약·인사이트만 싣고 원본 링크로 연결한다. 자막 전문은 SQLite에만 보관하고 공개하지 않는다.
- 정적 사이트는 GitHub Actions로 빌드 후 Pages에 배포 (구현 단계에서 생성기 방식 확정)

### 7. Discord 알림 / 수동 요청

- 신규 영상이 처리되면 Discord에 자동으로 3줄 요약 + 유튜브 링크 전송 (프로젝트 CLAUDE.md의 응답 규약 준수)
- 사용자가 Discord에 유튜브 링크를 보내면 같은 파이프라인이 즉시 실행되어 결과를 응답

## 에러 처리

- 자막 없음 → 스킵 + 로그, Notion 상태 "실패"로 표시. 재시도 없음.
- OAuth 토큰 만료 → Discord로 재인증 필요 알림.
- RSS 파싱 실패 → 로그 남기고 다음 폴링 주기에 재시도 (무한 재시도 없음).
- Notion/SQLite 쓰기 실패 → 로그, Discord로 실패 알림.

## 리포지토리

- `https://github.com/Azderica/project-youtube-insight` (public)
- 기존 다른 프로젝트와 동일하게 독립 레포로 유지, `business` 모노레포 하위 디렉터리에는 코드가 위치하지 않고 별도 clone/worktree 없이 이 디렉터리 자체가 레포 루트.

## 테스트 범위 (구현 단계에서 상세화)

- RSS 신규 영상 판별 로직 단위 테스트
- 자막 추출 실패/성공 케이스 단위 테스트
- 요약 포맷팅(15줄 제한) 단위 테스트
- SQLite ↔ Notion 동기화 실패 시 상태 처리 테스트

## 미결 사항 (구현 단계에서 결정)

- 정적 사이트 생성기 선택 (순수 마크다운→HTML 변환 vs 정적 사이트 프레임워크) — 규모가 작으므로 최대한 단순하게
- Discord 봇 연동 방식 — 기존 `backend`(ai-team-bot) 프로젝트와의 통합 지점
