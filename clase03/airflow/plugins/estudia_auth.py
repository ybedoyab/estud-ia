"""Login de Airflow con la cuenta de PostgreSQL. Cada estudiante solo ve su DAG."""

from __future__ import annotations

import os
import re

from fastapi import HTTPException

from airflow.api_fastapi.app import get_auth_manager
from airflow.api_fastapi.auth.managers.simple.services.login import SimpleAuthManagerLogin
from airflow.api_fastapi.auth.managers.simple.simple_auth_manager import SimpleAuthManager
from airflow.api_fastapi.auth.managers.simple.user import SimpleAuthManagerUser
from airflow.configuration import conf

USUARIO = re.compile(r"^estudiante(?:0[1-9]|[1-9][0-9])$")
_ORIGINAL = SimpleAuthManagerLogin.create_token
_FALLOS: dict[str, int] = {}


def _postgres_ok(usuario: str, contrasena: str) -> bool:
    try:
        import psycopg

        with psycopg.connect(
            host=os.environ["ESTUDIA_PGHOST"],
            port=int(os.environ.get("ESTUDIA_PGPORT", "6432")),
            dbname=os.environ.get("ESTUDIA_PGDATABASE", "retail_dwh"),
            user=usuario,
            password=contrasena,
            sslmode="require",
            connect_timeout=8,
            autocommit=True,
        ) as conn:
            actual = conn.execute("SELECT current_user").fetchone()[0]
        return actual == usuario
    except Exception:
        return False


def _create_token(body, expiration_time_in_seconds=None):
    if expiration_time_in_seconds is None:
        expiration_time_in_seconds = conf.getint("api_auth", "jwt_expiration_time")
    try:
        token = _ORIGINAL(body, expiration_time_in_seconds=expiration_time_in_seconds)
        _FALLOS.pop(getattr(body, "username", ""), None)
        return token
    except HTTPException as exc:
        if exc.status_code != 401:
            raise
    usuario = str(getattr(body, "username", "") or "").strip()
    if _FALLOS.get(usuario, 0) >= 8:
        raise HTTPException(status_code=429, detail="Invalid credentials")
    if not USUARIO.fullmatch(usuario) or not _postgres_ok(usuario, str(getattr(body, "password", "") or "")):
        _FALLOS[usuario] = _FALLOS.get(usuario, 0) + 1
        raise HTTPException(status_code=401, detail="Invalid credentials")
    _FALLOS.pop(usuario, None)
    estudiante = SimpleAuthManagerUser(username=usuario, role="viewer")
    return get_auth_manager().generate_jwt(
        user=estudiante,
        expiration_time_in_seconds=expiration_time_in_seconds,
    )


SimpleAuthManagerLogin.create_token = _create_token


class EstudiaAuthManager(SimpleAuthManager):
    """El docente conserva el acceso completo. Un estudiante solo lee y dispara su DAG."""

    def is_authorized_dag(self, *, method, user, access_entity=None, details=None):
        if self._is_admin(user):
            return super().is_authorized_dag(
                method=method, user=user, access_entity=access_entity, details=details
            )
        if method == "GET" and (details is None or not getattr(details, "id", None)):
            return True
        propio = f"estudia_{user.username}_pipeline"
        if not details or details.id != propio:
            return False
        return method in {"GET", "POST"}

    def filter_authorized_dag_ids(self, *, dag_ids, user, method="GET", team_name=None):
        if self._is_admin(user):
            return super().filter_authorized_dag_ids(
                dag_ids=dag_ids, user=user, method=method, team_name=team_name
            )
        propio = f"estudia_{user.username}_pipeline"
        if method in {"GET", "POST"} and propio in dag_ids:
            return {propio}
        return set()

    def is_authorized_configuration(self, *, method, user, details=None):
        if self._is_admin(user):
            return super().is_authorized_configuration(method=method, user=user, details=details)
        return False
