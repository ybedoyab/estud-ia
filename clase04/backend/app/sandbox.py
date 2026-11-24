"""Sandbox de tareas ficticias, aislado por jti. Un solo proceso de Uvicorn."""

from threading import Lock
from time import time
from uuid import uuid4

from fastapi import HTTPException

MAX_TAREAS = 30
_datos: dict[str, dict] = {}
_candado = Lock()


def _limpiar(ahora: float) -> None:
    vencidas = [sesion for sesion, bolsa in _datos.items() if bolsa["expira"] <= ahora]
    for sesion in vencidas:
        _datos.pop(sesion, None)


def _bolsa(sesion: str, expira: float) -> dict:
    ahora = time()
    _limpiar(ahora)
    bolsa = _datos.get(sesion)
    if bolsa is None or bolsa["expira"] <= ahora:
        bolsa = {"expira": expira, "tareas": {}}
        _datos[sesion] = bolsa
    return bolsa


def listar(sesion: str, expira: float) -> list[dict]:
    with _candado:
        return list(_bolsa(sesion, expira)["tareas"].values())


def crear(sesion: str, expira: float, campos: dict) -> dict:
    with _candado:
        bolsa = _bolsa(sesion, expira)
        if len(bolsa["tareas"]) >= MAX_TAREAS:
            raise HTTPException(status_code=400, detail="La sesion ya alcanzo el maximo de 30 tareas.")
        tarea = {"id_tarea": uuid4().hex[:12], **campos}
        bolsa["tareas"][tarea["id_tarea"]] = tarea
        return tarea


def obtener(sesion: str, expira: float, id_tarea: str) -> dict:
    with _candado:
        tarea = _bolsa(sesion, expira)["tareas"].get(id_tarea)
    if tarea is None:
        raise HTTPException(status_code=404, detail="La tarea no existe en esta sesion.")
    return tarea


def reemplazar(sesion: str, expira: float, id_tarea: str, campos: dict) -> dict:
    with _candado:
        bolsa = _bolsa(sesion, expira)
        if id_tarea not in bolsa["tareas"]:
            raise HTTPException(status_code=404, detail="La tarea no existe en esta sesion.")
        tarea = {"id_tarea": id_tarea, **campos}
        bolsa["tareas"][id_tarea] = tarea
        return tarea


def actualizar(sesion: str, expira: float, id_tarea: str, campos: dict) -> dict:
    with _candado:
        bolsa = _bolsa(sesion, expira)
        actual = bolsa["tareas"].get(id_tarea)
        if actual is None:
            raise HTTPException(status_code=404, detail="La tarea no existe en esta sesion.")
        actual.update(campos)
        return actual


def eliminar(sesion: str, expira: float, id_tarea: str) -> None:
    with _candado:
        bolsa = _bolsa(sesion, expira)
        if id_tarea not in bolsa["tareas"]:
            raise HTTPException(status_code=404, detail="La tarea no existe en esta sesion.")
        del bolsa["tareas"][id_tarea]


def reiniciar() -> None:
    with _candado:
        _datos.clear()
