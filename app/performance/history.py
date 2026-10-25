from app.database import (
    get_connection,
    get_saved_reports,
    save_report,
)


performance_history = []


def add_performance_report(report: dict) -> None:
    if "report" in report and isinstance(report["report"], dict):
        report = report["report"]

    save_report(report)


def get_performance_history() -> list:
    return get_saved_reports()


def clear_performance_history() -> None:
    performance_history.clear()

    with get_connection() as connection:
        connection.execute("DELETE FROM performance_reports")


def get_performance_summary() -> dict:
    reports = get_saved_reports()

    if not reports:
        return {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "average_response_time_ms": 0.0,
            "average_success_rate_percent": 0.0,
            "latest_status": None,
        }

    passed_tests = sum(
        1
        for report in reports
        if report.get("performance_status") == "PASS"
    )

    failed_tests = len(reports) - passed_tests

    average_response_time = sum(
        report.get("average_response_time_ms", 0.0)
        for report in reports
    ) / len(reports)

    average_success_rate = sum(
        report.get("success_rate_percent", 0.0)
        for report in reports
    ) / len(reports)

    return {
        "total_tests": len(reports),
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "average_response_time_ms": round(
            average_response_time, 2
        ),
        "average_success_rate_percent": round(
            average_success_rate, 2
        ),
        "latest_status": reports[-1].get("performance_status"),
    }


def get_load_level_comparison() -> list:
    comparison = []

    for report in get_saved_reports():
        comparison.append({
            "generated_at": report.get("generated_at"),
            "total_requests": report.get("total_requests"),
            "average_response_time_ms": report.get(
                "average_response_time_ms"
            ),
            "p95_response_time_ms": report.get(
                "p95_response_time_ms"
            ),
            "p99_response_time_ms": report.get(
                "p99_response_time_ms"
            ),
            "requests_per_second": report.get(
                "requests_per_second"
            ),
            "success_rate_percent": report.get(
                "success_rate_percent"
            ),
            "performance_status": report.get("performance_status"),
        })

    return comparison