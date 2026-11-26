"""Práctica de la clase 05. Airflow importa este archivo aunque dejes COMPLETA.

Al ejecutarlo, la primera tarea se detiene hasta que reemplaces cada COMPLETA.
La cadena del grafo ya está dibujada para que el laboratorio no dispare las tareas en paralelo.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
except ImportError:
    DAG = None
    PythonOperator = None

RUTA_VENTAS = "COMPLETA"
REGION = "COMPLETA"
PAGE_SIZE = "COMPLETA"
PAGINAS = "COMPLETA"
PREFIJO_AUTH = "COMPLETA"
COLUMNA_CATEGORIA = "COMPLETA"
COLUMNA_REGION = "COMPLETA"
REGLA_DUPLICADOS = "COMPLETA"
CADENA = "COMPLETA"
CADENA_ESPERADA = "extraer_api>guardar_bronze>transformar_silver>validar_datos>generar_gold>exportar_reporte"
COLUMNAS = ["id_transaccion", "fecha", "cantidad", "importe_neto", "categoria", "region"]


def listo(valor: object) -> None:
    if isinstance(valor, str) and "COMPLETA" in valor:
        raise RuntimeError("Completa el campo antes de seguir. El DAG ya estaba importado.")


def sanear(run_id: str) -> str:
    limpio = "".join(caracter if caracter.isalnum() or caracter in "-_" else "_" for caracter in str(run_id))
    return (limpio or "ejecucion")[:80]


def raiz() -> Path:
    if os.environ.get("ESTUDIA_DATA"):
        return Path(os.environ["ESTUDIA_DATA"])
    if Path("/opt/airflow").exists():
        return Path("/opt/airflow/data")
    return Path(__file__).resolve().parents[1] / "data"


def carpeta(capa: str, run_id: str) -> Path:
    return raiz() / capa / sanear(run_id)


def escribir(ruta: Path, texto: str) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    temporal.write_text(texto, encoding="utf-8")
    os.replace(temporal, ruta)


def base_de(host: str, esquema: str | None) -> str:
    texto = (host or "").strip().rstrip("/")
    if texto.startswith("http://") or texto.startswith("https://"):
        return texto
    protocolo = esquema if esquema in {"http", "https"} else "https"
    return f"{protocolo}://{texto}"


def credenciales() -> tuple[str, str, str]:
    base = os.environ.get("ESTUDIA_BASE", "https://34.95.210.33.sslip.io")
    usuario = os.environ.get("ESTUDIA_USUARIO")
    password = os.environ.get("ESTUDIA_PASSWORD")
    if DAG is None or os.environ.get("ESTUDIA_FIXTURE"):
        return base, usuario or "", password or ""
    from airflow.hooks.base import BaseHook

    datos = BaseHook.get_connection("estudia_api")
    return base_de(datos.host, datos.schema), datos.login or "", datos.password or ""


def extraer_api(**contexto):
    listo(CADENA)
    if CADENA != CADENA_ESPERADA:
        raise RuntimeError("La cadena debe ser " + CADENA_ESPERADA)
    run_id = sanear(contexto["run_id"])
    fixture = os.environ.get("ESTUDIA_FIXTURE")
    if fixture:
        extraccion = json.loads(Path(fixture).read_text(encoding="utf-8"))
    else:
        listo(RUTA_VENTAS)
        listo(REGION)
        listo(PAGE_SIZE)
        listo(PAGINAS)
        listo(PREFIJO_AUTH)
        base, usuario, password = credenciales()
        alta = requests.post(
            f"{base}/api/v4/auth/login",
            json={"username": usuario, "password": password},
            timeout=20,
        )
        if alta.status_code != 200:
            raise RuntimeError(f"El login respondio {alta.status_code}.")
        token = alta.json()["access_token"]
        try:
            paginas = []
            for numero in range(1, int(PAGINAS) + 1):
                params = {
                    "region": REGION,
                    "page": numero,
                    "page_size": int(PAGE_SIZE),
                    "orden": "id_transaccion",
                    "direccion": "asc",
                }
                respuesta = requests.get(
                    f"{base}{RUTA_VENTAS}",
                    headers={"Authorization": PREFIJO_AUTH + " " + token, "Accept": "application/json"},
                    params=params,
                    timeout=60,
                )
                respuesta.raise_for_status()
                cuerpo = respuesta.json()
                paginas.append(
                    {
                        "numero": numero,
                        "filas": len(cuerpo["data"]),
                        "has_next": bool(cuerpo["pagination"]["has_next"]),
                        "cuerpo": cuerpo,
                    }
                )
                if not cuerpo["pagination"]["has_next"]:
                    break
            filas = sum(pagina["filas"] for pagina in paginas)
            total = paginas[-1]["cuerpo"]["pagination"]["total_records"]
            extraccion = {
                "paginas": paginas,
                "cobertura": {
                    "filtros": {"region": REGION},
                    "page_size": int(PAGE_SIZE),
                    "paginas": [
                        {"page": pagina["numero"], "filas": pagina["filas"], "has_next": pagina["has_next"]}
                        for pagina in paginas
                    ],
                    "filas": filas,
                    "total_records": total,
                    "total_pages": paginas[-1]["cuerpo"]["pagination"]["total_pages"],
                    "alcance": "completo" if filas == total else "parcial",
                    "fuente": "api",
                    "nota": "Esta extraccion no es el censo.",
                },
            }
        finally:
            del token
    escribir(carpeta("staging", run_id) / "extraccion.json", json.dumps(extraccion, ensure_ascii=False))
    return run_id


def _id(contexto, tarea: str) -> str:
    return sanear(contexto["ti"].xcom_pull(task_ids=tarea))


def guardar_bronze(**contexto):
    run_id = _id(contexto, "extraer_api")
    origen = carpeta("staging", run_id) / "extraccion.json"
    if not origen.exists() and (carpeta("bronze", run_id) / "cobertura.json").exists():
        return run_id
    extraccion = json.loads(origen.read_text(encoding="utf-8"))
    destino = carpeta("bronze", run_id)
    for pagina in extraccion["paginas"]:
        escribir(destino / f"pagina_{pagina['numero']}.json", json.dumps(pagina["cuerpo"], ensure_ascii=False))
    escribir(destino / "cobertura.json", json.dumps(extraccion["cobertura"], ensure_ascii=False))
    (carpeta("staging", run_id) / "extraccion.json").unlink(missing_ok=True)
    return run_id


def transformar_silver(**contexto):
    listo(COLUMNA_CATEGORIA)
    listo(COLUMNA_REGION)
    run_id = _id(contexto, "guardar_bronze")
    marcos = []
    for ruta in sorted(carpeta("bronze", run_id).glob("pagina_*.json")):
        marcos.append(pd.DataFrame(json.loads(ruta.read_text(encoding="utf-8"))["data"]))
    marco = pd.concat(marcos, ignore_index=True)
    if COLUMNA_CATEGORIA not in marco.columns or COLUMNA_REGION not in marco.columns:
        raise RuntimeError("Las columnas de agrupacion no estan en la respuesta plana de /ventas.")
    marco = marco[COLUMNAS].copy()
    marco["fecha"] = pd.to_datetime(marco["fecha"], errors="coerce")
    marco["importe_neto"] = pd.to_numeric(marco["importe_neto"], errors="coerce")
    marco["id_transaccion"] = pd.to_numeric(marco["id_transaccion"], errors="coerce")
    destino = carpeta("silver", run_id) / "ventas.csv"
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_suffix(".csv.tmp")
    marco.to_csv(temporal, index=False)
    os.replace(temporal, destino)
    return run_id


def validar_datos(**contexto):
    listo(REGLA_DUPLICADOS)
    if REGLA_DUPLICADOS != "rechazar":
        raise RuntimeError("La regla de la practica es rechazar duplicados, no borrarlos ni poner cero.")
    run_id = _id(contexto, "transformar_silver")
    marco = pd.read_csv(carpeta("silver", run_id) / "ventas.csv")
    cobertura = json.loads((carpeta("bronze", run_id) / "cobertura.json").read_text(encoding="utf-8"))
    if marco["id_transaccion"].isna().any():
        raise RuntimeError("Hay id_transaccion nulo.")
    if marco["id_transaccion"].duplicated().any():
        raise RuntimeError("Hay identificadores duplicados. No se eliminan.")
    if pd.to_datetime(marco["fecha"], errors="coerce").isna().any():
        raise RuntimeError("Hay fechas invalidas.")
    if int(marco.shape[0]) != int(cobertura["filas"]):
        raise RuntimeError("El conteo no coincide con bronze.")
    return run_id


def generar_gold(**contexto):
    run_id = _id(contexto, "validar_datos")
    marco = pd.read_csv(carpeta("silver", run_id) / "ventas.csv")
    cobertura = json.loads((carpeta("bronze", run_id) / "cobertura.json").read_text(encoding="utf-8"))
    importes = pd.to_numeric(marco["importe_neto"], errors="coerce")
    por_categoria = marco.assign(importe_neto=importes).groupby(COLUMNA_CATEGORIA, as_index=False)["importe_neto"].sum()
    por_region = marco.assign(importe_neto=importes).groupby(COLUMNA_REGION, as_index=False)["importe_neto"].sum()
    resumen = {
        "transacciones": int(marco.shape[0]),
        "importe_neto": float(importes.sum()),
        "importe_promedio": float(importes.mean()),
        "alcance": cobertura["alcance"],
        "nota": "Indicadores de esta extraccion, no de las 50000 ventas.",
    }
    destino = carpeta("gold", run_id)
    escribir(destino / "por_categoria.csv", por_categoria.to_csv(index=False))
    escribir(destino / "por_region.csv", por_region.to_csv(index=False))
    escribir(destino / "resumen.json", json.dumps(resumen, ensure_ascii=False))
    return run_id


def exportar_reporte(**contexto):
    run_id = _id(contexto, "generar_gold")
    resumen = json.loads((carpeta("gold", run_id) / "resumen.json").read_text(encoding="utf-8"))
    destino = carpeta("reports", run_id)
    escribir(destino / "resumen.json", json.dumps(resumen, ensure_ascii=False))
    escribir(
        destino / "manifiesto.json",
        json.dumps({"run_id": run_id, "alcance": resumen["alcance"], "filas": resumen["transacciones"], "cadena": CADENA}, ensure_ascii=False),
    )
    return run_id


if DAG is not None:
    with DAG(
        dag_id="estudia_clase05_api_medallion",
        description="Practica: de la API a bronze, silver y gold. Nace en pausa.",
        start_date=datetime(2026, 11, 26),
        schedule=None,
        catchup=False,
        max_active_runs=1,
        is_paused_upon_creation=True,
        default_args={"retries": 1, "retry_delay": timedelta(seconds=30)},
        tags=["clase05", "practica"],
    ) as dag:
        extraer = PythonOperator(task_id="extraer_api", python_callable=extraer_api)
        bronze = PythonOperator(task_id="guardar_bronze", python_callable=guardar_bronze)
        silver = PythonOperator(task_id="transformar_silver", python_callable=transformar_silver)
        revision = PythonOperator(task_id="validar_datos", python_callable=validar_datos)
        gold = PythonOperator(task_id="generar_gold", python_callable=generar_gold)
        reporte = PythonOperator(task_id="exportar_reporte", python_callable=exportar_reporte)
        extraer >> bronze >> silver >> revision >> gold >> reporte
