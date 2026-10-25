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

def detect_performance_regression(
    regression_threshold_percent: float = 50.0,
) -> dict:
    """
    Compare the latest performance report with an earlier
    report for the same URL and detect potential regressions.
    """

    if regression_threshold_percent < 0:
        raise ValueError(
            "Regression threshold cannot be negative"
        )

    reports = get_saved_reports()

    if len(reports) < 2:
        return {
            "regression_detected": False,
            "message": (
                "At least two performance reports are required"
            ),
            "baseline_response_time_ms": None,
            "latest_response_time_ms": None,
            "response_time_change_percent": None,
        }

    latest = reports[-1]

    # Find the most recent earlier report for the same URL.
    baseline = None

    for report in reversed(reports[:-1]):
        if report.get("url") == latest.get("url"):
            baseline = report
            break

    if baseline is None:
        return {
            "regression_detected": False,
            "message": (
                "No earlier performance report exists for this URL"
            ),
            "baseline_response_time_ms": None,
            "latest_response_time_ms": latest.get(
                "average_response_time_ms"
            ),
            "response_time_change_percent": None,
        }

    baseline_time = baseline.get(
        "average_response_time_ms"
    )
    latest_time = latest.get(
        "average_response_time_ms"
    )

    if (
        not isinstance(baseline_time, (int, float))
        or isinstance(baseline_time, bool)
        or not isinstance(latest_time, (int, float))
        or isinstance(latest_time, bool)
        or baseline_time < 0
        or latest_time < 0
    ):
        return {
            "regression_detected": False,
            "message": "Invalid response-time data",
            "baseline_response_time_ms": baseline_time,
            "latest_response_time_ms": latest_time,
            "response_time_change_percent": None,
        }

    if baseline_time == 0:
        if latest_time == 0:
            change_percent = 0.0
        else:
            return {
                "regression_detected": True,
                "message": (
                    "Response time increased from zero; "
                    "percentage change cannot be calculated"
                ),
                "baseline_response_time_ms": baseline_time,
                "latest_response_time_ms": latest_time,
                "response_time_change_percent": None,
                "regression_threshold_percent": (
                    regression_threshold_percent
                ),
            }
    else:
        change_percent = (
            (latest_time - baseline_time)
            / baseline_time
        ) * 100

    regression_detected = (
        change_percent > regression_threshold_percent
    )

    return {
        "url": latest.get("url"),
        "baseline_response_time_ms": baseline_time,
        "latest_response_time_ms": latest_time,
        "response_time_change_percent": round(
            change_percent, 2
        ),
        "regression_threshold_percent": (
            regression_threshold_percent
        ),
        "regression_detected": regression_detected,
        "message": (
            "Potential performance regression detected"
            if regression_detected
            else "No significant performance regression detected"
        ),
    }