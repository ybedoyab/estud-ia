-- Consultas de la clase. Cada una responde una pregunta de la cadena retail.
-- descuento_pct está guardado como fracción: 0.10 = 10%.

-- Exploración
SELECT * FROM curso.productos LIMIT 10;
SELECT DISTINCT categoria FROM curso.productos ORDER BY categoria;
SELECT nombre AS producto, precio_unitario AS precio FROM curso.productos LIMIT 10;

-- Filtros
SELECT nombre, categoria, precio_unitario
FROM curso.productos
WHERE categoria = 'Alimentación'
  AND precio_unitario BETWEEN 5 AND 20
ORDER BY precio_unitario;

SELECT ciudad, segmento
FROM curso.clientes
WHERE region IN ('Andalucía', 'Cataluña')
  AND segmento <> 'Ocasional';

SELECT nombre
FROM curso.productos
WHERE nombre ILIKE '%arroz%'
   OR nombre LIKE 'Smartphone%';

SELECT id_cliente, nombre
FROM curso.clientes c
WHERE NOT EXISTS (
    SELECT 1 FROM curso.ventas v WHERE v.id_cliente = c.id_cliente
);

-- IS NULL: clientes sin ninguna venta (LEFT JOIN)
SELECT c.id_cliente, c.nombre, c.segmento
FROM curso.clientes c
LEFT JOIN curso.ventas v ON v.id_cliente = c.id_cliente
WHERE v.id_transaccion IS NULL
LIMIT 20;

-- Orden
SELECT nombre, ciudad, metros_cuadrados
FROM curso.tiendas
ORDER BY metros_cuadrados DESC, nombre ASC
LIMIT 10;

-- Agregación y agrupación
SELECT
    categoria,
    COUNT(*) AS productos,
    ROUND(AVG(precio_unitario), 2) AS precio_medio,
    MIN(precio_unitario) AS precio_min,
    MAX(precio_unitario) AS precio_max
FROM curso.productos
GROUP BY categoria
ORDER BY precio_medio DESC;

SELECT
    canal,
    COUNT(*) AS transacciones,
    SUM(cantidad) AS unidades,
    ROUND(SUM(importe_neto), 2) AS venta_neta
FROM curso.ventas
GROUP BY canal
HAVING SUM(importe_neto) > 0
ORDER BY venta_neta DESC;

-- Relaciones
SELECT
    t.region,
    t.tipo,
    COUNT(*) AS transacciones,
    ROUND(SUM(v.importe_neto), 2) AS venta_neta
FROM curso.ventas v
JOIN curso.tiendas t ON t.id_tienda = v.id_tienda
GROUP BY t.region, t.tipo
ORDER BY venta_neta DESC
LIMIT 15;

SELECT
    p.categoria,
    c.segmento,
    ROUND(SUM(v.importe_neto), 2) AS venta_neta
FROM curso.ventas v
JOIN curso.productos p ON p.id_producto = v.id_producto
JOIN curso.clientes c ON c.id_cliente = v.id_cliente
GROUP BY p.categoria, c.segmento
ORDER BY venta_neta DESC
LIMIT 15;

-- Fechas
SELECT
    f.anio,
    f.trimestre,
    COUNT(*) AS transacciones,
    ROUND(SUM(v.importe_neto), 2) AS venta_neta
FROM curso.ventas v
JOIN curso.fechas f ON f.id_fecha = v.id_fecha
WHERE f.es_festivo
GROUP BY f.anio, f.trimestre
ORDER BY f.anio, f.trimestre;

SELECT
    DATE_TRUNC('month', f.fecha)::date AS mes,
    ROUND(SUM(v.importe_neto), 2) AS venta_neta
FROM curso.ventas v
JOIN curso.fechas f ON f.id_fecha = v.id_fecha
GROUP BY DATE_TRUNC('month', f.fecha)
ORDER BY mes
LIMIT 12;

SELECT EXTRACT(ISODOW FROM fecha) AS isodow, dia_semana, COUNT(*) AS dias
FROM curso.fechas
GROUP BY EXTRACT(ISODOW FROM fecha), dia_semana
ORDER BY isodow;

-- Lógica
SELECT
    metodo_pago,
    COUNT(*) AS transacciones,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM curso.ventas
GROUP BY metodo_pago
ORDER BY transacciones DESC;

SELECT
    id_transaccion,
    importe_neto,
    CASE
        WHEN importe_neto >= 200 THEN 'alta'
        WHEN importe_neto >= 50 THEN 'media'
        ELSE 'baja'
    END AS franja_importe,
    COALESCE(canal, 'sin canal') AS canal
FROM curso.ventas
ORDER BY importe_neto DESC
LIMIT 20;

-- CTE
WITH venta_cliente AS (
    SELECT
        c.segmento,
        v.id_cliente,
        SUM(v.importe_neto) AS venta_neta
    FROM curso.ventas v
    JOIN curso.clientes c ON c.id_cliente = v.id_cliente
    GROUP BY c.segmento, v.id_cliente
)
SELECT
    segmento,
    COUNT(*) AS clientes_activos,
    ROUND(AVG(venta_neta), 2) AS venta_media_por_cliente
FROM venta_cliente
GROUP BY segmento
ORDER BY venta_media_por_cliente DESC;

-- Subconsulta
SELECT nombre, categoria, precio_unitario
FROM curso.productos
WHERE precio_unitario > (
    SELECT AVG(precio_unitario) FROM curso.productos
)
ORDER BY precio_unitario DESC
LIMIT 10;

-- Analítica
WITH mensual AS (
    SELECT
        f.anio,
        f.mes,
        f.nombre_mes,
        SUM(v.importe_neto) AS venta_neta
    FROM curso.ventas v
    JOIN curso.fechas f ON f.id_fecha = v.id_fecha
    GROUP BY f.anio, f.mes, f.nombre_mes
)
SELECT
    anio,
    mes,
    nombre_mes,
    ROUND(venta_neta, 2) AS venta_neta,
    ROUND(LAG(venta_neta) OVER (ORDER BY anio, mes), 2) AS venta_mes_anterior,
    ROUND(
        venta_neta - LAG(venta_neta) OVER (ORDER BY anio, mes),
        2
    ) AS diferencia,
    ROUND(
        SUM(venta_neta) OVER (PARTITION BY anio ORDER BY mes),
        2
    ) AS venta_acumulada_anio
FROM mensual
ORDER BY anio, mes
LIMIT 18;

WITH ranking AS (
    SELECT
        p.categoria,
        p.nombre,
        SUM(v.importe_neto) AS venta_neta,
        ROW_NUMBER() OVER (
            PARTITION BY p.categoria ORDER BY SUM(v.importe_neto) DESC
        ) AS fila,
        RANK() OVER (
            PARTITION BY p.categoria ORDER BY SUM(v.importe_neto) DESC
        ) AS ranking
    FROM curso.ventas v
    JOIN curso.productos p ON p.id_producto = v.id_producto
    GROUP BY p.categoria, p.nombre
)
SELECT categoria, nombre, ROUND(venta_neta, 2) AS venta_neta, fila, ranking
FROM ranking
WHERE fila <= 3
ORDER BY categoria, fila;
