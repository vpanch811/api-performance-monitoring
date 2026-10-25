# API Performance Testing & Automated Deployment Monitoring

A DevOps-focused project for testing API performance, evaluating performance against defined thresholds, and monitoring historical performance results.

## Project Overview

This project provides a REST API that can execute performance tests against HTTP/HTTPS endpoints and generate structured performance reports.

The system measures response time, success rate, throughput, and percentile-based performance metrics. It also evaluates the results against configurable performance thresholds and maintains a history of previous performance tests.

## Current Features

- REST API built with FastAPI
- User CRUD operations
- Sequential API performance testing
- Concurrent API performance testing
- Response time measurement
- Average response time
- Minimum response time
- Maximum response time
- P95 response time
- P99 response time
- Successful and failed request tracking
- Success rate calculation
- Requests-per-second calculation
- Structured performance reports
- Performance threshold evaluation
- Automatic PASS/FAIL performance status
- Performance test history
- Performance history API
- Automated testing with pytest

## API Endpoints

### Basic Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check that the API is running |
| GET | `/health` | Health check |
| GET | `/users` | Get all users |
| GET | `/users/{user_id}` | Get a specific user |
| POST | `/users` | Create a user |
| PUT | `/users/{user_id}` | Update a user |
| DELETE | `/users/{user_id}` | Delete a user |

### Performance Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/performance-test` | Run an API performance test |
| GET | `/performance-history` | View previous performance test reports |

## Performance Testing

The `/performance-test` endpoint supports two modes:

### Sequential

Requests are executed one after another.

```json
{
  "url": "https://httpbin.org/get",
  "number_of_requests": 5,
  "mode": "sequential"
}

## Automated Performance Testing

The project includes an automated load-testing script that runs concurrent performance tests against the API at multiple load levels.

### Load Test Levels

The automated runner tests:

* 10 concurrent requests
* 50 concurrent requests
* 100 concurrent requests

For each load level, the following metrics are collected:

* Total requests
* Successful requests
* Failed requests
* Success rate
* Average response time
* P95 response time
* P99 response time
* Requests per second

The results are automatically evaluated against the configured performance thresholds:

* Maximum average response time: **500 ms**
* Minimum success rate: **95%**

Each load level receives a **PASS** or **FAIL** status, followed by an overall performance result.

### Running Automated Load Tests

Make sure the FastAPI application is running first:

```bash
uvicorn app.main:app --reload
```

Then, from the project root, run:

```bash
python scripts/run_load_tests.py
```

Example output:

```text
API Performance Load Test
==================================================

Testing 10 concurrent requests...
...
Performance status:   PASS

Testing 50 concurrent requests...
...
Performance status:   PASS

Testing 100 concurrent requests...
...
Performance status:   PASS

==================================================
Load Test Summary
==================================================
10 requests:        PASS
50 requests:        PASS
100 requests:       PASS

Overall performance: PASS
```

### Performance Monitoring Features

The performance monitoring system now provides:

1. Sequential API performance testing
2. Concurrent API performance testing
3. Response-time measurement
4. Minimum and maximum response times
5. Average response time
6. P95 and P99 latency
7. Requests-per-second measurement
8. Success-rate monitoring
9. Configurable performance thresholds
10. Automatic PASS/FAIL evaluation
11. Performance report generation
12. Performance history tracking
13. Performance summary
14. Load-level comparison
15. Automated multi-level load testing

The automated load-testing workflow makes it possible to repeatedly test API performance under increasing levels of concurrent traffic and quickly determine whether the API meets the defined performance requirements.

## Performance Regression Detection

The project includes a performance regression detection feature
that compares the latest performance report with the most recent
earlier report for the same URL.

It detects whether the average response time has increased beyond
a configurable percentage threshold.

### Endpoint

`GET /performance-regression`

### Default Usage

Send a GET request to:

`http://127.0.0.1:8000/performance-regression`

By default, the regression threshold is 50%.

### Custom Threshold

You can specify a custom threshold using a query parameter:

`http://127.0.0.1:8000/performance-regression?regression_threshold_percent=30`

For example, a threshold of 30 means a regression is detected when
the average response time increases by more than 30% compared with
the baseline report.

### Example Response

```json
{
  "url": "https://example.com/api",
  "baseline_response_time_ms": 100.0,
  "latest_response_time_ms": 180.0,
  "response_time_change_percent": 80.0,
  "regression_threshold_percent": 50.0,
  "regression_detected": true,
  "message": "Potential performance regression detected"
}
