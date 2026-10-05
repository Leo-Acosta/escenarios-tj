"""Historial local transaccional de análisis."""
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


def save_snapshot(path: Path, result: dict) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as db, db:
        db.execute('CREATE TABLE IF NOT EXISTS snapshots (id INTEGER PRIMARY KEY, created_at TEXT NOT NULL, payload TEXT NOT NULL)')
        cursor = db.execute('INSERT INTO snapshots(created_at,payload) VALUES (?,?)',
                            (datetime.now(timezone.utc).isoformat(), json.dumps(result, ensure_ascii=False, allow_nan=False)))
        return cursor.lastrowid


def list_snapshots(path: Path) -> list:
    if not path.exists():
        return []
    with closing(sqlite3.connect(path)) as db:
        return [dict(id=r[0], created_at=r[1], result=json.loads(r[2]))
                for r in db.execute('SELECT id,created_at,payload FROM snapshots ORDER BY id DESC LIMIT 20')]
