"""Rutas de sesión. El usuario compartido puede entrar; cada login crea su propio jti."""

from fastapi import APIRouter, HTTPException, Request

from app.bitacora import bitacora
from app.esquemas import LoginBody
from app.limite import limitar
from app.seguridad import autenticar_postgres, emitir_token, leer_token, usuario_permitido

router = APIRouter(prefix="/api/v4/auth", tags=["Autenticacion"])


def _ip(request: Request) -> str:
    reenviada = request.headers.get("x-forwarded-for", "")
    if reenviada:
        return reenviada.split(",")[0].strip()[:64]
    return request.client.host if request.client else "desconocida"


@router.post("/login")
def login(body: LoginBody, request: Request):
    ip = _ip(request)
    limitar(f"login:{ip}", 180, 60, reintento=10)
    usuario = body.username.strip()
    if not usuario_permitido(usuario):
        limitar(f"login-fallo:{ip}", 40, 600, reintento=60)
        bitacora.info("login_rechazado", extra={"datos": {"ip": ip}})
        raise HTTPException(status_code=401, detail="Usuario o contrasena incorrectos.")
    try:
        autenticar_postgres(usuario, body.password)
    except HTTPException:
        limitar(f"login-fallo:{ip}", 40, 600, reintento=60)
        bitacora.info("login_fallido", extra={"datos": {"usuario": usuario}})
        raise
    token, sesion, segundos = emitir_token(usuario)
    bitacora.info(
        "login_ok",
        extra={"datos": {"usuario": usuario, "sesion": sesion, "compartida": usuario == "estudiante"}},
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": segundos,
        "usuario": usuario,
        "scope": "retail:read",
    }


@router.get("/me")
def yo(request: Request):
    datos = leer_token(request)
    from datetime import datetime, timezone

    expira = int(datos["exp"])
    ahora = int(datetime.now(timezone.utc).timestamp())
    return {
        "usuario": datos["sub"],
        "scope": datos["scope"],
        "sesion": datos["jti"],
        "identidad": "compartida" if datos["sub"] == "estudiante" else "individual",
        "expira": datetime.fromtimestamp(expira, timezone.utc).isoformat(),
        "expires_in": max(0, expira - ahora),
    }
