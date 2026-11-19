# 4. Relacionar tablas

Objetivo: una venta no dice el nombre del producto ni la ciudad de la tienda. Esas columnas están en otras vistas. El `JOIN` las trae.

Dibuja esto antes de escribir SQL:

```text
curso.ventas.id_producto  =  curso.productos.id_producto
curso.ventas.id_cliente   =  curso.clientes.id_cliente
curso.ventas.id_tienda    =  curso.tiendas.id_tienda
curso.ventas.id_fecha     =  curso.fechas.id_fecha
```

El alias corto (`v`, `p`, `t`) evita repetir el nombre de la vista.

## Venta por región y tipo de tienda

**Pregunta:** ¿qué combinación de región y tipo de tienda factura más?

`JOIN` sin más palabras es un `INNER JOIN`: solo quedan las ventas que encuentran su tienda. En estos datos todas la encuentran.

```sql
SELECT
    t.region,
    t.tipo,
    COUNT(*) AS transacciones,
    ROUND(SUM(v.importe_neto), 2) AS venta_neta
FROM curso.ventas v
JOIN curso.tiendas t
    ON t.id_tienda = v.id_tienda
GROUP BY t.region, t.tipo
ORDER BY venta_neta DESC
LIMIT 15;
```

Si se les olvida el `ON`, el motor cruza todas las ventas con todas las tiendas. El número de filas se dispara. Vale la pena mostrarlo y cortarlo con `LIMIT` solo si la consulta tarda, o explicarlo sin ejecutarla.

## Categoría y segmento del cliente

**Pregunta:** ¿los clientes Premium compran las mismas categorías que el resto?

Hacen falta dos cruces: de la venta al producto y de la venta al cliente.

```sql
SELECT
    p.categoria,
    c.segmento,
    ROUND(SUM(v.importe_neto), 2) AS venta_neta
FROM curso.ventas v
JOIN curso.productos p
    ON p.id_producto = v.id_producto
JOIN curso.clientes c
    ON c.id_cliente = v.id_cliente
GROUP BY p.categoria, c.segmento
ORDER BY venta_neta DESC
LIMIT 15;
```

## Productos con pocas ventas

**Pregunta:** ¿hay productos que casi no se venden?

`LEFT JOIN` conserva el producto aunque tenga pocas o ninguna venta. `COUNT(v.id_transaccion)` cuenta ventas, no filas vacías. `COUNT(*)` contaría también el producto sin ventas y daría 1.

```sql
SELECT
    p.nombre,
    p.categoria,
    COUNT(v.id_transaccion) AS ventas
FROM curso.productos p
LEFT JOIN curso.ventas v
    ON v.id_producto = p.id_producto
GROUP BY p.nombre, p.categoria
ORDER BY ventas ASC
LIMIT 10;
```
