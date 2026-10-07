from datetime import datetime

from pydantic import BaseModel


class AnalysisResponse(BaseModel):
    id: int

    source_ip: str | None
    destination_ip: str | None
    protocol: str | None

    packet_count: int | None
    byte_count: int | None

    status: str
    confidence: float | None

    created_at: datetime

    class Config:
        from_attributes = True