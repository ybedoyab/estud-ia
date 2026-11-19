#!/usr/bin/env python3
"""Comprueba CREATE DATABASE directo a PostgreSQL, sin PgBouncer. No imprime secretos."""

import csv

import psycopg2

student = list(csv.DictReader(open("/root/estudia-lab/student_credentials.csv", encoding="utf-8")))[0]
conn = psycopg2.connect(
    host="127.0.0.1",
    port=5432,
    dbname="retail_dwh",
    user=student["usuario"],
    password=student["password"],
)
conn.autocommit = True
cur = conn.cursor()
cur.execute("SET default_transaction_read_only TO off")
cur.execute("SHOW default_transaction_read_only")
print("read_only_now", cur.fetchone()[0])
try:
    cur.execute("CREATE DATABASE estudia_hack")
    print("create_database FAIL succeeded")
except Exception as exc:
    print("create_database PASS", str(exc).splitlines()[0])
cur.close()
conn.close()
