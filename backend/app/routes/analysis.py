# backend/app/routes/analysis.py

from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.services.analysis_service import analyze_pcap
from app.database.database import SessionLocal
from app.models.detection import Detection
from app.utils.security import generate_detection_hash


router = APIRouter(
    prefix="/api/analysis",
    tags=["Analysis"],
)


@router.post("/upload")
async def upload_pcap(
    file: UploadFile = File(...)
):
    """
    Upload a PCAP file, analyze it using LUCID,
    save the detection result to SQLite,
    and return the result.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

    if not file.filename.lower().endswith(
        (".pcap", ".pcapng", ".cap")
    ):
        raise HTTPException(
            status_code=400,
            detail="Only PCAP, PCAPNG, and CAP files are allowed."
        )

    try:
        # Run LUCID analysis
        result = await analyze_pcap(file)

        # Get the actual analysis result
        analysis = result.get("result", {})

        # Current date and time
        now = datetime.now()

        # Create database session
        db: Session = SessionLocal()

        try:
            date = now.strftime("%Y-%m-%d")
            time = now.strftime("%H:%M:%S")

            status = analysis.get("status", "Unknown")
            ddos_percentage = analysis.get("ddos_percentage", 0)
            packets = analysis.get("packets", 0)
            samples = analysis.get("samples", 0)
            windows = analysis.get("windows", 0)

            record_hash = generate_detection_hash(
                filename=file.filename,
                date=date,
                time=time,
                status=status,
                ddos_percentage=ddos_percentage,
                packets=packets,
                samples=samples,
                windows=windows,
            )

            detection = Detection(
                filename=file.filename,

                date=date,
                time=time,

                status=status,

                ddos_percentage=ddos_percentage,

                packets=packets,
                samples=samples,
                windows=windows,

                record_hash=record_hash,
            )   

            db.add(detection)
            db.commit()
            db.refresh(detection)

        finally:
            db.close()

        return result

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(exc)}"
        )


@router.get("/history")
def get_detection_history():
    """
    Return all previous detection records from the database.
    """

    db: Session = SessionLocal()

    try:
        detections = (
            db.query(Detection)
            .order_by(Detection.id.desc())
            .all()
        )

        return {
            "success": True,
            "detections": [
                {
                    "id": detection.id,
                    "filename": detection.filename,
                    "date": detection.date,
                    "time": detection.time,
                    "status": detection.status,
                    "ddos_percentage": detection.ddos_percentage,
                    "packets": detection.packets,
                    "samples": detection.samples,
                    "windows": detection.windows,
                }
                for detection in detections
            ],
        }

    finally:
        db.close()