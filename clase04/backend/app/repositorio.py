"""Consultas parametrizadas sobre las vistas de solo lectura del esquema curso."""

from datetime import date, datetime
from decimal import Decimal

from app.db import consultar

ORDEN = {
    "id_transaccion": "v.id_transaccion",
    "fecha": "f.fecha",
    "importe_neto": "v.importe_neto",
    "cantidad": "v.cantidad",
}


def _valor(dato):
    if isinstance(dato, Decimal):
        return float(dato)
    if isinstance(dato, datetime):
        return dato.date().isoformat()
    if isinstance(dato, date):
        return dato.isoformat()
    return dato


def _filas(sql: str, params: tuple) -> list[dict]:
    return [{clave: _valor(valor) for clave, valor in fila.items()} for fila in consultar(sql, params)]


def _pagina(total: int, page: int, page_size: int) -> dict:
    paginas = (total + page_size - 1) // page_size if total else 0
    return {
        "page": page,
        "page_size": page_size,
        "total_records": total,
        "total_pages": paginas,
        "has_next": page < paginas,
    }


def productos(categoria: str | None, q: str | None, page: int, page_size: int) -> dict:
    where = "WHERE (%s::text IS NULL OR categoria = %s) AND (%s::text IS NULL OR nombre ILIKE %s ESCAPE '!')"
    patron = None if not q else "%" + q.replace("!", "!!").replace("%", "!%").replace("_", "!_") + "%"
    params = (categoria, categoria, patron, patron)
    total = int(consultar(f"SELECT count(*) AS total FROM curso.productos {where}", params)[0]["total"])
    offset = (page - 1) * page_size
    filas = _filas(
        f"""
        SELECT id_producto, codigo_producto, nombre, categoria, subcategoria, marca,
               proveedor, costo_unitario, precio_unitario, margen_pct
        FROM curso.productos
        {where}
        ORDER BY id_producto
        LIMIT %s OFFSET %s
        """,
        params + (page_size, offset),
    )
    return {"data": filas, "pagination": _pagina(total, page, page_size)}


def producto(id_producto: int) -> dict | None:
    filas = _filas(
        """
        SELECT id_producto, codigo_producto, nombre, categoria, subcategoria, marca,
               proveedor, costo_unitario, precio_unitario, margen_pct
        FROM curso.productos
        WHERE id_producto = %s
        """,
        (id_producto,),
    )
    return filas[0] if filas else None


def categorias() -> dict:
    filas = _filas(
        """
        SELECT categoria, count(*)::int AS productos
        FROM curso.productos
        GROUP BY categoria
        ORDER BY categoria
        """,
        (),
    )
    return {"data": filas}


def tiendas(region: str | None, page: int, page_size: int) -> dict:
    where = "WHERE (%s::text IS NULL OR region = %s)"
    params = (region, region)
    total = int(consultar(f"SELECT count(*) AS total FROM curso.tiendas {where}", params)[0]["total"])
    offset = (page - 1) * page_size
    filas = _filas(
        f"""
        SELECT id_tienda, codigo_tienda, nombre, ciudad, region, pais, tipo, metros_cuadrados
        FROM curso.tiendas
        {where}
        ORDER BY id_tienda
        LIMIT %s OFFSET %s
        """,
        params + (page_size, offset),
    )
    return {"data": filas, "pagination": _pagina(total, page, page_size)}


def tienda(id_tienda: int) -> dict | None:
    filas = _filas(
        """
        SELECT id_tienda, codigo_tienda, nombre, ciudad, region, pais, tipo, metros_cuadrados
        FROM curso.tiendas
        WHERE id_tienda = %s
        """,
        (id_tienda,),
    )
    return filas[0] if filas else None


def _filtros_venta(filtros: dict) -> tuple[str, tuple]:
    return (
        """
        WHERE (%s::text IS NULL OR t.region = %s)
          AND (%s::text IS NULL OR p.categoria = %s)
          AND (%s::text IS NULL OR v.canal = %s)
          AND (%s::text IS NULL OR v.metodo_pago = %s)
          AND (%s::date IS NULL OR f.fecha >= %s)
          AND (%s::date IS NULL OR f.fecha <= %s)
          AND (%s::int IS NULL OR p.id_producto = %s)
          AND (%s::int IS NULL OR t.id_tienda = %s)
        """,
        (
            filtros.get("region"), filtros.get("region"),
            filtros.get("categoria"), filtros.get("categoria"),
            filtros.get("canal"), filtros.get("canal"),
            filtros.get("metodo_pago"), filtros.get("metodo_pago"),
            filtros.get("fecha_desde"), filtros.get("fecha_desde"),
            filtros.get("fecha_hasta"), filtros.get("fecha_hasta"),
            filtros.get("id_producto"), filtros.get("id_producto"),
            filtros.get("id_tienda"), filtros.get("id_tienda"),
        ),
    )


_DESDE = """
FROM curso.ventas v
JOIN curso.productos p ON p.id_producto = v.id_producto
JOIN curso.tiendas t ON t.id_tienda = v.id_tienda
JOIN curso.fechas f ON f.id_fecha = v.id_fecha
"""


def ventas(filtros: dict, orden: str, direccion: str, page: int, page_size: int) -> dict:
    where, params = _filtros_venta(filtros)
    total = int(consultar(f"SELECT count(*) AS total {_DESDE} {where}", params)[0]["total"])
    offset = (page - 1) * page_size
    columna = ORDEN[orden]
    sentido = "DESC" if direccion == "desc" else "ASC"
    filas = _filas(
        f"""
        SELECT v.id_transaccion, f.fecha, v.cantidad, v.importe_neto, v.descuento_pct,
               v.canal, v.metodo_pago, p.id_producto, p.categoria, t.id_tienda, t.region
        {_DESDE}
        {where}
        ORDER BY {columna} {sentido}, v.id_transaccion ASC
        LIMIT %s OFFSET %s
        """,
        params + (page_size, offset),
    )
    return {"data": filas, "pagination": _pagina(total, page, page_size)}


def venta(id_transaccion: int) -> dict | None:
    filas = _filas(
        f"""
        SELECT v.id_transaccion, f.fecha, v.cantidad, v.importe_neto, v.descuento_pct,
               v.canal, v.metodo_pago,
               p.id_producto, p.nombre AS producto_nombre, p.categoria, p.marca,
               t.id_tienda, t.nombre AS tienda_nombre, t.region, t.ciudad
        {_DESDE}
        WHERE v.id_transaccion = %s
        """,
        (id_transaccion,),
    )
    if not filas:
        return None
    fila = filas[0]
    return {
        "id_transaccion": fila["id_transaccion"],
        "fecha": fila["fecha"],
        "cantidad": fila["cantidad"],
        "importe_neto": fila["importe_neto"],
        "descuento_pct": fila["descuento_pct"],
        "canal": fila["canal"],
        "metodo_pago": fila["metodo_pago"],
        "producto": {
            "id_producto": fila["id_producto"],
            "nombre": fila["producto_nombre"],
            "categoria": fila["categoria"],
            "marca": fila["marca"],
        },
        "tienda": {
            "id_tienda": fila["id_tienda"],
            "nombre": fila["tienda_nombre"],
            "region": fila["region"],
            "ciudad": fila["ciudad"],
        },
    }


def muestra(limite: int) -> dict:
    filas = _filas(
        f"""
        SELECT v.id_transaccion, f.fecha, v.cantidad, v.importe_neto,
               p.id_producto, p.nombre AS producto_nombre, p.categoria,
               t.id_tienda, t.region
        {_DESDE}
        ORDER BY v.id_transaccion
        LIMIT %s
        """,
        (limite,),
    )
    data = [
        {
            "id_transaccion": fila["id_transaccion"],
            "fecha": fila["fecha"],
            "cantidad": fila["cantidad"],
            "importe_neto": fila["importe_neto"],
            "producto": {
                "id_producto": fila["id_producto"],
                "nombre": fila["producto_nombre"],
                "categoria": fila["categoria"],
            },
            "tienda": {
                "id_tienda": fila["id_tienda"],
                "region": fila["region"],
            },
        }
        for fila in filas
    ]
    return {"data": data, "total": len(data), "nota": "Extraccion pequena y determinista para la practica."}


def resumen(fecha_desde: date | None, fecha_hasta: date | None) -> dict:
    filas = _filas(
        f"""
        SELECT count(*)::int AS transacciones,
               coalesce(sum(v.importe_neto), 0) AS importe_neto,
               coalesce(sum(v.cantidad), 0)::int AS cantidad,
               coalesce(avg(v.importe_neto), 0) AS ticket_promedio,
               min(f.fecha) AS fecha_min,
               max(f.fecha) AS fecha_max
        {_DESDE}
        WHERE (%s::date IS NULL OR f.fecha >= %s)
          AND (%s::date IS NULL OR f.fecha <= %s)
        """,
        (fecha_desde, fecha_desde, fecha_hasta, fecha_hasta),
    )
    return filas[0]


def por_categoria() -> dict:
    return {
        "data": _filas(
            f"""
            SELECT p.categoria,
                   count(*)::int AS transacciones,
                   coalesce(sum(v.importe_neto), 0) AS importe_neto,
                   coalesce(sum(v.cantidad), 0)::int AS cantidad
            {_DESDE}
            GROUP BY p.categoria
            ORDER BY p.categoria
            """,
            (),
        )
    }


def por_region() -> dict:
    return {
        "data": _filas(
            f"""
            SELECT t.region,
                   count(*)::int AS transacciones,
                   coalesce(sum(v.importe_neto), 0) AS importe_neto,
                   coalesce(sum(v.cantidad), 0)::int AS cantidad
            {_DESDE}
            GROUP BY t.region
            ORDER BY t.region
            """,
            (),
        )
    }


def por_periodo(granularidad: str) -> dict:
    if granularidad == "trimestre":
        sql = f"""
            SELECT f.anio, f.trimestre,
                   count(*)::int AS transacciones,
                   coalesce(sum(v.importe_neto), 0) AS importe_neto
            {_DESDE}
            GROUP BY f.anio, f.trimestre
            ORDER BY f.anio, f.trimestre
        """
    else:
        sql = f"""
            SELECT f.anio, f.mes, f.nombre_mes,
                   count(*)::int AS transacciones,
                   coalesce(sum(v.importe_neto), 0) AS importe_neto
            {_DESDE}
            GROUP BY f.anio, f.mes, f.nombre_mes
            ORDER BY f.anio, f.mes
        """
    return {"granularidad": granularidad, "data": _filas(sql, ())}


def ping() -> bool:
    return consultar("SELECT 1 AS ok", ())[0]["ok"] == 1
