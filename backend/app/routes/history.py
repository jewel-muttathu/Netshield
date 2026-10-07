from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import AnalysisResult
from app.schemas.response import AnalysisResponse

router = APIRouter(
    prefix="/history",
    tags=["History"]
)


@router.get("/", response_model=list[AnalysisResponse])
def get_history(
    db: Session = Depends(get_db)
):
    results = (
        db.query(AnalysisResult)
        .order_by(AnalysisResult.created_at.desc())
        .all()
    )

    return results


@router.get("/{result_id}", response_model=AnalysisResponse)
def get_result(
    result_id: int,
    db: Session = Depends(get_db)
):

    result = (
        db.query(AnalysisResult)
        .filter(AnalysisResult.id == result_id)
        .first()
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis result not found"
        )

    return result