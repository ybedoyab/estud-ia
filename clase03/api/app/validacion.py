"""Validacion declarativa. No ejecuta SQL ni codigo del estudiante."""

from __future__ import annotations

import re

USUARIO = re.compile(r"^estudiante(?:0[1-9]|[1-9][0-9])$")
TAREA_ID = re.compile(r"^[a-z][a-z0-9_]{0,30}$")
INTERVALOS = {5, 10, 15}
TIPOS = {"sql", "validacion", "transformacion", "agrupacion", "reporte_csv"}
TRANSFORMACIONES = {"quitar_nulos", "rellenar_ceros"}
METRICAS = {"sum", "mean", "count", "min", "max"}
COLUMNAS = {
    "categoria",
    "region",
    "canal",
    "metodo_pago",
    "segmento",
    "marca",
    "ciudad",
    "tipo",
    "anio",
    "nombre_mes",
    "trimestre",
    "importe_neto",
    "cantidad",
    "margen",
    "precio_unitario",
    "transacciones",
}
PROHIBIDAS = re.compile(
    r"\b(insert|update|delete|drop|alter|create|grant|revoke|copy|truncate|"
    r"vacuum|comment|do|call|execute|prepare|listen|notify|set|reset|show|"
    r"into|outfile|pg_sleep|pg_read_file|lo_import|dblink)\b",
    re.IGNORECASE,
)
MAX_TAREAS = 5
MAX_SQL = 4000


class EntregaInvalida(ValueError):
    pass


def usuario_permitido(usuario: str) -> bool:
    return bool(USUARIO.fullmatch(usuario or ""))


def _sin_comentarios(sql: str) -> str:
    sin_bloque = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    return re.sub(r"--[^\n]*", " ", sin_bloque)


def sql_es_segura(sql: str) -> str:
    if not isinstance(sql, str) or not sql.strip():
        raise EntregaInvalida("La consulta SQL esta vacia.")
    if len(sql) > MAX_SQL:
        raise EntregaInvalida("La consulta supera el limite de 4000 caracteres.")
    limpio = _sin_comentarios(sql).strip()
    if limpio.endswith(";"):
        limpio = limpio[:-1].strip()
    if ";" in limpio:
        raise EntregaInvalida("Solo se permite una sentencia SQL.")
    if not re.match(r"^(select|with)\b", limpio, re.IGNORECASE):
        raise EntregaInvalida("La consulta debe empezar por SELECT o WITH.")
    if PROHIBIDAS.search(limpio):
        raise EntregaInvalida("La consulta contiene una operacion que no es de lectura.")
    if re.search(r"\b(pg_catalog|information_schema|pgbouncer|public)\b", limpio, re.IGNORECASE):
        raise EntregaInvalida("La consulta solo puede usar el esquema curso.")
    if "curso." not in limpio.lower():
        raise EntregaInvalida("La consulta debe leer una vista de curso, por ejemplo curso.ventas.")
    return limpio


def validar_pipeline(datos: dict) -> dict:
    if not isinstance(datos, dict):
        raise EntregaInvalida("El pipeline debe ser un objeto.")
    nombre = str(datos.get("nombre") or "").strip()
    if not nombre or len(nombre) > 80:
        raise EntregaInvalida("El nombre del pipeline debe tener entre 1 y 80 caracteres.")
    try:
        intervalo = int(datos.get("intervalo_minutos", 10))
    except (TypeError, ValueError) as exc:
        raise EntregaInvalida("El intervalo debe ser 5, 10 o 15 minutos.") from exc
    if intervalo not in INTERVALOS:
        raise EntregaInvalida("El intervalo debe ser 5, 10 o 15 minutos.")
    tareas = datos.get("tareas")
    if not isinstance(tareas, list) or not 3 <= len(tareas) <= MAX_TAREAS:
        raise EntregaInvalida("El pipeline debe tener entre 3 y 5 tareas.")
    vistos = set()
    normalizadas = []
    for cruda in tareas:
        if not isinstance(cruda, dict):
            raise EntregaInvalida("Cada tarea debe ser un objeto.")
        tarea_id = str(cruda.get("id") or "")
        tipo = str(cruda.get("tipo") or "")
        if not TAREA_ID.fullmatch(tarea_id):
            raise EntregaInvalida(f"Identificador de tarea no permitido: {tarea_id!r}.")
        if tarea_id in vistos:
            raise EntregaInvalida(f"La tarea {tarea_id} esta repetida.")
        if tipo not in TIPOS:
            raise EntregaInvalida(f"Tipo de tarea no permitido: {tipo}.")
        vistos.add(tarea_id)
        depende = cruda.get("depende_de") or []
        if not isinstance(depende, list) or any(not isinstance(item, str) for item in depende):
            raise EntregaInvalida(f"Las dependencias de {tarea_id} deben ser una lista de nombres.")
        tarea = {"id": tarea_id, "tipo": tipo, "depende_de": depende}
        if tipo == "sql":
            tarea["consulta"] = sql_es_segura(str(cruda.get("consulta") or ""))
        elif tipo == "transformacion":
            operacion = str(cruda.get("operacion") or "quitar_nulos")
            if operacion not in TRANSFORMACIONES:
                raise EntregaInvalida("La transformacion debe ser quitar_nulos o rellenar_ceros.")
            tarea["operacion"] = operacion
        elif tipo == "agrupacion":
            columnas = cruda.get("columnas") or []
            metrica = str(cruda.get("metrica") or "")
            campo = str(cruda.get("campo") or "")
            if not isinstance(columnas, list) or not columnas:
                raise EntregaInvalida("La agrupacion necesita al menos una columna.")
            if any(columna not in COLUMNAS for columna in columnas):
                raise EntregaInvalida("Hay una columna de agrupacion que no esta permitida.")
            if metrica not in METRICAS or campo not in COLUMNAS:
                raise EntregaInvalida("La metrica o el campo de la agrupacion no estan permitidos.")
            tarea["columnas"] = columnas
            tarea["metrica"] = metrica
            tarea["campo"] = campo
        normalizadas.append(tarea)
    if not any(tarea["tipo"] == "sql" for tarea in normalizadas):
        raise EntregaInvalida("El pipeline necesita una tarea SQL.")
    if not any(tarea["tipo"] == "reporte_csv" for tarea in normalizadas):
        raise EntregaInvalida("El pipeline necesita una tarea reporte_csv.")
    for tarea in normalizadas:
        for origen in tarea["depende_de"]:
            if origen not in vistos:
                raise EntregaInvalida(f"{tarea['id']} depende de {origen}, que no existe.")
            if origen == tarea["id"]:
                raise EntregaInvalida(f"{tarea['id']} no puede depender de si misma.")
    _sin_ciclos(normalizadas)
    return {"nombre": nombre, "intervalo_minutos": intervalo, "tareas": normalizadas}


def _sin_ciclos(tareas: list[dict]) -> None:
    grafo = {tarea["id"]: tarea["depende_de"] for tarea in tareas}
    estado = {}

    def visitar(nodo: str) -> None:
        estado[nodo] = "gris"
        for origen in grafo[nodo]:
            if estado.get(origen) == "gris":
                raise EntregaInvalida("Las dependencias forman un ciclo.")
            if origen not in estado:
                visitar(origen)
        estado[nodo] = "negro"

    for nodo in grafo:
        if nodo not in estado:
            visitar(nodo)


def orden_tareas(tareas: list[dict]) -> list[str]:
    pendientes = {tarea["id"]: set(tarea["depende_de"]) for tarea in tareas}
    orden = []
    while pendientes:
        listas = [nodo for nodo, deps in pendientes.items() if not deps]
        if not listas:
            raise EntregaInvalida("Las dependencias forman un ciclo.")
        nodo = sorted(listas)[0]
        orden.append(nodo)
        pendientes.pop(nodo)
        for deps in pendientes.values():
            deps.discard(nodo)
    return orden


def dag_id(usuario: str) -> str:
    if not usuario_permitido(usuario):
        raise EntregaInvalida("El usuario no puede publicar un pipeline individual.")
    return f"estudia_{usuario}_pipeline"
