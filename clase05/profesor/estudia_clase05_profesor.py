"""DAG resuelto. No va en dags/ ni en el ZIP del estudiante.

Para una demostración local, copia este archivo a dags/ despues de apartar la practica.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path("/opt/airflow/extra")))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.providers.standard.operators.python import PythonOperator

from pipeline.medallion import (
    base_de,
    exportar_reporte,
    extraer_ventas,
    generar_gold,
    guardar_bronze,
    guardar_staging,
    login,
    sanear,
    transformar_silver,
    validar_datos,
)

CONEXION = "estudia_api"


def extraer_api(**contexto):
    datos = BaseHook.get_connection(CONEXION)
    base = base_de(datos.host, datos.schema)
    run_id = sanear(contexto["run_id"])
    token = login(base, datos.login, datos.password)
    try:
        return guardar_staging(run_id, extraer_ventas(base, token))
    finally:
        del token


def _siguiente(contexto, tarea: str) -> str:
    return sanear(contexto["ti"].xcom_pull(task_ids=tarea))


def bronze(**contexto):
    return guardar_bronze(_siguiente(contexto, "extraer_api"))


def silver(**contexto):
    return transformar_silver(_siguiente(contexto, "guardar_bronze"))


def revision(**contexto):
    return validar_datos(_siguiente(contexto, "transformar_silver"))


def gold(**contexto):
    return generar_gold(_siguiente(contexto, "validar_datos"))


def reporte(**contexto):
    return exportar_reporte(_siguiente(contexto, "generar_gold"))


with DAG(
    dag_id="estudia_clase05_api_medallion",
    description="Solucion docente. Extraccion parcial, Medallion e informe.",
    start_date=datetime(2026, 11, 26),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    is_paused_upon_creation=True,
    default_args={"retries": 1, "retry_delay": timedelta(seconds=30)},
    tags=["clase05", "profesor"],
) as dag:
    extraer = PythonOperator(task_id="extraer_api", python_callable=extraer_api)
    paso_bronze = PythonOperator(task_id="guardar_bronze", python_callable=bronze)
    paso_silver = PythonOperator(task_id="transformar_silver", python_callable=silver)
    paso_validar = PythonOperator(task_id="validar_datos", python_callable=revision)
    paso_gold = PythonOperator(task_id="generar_gold", python_callable=gold)
    paso_reporte = PythonOperator(task_id="exportar_reporte", python_callable=reporte)
    extraer >> paso_bronze >> paso_silver >> paso_validar >> paso_gold >> paso_reporte
