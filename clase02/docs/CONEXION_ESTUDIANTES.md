# Conexión de estudiantes

La contraseña la entrega el profesor. No está en este documento. En clase todo el mundo entra con el usuario `estudiante`. Las cuentas `estudiante01` … `estudiante45` siguen existiendo, una por persona, por si hace falta separarlas.

| Dato | Valor |
|---|---|
| Host | `34.39.202.205` |
| Puerto | `6432` |
| Base de datos | `retail_dwh` |
| SSL | `require` |

Solo se puede leer. `INSERT`, `UPDATE`, `DELETE`, `CREATE` y `DROP` van a fallar. Eso es lo esperado.

## psql

```bash
psql "host=34.39.202.205 port=6432 dbname=retail_dwh user=estudiante sslmode=require"
```

psql pide la contraseña. No la pegues en el comando si la pantalla se comparte.

## DBeaver

| Campo | Valor |
|---|---|
| Host | `34.39.202.205` |
| Port | `6432` |
| Database | `retail_dwh` |
| Username | `estudiante` |
| Password | la de tu usuario |
| SSL | require |

En la pestaña SSL marca **Use SSL** y deja el modo en **require**. No hace falta un certificado de cliente.

## Primeras consultas

```sql
SELECT * FROM curso.productos LIMIT 10;
```

```sql
SELECT * FROM curso.clientes LIMIT 10;
```

```sql
SELECT * FROM curso.tiendas LIMIT 10;
```

```sql
SELECT * FROM curso.fechas LIMIT 10;
```

```sql
SELECT * FROM curso.ventas LIMIT 10;
```

## Filtros y orden

`descuento_pct` es una fracción: `0.10` significa 10 %.

```sql
SELECT nombre, categoria, precio_unitario
FROM curso.productos
WHERE categoria = 'Alimentación'
  AND precio_unitario BETWEEN 5 AND 30
ORDER BY precio_unitario;
```

```sql
SELECT nombre
FROM curso.productos
WHERE nombre ILIKE '%arroz%'
   OR nombre LIKE 'Smartphone%';
```

## Agregación

```sql
SELECT canal, COUNT(*) AS transacciones, ROUND(SUM(importe_neto), 2) AS venta_neta
FROM curso.ventas
GROUP BY canal
HAVING SUM(importe_neto) > 0
ORDER BY venta_neta DESC;
```

## JOIN

```sql
SELECT t.region, p.categoria, ROUND(SUM(v.importe_neto), 2) AS venta_neta
FROM curso.ventas v
JOIN curso.productos p ON p.id_producto = v.id_producto
JOIN curso.tiendas t ON t.id_tienda = v.id_tienda
GROUP BY t.region, p.categoria
ORDER BY venta_neta DESC
LIMIT 15;
```

Las llaves son `ventas.id_producto`, `ventas.id_cliente`, `ventas.id_tienda` y `ventas.id_fecha`.

## Fecha, CTE y ventana

```sql
SELECT f.anio, DATE_TRUNC('month', f.fecha)::date AS mes, ROUND(SUM(v.importe_neto), 2) AS venta_neta
FROM curso.ventas v
JOIN curso.fechas f ON f.id_fecha = v.id_fecha
GROUP BY f.anio, DATE_TRUNC('month', f.fecha)
ORDER BY mes
LIMIT 12;
```

El archivo `sql/05_consultas_clase.sql` tiene el resto del temario: `CASE`, `COALESCE`, subconsultas, `WITH`, `ROW_NUMBER`, `RANK`, `LAG` y `SUM() OVER`.

Dentro de cada categoría el generador solo produjo una subcategoría (por ejemplo, Alimentación es siempre Arroz). Las cinco categorías, los segmentos, los canales y las tiendas sí sirven para agrupar y cruzar.
