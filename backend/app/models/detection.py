from sqlalchemy import Column, Integer, String, Float

from app.database.database import Base


class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, nullable=False)

    date = Column(String, nullable=False)
    time = Column(String, nullable=False)

    status = Column(String, nullable=False)

    ddos_percentage = Column(Float, nullable=False)

    packets = Column(Integer, nullable=False)
    samples = Column(Integer, nullable=False)
    windows = Column(Integer, nullable=False)
    record_hash = Column(String(64), nullable=False)