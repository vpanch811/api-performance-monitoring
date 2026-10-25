import json

from app.database import (
    get_connection,
    initialize_database,
    save_report,
    get_saved_reports,
)
def test_initialize_database():
    initialize_database()

    with get_connection() as connection:
        result = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'performance_reports'
            """
        ).fetchone()
    assert result is not None

def test_save_and_retrieve_report():
    initialize_database()

    report = {
        "performance_status": "PASS",
        "average_response_time_ms": 100.0,
    }

    report_id = save_report(report)
    
    assert isinstance(report_id, int)
    assert report_id > 0
    
    reports = get_saved_reports()
    
    assert report in reports

def test_database_report_contains_valid_json():
    initialize_database()

    report = {
        "performance_status": "PASS",
        "average_response_time_ms": 150.0,
    }

    save_report(report)
    
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT report_json
            FROM performance_reports
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()
    
    assert row is not None
    assert json.loads(row["report_json"]) == report