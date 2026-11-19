#!/usr/bin/env python3
"""Confirma que, aunque la transacción sea READ WRITE, el estudiante no escribe."""

import argparse
import sys

import psycopg

from credentials import load_student, scrub


PACKETS = [
    ("create_table", b"BEGIN READ WRITE; CREATE TABLE curso.prueba_hack (id integer); ROLLBACK;"),
    ("insert_base", b"BEGIN READ WRITE; INSERT INTO public.fact_sales (transaction_id, date_key, product_sk, customer_sk, store_sk) VALUES (999999999, 20220101, 1, 1, 1); ROLLBACK;"),
    ("update_base", b"BEGIN READ WRITE; UPDATE public.fact_sales SET quantity = quantity WHERE transaction_id = 1; ROLLBACK;"),
    ("delete_base", b"BEGIN READ WRITE; DELETE FROM public.fact_sales WHERE transaction_id = 1; ROLLBACK;"),
    ("drop_table", b"BEGIN READ WRITE; DROP TABLE public.fact_sales; ROLLBACK;"),
    ("create_role", b"BEGIN READ WRITE; CREATE ROLE estudia_hacker LOGIN; ROLLBACK;"),
    ("alter_role", b"BEGIN READ WRITE; ALTER ROLE estudiante01 SUPERUSER; ROLLBACK;"),
    ("create_extension", b"BEGIN READ WRITE; CREATE EXTENSION pg_stat_statements; ROLLBACK;"),
    ("create_database", b"CREATE DATABASE estudia_hack;"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--credentials", required=True)
    args = parser.parse_args()
    student = load_student(args.credentials, "estudiante01")
    secret = student["password"]
    failed = False
    count = None
    for name, packet in PACKETS:
        conn = psycopg.connect(
            host=student["host"],
            port=int(student["port"]),
            dbname=student["database"],
            user=student["usuario"],
            password=secret,
            sslmode=student["sslmode"],
            prepare_threshold=None,
            autocommit=True,
        )
        conn.pgconn.exec_(b"ROLLBACK;")
        conn.pgconn.exec_(packet)
        message = (conn.pgconn.error_message or b"").decode().strip()
        conn.pgconn.exec_(b"ROLLBACK;")
        if message:
            print(f"{name}: PASS {scrub(message, [secret]).splitlines()[0]}")
        else:
            print(f"{name}: FAIL la operacion no devolvio error")
            failed = True
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM curso.ventas")
            count = cur.fetchone()[0]
        conn.close()
    print(f"rows: {count}")
    if count != 50000:
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
