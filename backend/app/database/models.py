from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database.database import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)

    source_ip = Column(String, nullable=True)
    destination_ip = Column(String, nullable=True)

    protocol = Column(String, nullable=True)

    packet_count = Column(Integer, nullable=True)
    byte_count = Column(Integer, nullable=True)

    status = Column(String, nullable=False)

    confidence = Column(Float, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )