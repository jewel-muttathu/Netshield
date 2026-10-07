import hashlib


def generate_detection_hash(
    filename,
    date,
    time,
    status,
    ddos_percentage,
    packets,
    samples,
    windows
):
    data = (
        f"{filename}|"
        f"{date}|"
        f"{time}|"
        f"{status}|"
        f"{ddos_percentage}|"
        f"{packets}|"
        f"{samples}|"
        f"{windows}"
    )

    return hashlib.sha256(data.encode("utf-8")).hexdigest()