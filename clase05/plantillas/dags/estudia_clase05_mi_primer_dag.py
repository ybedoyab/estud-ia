"""Primer DAG. No lo copies a dags/ a mano: usa activar_dags cuando no queden huecos."""

from datetime import datetime

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator


def saludar():
    print("Mi primer DAG")


def finalizar():
    print("Pipeline terminado")


with DAG(
    dag_id="COMPLETA",
    start_date=datetime(2026, 11, 26),
    schedule=COMPLETA,
    catchup=COMPLETA,
    is_paused_upon_creation=True,
    tags=["clase05", "primero"],
) as dag:
    inicio = PythonOperator(
        task_id="COMPLETA",
        python_callable=COMPLETA,
    )
    fin = PythonOperator(
        task_id="COMPLETA",
        python_callable=COMPLETA,
    )
    # Escribe debajo la dependencia: inicio >> fin
