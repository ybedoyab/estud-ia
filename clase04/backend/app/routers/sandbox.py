"""CRUD ficticio. Los objetos viven solo en la sesión del token."""

from fastapi import APIRouter, HTTPException, Request, Response

from app.esquemas import TareaBody, TareaPatch
from app.limite import limitar
from app.sandbox import actualizar, crear, eliminar, listar, obtener, reemplazar
from app.seguridad import leer_token

router = APIRouter(prefix="/api/v4/sandbox/tareas", tags=["Sandbox"])


def _contexto(request: Request) -> tuple[str, float]:
    datos = leer_token(request)
    limitar(f"sandbox:{datos['jti']}", 60, 60, reintento=5)
    return str(datos["jti"]), float(datos["exp"])


@router.get("")
def lista(request: Request):
    sesion, expira = _contexto(request)
    return {"data": listar(sesion, expira)}


@router.post("", status_code=201)
def alta(body: TareaBody, request: Request):
    sesion, expira = _contexto(request)
    return crear(sesion, expira, body.model_dump())


@router.get("/{id_tarea}")
def una(id_tarea: str, request: Request):
    sesion, expira = _contexto(request)
    return obtener(sesion, expira, id_tarea)


@router.put("/{id_tarea}")
def reemplazo(id_tarea: str, body: TareaBody, request: Request):
    sesion, expira = _contexto(request)
    return reemplazar(sesion, expira, id_tarea, body.model_dump())


@router.patch("/{id_tarea}")
def parcial(id_tarea: str, body: TareaPatch, request: Request):
    cambios = body.model_dump(exclude_unset=True)
    if not cambios:
        raise HTTPException(status_code=400, detail="El PATCH no incluye ningun campo.")
    sesion, expira = _contexto(request)
    return actualizar(sesion, expira, id_tarea, cambios)


@router.delete("/{id_tarea}", status_code=204)
def baja(id_tarea: str, request: Request):
    sesion, expira = _contexto(request)
    eliminar(sesion, expira, id_tarea)
    return Response(status_code=204)
