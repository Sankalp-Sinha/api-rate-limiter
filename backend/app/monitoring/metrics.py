from prometheus_client import (
    Counter,
    Histogram,
)


# --------------------------------------------------
# Generic FastAPI HTTP metrics
# --------------------------------------------------

HTTP_REQUESTS_TOTAL = Counter(
    "rateguard_http_requests_total",
    (
        "Total number of HTTP requests "
        "handled by RateGuard"
    ),
    [
        "method",
        "route",
        "status_code",
    ],
)


HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "rateguard_http_request_duration_seconds",
    (
        "Duration of HTTP requests "
        "handled by RateGuard"
    ),
    [
        "method",
        "route",
    ],
    buckets=(
        0.005,
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
    ),
)


# --------------------------------------------------
# RateGuard /v1/check business metrics
# --------------------------------------------------

CHECK_DECISIONS_TOTAL = Counter(
    "rateguard_check_decisions_total",
    (
        "Total successful rate-limit "
        "decisions returned by /v1/check"
    ),
    [
        "decision",
    ],
)


CHECK_DURATION_SECONDS = Histogram(
    "rateguard_check_duration_seconds",
    (
        "End-to-end duration of successful "
        "/v1/check decisions"
    ),
    [
        "decision",
    ],
    buckets=(
        0.001,
        0.0025,
        0.005,
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
    ),
)


CHECK_FAILURES_TOTAL = Counter(
    "rateguard_check_failures_total",
    (
        "Total /v1/check failures "
        "before a decision was produced"
    ),
    [
        "reason",
    ],
)