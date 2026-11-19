"""Carga cuentas de prueba desde la VM. No imprime contraseñas."""

from __future__ import annotations

import subprocess
from pathlib import Path

KEY = str(Path.home() / ".ssh" / "google_compute_engine")
KNOWN_AIR = str(Path.home() / "AppData/Local/Temp/estudia_airflow_known")
API = "https://34.95.210.33.sslip.io"
DB_HOST = "34.39.202.205"
DB_PORT = 6432
DB_NAME = "retail_dwh"


def ssh(remote: str, data: str | None = None) -> str:
    command = [
        "ssh", "-i", KEY, "-p", "2223",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", f"UserKnownHostsFile={KNOWN_AIR}",
        "yulcr@127.0.0.1", remote,
    ]
    result = subprocess.run(command, input=data, text=True, capture_output=True)
    if result.returncode != 0:
        raise SystemExit(result.stderr[-800:])
    return result.stdout


def cuentas() -> dict[str, str]:
    texto = ssh("sudo cat /root/estudia-clase03/cuentas_prueba.csv")
    salida = {}
    for linea in texto.splitlines():
        if not linea or linea.startswith("usuario,"):
            continue
        usuario, password = linea.split(",", 1)
        salida[usuario] = password
    return salida


def secreto(nombre: str) -> str:
    texto = ssh("sudo cat /root/estudia-clase03/secrets.env")
    for linea in texto.splitlines():
        if linea.startswith(nombre + "="):
            return linea.split("=", 1)[1]
    raise SystemExit(f"falta {nombre}")
