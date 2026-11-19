#!/usr/bin/env python3
"""45 conexiones simultáneas de estudiantes contra PgBouncer."""

import argparse
import asyncio
import ssl
import sys
import time

import asyncpg

from credentials import load_students, scrub


QUERY = """
SELECT p.categoria, COUNT(*) AS n, ROUND(SUM(v.importe_neto), 2) AS venta
FROM curso.ventas v
JOIN curso.productos p ON p.id_producto = v.id_producto
GROUP BY p.categoria
ORDER BY venta DESC
"""


def ssl_context():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


async def one(student, hold_seconds):
    started = time.perf_counter()
    password = student["password"]
    try:
        conn = await asyncpg.connect(
            host=student["host"],
            port=int(student["port"]),
            database=student["database"],
            user=student["usuario"],
            password=password,
            ssl=ssl_context(),
            timeout=20,
            statement_cache_size=0,
            command_timeout=60,
        )
        connected = time.perf_counter()
        await conn.execute("SELECT 1")
        rows = await conn.fetch(QUERY)
        queried = time.perf_counter()
        if hold_seconds:
            print(f"HOLDING {student['usuario']}", flush=True)
            await asyncio.sleep(hold_seconds)
        await conn.close()
        if not rows:
            raise RuntimeError("consulta sin filas")
        return {
            "user": student["usuario"],
            "ok": True,
            "connect_ms": (connected - started) * 1000,
            "query_ms": (queried - connected) * 1000,
            "error": "",
        }
    except Exception as exc:
        return {
            "user": student["usuario"],
            "ok": False,
            "connect_ms": None,
            "query_ms": None,
            "error": scrub(exc, [password]),
        }


async def run(path, hold_seconds):
    students = load_students(path)
    if len(students) < 45:
        raise RuntimeError(f"se esperaban 45 credenciales y hay {len(students)}")
    started = time.perf_counter()
    results = await asyncio.gather(*(one(student, hold_seconds) for student in students[:45]))
    elapsed = time.perf_counter() - started
    ok = [item for item in results if item["ok"]]
    bad = [item for item in results if not item["ok"]]
    query_times = [item["query_ms"] for item in ok]
    connect_times = [item["connect_ms"] for item in ok]
    print(f"successful: {len(ok)}/45")
    print(f"failed: {len(bad)}")
    print(f"total_seconds: {elapsed:.2f}")
    if connect_times:
        print(f"connect_ms_avg: {sum(connect_times)/len(connect_times):.1f}")
        print(f"connect_ms_max: {max(connect_times):.1f}")
    if query_times:
        print(f"query_ms_avg: {sum(query_times)/len(query_times):.1f}")
        print(f"query_ms_max: {max(query_times):.1f}")
    for item in bad:
        print(f"ERROR {item['user']}: {item['error']}")
    return 0 if len(ok) == 45 else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--credentials", required=True)
    parser.add_argument("--hold-seconds", type=float, default=0)
    args = parser.parse_args()
    return asyncio.run(run(args.credentials, args.hold_seconds))


if __name__ == "__main__":
    sys.exit(main())
