# backend/app/services/lucid_service.py

import re
import subprocess
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[2]

LUCID_DIR = BACKEND_DIR / "app" / "models"

LUCID_SCRIPT = LUCID_DIR / "lucid_cnn.py"

MODEL_PATH = LUCID_DIR / "10t-10n-DOS2019-LUCID.h5"


def run_lucid(pcap_path: Path) -> dict:
    if not pcap_path.exists():
        raise FileNotFoundError(
            f"PCAP file does not exist: {pcap_path}"
        )

    if not LUCID_SCRIPT.exists():
        raise FileNotFoundError(
            f"lucid_cnn.py not found at: {LUCID_SCRIPT}"
        )

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found at: {MODEL_PATH}"
        )

    command = [
        sys.executable,
        str(LUCID_SCRIPT),
        "--predict_live",
        str(pcap_path),
        "--model",
        str(MODEL_PATH),
        "--dataset_type",
        "DOS2019",
    ]

    try:
        result = subprocess.run(
            command,
            cwd=str(LUCID_DIR),
            capture_output=True,
            text=True,
            timeout=1800,
        )

    except subprocess.TimeoutExpired:
        raise RuntimeError(
            "LUCID analysis timed out after 5 minutes."
        )

    if result.returncode != 0:
        raise RuntimeError(
            "LUCID failed.\n\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}"
        )

    return parse_lucid_output(result.stdout)


def parse_lucid_output(output: str) -> dict:
    predictions = []

    # LUCID prints each prediction as a multi-line dictionary.
    # Extract the fields we actually need from each dictionary.

    pattern = re.compile(
        r"'Packets':\s*np\.int64\((\d+)\).*?"
        r"'Samples':\s*(\d+).*?"
        r"'DDOS%':\s*'([0-9.]+)'",
        re.DOTALL,
    )

    matches = pattern.findall(output)

    for packets, samples, ddos_percentage in matches:
        predictions.append(
            {
                "packets": int(packets),
                "samples": int(samples),
                "ddos_percentage": float(ddos_percentage),
            }
        )

    if not predictions:
        raise RuntimeError(
            "LUCID completed but returned no prediction results."
        )

    total_packets = sum(
        p["packets"] for p in predictions
    )

    total_samples = sum(
        p["samples"] for p in predictions
    )

    # Convert each window's DDOS% into the number of
    # DDoS predictions in that window.

    total_ddos_samples = sum(
        p["ddos_percentage"] * p["samples"]
        for p in predictions
    )

    if total_samples > 0:
        ddos_percentage = (
            total_ddos_samples / total_samples
        )
    else:
        ddos_percentage = 0.0

    status = (
        "DDoS Attack"
        if ddos_percentage >= 0.5
        else "Normal"
    )

    return {
        "status": status,
        "ddos_percentage": round(
            ddos_percentage * 100,
            2,
        ),
        "packets": total_packets,
        "samples": total_samples,
        "windows": len(predictions),
    }