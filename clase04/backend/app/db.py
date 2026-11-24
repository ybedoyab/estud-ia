"""Pool de la cuenta técnica de solo lectura. Las consultas de datos no usan la contraseña del estudiante."""

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool, PoolTimeout

from app.bitacora import bitacora
from app.config import ajustes

_pool: ConnectionPool | None = None


def abrir_pool() -> None:
    global _pool
    if _pool is not None:
        return
    cfg = ajustes()
    _pool = ConnectionPool(
        conninfo=cfg.conninfo,
        min_size=1,
        max_size=8,
        timeout=5,
        kwargs={"prepare_threshold": None, "row_factory": dict_row},
        open=True,
    )


def cerrar_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


def consultar(sql: str, params: tuple = ()) -> list[dict]:
    if _pool is None:
        abrir_pool()
    assert _pool is not None
    try:
        with _pool.connection() as conn:
            conn.execute("SET statement_timeout = '8s'")
            conn.execute("SET default_transaction_read_only = on")
            cursor = conn.execute(sql, params)
            if cursor.description is None:
                return []
            return list(cursor.fetchall())
    except PoolTimeout:
        bitacora.warning("pool_agotado")
        raise
