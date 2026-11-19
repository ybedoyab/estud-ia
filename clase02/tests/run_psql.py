#!/usr/bin/env python3
"""Ejecuta psql real contra la IP pública. La contraseña va en un env-file temporal."""

import csv
import os
import subprocess
import sys
from pathlib import Path


def main():
    with Path("clase02/student_credentials.csv").open(encoding="utf-8", newline="") as handle:
        student = next(csv.DictReader(handle))
    env_file = Path("clase02/.secrets/psql.env")
    env_file.write_text(f"PGPASSWORD={student['password']}\n", encoding="utf-8")
    dsn = (
        f"host={student['host']} port={student['port']} dbname={student['database']} "
        f"user={student['usuario']} sslmode=require"
    )
    queries = [
        "SELECT 1 AS ok;",
        "SELECT * FROM curso.productos LIMIT 5;",
        "SELECT categoria, COUNT(*) FROM curso.productos GROUP BY categoria ORDER BY categoria;",
        "SELECT MIN(anio) AS anio_min, MAX(anio) AS anio_max, COUNT(*) AS dias FROM curso.fechas;",
        "SELECT segmento, COUNT(*) FROM curso.clientes GROUP BY segmento ORDER BY segmento;",
        "SELECT canal, COUNT(*) FROM curso.ventas GROUP BY canal ORDER BY canal;",
        "SELECT metodo_pago, COUNT(*) FROM curso.ventas GROUP BY metodo_pago ORDER BY metodo_pago;",
        "SELECT region, COUNT(*) FROM curso.tiendas GROUP BY region ORDER BY region;",
        "SELECT pg_size_pretty(pg_database_size(current_database())) AS tamano;",
        "SELECT COUNT(*) AS ventas FROM curso.ventas;",
    ]
    psql = Path(r"C:\Program Files\PostgreSQL\17\bin\psql.exe")
    if psql.exists():
        command = [str(psql), dsn, "-v", "ON_ERROR_STOP=1"]
    else:
        command = [
            "docker",
            "run",
            "--rm",
            "--env-file",
            str(env_file.resolve()),
            "postgres:16-alpine",
            "psql",
            dsn,
            "-v",
            "ON_ERROR_STOP=1",
        ]
    for query in queries:
        command.extend(["-c", query])
    env = None
    if psql.exists():
        env = os.environ.copy()
        env["PGPASSWORD"] = student["password"]
        env["PGSSLMODE"] = "require"
    try:
        return subprocess.call(command, env=env)
    finally:
        env_file.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
