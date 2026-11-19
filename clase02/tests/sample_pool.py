#!/usr/bin/env python3
"""Mide el pool con 45 clientes abiertos. No imprime secretos."""

import asyncio
import csv
import ssl
from pathlib import Path

import asyncpg
import psycopg


def load_students():
    with Path("clase02/student_credentials.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_admin():
    env = {}
    for line in Path("clase02/.secrets/admin.env").read_text(encoding="utf-8").splitlines():
        if line.strip() and "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            env[key] = value
    return env


def ssl_context():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def summarize(students, admin, label):
    conn = psycopg.connect(
        host=students[0]["host"],
        port=6432,
        dbname="pgbouncer",
        user="pgbouncer_admin",
        password=admin["PGBOUNCER_ADMIN_PASSWORD"],
        sslmode="require",
        prepare_threshold=None,
        autocommit=True,
    )
    cur = conn.cursor()
    cur.execute("SHOW POOLS")
    rows = cur.fetchall()
    cols = [item[0] for item in cur.description]
    index = {name: pos for pos, name in enumerate(cols)}
    users = cl_active = sv_active = sv_idle = 0
    for row in rows:
        if row[index["database"]] != "retail_dwh":
            continue
        if not str(row[index["user"]]).startswith("estudiante"):
            continue
        users += 1
        cl_active += row[index["cl_active"]]
        sv_active += row[index["sv_active"]]
        sv_idle += row[index["sv_idle"]]
    print(
        f"{label} users={users} cl_active={cl_active} "
        f"sv_active={sv_active} sv_idle={sv_idle}"
    )
    conn.close()


async def open_one(student):
    conn = await asyncpg.connect(
        host=student["host"],
        port=int(student["port"]),
        database=student["database"],
        user=student["usuario"],
        password=student["password"],
        ssl=ssl_context(),
        timeout=20,
        statement_cache_size=0,
        command_timeout=60,
    )
    await conn.execute("SELECT 1")
    await conn.fetch("SELECT categoria, COUNT(*) FROM curso.productos GROUP BY categoria")
    return conn


async def main():
    students = load_students()
    admin = load_admin()
    conns = await asyncio.gather(*(open_one(student) for student in students))
    print("connected", len(conns))
    summarize(students, admin, "t0_after_query")
    await asyncio.sleep(12)
    summarize(students, admin, "t12_clients_still_open")
    await asyncio.gather(*(conn.close() for conn in conns))
    await asyncio.sleep(2)
    summarize(students, admin, "t_after_close")


if __name__ == "__main__":
    asyncio.run(main())
