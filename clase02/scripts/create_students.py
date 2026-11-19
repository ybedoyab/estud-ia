#!/usr/bin/env python3
"""Crea estudiante01..estudianteNN con contraseñas distintas y solo lectura."""

import argparse
import csv
import secrets
import sys

import psycopg2
from psycopg2 import sql


def ensure_student(cur, username, password, connection_limit=2):
    cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (username,))
    attributes = (
        "LOGIN PASSWORD %s NOSUPERUSER NOCREATEDB NOCREATEROLE "
        "NOREPLICATION NOBYPASSRLS INHERIT CONNECTION LIMIT %s"
    )
    if cur.fetchone():
        cur.execute(
            sql.SQL("ALTER ROLE {} WITH " + attributes).format(sql.Identifier(username)),
            (password, connection_limit),
        )
    else:
        cur.execute(
            sql.SQL("CREATE ROLE {} WITH " + attributes).format(sql.Identifier(username)),
            (password, connection_limit),
        )
    cur.execute(sql.SQL("GRANT rol_estudiante TO {}").format(sql.Identifier(username)))
    for setting in (
        "statement_timeout = '60s'",
        "idle_in_transaction_session_timeout = '30s'",
        "idle_session_timeout = '15min'",
        "lock_timeout = '5s'",
        "temp_file_limit = '128MB'",
        "default_transaction_read_only = on",
        "search_path = curso",
        "timezone = 'America/Bogota'",
    ):
        cur.execute(
            sql.SQL("ALTER ROLE {} SET " + setting).format(sql.Identifier(username))
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=45)
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", default="6432")
    parser.add_argument("--database", default="retail_dwh")
    parser.add_argument("--sslmode", default="require")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    conn = psycopg2.connect(dbname="retail_dwh", user="postgres", host="/var/run/postgresql")
    conn.autocommit = True
    cur = conn.cursor()
    rows = []
    shared_password = secrets.token_urlsafe(18)
    ensure_student(cur, "estudiante", shared_password, connection_limit=50)
    rows.append(
        {
            "usuario": "estudiante",
            "password": shared_password,
            "host": args.host,
            "port": args.port,
            "database": args.database,
            "sslmode": args.sslmode,
        }
    )
    for number in range(1, args.count + 1):
        username = f"estudiante{number:02d}"
        password = secrets.token_urlsafe(18)
        ensure_student(cur, username, password)
        rows.append(
            {
                "usuario": username,
                "password": password,
                "host": args.host,
                "port": args.port,
                "database": args.database,
                "sslmode": args.sslmode,
            }
        )
    cur.close()
    conn.close()

    with open(args.out, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["usuario", "password", "host", "port", "database", "sslmode"],
        )
        writer.writeheader()
        writer.writerows(rows)
    os_chmod = __import__("os").chmod
    os_chmod(args.out, 0o600)
    print(f"created {len(rows)} student accounts -> {args.out}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"student setup failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
