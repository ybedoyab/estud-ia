"""Pipeline de practica. Permanece fuera de dags/ hasta activar_dags.

La escritura atomica y el saneo del run_id ya estan resueltos.
Completa la Connection, el HTTP, la paginacion, silver, la validacion,
gold, dos XCom y los seis operadores con inicio >> fin real.
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
    from airflow.hooks.base import BaseHook
    from airflow.providers.standard.operators.python import PythonOperator
except ImportError:
    DAG = None
    BaseHook = None
    PythonOperator = None


def sanear(run_id: str) -> str:
    limpio = "".join(caracter if caracter.isalnum() or caracter in "-_" else "_" for caracter in str(run_id))
    return (limpio or "ejecucion")[:80]


def raiz() -> Path:
    if os.environ.get("ESTUDIA_DATA"):
        return Path(os.environ["ESTUDIA_DATA"])
    if Path("/opt/airflow").exists():
        return Path("/opt/airflow/data")
    for padre in Path(__file__).resolve().parents:
        if (padre / "fixtures").is_dir():
            return padre / "data"
    return Path("data")


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


def tirar(contexto, tarea: str) -> str:
    return sanear(contexto["ti"].xcom_pull(task_ids=tarea))


def extraer_api(**contexto):
    run_id = sanear(contexto["run_id"])
    fixture = os.environ.get("ESTUDIA_FIXTURE")
    if fixture:
        escribir(carpeta("staging", run_id) / "extraccion.json", Path(fixture).read_text(encoding="utf-8"))
        return run_id
    conexion = BaseHook.get_connection("estudia_api")
    base = base_de(conexion.host, conexion.schema)
    respuesta_login = requests.post(
        f"{base}/api/v4/auth/login",
        json={"username": conexion.login, "password": conexion.password},
        timeout=20,
    )
    respuesta_login.raise_for_status()
    token = respuesta_login.json()["access_token"]
    try:
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        paginas = []
        for numero in range(1, 3):
            parametros = {
                "region": "Aragón",
                "page": numero,
                "page_size": 100,
                "orden": "id_transaccion",
                "direccion": "asc",
            }
            respuesta = requests.get(
                f"{base}/api/v4/ventas",
                headers=headers,
                params=parametros,
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
                "filtros": {"region": parametros["region"]},
                "page_size": parametros["page_size"],
                "filas": filas,
                "total_records": total,
                "alcance": "completo" if filas == total else "parcial",
                "fuente": "api",
                "nota": "Esta extraccion no es el censo de 50000 ventas.",
            },
        }
    finally:
        del token
    escribir(carpeta("staging", run_id) / "extraccion.json", json.dumps(extraccion, ensure_ascii=False))
    return run_id


def guardar_bronze(**contexto):
    run_id = tirar(contexto, "extraer_api")
    origen = carpeta("staging", run_id) / "extraccion.json"
    if not origen.exists() and (carpeta("bronze", run_id) / "cobertura.json").exists():
        return run_id
    extraccion = json.loads(origen.read_text(encoding="utf-8"))
    if "access_token" in origen.read_text(encoding="utf-8"):
        raise RuntimeError("Bronze no puede guardar el token.")
    destino = carpeta("bronze", run_id)
    for pagina in extraccion["paginas"]:
        escribir(destino / f"pagina_{pagina['numero']}.json", json.dumps(pagina["cuerpo"], ensure_ascii=False))
    escribir(destino / "cobertura.json", json.dumps(extraccion["cobertura"], ensure_ascii=False))
    origen.unlink(missing_ok=True)
    return run_id


def transformar_silver(**contexto):
    run_id = tirar(contexto, "guardar_bronze")
    marcos = []
    for ruta in sorted(carpeta("bronze", run_id).glob("pagina_*.json")):
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        marcos.append(pd.DataFrame(datos["data"]))
    df = pd.concat(marcos, ignore_index=True)
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["importe_neto"] = pd.to_numeric(df["importe_neto"], errors="coerce")
    df = df[["id_transaccion", "fecha", "cantidad", "importe_neto", "categoria", "region"]].copy()
    destino = carpeta("silver", run_id) / "ventas.csv"
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_suffix(".csv.tmp")
    df.to_csv(temporal, index=False)
    os.replace(temporal, destino)
    return run_id


def validar_datos(**contexto):
    run_id = tirar(contexto, "transformar_silver")
    df = pd.read_csv(carpeta("silver", run_id) / "ventas.csv")
    cobertura = json.loads((carpeta("bronze", run_id) / "cobertura.json").read_text(encoding="utf-8"))
    if df["id_transaccion"].isna().any():
        raise RuntimeError("Identificador nulo")
    if df["id_transaccion"].duplicated().any():
        raise RuntimeError("Identificador duplicado")
    if pd.to_datetime(df["fecha"], errors="coerce").isna().any():
        raise RuntimeError("Hay fechas invalidas.")
    if pd.to_numeric(df["importe_neto"], errors="coerce").isna().any():
        raise RuntimeError("Hay importes que no son numeros.")
    if int(df.shape[0]) != int(cobertura["filas"]):
        raise RuntimeError("El conteo no coincide con bronze.")
    return run_id


def generar_gold(**contexto):
    run_id = tirar(contexto, "validar_datos")
    df = pd.read_csv(carpeta("silver", run_id) / "ventas.csv")
    cobertura = json.loads((carpeta("bronze", run_id) / "cobertura.json").read_text(encoding="utf-8"))
    df["importe_neto"] = pd.to_numeric(df["importe_neto"], errors="coerce")
    por_categoria = df.groupby("categoria", as_index=False)["importe_neto"].sum()
    por_region = df.groupby("region", as_index=False)["importe_neto"].sum()
    resumen = {
        "transacciones": int(df.shape[0]),
        "importe_neto": float(df["importe_neto"].sum()),
        "importe_promedio": float(df["importe_neto"].mean()),
        "alcance": cobertura.get("alcance", "parcial"),
        "nota": "Indicadores de esta extraccion, no de las 50000 ventas.",
    }
    destino = carpeta("gold", run_id)
    escribir(destino / "por_categoria.csv", por_categoria.to_csv(index=False))
    escribir(destino / "por_region.csv", por_region.to_csv(index=False))
    escribir(destino / "resumen.json", json.dumps(resumen, ensure_ascii=False))
    return run_id


def exportar_reporte(**contexto):
    run_id = tirar(contexto, "generar_gold")
    resumen = json.loads((carpeta("gold", run_id) / "resumen.json").read_text(encoding="utf-8"))
    destino = carpeta("reports", run_id)
    escribir(destino / "resumen.json", json.dumps(resumen, ensure_ascii=False))
    escribir(
        destino / "manifiesto.json",
        json.dumps(
            {
                "dag": "estudia_clase05_api_medallion",
                "run_id": run_id,
                "alcance": resumen["alcance"],
                "filas": resumen["transacciones"],
                "nota": resumen["nota"],
            },
            ensure_ascii=False,
        ),
    )
    return run_id


if DAG is not None:
    with DAG(
        dag_id="estudia_clase05_api_medallion",
        start_date=datetime(2026, 11, 26),
        schedule=None,
        catchup=False,
        max_active_runs=1,
        is_paused_upon_creation=True,
        default_args={"retries": 1, "retry_delay": timedelta(seconds=20)},
        tags=["clase05", "practica"],
    ) as dag:
        t1 = PythonOperator(task_id="extraer_api", python_callable=extraer_api)
        t2 = PythonOperator(task_id="guardar_bronze", python_callable=guardar_bronze)
        t3 = PythonOperator(task_id="transformar_silver", python_callable=transformar_silver)
        t4 = PythonOperator(task_id="validar_datos", python_callable=validar_datos)
        t5 = PythonOperator(task_id="generar_gold", python_callable=generar_gold)
        t6 = PythonOperator(task_id="exportar_reporte", python_callable=exportar_reporte)
        t1 >> t2 >> t3 >> t4 >> t5 >> t6
