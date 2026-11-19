"""Pide una ejecución de cada DAG de prueba y espera a que el pool las termine."""

import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _entorno import API, cuentas, ssh

USUARIOS = [f"estudiante{n:02d}" for n in range(80, 100)]


def main():
    personas = cuentas()
    tokens = {}
    for usuario in USUARIOS:
        login = requests.post(
            f"{API}/auth/login",
            json={"username": usuario, "password": personas[usuario]},
            timeout=30,
        )
        login.raise_for_status()
        tokens[usuario] = login.json()["access_token"]
        requests.post(
            f"{API}/pipelines/me/trigger",
            headers={"Authorization": f"Bearer {tokens[usuario]}"},
            timeout=30,
        ).raise_for_status()
    pendientes = set(USUARIOS)
    for _ in range(30):
        time.sleep(5)
        for usuario in list(pendientes):
            corridas = requests.get(
                f"{API}/pipelines/me/runs",
                headers={"Authorization": f"Bearer {tokens[usuario]}"},
                timeout=30,
            ).json()["ejecuciones"]
            if any(item.get("estado") == "success" for item in corridas):
                pendientes.discard(usuario)
        if not pendientes:
            break
    print("exitos", 20 - len(pendientes), "pendientes", ",".join(sorted(pendientes)) or "ninguno")
    print(ssh("free -m | head -n 2"))
    print(ssh("sudo docker stats --no-stream --format '{{.Name}} {{.CPUPerc}} {{.MemUsage}}'"))
    return 0 if not pendientes else 1


if __name__ == "__main__":
    raise SystemExit(main())
