import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from fastapi.testclient import TestClient

from app.main import app
from app.performance.history import clear_performance_history


client = TestClient(app)


class PerformanceTestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/test-performance":
            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/json"
            )
            self.end_headers()

            self.wfile.write(
                b'{"status": "ok"}'
            )

    def log_message(self, format, *args):
        return


def start_test_server():
    server = HTTPServer(
        ("127.0.0.1", 0),
        PerformanceTestHandler
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True
    )

    thread.start()

    port = server.server_address[1]

    return server, f"http://127.0.0.1:{port}/test-performance"


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "API Performance Monitoring System is running"
    }


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }


def test_get_users():
    response = client.get("/users")

    assert response.status_code == 200

    users = response.json()

    assert len(users) >= 2
    assert users[0]["name"] == "Alice"
    assert users[1]["name"] == "Bob"


def test_get_user():
    response = client.get("/users/1")

    assert response.status_code == 200

    user = response.json()

    assert user["id"] == 1
    assert user["name"] == "Alice"
    assert user["email"] == "alice@example.com"


def test_get_nonexistent_user():
    response = client.get("/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_create_user():
    response = client.post(
        "/users",
        json={
            "name": "Charlie",
            "email": "charlie@example.com"
        }
    )

    assert response.status_code == 201

    user = response.json()

    assert user["name"] == "Charlie"
    assert user["email"] == "charlie@example.com"
    assert "id" in user


def test_invalid_email():
    response = client.post(
        "/users",
        json={
            "name": "Test User",
            "email": "invalid-email"
        }
    )

    assert response.status_code == 422


def test_update_user():
    response = client.put(
        "/users/1",
        json={
            "name": "Alice Updated",
            "email": "alice.updated@example.com"
        }
    )

    assert response.status_code == 200

    user = response.json()

    assert user["id"] == 1
    assert user["name"] == "Alice Updated"
    assert user["email"] == "alice.updated@example.com"


def test_update_nonexistent_user():
    response = client.put(
        "/users/999",
        json={
            "name": "Nobody",
            "email": "nobody@example.com"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user():
    response = client.delete("/users/2")

    assert response.status_code == 200
    assert response.json() == {
        "message": "User deleted successfully"
    }


def test_delete_nonexistent_user():
    response = client.delete("/users/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_performance_test():
    server, url = start_test_server()

    try:
        response = client.post(
            "/performance-test",
            json={
                "url": url,
                "number_of_requests": 3
            }
        )

        assert response.status_code == 200

        result = response.json()
        report = result["report"]

        assert report["url"] == url
        assert report["total_requests"] == 3
        assert report["successful_requests"] == 3
        assert report["failed_requests"] == 0

        assert report["success_rate_percent"] == 100.0

        assert report["average_response_time_ms"] > 0
        assert report["minimum_response_time_ms"] > 0
        assert report["maximum_response_time_ms"] > 0

        assert report["maximum_response_time_ms"] >= (
            report["minimum_response_time_ms"]
        )

        assert report["p95_response_time_ms"] > 0
        assert report["p99_response_time_ms"] > 0

        assert report["p95_response_time_ms"] >= (
            report["minimum_response_time_ms"]
        )

        assert report["p99_response_time_ms"] >= (
            report["p95_response_time_ms"]
        )

        assert report["requests_per_second"] > 0
        assert report["total_test_time_seconds"] > 0

    finally:
        server.shutdown()


def test_concurrent_performance_test():
    server, url = start_test_server()

    try:
        response = client.post(
            "/performance-test",
            json={
                "url": url,
                "number_of_requests": 3,
                "mode": "concurrent"
            }
        )

        assert response.status_code == 200

        result = response.json()
        report = result["report"]

        assert report["url"] == url
        assert report["total_requests"] == 3
        assert report["successful_requests"] == 3
        assert report["failed_requests"] == 0
        assert report["success_rate_percent"] == 100.0

        assert report["average_response_time_ms"] > 0
        assert report["minimum_response_time_ms"] > 0
        assert report["maximum_response_time_ms"] > 0

        assert report["p95_response_time_ms"] > 0
        assert report["p99_response_time_ms"] > 0

        assert report["p95_response_time_ms"] >= (
            report["minimum_response_time_ms"]
        )

        assert report["p99_response_time_ms"] >= (
            report["p95_response_time_ms"]
        )

        assert report["requests_per_second"] > 0
        assert report["total_test_time_seconds"] > 0

    finally:
        server.shutdown()


def test_sequential_performance_test():
    server, url = start_test_server()

    try:
        response = client.post(
            "/performance-test",
            json={
                "url": url,
                "number_of_requests": 3,
                "mode": "sequential"
            }
        )

        assert response.status_code == 200

        result = response.json()
        report = result["report"]

        assert report["url"] == url
        assert report["total_requests"] == 3
        assert report["successful_requests"] == 3
        assert report["failed_requests"] == 0
        assert report["success_rate_percent"] == 100.0

        assert report["average_response_time_ms"] > 0
        assert report["minimum_response_time_ms"] > 0
        assert report["maximum_response_time_ms"] > 0

        assert report["p95_response_time_ms"] > 0
        assert report["p99_response_time_ms"] > 0

        assert report["p95_response_time_ms"] >= (
            report["minimum_response_time_ms"]
        )

        assert report["p99_response_time_ms"] >= (
            report["p95_response_time_ms"]
        )

        assert report["requests_per_second"] > 0
        assert report["total_test_time_seconds"] > 0

    finally:
        server.shutdown()


def test_invalid_performance_test_mode():
    response = client.post(
        "/performance-test",
        json={
            "url": "http://127.0.0.1/test",
            "number_of_requests": 3,
            "mode": "invalid"
        }
    )

    assert response.status_code == 422


def test_invalid_performance_test_url():
    response = client.post(
        "/performance-test",
        json={
            "url": "not-a-valid-url",
            "number_of_requests": 3
        }
    )

    assert response.status_code == 422


def test_unsupported_performance_test_url_scheme():
    response = client.post(
        "/performance-test",
        json={
            "url": "ftp://example.com/file",
            "number_of_requests": 3
        }
    )

    assert response.status_code == 422

def test_performance_history():
    clear_performance_history()

    server, url = start_test_server()

    try:
        response = client.post(
            "/performance-test",
            json={
                "url": url,
                "number_of_requests": 3
            }
        )

        assert response.status_code == 200

        history_response = client.get(
            "/performance-history"
        )

        assert history_response.status_code == 200

        history = history_response.json()

        assert history["total_tests"] == 1
        assert len(history["tests"]) == 1

        report = history["tests"][0]["report"]

        assert report["url"] == url
        assert report["total_requests"] == 3
        assert report["successful_requests"] == 3
        assert report["failed_requests"] == 0
        assert report["performance_status"] == "PASS"

    finally:
        server.shutdown()
        clear_performance_history()

def test_multiple_performance_history():
    clear_performance_history()

    server, url = start_test_server()

    try:
        first_response = client.post(
            "/performance-test",
            json={
                "url": url,
                "number_of_requests": 2
            }
        )

        assert first_response.status_code == 200

        second_response = client.post(
            "/performance-test",
            json={
                "url": url,
                "number_of_requests": 4
            }
        )

        assert second_response.status_code == 200

        history_response = client.get(
            "/performance-history"
        )

        assert history_response.status_code == 200

        history = history_response.json()

        assert history["total_tests"] == 2
        assert len(history["tests"]) == 2

        first_report = history["tests"][0]["report"]
        second_report = history["tests"][1]["report"]

        assert first_report["total_requests"] == 2
        assert second_report["total_requests"] == 4

    finally:
        server.shutdown()
        clear_performance_history()

def test_performance_regression_endpoint():
    response = client.get("/performance-regression")

    assert response.status_code == 200
    assert "regression_detected" in response.json()


def test_performance_regression_custom_threshold():
    response = client.get(
        "/performance-regression",
        params={"regression_threshold_percent": 30},
    )

    assert response.status_code == 200
    assert "regression_detected" in response.json()


def test_performance_regression_negative_threshold():
    response = client.get(
        "/performance-regression",
        params={"regression_threshold_percent": -10},
    )

    assert response.status_code == 422