"""DAG del docente. Consulta la base educativa y puede fallar de forma controlada."""

from datetime import datetime, timedelta

try:
    from airflow.operators.python import PythonOperator
except ImportError:
    from airflow.providers.standard.operators.python import PythonOperator
from airflow import DAG
from airflow.timetables.trigger import CronTriggerTimetable

from estudia_runtime import _sql, validar_demo

CONSULTA = """
SELECT p.categoria, ROUND(SUM(v.importe_neto), 2) AS importe_neto, SUM(v.cantidad) AS cantidad
FROM curso.ventas v
JOIN curso.productos p ON p.id_producto = v.id_producto
GROUP BY p.categoria
"""


def extraer():
    marco = _sql(CONSULTA)
    ruta = "/opt/airflow/reportes/docente/demo_extracto.csv"
    from pathlib import Path

    Path(ruta).parent.mkdir(parents=True, exist_ok=True)
    marco.to_csv(ruta, index=False)
    return ruta


def validar():
    import pandas as pd

    marco = pd.read_csv("/opt/airflow/reportes/docente/demo_extracto.csv")
    validar_demo(marco)


def reporte():
    from datetime import timezone
    from pathlib import Path

    import pandas as pd

    marco = pd.read_csv("/opt/airflow/reportes/docente/demo_extracto.csv")
    marco.insert(0, "estudiante", "docente")
    marco.insert(1, "generado_en", datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec="seconds"))
    destino = Path("/opt/airflow/reportes/docente/reporte_ventas.csv")
    marco.to_csv(destino, index=False)


with DAG(
    dag_id="estudia_clase03_demo",
    description="Demostracion del docente, cada cinco minutos",
    start_date=datetime(2026, 11, 19),
    schedule=CronTriggerTimetable("*/5 * * * *", timezone="America/Bogota"),
    catchup=False,
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=4),
    is_paused_upon_creation=False,
    default_args={
        "retries": 0,
        "execution_timeout": timedelta(minutes=3),
    },
    tags=["clase03", "docente"],
) as dag:
    extraer_tarea = PythonOperator(task_id="extraer", python_callable=extraer, pool="clase03")
    validar_tarea = PythonOperator(task_id="validar", python_callable=validar, pool="clase03")
    reporte_tarea = PythonOperator(task_id="reporte", python_callable=reporte, pool="clase03")
    extraer_tarea >> validar_tarea >> reporte_tarea
