import json
import sqlite3
from pathlib import Path
from typing import Any

DATABASE_PATH = Path(__file__).resolve().parent / "performance_history.db"

def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
    """
    CREATE TABLE IF NOT EXISTS performance_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
)

def save_report(report: dict[str, Any]) -> int:
    report_json = json.dumps(report)
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO performance_reports (report_json)
            VALUES (?)
            """,
            (report_json,),
        )
        return cursor.lastrowid

def get_saved_reports() -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT report_json
            FROM performance_reports
            ORDER BY id ASC
            """
        ).fetchall()
    return [json.loads(row["report_json"]) for row in rows]