"""Publica 20 pipelines y mide si el servidor sigue respondiendo."""

import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _entorno import API, cuentas, ssh


def cuerpo(usuario):
    return {
        "nombre": f"Carga {usuario}",
        "intervalo_minutos": 15,
        "tareas": [
            {
                "id": "extraer",
                "tipo": "sql",
                "consulta": "SELECT p.categoria, SUM(v.cantidad) AS cantidad FROM curso.ventas v JOIN curso.productos p ON p.id_producto = v.id_producto GROUP BY p.categoria",
                "depende_de": [],
            },
            {"id": "validar", "tipo": "validacion", "depende_de": ["extraer"]},
            {"id": "reporte", "tipo": "reporte_csv", "depende_de": ["validar"]},
        ],
    }


def publicar(usuario, password):
    inicio = time.perf_counter()
    login = requests.post(f"{API}/auth/login", json={"username": usuario, "password": password}, timeout=30)
    if login.status_code != 200:
        return usuario, login.status_code, 0
    token = login.json()["access_token"]
    respuesta = requests.post(
        f"{API}/pipelines/publish",
        json=cuerpo(usuario),
        headers={"Authorization": f"Bearer {token}"},
        timeout=180,
    )
    return usuario, respuesta.status_code, round(time.perf_counter() - inicio, 1)


def main():
    personas = cuentas()
    usuarios = [f"estudiante{n:02d}" for n in range(80, 100)]
    inicio = time.perf_counter()
    resultados = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futuros = [pool.submit(publicar, usuario, personas[usuario]) for usuario in usuarios]
        for futuro in as_completed(futuros):
            resultados.append(futuro.result())
            print(resultados[-1][0], resultados[-1][1], resultados[-1][2])
    ok = sum(1 for _, codigo, _ in resultados if codigo == 200)
    stats = ssh("sudo docker stats --no-stream --format '{{.Name}} {{.CPUPerc}} {{.MemUsage}}'")
    print(stats)
    print(f"publicados {ok}/20 en {round(time.perf_counter() - inicio, 1)} s")
    print("CARGA", "PASS" if ok == 20 else "FAIL")
    return 0 if ok == 20 else 1


if __name__ == "__main__":
    raise SystemExit(main())
