"""Lee student_credentials.csv sin imprimir contraseñas."""

import csv
from pathlib import Path


def load_students(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise RuntimeError(f"sin estudiantes en {path}")
    return rows


def load_student(path, username=None):
    rows = load_students(path)
    if username is None:
        return rows[0]
    for row in rows:
        if row["usuario"] == username:
            return row
    raise RuntimeError(f"no está {username}")


def scrub(text, secrets):
    redacted = str(text)
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "***")
    return redacted
