"""SQLite persistence for apps, resources and status history."""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path

DB_PATH = Path("olho.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            environment TEXT DEFAULT 'prod',
            team TEXT,
            thresholds TEXT DEFAULT '{}',
            visible INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id INTEGER,
            source TEXT NOT NULL,          -- okd, eks, elk, dynatrace, ec2, ecs
            external_id TEXT NOT NULL,
            display_name TEXT,
            metadata TEXT DEFAULT '{}',
            FOREIGN KEY (app_id) REFERENCES apps(id)
        );

        CREATE TABLE IF NOT EXISTS status_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id INTEGER,
            overall_status TEXT,
            details TEXT,                  -- JSON per source
            source_states TEXT,            -- JSON of source health
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (app_id) REFERENCES apps(id)
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT NOT NULL,
            resource TEXT,
            details TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


def upsert_app(name: str, environment: str = "prod", team: Optional[str] = None) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO apps (name, environment, team) VALUES (?, ?, ?)",
        (name, environment, team),
    )
    c.execute("SELECT id FROM apps WHERE name = ?", (name,))
    app_id = c.fetchone()[0]
    conn.commit()
    conn.close()
    return app_id


def save_snapshot(app_id: int, overall: str, details: Dict, source_states: Dict):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """INSERT INTO status_snapshots (app_id, overall_status, details, source_states)
           VALUES (?, ?, ?, ?)""",
        (app_id, overall, json.dumps(details), json.dumps(source_states)),
    )
    conn.commit()
    conn.close()


def save_connection(app_id: int, kind: str, host: str, port: Optional[int] = None, name: Optional[str] = None, metadata: Optional[Dict] = None):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """INSERT OR REPLACE INTO app_connections (app_id, kind, host, port, name, metadata)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (app_id, kind, host, port, name, json.dumps(metadata or {})),
    )
    conn.commit()
    conn.close()


def log_audit(username: str, action: str, resource: Optional[str] = None, details: Optional[Dict] = None):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO audit_log (username, action, resource, details) VALUES (?, ?, ?, ?)",
        (username, action, resource, json.dumps(details or {})),
    )
    conn.commit()
    conn.close()
