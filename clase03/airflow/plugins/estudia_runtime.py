"""Ejecucion confiable de un pipeline declarativo. No evalua codigo del estudiante."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import psycopg

SPECS = Path(os.environ.get("ESTUDIA_SPECS", "/opt/airflow/specs"))
REPORTES = Path(os.environ.get("ESTUDIA_REPORTES", "/opt/airflow/reportes"))
LIMITE_FILAS = 5000


def intervalo_de(usuario: str) -> int:
    spec = json.loads((SPECS / f"{usuario}.json").read_text(encoding="utf-8"))
    minutos = int(spec["intervalo_minutos"])
    if minutos not in {5, 10, 15}:
        return 10
    return minutos


def ejecutar_tarea(usuario: str, **_):
    spec = json.loads((SPECS / f"{usuario}.json").read_text(encoding="utf-8"))
    carpeta = REPORTES / usuario
    carpeta.mkdir(parents=True, exist_ok=True)
    _limpiar(carpeta)
    marco = None
    for tarea in _orden(spec["tareas"]):
        if tarea["tipo"] == "sql":
            marco = _sql(tarea["consulta"])
        elif tarea["tipo"] == "validacion":
            _validar(marco)
        elif tarea["tipo"] == "transformacion":
            marco = _transformar(marco, tarea.get("operacion", "quitar_nulos"))
        elif tarea["tipo"] == "agrupacion":
            marco = _agrupar(marco, tarea)
        elif tarea["tipo"] == "reporte_csv":
            _reporte(marco, carpeta, usuario)
        else:
            raise RuntimeError(f"Tipo de tarea no reconocido: {tarea['tipo']}")
    return str(carpeta / "reporte_ventas.csv")


def _orden(tareas: list[dict]) -> list[dict]:
    pendientes = {tarea["id"]: tarea for tarea in tareas}
    hechas = set()
    orden = []
    while pendientes:
        listas = [
            tarea for tarea in pendientes.values() if set(tarea.get("depende_de") or []).issubset(hechas)
        ]
        if not listas:
            raise RuntimeError("Las dependencias del pipeline no se pueden resolver.")
        tarea = sorted(listas, key=lambda item: item["id"])[0]
        orden.append(tarea)
        hechas.add(tarea["id"])
        pendientes.pop(tarea["id"])
    return orden


def _conectar():
    return psycopg.connect(
        host=os.environ["ESTUDIA_PGHOST"],
        port=int(os.environ.get("ESTUDIA_PGPORT", "6432")),
        dbname=os.environ.get("ESTUDIA_PGDATABASE", "retail_dwh"),
        user=os.environ["ESTUDIA_PGUSER"],
        password=os.environ["ESTUDIA_PGPASSWORD"],
        sslmode="require",
        connect_timeout=15,
    )


def _sql(consulta: str) -> pd.DataFrame:
    sentencia = f"SELECT * FROM ({consulta}) AS estudia_q LIMIT {LIMITE_FILAS}"
    with _conectar() as conn:
        with conn.transaction():
            conn.execute("SET LOCAL statement_timeout = '15s'")
            conn.execute("SET LOCAL default_transaction_read_only = on")
            with conn.cursor() as cur:
                cur.execute(sentencia)
                columnas = [item.name for item in cur.description]
                return pd.DataFrame(cur.fetchall(), columns=columnas)


def _validar(marco: pd.DataFrame | None) -> None:
    if marco is None or marco.empty:
        raise RuntimeError("La validacion no encontro filas.")
    if marco.isna().all().all():
        raise RuntimeError("La validacion encontro solo valores vacios.")


def _transformar(marco: pd.DataFrame | None, operacion: str) -> pd.DataFrame:
    if marco is None:
        raise RuntimeError("No hay datos para transformar.")
    if operacion == "rellenar_ceros":
        return marco.fillna(0)
    return marco.dropna()


def _agrupar(marco: pd.DataFrame | None, tarea: dict) -> pd.DataFrame:
    if marco is None:
        raise RuntimeError("No hay datos para agrupar.")
    columnas = tarea["columnas"]
    campo = tarea["campo"]
    faltan = [columna for columna in columnas + [campo] if columna not in marco.columns]
    if faltan:
        raise RuntimeError("Faltan columnas para agrupar: " + ", ".join(faltan))
    metrica = tarea["metrica"]
    if metrica == "count":
        return marco.groupby(columnas, dropna=False)[campo].count().reset_index(name=f"{metrica}_{campo}")
    serie = getattr(marco.groupby(columnas, dropna=False)[campo], metrica)()
    return serie.reset_index(name=f"{metrica}_{campo}")


def _reporte(marco: pd.DataFrame | None, carpeta: Path, usuario: str) -> None:
    if marco is None or marco.empty:
        raise RuntimeError("No hay datos para el reporte.")
    salida = marco.copy()
    salida.insert(0, "estudiante", usuario)
    salida.insert(1, "generado_en", datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec="seconds"))
    destino = carpeta / "reporte_ventas.csv"
    salida.to_csv(destino, index=False)
    historico = carpeta / f"reporte_{datetime.now().strftime('%Y%m%dT%H%M%S')}.csv"
    salida.to_csv(historico, index=False)


def _limpiar(carpeta: Path) -> None:
    historicos = sorted(carpeta.glob("reporte_2*.csv"))
    for viejo in historicos[:-20]:
        viejo.unlink(missing_ok=True)


def validar_demo(marco: pd.DataFrame) -> None:
    try:
        from airflow.sdk import Variable
    except ImportError:
        from airflow.models import Variable
    try:
        valor = Variable.get("estudia_demo_forzar_error", default="0")
    except TypeError:
        valor = Variable.get("estudia_demo_forzar_error", default_var="0")
    if str(valor) == "1":
        raise RuntimeError("Error de demostracion controlado por el docente. Los datos no se modificaron.")
    _validar(marco)
