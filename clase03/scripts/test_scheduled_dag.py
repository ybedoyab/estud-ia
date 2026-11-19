"""Espera una ejecución periódica real del DAG de prueba."""

import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _entorno import API, cuentas


def main():
    persona = cuentas()["estudiante90"]
    login = requests.post(
        f"{API}/auth/login",
        json={"username": "estudiante90", "password": persona},
        timeout=30,
    )
    login.raise_for_status()
    token = login.json()["access_token"]
    cabeceras = {"Authorization": f"Bearer {token}"}
    for _ in range(40):
        corridas = requests.get(f"{API}/pipelines/me/runs", headers=cabeceras, timeout=30).json()
        periodicas = [
            item for item in corridas.get("ejecuciones", [])
            if str(item.get("run_id", "")).startswith("scheduled__") and item.get("estado") == "success"
        ]
        if periodicas:
            print("PASS programacion periodica", periodicas[0]["run_id"], periodicas[0]["estado"])
            return 0
        time.sleep(30)
    print("FAIL no hubo una ejecucion periodica exitosa")
    print(corridas)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
