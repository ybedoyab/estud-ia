"""Demostración docente. No está cargada en el scheduler.

La conexión Airflow `estudia_clase04_api` debe ser de tipo HTTP:
host = https://34.95.210.33.sslip.io
login = usuario de lectura
password = contraseña de ese usuario

El DAG no contiene la contraseña. schedule es None y nace en pausa.
"""

from datetime import datetime

import pandas as pd
import requests
from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator

CONEXION = "estudia_clase04_api"


def _token() -> tuple[str, str]:
    datos = BaseHook.get_connection(CONEXION)
    base = datos.host.rstrip("/")
    respuesta = requests.post(
        f"{base}/api/v4/auth/login",
        json={"username": datos.login, "password": datos.password},
        timeout=20,
    )
    respuesta.raise_for_status()
    return base, respuesta.json()["access_token"]


def extraer_api(**_):
    base, token = _token()
    respuesta = requests.get(
        f"{base}/api/v4/ventas/muestra",
        headers={"Authorization": f"Bearer {token}"},
        params={"limite": 200},
        timeout=30,
    )
    respuesta.raise_for_status()
    ruta = "/tmp/estudia_clase04_raw.json"
    with open(ruta, "w", encoding="utf-8") as handle:
        handle.write(respuesta.text)
    return ruta


def guardar_raw(**contexto):
    return contexto["ti"].xcom_pull(task_ids="extraer_api")


def normalizar(**contexto):
    import json
    from pathlib import Path

    ruta = contexto["ti"].xcom_pull(task_ids="extraer_api")
    marco = pd.json_normalize(json.loads(Path(ruta).read_text(encoding="utf-8"))["data"])
    destino = "/tmp/estudia_clase04_normalizado.csv"
    marco.to_csv(destino, index=False)
    return destino


def validar(**contexto):
    marco = pd.read_csv(contexto["ti"].xcom_pull(task_ids="normalizar"))
    if marco.empty or marco["id_transaccion"].duplicated().any():
        raise RuntimeError("La extraccion no paso la validacion.")
    return int(marco.shape[0])


def generar_reporte(**contexto):
    marco = pd.read_csv(contexto["ti"].xcom_pull(task_ids="normalizar"))
    resumen = marco.groupby("producto.categoria", as_index=False)["importe_neto"].sum()
    destino = "/tmp/estudia_clase04_reporte.csv"
    resumen.to_csv(destino, index=False)
    return destino


with DAG(
    dag_id="estudia_clase04_demo_api",
    description="Demostracion docente: extraer la API de la clase 04",
    start_date=datetime(2026, 11, 24),
    schedule=None,
    catchup=False,
    is_paused_upon_creation=True,
    tags=["clase04", "docente"],
) as dag:
    extraer = PythonOperator(task_id="extraer_api", python_callable=extraer_api)
    crudo = PythonOperator(task_id="guardar_raw", python_callable=guardar_raw)
    plano = PythonOperator(task_id="normalizar", python_callable=normalizar)
    revision = PythonOperator(task_id="validar", python_callable=validar)
    reporte = PythonOperator(task_id="generar_reporte", python_callable=generar_reporte)
    extraer >> crudo >> plano >> revision >> reporte
