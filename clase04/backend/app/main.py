"""API educativa de la clase 04. Solo lectura sobre retail_dwh y un sandbox por sesión."""

from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from psycopg_pool import PoolTimeout

from app.bitacora import bitacora
from app.config import ajustes
from app.db import abrir_pool, cerrar_pool
from app.repositorio import ping
from app.routers import auth, datos, ejemplos, sandbox

PREFIJO_ID = __import__("re").compile(r"^[A-Za-z0-9-]{8,64}$")


@asynccontextmanager
async def vida(app: FastAPI):
    if not ajustes().skip_db:
        abrir_pool()
    yield
    if not ajustes().skip_db:
        cerrar_pool()


app = FastAPI(
    title="EstudIA clase 04",
    summary="API de solo lectura para practicar REST, Postman y extraccion de datos.",
    version="1.0.0",
    openapi_url="/api/v4/openapi.json",
    docs_url="/api/v4/docs",
    redoc_url=None,
    lifespan=vida,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://colab.research.google.com", "https://colab.google.com"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)
app.include_router(auth.router)
app.include_router(datos.router)
app.include_router(sandbox.router)
app.include_router(ejemplos.router)

RUTAS_SIN_TOKEN = {"/api/v4/health", "/api/v4/auth/login"}


def esquema_openapi():
    """Documenta el Bearer en Swagger. No cambia quién puede llamar la API."""
    if app.openapi_schema:
        return app.openapi_schema
    from fastapi.openapi.utils import get_openapi

    esquema = get_openapi(
        title=app.title,
        version=app.version,
        summary=app.summary,
        routes=app.routes,
    )
    esquemas = esquema.setdefault("components", {}).setdefault("securitySchemes", {})
    esquemas["HTTPBearer"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Pega el access_token de POST /api/v4/auth/login. No lo compartas.",
    }
    for ruta, operaciones in esquema.get("paths", {}).items():
        if ruta in RUTAS_SIN_TOKEN:
            continue
        for metodo, operacion in operaciones.items():
            if metodo in {"get", "post", "put", "patch", "delete"}:
                operacion["security"] = [{"HTTPBearer": []}]
    app.openapi_schema = esquema
    return esquema


app.openapi = esquema_openapi


@app.middleware("http")
async def solicitud(request: Request, call_next):
    largo = request.headers.get("content-length")
    if largo and largo.isdigit() and int(largo) > 16384:
        return JSONResponse(status_code=400, content={"detail": "El cuerpo de la peticion es demasiado grande."})
    recibido = request.headers.get("x-request-id", "")
    request_id = recibido if PREFIJO_ID.fullmatch(recibido) else uuid4().hex
    try:
        respuesta = await call_next(request)
    except PoolTimeout:
        bitacora.warning("servicio_ocupado", extra={"datos": {"request_id": request_id}})
        respuesta = JSONResponse(status_code=503, content={"detail": "Servicio temporalmente no disponible."})
    respuesta.headers["X-Request-ID"] = request_id
    bitacora.info(
        "solicitud",
        extra={
            "datos": {
                "request_id": request_id,
                "metodo": request.method,
                "ruta": request.url.path,
                "estado": respuesta.status_code,
            }
        },
    )
    return respuesta


@app.exception_handler(RequestValidationError)
async def validacion(_request: Request, _exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": "La peticion no cumple el formato esperado."})


@app.exception_handler(PoolTimeout)
async def ocupado(request: Request, _exc: PoolTimeout):
    bitacora.warning("servicio_ocupado", extra={"datos": {"ruta": request.url.path}})
    return JSONResponse(
        status_code=503,
        content={"detail": "Servicio temporalmente no disponible."},
    )


@app.exception_handler(Exception)
async def interno(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers,
        )
    bitacora.error(
        "error_interno",
        extra={"datos": {"tipo": type(exc).__name__, "ruta": request.url.path}},
    )
    return JSONResponse(status_code=500, content={"detail": "Error interno."})


@app.get("/api/v4/health", tags=["Salud"])
def salud():
    if ajustes().skip_db:
        return {"ok": True, "servicio": "estudia-clase04"}
    try:
        if not ping():
            raise RuntimeError("ping")
    except Exception:
        bitacora.warning("salud_degradada", extra={"datos": {"tipo": "db"}})
        return JSONResponse(status_code=503, content={"ok": False, "servicio": "estudia-clase04"})
    return {"ok": True, "servicio": "estudia-clase04"}
