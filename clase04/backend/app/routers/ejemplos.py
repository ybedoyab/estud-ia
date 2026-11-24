"""Respuestas fijas para practicar errores sin saturar la base."""

from fastapi import APIRouter, HTTPException, Request

from app.seguridad import leer_token

router = APIRouter(prefix="/api/v4/ejemplos", tags=["Ejemplos de error"])


@router.get("/demasiado-rapido")
def demasiado_rapido(request: Request):
    leer_token(request)
    raise HTTPException(
        status_code=429,
        detail="Ejemplo controlado de limite. No hace falta repetir la llamada.",
        headers={"Retry-After": "2"},
    )


@router.get("/error-interno")
def error_interno(request: Request):
    leer_token(request)
    raise HTTPException(status_code=500, detail="Ejemplo controlado de error interno.")


@router.get("/no-disponible")
def no_disponible(request: Request):
    leer_token(request)
    raise HTTPException(status_code=503, detail="Ejemplo controlado: servicio no disponible.")


@router.get("/prohibido")
def prohibido(request: Request):
    leer_token(request)
    raise HTTPException(
        status_code=403,
        detail="Ejemplo controlado: la sesion tiene alcance retail:read y esta accion no esta permitida.",
    )
