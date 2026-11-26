"""Pipeline Medallion de la clase 05.

No importa Airflow. No imprime contraseñas ni tokens.
Las ventas de /ventas llegan planas. La muestra anidada no se mezcla aquí.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

COLUMNAS = ["id_transaccion", "fecha", "cantidad", "importe_neto", "categoria", "region"]
CADENA = "extraer_api>guardar_bronze>transformar_silver>validar_datos>generar_gold>exportar_reporte"


def base_de(host: str, esquema: str | None = None) -> str:
    texto = (host or "").strip().rstrip("/")
    if texto.startswith("http://") or texto.startswith("https://"):
        return texto
    protocolo = esquema if esquema in {"http", "https"} else "https"
    return f"{protocolo}://{texto}"


def sanear(run_id: str) -> str:
    limpio = "".join(caracter if caracter.isalnum() or caracter in "-_" else "_" for caracter in str(run_id))
    return (limpio or "ejecucion")[:80]


def raiz_datos() -> Path:
    if os.environ.get("ESTUDIA_DATA"):
        return Path(os.environ["ESTUDIA_DATA"])
    if Path("/opt/airflow").exists():
        return Path("/opt/airflow/data")
    return Path(__file__).resolve().parents[1] / "data"


def carpeta(capa: str, run_id: str) -> Path:
    return raiz_datos() / capa / sanear(run_id)


def escribir(ruta: Path, texto: str) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_suffix(ruta.suffix + ".tmp")
    temporal.write_text(texto, encoding="utf-8")
    os.replace(temporal, ruta)


def login(base: str, usuario: str, password: str) -> str:
    respuesta = requests.post(
        f"{base}/api/v4/auth/login",
        json={"username": usuario, "password": password},
        timeout=20,
    )
    if respuesta.status_code != 200:
        raise RuntimeError(f"El login respondio {respuesta.status_code}.")
    token = respuesta.json().get("access_token")
    if not isinstance(token, str) or not token:
        raise RuntimeError("El login no devolvio access_token.")
    return token


def pedir(base: str, token: str, ruta: str, params: dict | None = None) -> dict:
    respuesta = requests.get(
        f"{base}{ruta}",
        headers={"Authorization": "Bearer " + token, "Accept": "application/json"},
        params=params,
        timeout=60,
    )
    if respuesta.status_code != 200:
        raise RuntimeError(f"GET {ruta} respondio {respuesta.status_code}.")
    return respuesta.json()


def extraer_ventas(base: str, token: str, region: str = "Aragón", page_size: int = 100, paginas: int = 2) -> dict:
    guardadas = []
    total_records = None
    total_pages = None
    for numero in range(1, paginas + 1):
        params = {
            "region": region,
            "page": numero,
            "page_size": page_size,
            "orden": "id_transaccion",
            "direccion": "asc",
        }
        cuerpo = pedir(base, token, "/api/v4/ventas", params)
        meta = cuerpo["pagination"]
        total_records = meta["total_records"]
        total_pages = meta["total_pages"]
        guardadas.append(
            {
                "numero": numero,
                "params": {clave: valor for clave, valor in params.items()},
                "cuerpo": cuerpo,
                "filas": len(cuerpo["data"]),
                "has_next": bool(meta["has_next"]),
            }
        )
        if not meta["has_next"]:
            break
    filas = sum(pagina["filas"] for pagina in guardadas)
    alcance = "completo" if total_records is not None and filas == total_records else "parcial"
    return {
        "paginas": guardadas,
        "cobertura": {
            "extraido_en": datetime.now(timezone.utc).isoformat(),
            "filtros": {"region": region, "orden": "id_transaccion", "direccion": "asc"},
            "page_size": page_size,
            "paginas": [
                {"page": pagina["numero"], "filas": pagina["filas"], "has_next": pagina["has_next"]}
                for pagina in guardadas
            ],
            "filas": filas,
            "total_records": total_records,
            "total_pages": total_pages,
            "alcance": alcance,
            "fuente": "api",
            "nota": "Los indicadores de esta corrida describen la extraccion, no las 50000 ventas.",
        },
    }


def guardar_staging(run_id: str, extraccion: dict) -> str:
    destino = carpeta("staging", run_id) / "extraccion.json"
    escribir(destino, json.dumps(extraccion, ensure_ascii=False))
    return sanear(run_id)


def guardar_bronze(run_id: str) -> str:
    origen = carpeta("staging", run_id) / "extraccion.json"
    destino = carpeta("bronze", run_id)
    if not origen.exists():
        if (destino / "cobertura.json").exists():
            return sanear(run_id)
        raise RuntimeError("No esta el staging ni el bronze de esta ejecucion.")
    texto = origen.read_text(encoding="utf-8")
    if "access_token" in texto:
        raise RuntimeError("Bronze no puede guardar un token.")
    extraccion = json.loads(texto)
    destino = carpeta("bronze", run_id)
    for pagina in extraccion["paginas"]:
        escribir(destino / f"pagina_{pagina['numero']}.json", json.dumps(pagina["cuerpo"], ensure_ascii=False))
    escribir(destino / "cobertura.json", json.dumps(extraccion["cobertura"], ensure_ascii=False))
    origen.unlink(missing_ok=True)
    return sanear(run_id)


def transformar_silver(run_id: str) -> str:
    bronze = carpeta("bronze", run_id)
    marcos = []
    for ruta in sorted(bronze.glob("pagina_*.json")):
        cuerpo = json.loads(ruta.read_text(encoding="utf-8"))
        marcos.append(pd.DataFrame(cuerpo["data"]))
    marco = pd.concat(marcos, ignore_index=True) if marcos else pd.DataFrame(columns=COLUMNAS)
    faltan = [columna for columna in COLUMNAS if columna not in marco.columns]
    if faltan:
        raise RuntimeError("Faltan columnas planas: " + ", ".join(faltan))
    marco = marco[COLUMNAS].copy()
    marco["fecha"] = pd.to_datetime(marco["fecha"], errors="coerce")
    marco["cantidad"] = pd.to_numeric(marco["cantidad"], errors="coerce")
    marco["importe_neto"] = pd.to_numeric(marco["importe_neto"], errors="coerce")
    marco["id_transaccion"] = pd.to_numeric(marco["id_transaccion"], errors="coerce")
    destino = carpeta("silver", run_id) / "ventas.csv"
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_suffix(".csv.tmp")
    marco.to_csv(temporal, index=False)
    os.replace(temporal, destino)
    return sanear(run_id)


def validar_marco(marco: pd.DataFrame, cobertura: dict) -> dict:
    faltan = [columna for columna in COLUMNAS if columna not in marco.columns]
    if faltan:
        raise RuntimeError("Faltan columnas obligatorias: " + ", ".join(faltan))
    if marco["id_transaccion"].isna().any():
        raise RuntimeError("Hay id_transaccion nulo. No se rellena ni se borra la fila.")
    if marco["id_transaccion"].duplicated().any():
        raise RuntimeError("Hay identificadores duplicados. No se eliminan automaticamente.")
    if pd.to_datetime(marco["fecha"], errors="coerce").isna().any():
        raise RuntimeError("Hay fechas que no se pudieron leer.")
    if int(marco.shape[0]) != int(cobertura["filas"]):
        raise RuntimeError("Silver no tiene las mismas filas que la cobertura de bronze.")
    if cobertura.get("alcance") not in {"parcial", "completo"}:
        raise RuntimeError("La cobertura no declara si la extraccion es parcial o completa.")
    return {"filas": int(marco.shape[0]), "alcance": cobertura["alcance"], "duplicados": 0}


def validar_datos(run_id: str) -> str:
    marco = pd.read_csv(carpeta("silver", run_id) / "ventas.csv")
    cobertura = json.loads((carpeta("bronze", run_id) / "cobertura.json").read_text(encoding="utf-8"))
    validar_marco(marco, cobertura)
    return sanear(run_id)


def generar_gold(run_id: str) -> str:
    marco = pd.read_csv(carpeta("silver", run_id) / "ventas.csv")
    cobertura = json.loads((carpeta("bronze", run_id) / "cobertura.json").read_text(encoding="utf-8"))
    importes = pd.to_numeric(marco["importe_neto"], errors="coerce")
    por_categoria = marco.assign(importe_neto=importes).groupby("categoria", as_index=False)["importe_neto"].sum()
    por_region = marco.assign(importe_neto=importes).groupby("region", as_index=False)["importe_neto"].sum()
    resumen = {
        "transacciones": int(marco.shape[0]),
        "importe_neto": float(importes.sum()) if len(marco) else 0.0,
        "importe_promedio": float(importes.mean()) if len(marco) else None,
        "alcance": cobertura["alcance"],
        "total_records_filtro": cobertura.get("total_records"),
        "nota": "Estos numeros describen la extraccion de esta corrida, no las 50000 ventas.",
    }
    destino = carpeta("gold", run_id)
    escribir(destino / "por_categoria.csv", por_categoria.to_csv(index=False))
    escribir(destino / "por_region.csv", por_region.to_csv(index=False))
    escribir(destino / "resumen.json", json.dumps(resumen, ensure_ascii=False))
    return sanear(run_id)


def exportar_reporte(run_id: str) -> str:
    gold = carpeta("gold", run_id)
    resumen = json.loads((gold / "resumen.json").read_text(encoding="utf-8"))
    cobertura = json.loads((carpeta("bronze", run_id) / "cobertura.json").read_text(encoding="utf-8"))
    manifiesto = {
        "dag": "estudia_clase05_api_medallion",
        "run_id": sanear(run_id),
        "fuente": cobertura.get("fuente", "api"),
        "alcance": resumen["alcance"],
        "filas": resumen["transacciones"],
        "total_records_filtro": resumen["total_records_filtro"],
        "cadena": CADENA,
        "nota": resumen["nota"],
    }
    destino = carpeta("reports", run_id)
    escribir(destino / "manifiesto.json", json.dumps(manifiesto, ensure_ascii=False))
    escribir(destino / "por_categoria.csv", (gold / "por_categoria.csv").read_text(encoding="utf-8"))
    escribir(destino / "resumen.json", json.dumps(resumen, ensure_ascii=False))
    return sanear(run_id)


def correr(paso: str, run_id: str, base: str | None = None, usuario: str | None = None, password: str | None = None) -> str:
    if paso == "extraer_api":
        token = login(base or "", usuario or "", password or "")
        try:
            extraccion = extraer_ventas(base or "", token)
            return guardar_staging(run_id, extraccion)
        finally:
            del token
    if paso == "guardar_bronze":
        return guardar_bronze(run_id)
    if paso == "transformar_silver":
        return transformar_silver(run_id)
    if paso == "validar_datos":
        return validar_datos(run_id)
    if paso == "generar_gold":
        return generar_gold(run_id)
    if paso == "exportar_reporte":
        return exportar_reporte(run_id)
    raise RuntimeError("Paso desconocido.")
