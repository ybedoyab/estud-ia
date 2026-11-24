"""Esquemas de entrada. Las respuestas de lectura salen de las columnas reales."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class LoginBody(BaseModel):
    username: str = Field(min_length=1, max_length=32)
    password: str = Field(min_length=1, max_length=200)


class TareaBody(BaseModel):
    titulo: str = Field(min_length=1, max_length=80)
    detalle: str = Field(default="", max_length=280)
    estado: Literal["pendiente", "en_progreso", "hecha"] = "pendiente"
    prioridad: int = Field(default=3, ge=1, le=5)


class TareaPatch(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=80)
    detalle: str | None = Field(default=None, max_length=280)
    estado: Literal["pendiente", "en_progreso", "hecha"] | None = None
    prioridad: int | None = Field(default=None, ge=1, le=5)


FiltroOrden = Literal["id_transaccion", "fecha", "importe_neto", "cantidad"]
Direccion = Literal["asc", "desc"]
Granularidad = Literal["mes", "trimestre"]


def fechas_validas(desde: date | None, hasta: date | None) -> None:
    from fastapi import HTTPException

    if desde and hasta and desde > hasta:
        raise HTTPException(status_code=400, detail="fecha_desde no puede ser posterior a fecha_hasta.")
