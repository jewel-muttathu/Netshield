# backend/app/services/pcap_service.py

from pathlib import Path
from fastapi import UploadFile
import time

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"

# Create uploads directory automatically
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def save_pcap(file: UploadFile) -> Path:
    """
    Save an uploaded PCAP file to the backend/uploads directory.
    """

    if not file.filename:
        raise ValueError("No filename provided.")

    filename = Path(file.filename).name

    if not filename.lower().endswith((".pcap", ".pcapng", ".cap")):
        raise ValueError("Only PCAP/PCAPNG files are allowed.")

    destination = UPLOAD_DIR / filename

    # Avoid accidentally overwriting another upload
    counter = 1

    while destination.exists():
        stem = Path(filename).stem
        suffix = Path(filename).suffix

        destination = UPLOAD_DIR / f"{stem}_{counter}{suffix}"
        counter += 1

    with destination.open("wb") as buffer:
        while True:
            chunk = await file.read(1024 * 1024)

            if not chunk:
                break

            buffer.write(chunk)

    await file.close()

    return destination


def delete_pcap(file_path: Path) -> None:
    if not file_path.exists():
        return

    max_attempts = 10

    for attempt in range(max_attempts):
        try:
            file_path.unlink()
            return

        except PermissionError:
            if attempt == max_attempts - 1:
                raise

            time.sleep(0.5)