#!/bin/bash
# Pausa los DAG generados para estudiantes. No detiene la VM ni el DAG del docente.
set -euo pipefail
cd /opt/estudia-clase03/airflow
docker compose exec -T fastapi python - << 'PY'
import os
import httpx

respuesta = httpx.post(
    "http://127.0.0.1:8000/admin/pause-all",
    headers={"X-Admin-Token": os.environ["ESTUDIA_ADMIN_TOKEN"]},
    timeout=120,
)
print(respuesta.status_code)
respuesta.raise_for_status()
print(respuesta.text)
PY
