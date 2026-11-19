#!/usr/bin/env python3
"""Crea los roles internos de PgBouncer. No imprime contraseñas."""

import os
import sys

import psycopg2
from psycopg2 import sql


def load_env(path):
    env = {}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env[key] = value
    return env


def ensure_login_role(cur, name, password, connection_limit):
    cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (name,))
    if cur.fetchone():
        cur.execute(
            sql.SQL(
                "ALTER ROLE {} WITH LOGIN PASSWORD %s "
                "NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS "
                "NOINHERIT CONNECTION LIMIT %s"
            ).format(sql.Identifier(name)),
            (password, connection_limit),
        )
    else:
        cur.execute(
            sql.SQL(
                "CREATE ROLE {} WITH LOGIN PASSWORD %s "
                "NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS "
                "NOINHERIT CONNECTION LIMIT %s"
            ).format(sql.Identifier(name)),
            (password, connection_limit),
        )


def main():
    env_path = os.environ.get("ESTUDIA_ADMIN_ENV", "/var/lib/postgresql/estudia-admin.env")
    env = load_env(env_path)
    conn = psycopg2.connect(dbname="retail_dwh", user="postgres", host="/var/run/postgresql")
    conn.autocommit = True
    cur = conn.cursor()
    ensure_login_role(cur, "pgbouncer_auth", env["PGBOUNCER_AUTH_PASSWORD"], 10)
    ensure_login_role(cur, "pgbouncer_admin", env["PGBOUNCER_ADMIN_PASSWORD"], 3)
    cur.execute(
        """
        GRANT CONNECT ON DATABASE retail_dwh TO pgbouncer_auth;
        GRANT USAGE ON SCHEMA pgbouncer TO pgbouncer_auth;
        GRANT EXECUTE ON FUNCTION pgbouncer.user_search(text) TO pgbouncer_auth;
        ALTER ROLE pgbouncer_auth SET search_path = pgbouncer;
        ALTER ROLE pgbouncer_auth SET default_transaction_read_only = on;
        ALTER ROLE pgbouncer_admin SET default_transaction_read_only = on;
        REVOKE ALL ON SCHEMA curso FROM pgbouncer_auth;
        REVOKE ALL ON SCHEMA public FROM pgbouncer_auth;
        """
    )
    cur.close()
    conn.close()
    print("service roles ready")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"service role setup failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
