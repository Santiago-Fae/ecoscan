"""Minimal SQLite persistence: statistics only, never images."""
import os
import sqlite3
import uuid
from contextlib import closing
from pathlib import Path

DB_PATH = Path(os.getenv("DB_PATH", Path(__file__).parent.parent / "data" / "ecoscan.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    found INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS detections (
    id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL REFERENCES analyses(id),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    material TEXT NOT NULL,          -- predicted by the model
    confidence REAL NOT NULL,
    uncertain INTEGER NOT NULL,
    feedback TEXT CHECK (feedback IN ('correct', 'corrected')),  -- NULL = unanswered
    real_material TEXT               -- material given by the user when correcting
);
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(_connect()) as conn, conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(SCHEMA)


def record_analysis(items: list[dict]) -> None:
    """Store the analysis and add an `id` (token used later for feedback) to each item."""
    analysis_id = uuid.uuid4().hex
    with closing(_connect()) as conn, conn:
        conn.execute("INSERT INTO analyses (id, found) VALUES (?, ?)", (analysis_id, int(bool(items))))
        for it in items:
            it["id"] = uuid.uuid4().hex
            conn.execute(
                "INSERT INTO detections (id, analysis_id, material, confidence, uncertain) VALUES (?, ?, ?, ?, ?)",
                (it["id"], analysis_id, it["material"]["key"], it["confidence"], int(it["uncertain"])),
            )


def record_feedback(detection_id: str, correct: bool, real_material: str | None) -> str | None:
    """Save the user's answer (one per detection). Return the final material, or None if invalid/already answered."""
    with closing(_connect()) as conn, conn:
        row = conn.execute(
            "SELECT material FROM detections WHERE id = ? AND feedback IS NULL", (detection_id,)
        ).fetchone()
        if row is None:
            return None
        if correct or real_material == row["material"]:
            conn.execute("UPDATE detections SET feedback = 'correct' WHERE id = ?", (detection_id,))
            return row["material"]
        conn.execute(
            "UPDATE detections SET feedback = 'corrected', real_material = ? WHERE id = ?",
            (real_material, detection_id),
        )
        return real_material


def stats() -> dict:
    with closing(_connect()) as conn:
        total_analyses = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
        without_object = conn.execute("SELECT COUNT(*) FROM analyses WHERE found = 0").fetchone()[0]
        # Final material: the one corrected by the user, when present
        by_material = conn.execute(
            "SELECT COALESCE(real_material, material) AS material, COUNT(*) AS total "
            "FROM detections GROUP BY 1 ORDER BY total DESC"
        ).fetchall()
        fb = conn.execute(
            "SELECT SUM(feedback = 'correct') AS ok, SUM(feedback = 'corrected') AS wrong FROM detections"
        ).fetchone()
        confusions = conn.execute(
            "SELECT material AS predicted, real_material AS actual, COUNT(*) AS total FROM detections "
            "WHERE feedback = 'corrected' GROUP BY 1, 2 ORDER BY total DESC LIMIT 5"
        ).fetchall()
        uncertain = conn.execute("SELECT COUNT(*) FROM detections WHERE uncertain = 1").fetchone()[0]
        total_items = conn.execute("SELECT COUNT(*) FROM detections").fetchone()[0]

    ok, wrong = fb["ok"] or 0, fb["wrong"] or 0
    answered = ok + wrong
    return {
        "total_analyses": total_analyses,
        "analyses_without_object": without_object,
        "total_items": total_items,
        "uncertain_items": uncertain,
        "by_material": [dict(r) for r in by_material],
        "feedback": {
            "answered": answered,
            "correct": ok,
            "corrected": wrong,
            "accuracy": round(ok / answered, 3) if answered else None,
        },
        "confusions": [dict(r) for r in confusions],
    }
