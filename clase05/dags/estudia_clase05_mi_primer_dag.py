"""Primer DAG resuelto. Copialo a dags/ solo en la demostracion docente."""

from datetime import datetime

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator


def saludar():
    print("Mi primer DAG")


def finalizar():
    print("Pipeline terminado")


with DAG(
    dag_id="estudia_clase05_mi_primer_dag",
    start_date=datetime(2026, 11, 26),
    schedule=None,
    catchup=False,
    is_paused_upon_creation=True,
    tags=["clase05", "primero"],
) as dag:
    inicio = PythonOperator(
        task_id="saludar",
        python_callable=saludar,
    )
    fin = PythonOperator(
        task_id="finalizar",
        python_callable=finalizar,
    )
    inicio >> fin
