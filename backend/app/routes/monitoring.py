import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

from app.services.website_monitor import run_three_checks
from app.services.anomaly_detector import (
    calculate_metrics,
    calculate_anomaly_score,
)


router = APIRouter(
    prefix="/monitor",
    tags=["Website Monitoring"],
)


class MonitorRequest(BaseModel):
    url: HttpUrl


@router.post("/start")
async def start_monitoring(
    request: MonitorRequest,
) -> dict[str, Any]:

    session_id = str(uuid.uuid4())

    url = str(request.url)

    try:

        # ---------------------------------------
        # Run exactly 3 checks
        # ---------------------------------------

        checks = await run_three_checks(url)

        # ---------------------------------------
        # Calculate session metrics
        # ---------------------------------------

        metrics = calculate_metrics(checks)

        # ---------------------------------------
        # Calculate anomaly score
        # ---------------------------------------

        detection = calculate_anomaly_score(metrics)

        # ---------------------------------------
        # Final response
        # ---------------------------------------

        return {
            "success": True,
            "session_id": session_id,
            "target": url,
            "monitoring_type": "three_check_session",

            "started_at": checks[0]["timestamp"],
            "completed_at": datetime.now(
                timezone.utc
            ).isoformat(),

            "check_count": len(checks),

            "checks": checks,

            "metrics": metrics,

            "detection": detection,

            "note": (
                "This mode performs black-box service monitoring. "
                "It does not measure the actual total network traffic "
                "received by the target server."
            ),
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Monitoring failed: {str(exc)}",
        )