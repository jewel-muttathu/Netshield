from typing import Any


def calculate_metrics(checks: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Calculate service-level metrics from the three checks.
    """

    total_checks = len(checks)

    if total_checks == 0:
        return {
            "availability_percent": 0,
            "failure_rate_percent": 100,
            "average_response_time_ms": None,
            "max_response_time_ms": None,
            "timeout_rate_percent": 0,
            "error_5xx_rate_percent": 0,
            "error_4xx_rate_percent": 0,
        }

    successful_checks = [
        check
        for check in checks
        if check.get("available") is True
    ]

    response_times = [
        check["response_time_ms"]
        for check in successful_checks
        if check.get("response_time_ms") is not None
    ]

    timeout_count = sum(
        1
        for check in checks
        if check.get("error") == "timeout"
    )

    server_error_count = sum(
        1
        for check in checks
        if check.get("status_code") is not None
        and 500 <= check["status_code"] <= 599
    )

    client_error_count = sum(
        1
        for check in checks
        if check.get("status_code") is not None
        and 400 <= check["status_code"] <= 499
    )

    availability_percent = (
        len(successful_checks) / total_checks
    ) * 100

    failure_rate_percent = (
        (total_checks - len(successful_checks))
        / total_checks
    ) * 100

    timeout_rate_percent = (
        timeout_count / total_checks
    ) * 100

    error_5xx_rate_percent = (
        server_error_count / total_checks
    ) * 100

    error_4xx_rate_percent = (
        client_error_count / total_checks
    ) * 100

    average_response_time = None
    max_response_time = None

    if response_times:
        average_response_time = round(
            sum(response_times) / len(response_times),
            2,
        )

        max_response_time = round(
            max(response_times),
            2,
        )

    return {
        "availability_percent": round(
            availability_percent,
            2,
        ),
        "failure_rate_percent": round(
            failure_rate_percent,
            2,
        ),
        "average_response_time_ms": average_response_time,
        "max_response_time_ms": max_response_time,
        "timeout_rate_percent": round(
            timeout_rate_percent,
            2,
        ),
        "error_5xx_rate_percent": round(
            error_5xx_rate_percent,
            2,
        ),
        "error_4xx_rate_percent": round(
            error_4xx_rate_percent,
            2,
        ),
    }


def calculate_anomaly_score(
    metrics: dict[str, Any],
) -> dict[str, Any]:
    """
    Calculate a simple service anomaly score.

    This is intentionally a transparent rule-based detector
    for the first prototype. It is NOT a DDoS proof.
    """

    score = 0.0
    reasons = []

    availability = metrics["availability_percent"]
    failure_rate = metrics["failure_rate_percent"]
    timeout_rate = metrics["timeout_rate_percent"]
    error_5xx_rate = metrics["error_5xx_rate_percent"]
    avg_response = metrics["average_response_time_ms"]

    # Availability
    if availability < 50:
        score += 0.35
        reasons.append("Very low availability")

    elif availability < 80:
        score += 0.20
        reasons.append("Reduced availability")

    # Failure rate
    if failure_rate >= 50:
        score += 0.25
        reasons.append("High failure rate")

    elif failure_rate >= 25:
        score += 0.15
        reasons.append("Elevated failure rate")

    # Timeout rate
    if timeout_rate >= 50:
        score += 0.25
        reasons.append("High timeout rate")

    elif timeout_rate > 0:
        score += 0.10
        reasons.append("Timeouts detected")

    # HTTP 5xx
    if error_5xx_rate >= 50:
        score += 0.25
        reasons.append("High HTTP 5xx error rate")

    elif error_5xx_rate > 0:
        score += 0.15
        reasons.append("HTTP 5xx errors detected")

    # Response time
    if avg_response is not None:

        if avg_response >= 5000:
            score += 0.25
            reasons.append("Very high response latency")

        elif avg_response >= 2000:
            score += 0.15
            reasons.append("High response latency")

        elif avg_response >= 1000:
            score += 0.08
            reasons.append("Elevated response latency")

    # Keep score between 0 and 1.
    score = min(score, 1.0)

    if score >= 0.70:
        status = "POSSIBLE_SERVICE_DEGRADATION"

    elif score >= 0.30:
        status = "SUSPICIOUS"

    else:
        status = "NORMAL"

    return {
        "anomaly_score": round(score, 2),
        "status": status,
        "reasons": reasons,
    }