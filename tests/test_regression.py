import pytest

from app.performance.history import detect_performance_regression


@pytest.fixture
def mock_reports(monkeypatch):
    reports = []

    def fake_get_saved_reports():
        return reports

    monkeypatch.setattr(
        "app.performance.history.get_saved_reports",
        fake_get_saved_reports,
    )

    return reports


def create_report(url, response_time):
    return {
        "url": url,
        "average_response_time_ms": response_time,
        "performance_status": "PASS",
    }


def test_regression_detected_when_response_time_increases(
    mock_reports,
):
    mock_reports.extend([
        create_report("https://example.com/api", 100.0),
        create_report("https://example.com/api", 180.0),
    ])

    result = detect_performance_regression(
        regression_threshold_percent=50.0
    )

    assert result["regression_detected"] is True
    assert result["baseline_response_time_ms"] == 100.0
    assert result["latest_response_time_ms"] == 180.0
    assert result["response_time_change_percent"] == 80.0


def test_no_regression_when_increase_is_below_threshold(
    mock_reports,
):
    mock_reports.extend([
        create_report("https://example.com/api", 100.0),
        create_report("https://example.com/api", 120.0),
    ])

    result = detect_performance_regression(
        regression_threshold_percent=50.0
    )

    assert result["regression_detected"] is False
    assert result["response_time_change_percent"] == 20.0


def test_no_regression_when_response_time_decreases(
    mock_reports,
):
    mock_reports.extend([
        create_report("https://example.com/api", 200.0),
        create_report("https://example.com/api", 100.0),
    ])

    result = detect_performance_regression()

    assert result["regression_detected"] is False
    assert result["response_time_change_percent"] == -50.0


def test_regression_requires_two_reports(mock_reports):
    mock_reports.append(
        create_report("https://example.com/api", 100.0)
    )

    result = detect_performance_regression()

    assert result["regression_detected"] is False
    assert "at least two" in result["message"].lower()


def test_regression_requires_matching_url(mock_reports):
    mock_reports.extend([
        create_report("https://example.com/api", 100.0),
        create_report("https://another.com/api", 200.0),
    ])

    result = detect_performance_regression()

    assert result["regression_detected"] is False
    assert "no earlier" in result["message"].lower()


def test_negative_threshold_is_rejected():
    with pytest.raises(ValueError):
        detect_performance_regression(
            regression_threshold_percent=-10.0
        )


def test_zero_baseline_and_positive_latest_time(
    mock_reports,
):
    mock_reports.extend([
        create_report("https://example.com/api", 0.0),
        create_report("https://example.com/api", 10.0),
    ])

    result = detect_performance_regression()

    assert result["regression_detected"] is True
    assert result["response_time_change_percent"] is None