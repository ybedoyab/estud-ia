"""Conexión de solo lectura a la base del laboratorio usando variables de entorno.

Variables:
  PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD, PGSSLMODE
"""

import os
import sys

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.pool import NullPool


def engine_from_env():
    missing = [
        name
        for name in ("PGHOST", "PGPORT", "PGDATABASE", "PGUSER", "PGPASSWORD")
        if not os.environ.get(name)
    ]
    if missing:
        sys.exit("faltan variables de entorno: " + ", ".join(missing))
    url = URL.create(
        "postgresql+psycopg",
        username=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        host=os.environ["PGHOST"],
        port=int(os.environ["PGPORT"]),
        database=os.environ["PGDATABASE"],
    )
    return create_engine(
        url,
        poolclass=NullPool,
        connect_args={
            "sslmode": os.environ.get("PGSSLMODE", "require"),
            "prepare_threshold": None,
            "connect_timeout": 20,
        },
    )


def main():
    engine = engine_from_env()
    ventas = pd.read_sql("SELECT * FROM curso.ventas LIMIT 20", engine)
    resumen = pd.read_sql(
        """
        SELECT p.categoria, t.region, ROUND(SUM(v.importe_neto), 2) AS venta_neta
        FROM curso.ventas v
        JOIN curso.productos p ON p.id_producto = v.id_producto
        JOIN curso.tiendas t ON t.id_tienda = v.id_tienda
        GROUP BY p.categoria, t.region
        ORDER BY venta_neta DESC
        LIMIT 10
        """,
        engine,
    )
    print("shape", ventas.shape)
    print("columns", list(ventas.columns))
    print(ventas.head())
    print("resumen_shape", resumen.shape)
    print(resumen.head())
    engine.dispose()


if __name__ == "__main__":
    main()
