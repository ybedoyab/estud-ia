-- Capa pedagógica en español. Solo usa columnas reales del esquema estrella.
-- UNION ALL ... WHERE false no añade filas y vuelve la vista no actualizable,
-- así un INSERT/UPDATE/DELETE directo sobre curso.* no puede reescribir la tabla base.

CREATE SCHEMA IF NOT EXISTS curso;
COMMENT ON SCHEMA curso IS
    'Vistas de solo lectura, en español, para la clase de análisis de datos.';

REVOKE ALL ON SCHEMA curso FROM PUBLIC;

CREATE OR REPLACE VIEW curso.productos AS
SELECT
    product_sk   AS id_producto,
    product_nk   AS codigo_producto,
    product_name AS nombre,
    category     AS categoria,
    subcategory  AS subcategoria,
    brand        AS marca,
    supplier     AS proveedor,
    unit_cost    AS costo_unitario,
    unit_price   AS precio_unitario,
    margin_pct   AS margen_pct
FROM public.dim_product
UNION ALL
SELECT
    NULL::int, NULL::int, NULL::varchar, NULL::varchar, NULL::varchar,
    NULL::varchar, NULL::varchar, NULL::numeric, NULL::numeric, NULL::numeric
WHERE false;

CREATE OR REPLACE VIEW curso.clientes AS
SELECT
    customer_sk   AS id_cliente,
    customer_nk   AS codigo_cliente,
    first_name    AS nombre,
    last_name     AS apellido,
    email         AS email,
    city          AS ciudad,
    region        AS region,
    segment       AS segmento,
    loyalty_since AS cliente_desde
FROM public.dim_customer
UNION ALL
SELECT
    NULL::int, NULL::int, NULL::varchar, NULL::varchar, NULL::varchar,
    NULL::varchar, NULL::varchar, NULL::varchar, NULL::date
WHERE false;

CREATE OR REPLACE VIEW curso.tiendas AS
SELECT
    store_sk   AS id_tienda,
    store_nk   AS codigo_tienda,
    store_name AS nombre,
    city       AS ciudad,
    region     AS region,
    country    AS pais,
    store_type AS tipo,
    sqm        AS metros_cuadrados
FROM public.dim_store
UNION ALL
SELECT
    NULL::int, NULL::int, NULL::varchar, NULL::varchar, NULL::varchar,
    NULL::varchar, NULL::varchar, NULL::int
WHERE false;

CREATE OR REPLACE VIEW curso.fechas AS
SELECT
    date_key     AS id_fecha,
    full_date    AS fecha,
    day_of_week  AS dia_semana_num,
    CASE day_name
        WHEN 'Sunday' THEN 'domingo'
        WHEN 'Monday' THEN 'lunes'
        WHEN 'Tuesday' THEN 'martes'
        WHEN 'Wednesday' THEN 'miércoles'
        WHEN 'Thursday' THEN 'jueves'
        WHEN 'Friday' THEN 'viernes'
        WHEN 'Saturday' THEN 'sábado'
        ELSE day_name
    END AS dia_semana,
    day_of_month AS dia_mes,
    day_of_year  AS dia_anio,
    week_of_year AS semana,
    month        AS mes,
    CASE month_name
        WHEN 'January' THEN 'enero'
        WHEN 'February' THEN 'febrero'
        WHEN 'March' THEN 'marzo'
        WHEN 'April' THEN 'abril'
        WHEN 'May' THEN 'mayo'
        WHEN 'June' THEN 'junio'
        WHEN 'July' THEN 'julio'
        WHEN 'August' THEN 'agosto'
        WHEN 'September' THEN 'septiembre'
        WHEN 'October' THEN 'octubre'
        WHEN 'November' THEN 'noviembre'
        WHEN 'December' THEN 'diciembre'
        ELSE month_name
    END AS nombre_mes,
    quarter    AS trimestre,
    semester   AS semestre,
    year       AS anio,
    is_weekend AS es_fin_de_semana,
    is_holiday AS es_festivo
FROM public.dim_date
UNION ALL
SELECT
    NULL::int, NULL::date, NULL::smallint, NULL::text,
    NULL::smallint, NULL::smallint, NULL::smallint, NULL::smallint, NULL::text,
    NULL::smallint, NULL::smallint, NULL::smallint, NULL::boolean, NULL::boolean
WHERE false;

CREATE OR REPLACE VIEW curso.ventas AS
SELECT
    transaction_id AS id_transaccion,
    date_key       AS id_fecha,
    product_sk     AS id_producto,
    customer_sk    AS id_cliente,
    store_sk       AS id_tienda,
    quantity       AS cantidad,
    unit_price     AS precio_unitario,
    discount_pct   AS descuento_pct,
    gross_amount   AS importe_bruto,
    net_amount     AS importe_neto,
    margin         AS margen,
    margin_pct     AS margen_pct,
    payment_method AS metodo_pago,
    channel        AS canal
FROM public.fact_sales
UNION ALL
SELECT
    NULL::bigint, NULL::int, NULL::int, NULL::int, NULL::int, NULL::int,
    NULL::numeric, NULL::numeric, NULL::numeric, NULL::numeric, NULL::numeric,
    NULL::numeric, NULL::varchar, NULL::varchar
WHERE false;

COMMENT ON VIEW curso.productos IS 'Catálogo. id_producto enlaza con curso.ventas.id_producto.';
COMMENT ON VIEW curso.clientes IS 'Clientes. id_cliente enlaza con curso.ventas.id_cliente.';
COMMENT ON VIEW curso.tiendas IS 'Tiendas. id_tienda enlaza con curso.ventas.id_tienda.';
COMMENT ON VIEW curso.fechas IS 'Calendario 2022-2024. id_fecha enlaza con curso.ventas.id_fecha.';
COMMENT ON VIEW curso.ventas IS
    'Una fila por transacción. descuento_pct es una fracción: 0.10 significa 10%.';
