import sqlite3
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS channels (
    channel_id TEXT PRIMARY KEY,
    channel_name TEXT NOT NULL,
    source TEXT NOT NULL CHECK(source IN ('subscription', 'manual')),
    added_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS videos (
    video_id TEXT PRIMARY KEY,
    channel_id TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    published_at TEXT NOT NULL,
    transcript_full TEXT,
    summary TEXT,
    insight TEXT,
    tags TEXT,
    status TEXT NOT NULL CHECK(status IN ('pending', 'success', 'no_transcript', 'failed')),
    processed_at TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS videos_fts USING fts5(
    video_id UNINDEXED, title, transcript_full, summary
);
"""


def init_db(conn: sqlite3.Connection) -> None:
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def add_channel(conn: sqlite3.Connection, channel_id: str, channel_name: str, source: str) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO channels (channel_id, channel_name, source, added_at) VALUES (?, ?, ?, ?)",
        (channel_id, channel_name, source, _now()),
    )
    conn.commit()


def remove_channel(conn: sqlite3.Connection, channel_id: str) -> None:
    conn.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
    conn.commit()


def list_channels(conn: sqlite3.Connection) -> list[dict]:
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM channels ORDER BY added_at").fetchall()
    return [dict(row) for row in rows]


def has_video(conn: sqlite3.Connection, video_id: str) -> bool:
    row = conn.execute("SELECT 1 FROM videos WHERE video_id = ?", (video_id,)).fetchone()
    return row is not None


def upsert_video(conn: sqlite3.Connection, video: dict) -> None:
    conn.execute(
        """
        INSERT INTO videos
            (video_id, channel_id, title, url, published_at, transcript_full,
             summary, insight, tags, status, processed_at)
        VALUES (:video_id, :channel_id, :title, :url, :published_at, :transcript_full,
                :summary, :insight, :tags, :status, :processed_at)
        ON CONFLICT(video_id) DO UPDATE SET
            title=excluded.title, transcript_full=excluded.transcript_full,
            summary=excluded.summary, insight=excluded.insight, tags=excluded.tags,
            status=excluded.status, processed_at=excluded.processed_at
        """,
        {**video, "processed_at": _now()},
    )
    conn.execute("DELETE FROM videos_fts WHERE video_id = ?", (video["video_id"],))
    if video.get("summary"):
        conn.execute(
            "INSERT INTO videos_fts (video_id, title, transcript_full, summary) VALUES (?, ?, ?, ?)",
            (video["video_id"], video["title"], video.get("transcript_full") or "", video.get("summary") or ""),
        )
    conn.commit()


def search_videos(conn: sqlite3.Connection, query: str) -> list[dict]:
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT v.* FROM videos v
        JOIN videos_fts fts ON v.video_id = fts.video_id
        WHERE videos_fts MATCH ?
        ORDER BY v.published_at DESC
        """,
        (query,),
    ).fetchall()
    return [dict(row) for row in rows]
