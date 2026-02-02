from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, List, Optional

from shared.config.settings import get_settings

settings = get_settings()


def _db_path() -> Path:
    if settings.memory_db_path:
        return Path(settings.memory_db_path)
    return Path(__file__).resolve().parents[2] / "data" / "memory.db"


def _ensure_db_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    path = _db_path()
    _ensure_db_dir(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                model_name TEXT,
                temperature REAL,
                safety_state TEXT,
                FOREIGN KEY(conversation_id) REFERENCES conversations(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                user_id INTEGER,
                rating TEXT NOT NULL,
                tags TEXT,
                rewrite_text TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(message_id) REFERENCES messages(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                verbosity TEXT,
                emoji_level TEXT,
                nsfw_intensity TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversation_summary (
                conversation_id TEXT PRIMARY KEY,
                summary TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                importance REAL NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS relationship_state (
                conversation_id TEXT PRIMARY KEY,
                affinity_score REAL NOT NULL,
                trust_level TEXT NOT NULL,
                intimacy_level TEXT NOT NULL,
                nicknames TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )


def upsert_summary(conversation_id: str, summary: str) -> None:
    now = datetime.utcnow().isoformat()
    conn = get_connection()
    with conn:
        conn.execute(
            """
            INSERT INTO conversation_summary (conversation_id, summary, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(conversation_id) DO UPDATE SET summary=excluded.summary, updated_at=excluded.updated_at
            """,
            (conversation_id, summary, now),
        )


def get_summary(conversation_id: str) -> Optional[str]:
    conn = get_connection()
    row = conn.execute(
        "SELECT summary FROM conversation_summary WHERE conversation_id = ?",
        (conversation_id,),
    ).fetchone()
    return row["summary"] if row else None


def insert_memory(conversation_id: str, memory_type: str, content: str, importance: float) -> None:
    now = datetime.utcnow().isoformat()
    conn = get_connection()
    with conn:
        conn.execute(
            """
            INSERT INTO memories (conversation_id, type, content, importance, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (conversation_id, memory_type, content, importance, now),
        )


def create_conversation(conversation_id: str, user_id: Optional[int]) -> None:
    now = datetime.utcnow().isoformat()
    conn = get_connection()
    with conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO conversations (id, user_id, created_at)
            VALUES (?, ?, ?)
            """,
            (conversation_id, user_id, now),
        )


def insert_message(
    conversation_id: str,
    role: str,
    content: str,
    model_name: Optional[str],
    temperature: Optional[float],
    safety_state: Optional[str],
) -> int:
    now = datetime.utcnow().isoformat()
    conn = get_connection()
    with conn:
        cursor = conn.execute(
            """
            INSERT INTO messages (conversation_id, role, content, created_at, model_name, temperature, safety_state)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (conversation_id, role, content, now, model_name, temperature, safety_state),
        )
        return int(cursor.lastrowid)


def create_user(username: str, password_hash: str) -> int:
    now = datetime.utcnow().isoformat()
    conn = get_connection()
    with conn:
        cursor = conn.execute(
            """
            INSERT INTO users (username, password_hash, created_at)
            VALUES (?, ?, ?)
            """,
            (username, password_hash, now),
        )
        return int(cursor.lastrowid)


def get_user_by_username(username: str) -> Optional[sqlite3.Row]:
    conn = get_connection()
    row = conn.execute(
        "SELECT id, username, password_hash, created_at FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    return row


def insert_feedback(
    message_id: int,
    user_id: Optional[int],
    rating: str,
    tags: Optional[str],
    rewrite_text: Optional[str],
) -> int:
    now = datetime.utcnow().isoformat()
    conn = get_connection()
    with conn:
        cursor = conn.execute(
            """
            INSERT INTO feedback (message_id, user_id, rating, tags, rewrite_text, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (message_id, user_id, rating, tags, rewrite_text, now),
        )
        return int(cursor.lastrowid)

def get_recent_memories(conversation_id: str, limit: int = 5) -> List[sqlite3.Row]:
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT type, content, importance, created_at
        FROM memories
        WHERE conversation_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (conversation_id, limit),
    ).fetchall()
    return list(rows)


def get_relationship_state(conversation_id: str) -> Optional[sqlite3.Row]:
    conn = get_connection()
    row = conn.execute(
        """
        SELECT conversation_id, affinity_score, trust_level, intimacy_level, nicknames, updated_at
        FROM relationship_state
        WHERE conversation_id = ?
        """,
        (conversation_id,),
    ).fetchone()
    return row


def ensure_relationship_state(
    conversation_id: str,
    affinity_score: float = 0.0,
    trust_level: str = "low",
    intimacy_level: str = "low",
    nicknames: str = "",
) -> None:
    now = datetime.utcnow().isoformat()
    conn = get_connection()
    with conn:
        conn.execute(
            """
            INSERT INTO relationship_state
                (conversation_id, affinity_score, trust_level, intimacy_level, nicknames, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(conversation_id) DO UPDATE SET
                updated_at=excluded.updated_at
            """,
            (conversation_id, affinity_score, trust_level, intimacy_level, nicknames, now),
        )


def touch_relationship_state(conversation_id: str) -> None:
    now = datetime.utcnow().isoformat()
    conn = get_connection()
    with conn:
        conn.execute(
            """
            UPDATE relationship_state
            SET updated_at = ?
            WHERE conversation_id = ?
            """,
            (now, conversation_id),
        )
