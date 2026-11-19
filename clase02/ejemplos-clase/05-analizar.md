# 5. Fechas, lógica y análisis

Objetivo: responder preguntas de evolución, no solo totales.

## Venta en días festivos

**Pregunta:** ¿cuánto se vendió en festivos, por año y trimestre?

`curso.fechas` trae el calendario. `es_festivo` marca los festivos fijos usados en el dataset. `EXTRACT` saca una parte de la fecha; aquí el año, para mostrar la función. `anio` ya viene calculado y es el que se usa para agrupar.

```sql
SELECT
    f.anio,
    f.trimestre,
    EXTRACT(YEAR FROM f.fecha) AS anio_de_la_fecha,
    COUNT(*) AS transacciones,
    ROUND(SUM(v.importe_neto), 2) AS venta_neta
FROM curso.ventas v
JOIN curso.fechas f
    ON f.id_fecha = v.id_fecha
WHERE f.es_festivo
GROUP BY f.anio, f.trimestre, EXTRACT(YEAR FROM f.fecha)
ORDER BY f.anio, f.trimestre;
```

## Venta mensual

**Pregunta:** ¿cómo se movió la venta mes a mes?

`DATE_TRUNC('month', fecha)` lleva cualquier día al primer día de su mes. Así todos los días de marzo caen en el mismo grupo.

```sql
SELECT
    DATE_TRUNC('month', f.fecha)::date AS mes,
    ROUND(SUM(v.importe_neto), 2) AS venta_neta
FROM curso.ventas v
JOIN curso.fechas f
    ON f.id_fecha = v.id_fecha
GROUP BY DATE_TRUNC('month', f.fecha)
ORDER BY mes
LIMIT 12;
```

`LIMIT 12` muestra solo el primer año. Quitar el `LIMIT` muestra 2022, 2023 y 2024.

## Clasificar el importe

**Pregunta:** ¿esta venta es alta, media o baja?

`CASE` recorre las condiciones en orden y se queda con la primera que se cumple. `COALESCE` sustituye un nulo por un texto. En estas ventas el canal siempre viene informado, así que el segundo argumento no se va a ver; sirve para explicar la función.

```sql
SELECT
    id_transaccion,
    importe_neto,
    CASE
        WHEN importe_neto >= 200 THEN 'alta'
        WHEN importe_neto >= 50 THEN 'media'
        ELSE 'baja'
    END AS franja,
    COALESCE(canal, 'sin canal') AS canal
FROM curso.ventas
ORDER BY importe_neto DESC
LIMIT 20;
```

## Un cálculo con nombre

**Pregunta:** ¿cuánto compra, en promedio, un cliente de cada segmento?

`WITH` guarda una consulta intermedia con un nombre. Aquí `venta_cliente` es la venta total de cada cliente. La consulta de fuera promedia esa cifra por segmento.

```sql
WITH venta_cliente AS (
    SELECT
        c.segmento,
        v.id_cliente,
        SUM(v.importe_neto) AS venta_neta
    FROM curso.ventas v
    JOIN curso.clientes c
        ON c.id_cliente = v.id_cliente
    GROUP BY c.segmento, v.id_cliente
)
SELECT
    segmento,
    COUNT(*) AS clientes_activos,
    ROUND(AVG(venta_neta), 2) AS venta_media_por_cliente
FROM venta_cliente
GROUP BY segmento
ORDER BY venta_media_por_cliente DESC;
```

Premium debería quedar por encima de Ocasional. Si no, revisa el `GROUP BY`: hay que agrupar por cliente antes de promediar.

## El mes contra el mes anterior

**Pregunta:** ¿la venta de este mes subió o bajó respecto al anterior, y cuánto llevamos acumulado en el año?

`LAG` mira la fila anterior. `SUM(...) OVER (PARTITION BY anio ...)` acumula dentro de cada año y vuelve a empezar en enero. No es un `GROUP BY`: no aplasta las filas.

```sql
WITH mensual AS (
    SELECT
        f.anio,
        f.mes,
        f.nombre_mes,
        SUM(v.importe_neto) AS venta_neta
    FROM curso.ventas v
    JOIN curso.fechas f
        ON f.id_fecha = v.id_fecha
    GROUP BY f.anio, f.mes, f.nombre_mes
)
SELECT
    anio,
    nombre_mes,
    ROUND(venta_neta, 2) AS venta_neta,
    ROUND(LAG(venta_neta) OVER (ORDER BY anio, mes), 2) AS mes_anterior,
    ROUND(
        venta_neta - LAG(venta_neta) OVER (ORDER BY anio, mes),
        2
    ) AS diferencia,
    ROUND(
        SUM(venta_neta) OVER (PARTITION BY anio ORDER BY mes),
        2
    ) AS acumulado_del_anio
FROM mensual
ORDER BY anio, mes;
```

Enero de 2022 no tiene mes anterior: `mes_anterior` y `diferencia` salen vacíos. Enero de 2023 sí se compara con diciembre de 2022, porque el `LAG` no está partido por año. El acumulado sí se parte: en enero vuelve a empezar.

## Los tres productos que más venden en cada categoría

**Pregunta:** ¿cuál es el top 3 de cada categoría?

`ROW_NUMBER` numera 1, 2, 3… sin empates. `RANK` deja el mismo puesto si hay empate y se salta el siguiente número. `PARTITION BY categoria` reinicia la cuenta en cada categoría.

```sql
WITH ranking AS (
    SELECT
        p.categoria,
        p.nombre,
        SUM(v.importe_neto) AS venta_neta,
        ROW_NUMBER() OVER (
            PARTITION BY p.categoria
            ORDER BY SUM(v.importe_neto) DESC
        ) AS fila,
        RANK() OVER (
            PARTITION BY p.categoria
            ORDER BY SUM(v.importe_neto) DESC
        ) AS puesto
    FROM curso.ventas v
    JOIN curso.productos p
        ON p.id_producto = v.id_producto
    GROUP BY p.categoria, p.nombre
)
SELECT
    categoria,
    nombre,
    ROUND(venta_neta, 2) AS venta_neta,
    fila,
    puesto
FROM ranking
WHERE fila <= 3
ORDER BY categoria, fila;
```

Deben salir 15 filas: 5 categorías por 3 productos.
