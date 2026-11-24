"""Autenticación. La contraseña de PostgreSQL solo se usa para comprobar el login y no se guarda."""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timedelta, timezone

import jwt
import psycopg
from fastapi import HTTPException, Request

from app.config import ajustes

EMISOR = "estudia-clase04"
AUDIENCIA = "estudia-clase04"
ALCANCE = "retail:read"
ALGORITMO = "HS256"
INDIVIDUAL = re.compile(r"^estudiante(?:0[1-9]|[1-9][0-9])$")


def usuario_permitido(usuario: str) -> bool:
    return usuario == "estudiante" or bool(INDIVIDUAL.fullmatch(usuario))


def autenticar_postgres(usuario: str, contrasena: str) -> None:
    cfg = ajustes()
    try:
        with psycopg.connect(
            host=cfg.pghost,
            port=cfg.pgport,
            dbname=cfg.pgdatabase,
            user=usuario,
            password=contrasena,
            sslmode="require",
            connect_timeout=8,
            autocommit=True,
            prepare_threshold=None,
        ) as conn:
            actual = conn.execute("SELECT current_user").fetchone()[0]
    except Exception:
        raise HTTPException(status_code=401, detail="Usuario o contrasena incorrectos.") from None
    if actual != usuario:
        raise HTTPException(status_code=401, detail="Usuario o contrasena incorrectos.")


def emitir_token(usuario: str) -> tuple[str, str, int]:
    cfg = ajustes()
    if not cfg.jwt_secret:
        raise HTTPException(status_code=500, detail="Error interno.")
    ahora = datetime.now(timezone.utc)
    segundos = cfg.jwt_horas * 3600
    sesion = str(uuid.uuid4())
    token = jwt.encode(
        {
            "iss": EMISOR,
            "aud": AUDIENCIA,
            "sub": usuario,
            "scope": ALCANCE,
            "jti": sesion,
            "iat": int(ahora.timestamp()),
            "exp": ahora + timedelta(seconds=segundos),
        },
        cfg.jwt_secret,
        algorithm=ALGORITMO,
    )
    return token, sesion, segundos


def leer_token(request: Request) -> dict:
    cabecera = request.headers.get("authorization", "")
    if not cabecera.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Falta el token de sesion.")
    cfg = ajustes()
    try:
        datos = jwt.decode(
            cabecera[7:].strip(),
            cfg.jwt_secret,
            algorithms=[ALGORITMO],
            audience=AUDIENCIA,
            issuer=EMISOR,
            options={"require": ["exp", "iat", "sub", "jti", "scope", "iss", "aud"]},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token expiro. Vuelve a iniciar sesion.") from None
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="El token no es valido.") from None
    usuario = str(datos.get("sub") or "")
    if datos.get("scope") != ALCANCE or not usuario_permitido(usuario):
        raise HTTPException(status_code=403, detail="El token no autoriza esta accion.")
    if not datos.get("jti"):
        raise HTTPException(status_code=401, detail="El token no es valido.")
    return datos
