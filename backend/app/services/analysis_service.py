# backend/app/services/analysis_service.py

from pathlib import Path

from fastapi import UploadFile

from app.services.pcap_service import save_pcap, delete_pcap
from app.services.lucid_service import run_lucid


async def analyze_pcap(file: UploadFile) -> dict:
    """
    Complete PCAP analysis pipeline:

        Upload
          ↓
        Save PCAP
          ↓
        Run LUCID
          ↓
        Return result
          ↓
        Delete temporary PCAP
    """

    pcap_path: Path | None = None

    try:
        # ------------------------------------------------------------
        # 1. Save uploaded PCAP
        # ------------------------------------------------------------

        pcap_path = await save_pcap(file)

        # ------------------------------------------------------------
        # 2. Run LUCID
        # ------------------------------------------------------------

        result = run_lucid(pcap_path)

        # ------------------------------------------------------------
        # 3. Return structured response
        # ------------------------------------------------------------

        return {
            "success": True,
            "filename": file.filename,
            "result": result,
        }

    finally:

        # ------------------------------------------------------------
        # 4. Remove temporary PCAP
        # ------------------------------------------------------------

        if pcap_path is not None:
            delete_pcap(pcap_path)