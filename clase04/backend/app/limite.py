"""Límites en memoria. El cupo de datos va por sesión, no por el usuario compartido."""

from collections import defaultdict, deque
from time import monotonic

from fastapi import HTTPException

_marcas: dict[str, deque[float]] = defaultdict(deque)


def limitar(clave: str, maximo: int, segundos: int, reintento: int = 5) -> None:
    ahora = monotonic()
    ventana = _marcas[clave]
    while ventana and ahora - ventana[0] > segundos:
        ventana.popleft()
    if len(ventana) >= maximo:
        raise HTTPException(
            status_code=429,
            detail="Demasiadas solicitudes. Espera un momento.",
            headers={"Retry-After": str(reintento)},
        )
    ventana.append(ahora)


def reiniciar() -> None:
    _marcas.clear()
