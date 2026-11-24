"""Configuración de la API educativa. No contiene secretos."""

import os
from dataclasses import dataclass
from functools import lru_cache


def _flag(nombre: str) -> bool:
    return os.environ.get(nombre, "").strip().lower() in {"1", "true", "si", "yes"}


@dataclass(frozen=True)
class Ajustes:
    pghost: str
    pgport: int
    pgdatabase: str
    pguser: str
    pgpassword: str
    jwt_secret: str
    jwt_horas: int
    public_base_url: str
    skip_db: bool

    @property
    def conninfo(self) -> str:
        return (
            f"host={self.pghost} port={self.pgport} dbname={self.pgdatabase} "
            f"user={self.pguser} password={self.pgpassword} "
            "sslmode=require connect_timeout=8"
        )


@lru_cache
def ajustes() -> Ajustes:
    return Ajustes(
        pghost=os.environ.get("ESTUDIA_PGHOST", "10.20.0.2"),
        pgport=int(os.environ.get("ESTUDIA_PGPORT", "6432")),
        pgdatabase=os.environ.get("ESTUDIA_PGDATABASE", "retail_dwh"),
        pguser=os.environ.get("ESTUDIA_PGUSER", "clase04_lectura"),
        pgpassword=os.environ.get("ESTUDIA_PGPASSWORD", ""),
        jwt_secret=os.environ.get("ESTUDIA_JWT_SECRET", ""),
        jwt_horas=int(os.environ.get("ESTUDIA_JWT_HORAS", "4")),
        public_base_url=os.environ.get("PUBLIC_BASE_URL", "https://34.95.210.33.sslip.io").rstrip("/"),
        skip_db=_flag("ESTUDIA_SKIP_DB"),
    )


def recargar() -> Ajustes:
    ajustes.cache_clear()
    return ajustes()
