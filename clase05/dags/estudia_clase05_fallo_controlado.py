"""Fallo de validación con un fixture local. No llama a la API ni a PostgreSQL."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from airflow import DAG
from airflow.operators.python import PythonOperator

COLUMNAS = ["id_transaccion", "fecha", "cantidad", "importe_neto", "categoria", "region"]


def validar_fixture(**_):
    ruta = Path(os.environ.get("ESTUDIA_FIXTURE_FALLO", "/opt/airflow/fixtures/validacion_falla.json"))
    if not ruta.is_file():
        ruta = Path(__file__).resolve().parents[1] / "fixtures" / "validacion_falla.json"
    cuerpo = json.loads(ruta.read_text(encoding="utf-8"))
    marco = pd.DataFrame(cuerpo["paginas"][0]["cuerpo"]["data"])
    if any(columna not in marco.columns for columna in COLUMNAS):
        raise RuntimeError("El fixture no trae las columnas obligatorias.")
    if marco["id_transaccion"].duplicated().any():
        raise RuntimeError("Fixture de clase: id_transaccion duplicado. No se borra la fila.")
    raise RuntimeError("Este fixture tenia que fallar por duplicados y no lo hizo.")


with DAG(
    dag_id="estudia_clase05_fallo_controlado",
    description="Validacion que falla a proposito con un JSON local.",
    start_date=datetime(2026, 11, 26),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    is_paused_upon_creation=True,
    default_args={"retries": 1, "retry_delay": timedelta(seconds=20)},
    tags=["clase05", "fallo"],
) as dag:
    PythonOperator(task_id="validar_datos", python_callable=validar_fixture)
