#!/usr/bin/env python3
"""Prueba TCP real contra PgBouncer con un estudiante y las consultas de clase."""

import argparse
import socket
import sys

import psycopg

from credentials import load_student, scrub


QUERIES = [
    ("select_1", "SELECT 1 AS ok", 1),
    ("productos", "SELECT * FROM curso.productos LIMIT 5", 1),
    ("clientes", "SELECT * FROM curso.clientes LIMIT 5", 1),
    ("distinct", "SELECT DISTINCT categoria FROM curso.productos", 1),
    ("where_between", """
        SELECT nombre FROM curso.productos
        WHERE categoria = 'Alimentación' AND precio_unitario BETWEEN 5 AND 30
        LIMIT 5
    """, 1),
    ("in_not", """
        SELECT id_cliente FROM curso.clientes
        WHERE region IN ('Andalucía', 'Cataluña') AND NOT (segmento = 'Ocasional')
        LIMIT 5
    """, 1),
    ("like_ilike", """
        SELECT nombre FROM curso.productos
        WHERE nombre ILIKE '%arroz%' OR nombre LIKE 'Smartphone%'
        LIMIT 5
    """, 1),
    ("is_not_null", "SELECT COUNT(*) FROM curso.ventas WHERE importe_neto IS NOT NULL", 1),
    ("is_null_left_join", """
        SELECT COUNT(*) FROM curso.clientes c
        LEFT JOIN curso.ventas v
          ON v.id_cliente = c.id_cliente AND v.metodo_pago = 'Bizum'
        WHERE v.id_transaccion IS NULL
    """, 1),
    ("order_by", """
        SELECT nombre, metros_cuadrados FROM curso.tiendas
        ORDER BY metros_cuadrados DESC, nombre ASC
        LIMIT 5
    """, 1),
    ("group_by", """
        SELECT categoria, COUNT(*), ROUND(AVG(precio_unitario), 2), MIN(precio_unitario), MAX(precio_unitario)
        FROM curso.productos GROUP BY categoria
    """, 1),
    ("having", """
        SELECT canal, SUM(importe_neto) FROM curso.ventas
        GROUP BY canal HAVING SUM(importe_neto) > 0
    """, 1),
    ("inner_join", """
        SELECT t.region, ROUND(SUM(v.importe_neto), 2)
        FROM curso.ventas v
        JOIN curso.tiendas t ON t.id_tienda = v.id_tienda
        GROUP BY t.region
    """, 1),
    ("left_join", """
        SELECT p.nombre, COUNT(v.id_transaccion)
        FROM curso.productos p
        LEFT JOIN curso.ventas v ON v.id_producto = p.id_producto
        GROUP BY p.nombre
        ORDER BY COUNT(v.id_transaccion) ASC
        LIMIT 5
    """, 1),
    ("fecha", """
        SELECT f.anio, DATE_TRUNC('month', f.fecha)::date AS mes, EXTRACT(YEAR FROM f.fecha), SUM(v.importe_neto)
        FROM curso.ventas v
        JOIN curso.fechas f ON f.id_fecha = v.id_fecha
        GROUP BY f.anio, DATE_TRUNC('month', f.fecha), EXTRACT(YEAR FROM f.fecha)
        ORDER BY mes
        LIMIT 6
    """, 1),
    ("case_coalesce", """
        SELECT CASE WHEN importe_neto >= 100 THEN 'alta' ELSE 'baja' END, COALESCE(canal, 'sin canal')
        FROM curso.ventas LIMIT 5
    """, 1),
    ("subquery", """
        SELECT nombre FROM curso.productos
        WHERE precio_unitario > (SELECT AVG(precio_unitario) FROM curso.productos)
        LIMIT 5
    """, 1),
    ("cte", """
        WITH venta_cliente AS (
            SELECT c.segmento, SUM(v.importe_neto) AS venta
            FROM curso.ventas v
            JOIN curso.clientes c ON c.id_cliente = v.id_cliente
            GROUP BY c.segmento, v.id_cliente
        )
        SELECT segmento, ROUND(AVG(venta), 2) FROM venta_cliente GROUP BY segmento
    """, 1),
    ("window", """
        WITH mensual AS (
            SELECT f.anio, f.mes, SUM(v.importe_neto) AS venta
            FROM curso.ventas v
            JOIN curso.fechas f ON f.id_fecha = v.id_fecha
            GROUP BY f.anio, f.mes
        )
        SELECT anio, mes,
               ROW_NUMBER() OVER (ORDER BY venta DESC) AS fila,
               RANK() OVER (PARTITION BY anio ORDER BY venta DESC) AS ranking,
               LAG(venta) OVER (ORDER BY anio, mes) AS mes_anterior,
               SUM(venta) OVER (PARTITION BY anio ORDER BY mes) AS acumulado
        FROM mensual
        ORDER BY anio, mes
        LIMIT 8
    """, 1),
]


def port_open(host, port, timeout=5):
    sock = socket.socket()
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--credentials", required=True)
    parser.add_argument("--user", default="estudiante01")
    args = parser.parse_args()
    student = load_student(args.credentials, args.user)
    host = student["host"]
    failed = False

    closed = not port_open(host, 5432, timeout=6)
    print(f"port_5432_closed: {'PASS' if closed else 'FAIL'}")
    failed = failed or not closed
    opened = port_open(host, int(student["port"]), timeout=8)
    print(f"port_6432_open: {'PASS' if opened else 'FAIL'}")
    failed = failed or not opened

    try:
        conn = psycopg.connect(
            host=host,
            port=int(student["port"]),
            dbname=student["database"],
            user=student["usuario"],
            password=student["password"],
            sslmode=student["sslmode"],
            connect_timeout=20,
            prepare_threshold=None,
        )
    except Exception as exc:
        print("connect: FAIL", scrub(exc, [student["password"]]))
        return 1

    conn.autocommit = True
    cur = conn.cursor()
    for name, query, minimum in QUERIES:
        try:
            cur.execute(query)
            rows = cur.fetchall()
            ok = len(rows) >= minimum
            print(f"{name}: {'PASS' if ok else 'FAIL'} rows={len(rows)}")
            failed = failed or not ok
        except Exception as exc:
            print(f"{name}: FAIL {scrub(exc, [student['password']])}")
            failed = True
    cur.close()
    conn.close()
    print("RESULT", "FAIL" if failed else "PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
