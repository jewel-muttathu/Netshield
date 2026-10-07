import asyncio
import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import httpx


CHECK_COUNT = 3
CHECK_INTERVAL_SECONDS = 2
REQUEST_TIMEOUT_SECONDS = 10


def validate_url(url: str) -> str:
    """
    Validate and normalize the URL.

    Only HTTP and HTTPS URLs are accepted.
    """

    url = url.strip()

    if not url:
        raise ValueError("URL cannot be empty")

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http:// and https:// URLs are supported")

    if not parsed.netloc:
        raise ValueError("Invalid URL")

    return url


async def check_website(url: str) -> dict[str, Any]:
    """
    Perform one normal HTTP health check.

    This is a monitoring request, not traffic generation.
    """

    start_time = time.perf_counter()

    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT_SECONDS,
            follow_redirects=True,
        ) as client:

            response = await client.get(
                url,
                headers={
                    "User-Agent": "NetShield-Monitor/1.0"
                },
            )

        elapsed = time.perf_counter() - start_time

        return {
            "timestamp": timestamp,
            "available": True,
            "status_code": response.status_code,
            "response_time_ms": round(elapsed * 1000, 2),
            "response_size_bytes": len(response.content),
            "error": None,
        }

    except httpx.TimeoutException:
        elapsed = time.perf_counter() - start_time

        return {
            "timestamp": timestamp,
            "available": False,
            "status_code": None,
            "response_time_ms": round(elapsed * 1000, 2),
            "response_size_bytes": 0,
            "error": "timeout",
        }

    except httpx.RequestError as exc:
        elapsed = time.perf_counter() - start_time

        return {
            "timestamp": timestamp,
            "available": False,
            "status_code": None,
            "response_time_ms": round(elapsed * 1000, 2),
            "response_size_bytes": 0,
            "error": str(exc),
        }

    except Exception as exc:
        elapsed = time.perf_counter() - start_time

        return {
            "timestamp": timestamp,
            "available": False,
            "status_code": None,
            "response_time_ms": round(elapsed * 1000, 2),
            "response_size_bytes": 0,
            "error": str(exc),
        }


async def run_three_checks(url: str) -> list[dict[str, Any]]:
    """
    Run exactly three checks during one monitoring session.
    """

    url = validate_url(url)

    results = []

    for check_number in range(1, CHECK_COUNT + 1):

        result = await check_website(url)

        result["check_number"] = check_number

        results.append(result)

        # Do not wait after the final check.
        if check_number < CHECK_COUNT:
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)

    return results