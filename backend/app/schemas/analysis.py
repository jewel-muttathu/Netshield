from pydantic import BaseModel


class AnalysisRequest(BaseModel):
    source_ip: str
    destination_ip: str
    protocol: str

    packet_count: int
    byte_count: int