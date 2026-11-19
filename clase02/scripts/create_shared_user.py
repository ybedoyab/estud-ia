#!/usr/bin/env python3
"""Crea el usuario compartido `estudiante` sin tocar estudiante01..45."""

import argparse
import csv
import secrets
import sys

import psycopg2
from psycopg2 import sql

from create_students import ensure_student


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", default="6432")
    parser.add_argument("--database", default="retail_dwh")
    parser.add_argument("--sslmode", default="require")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    password = secrets.token_urlsafe(18)
    conn = psycopg2.connect(dbname="retail_dwh", user="postgres", host="/var/run/postgresql")
    conn.autocommit = True
    cur = conn.cursor()
    ensure_student(cur, "estudiante", password, connection_limit=50)
    cur.close()
    conn.close()

    with open(args.out, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["usuario", "password", "host", "port", "database", "sslmode"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "usuario": "estudiante",
                "password": password,
                "host": args.host,
                "port": args.port,
                "database": args.database,
                "sslmode": args.sslmode,
            }
        )
    print("shared user ready")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"shared user failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
