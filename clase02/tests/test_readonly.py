#!/usr/bin/env python3
"""Comprueba que un estudiante no puede modificar el servidor."""

import argparse
import sys

import psycopg

from credentials import load_student, scrub


ATTEMPTS = [
    ("create_table", "CREATE TABLE curso.prueba_hack (id integer)"),
    ("insert_view", "INSERT INTO curso.productos (id_producto, codigo_producto, nombre) VALUES (999999, 999999, 'hack')"),
    ("insert_base", "INSERT INTO public.dim_product (product_nk, product_name) VALUES (999999, 'hack')"),
    ("update_view", "UPDATE curso.productos SET nombre = 'hack' WHERE id_producto = 1"),
    ("update_base", "UPDATE public.fact_sales SET quantity = 0"),
    ("delete_view", "DELETE FROM curso.ventas WHERE id_transaccion = 1"),
    ("delete_base", "DELETE FROM public.fact_sales WHERE transaction_id = 1"),
    ("drop_table", "DROP TABLE public.fact_sales"),
    ("drop_view", "DROP VIEW curso.productos"),
    ("truncate", "TRUNCATE public.fact_sales"),
    ("create_database", "CREATE DATABASE estudia_hack"),
    ("create_role", "CREATE ROLE estudia_hacker LOGIN"),
    ("alter_role_superuser", "ALTER ROLE estudiante01 SUPERUSER"),
    ("alter_role_postgres", "ALTER ROLE postgres SUPERUSER"),
    ("create_extension", "CREATE EXTENSION IF NOT EXISTS pg_stat_statements"),
    ("create_schema", "CREATE SCHEMA estudia_hack"),
    ("create_temp", "CREATE TEMP TABLE estudia_temp (id integer)"),
    ("read_passwords", "SELECT rolpassword FROM pg_authid LIMIT 1"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--credentials", required=True)
    parser.add_argument("--user", default="estudiante01")
    args = parser.parse_args()
    student = load_student(args.credentials, args.user)
    secret = student["password"]
    failed = False
    conn = psycopg.connect(
        host=student["host"],
        port=int(student["port"]),
        dbname=student["database"],
        user=student["usuario"],
        password=secret,
        sslmode=student["sslmode"],
        connect_timeout=20,
        prepare_threshold=None,
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM curso.ventas")
    before = cur.fetchone()[0]

    for name, statement in ATTEMPTS:
        try:
            cur.execute(statement)
            print(f"{name}: FAIL (la operacion tuvo exito)")
            failed = True
        except Exception as exc:
            print(f"{name}: PASS blocked {scrub(exc, [secret]).splitlines()[0]}")

    try:
        cur.execute("SET default_transaction_read_only TO off")
        cur.execute(
            """
            INSERT INTO public.fact_sales (transaction_id, date_key, product_sk, customer_sk, store_sk)
            VALUES (999999999, 20220101, 1, 1, 1)
            """
        )
        print("insert_after_read_only_off: FAIL (la operacion tuvo exito)")
        failed = True
    except Exception as exc:
        print(f"insert_after_read_only_off: PASS blocked {scrub(exc, [secret]).splitlines()[0]}")

    cur.execute("SELECT COUNT(*) FROM curso.ventas")
    after = cur.fetchone()[0]
    unchanged = before == after
    print(f"row_count_unchanged: {'PASS' if unchanged else 'FAIL'} before={before} after={after}")
    failed = failed or not unchanged
    cur.execute("SELECT 1")
    print("select_still_works:", "PASS" if cur.fetchone()[0] == 1 else "FAIL")
    cur.close()
    conn.close()
    print("RESULT", "FAIL" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
