-- Carga del esquema estrella a partir de los CSV oficiales de generate_data.py.
-- Equivale a src/transform/transform.py, sin dejar Spark en ejecución.
-- Rutas inyectadas por psql -v.

DROP SCHEMA IF EXISTS etl CASCADE;
CREATE SCHEMA etl;

CREATE TABLE etl.products (
    product_id    INT,
    product_name  TEXT,
    category      TEXT,
    subcategory   TEXT,
    brand         TEXT,
    unit_cost     NUMERIC(10,2),
    unit_price    NUMERIC(10,2),
    supplier      TEXT
);

CREATE TABLE etl.customers (
    customer_id    INT,
    first_name     TEXT,
    last_name      TEXT,
    email          TEXT,
    city           TEXT,
    region         TEXT,
    segment        TEXT,
    loyalty_since  DATE
);

CREATE TABLE etl.stores (
    store_id    INT,
    store_name  TEXT,
    city        TEXT,
    region      TEXT,
    country     TEXT,
    store_type  TEXT,
    sqm         INT
);

CREATE TABLE etl.sales (
    transaction_id  BIGINT,
    sale_date       DATE,
    product_id      INT,
    customer_id     INT,
    store_id        INT,
    quantity        INT,
    unit_price      NUMERIC(10,2),
    discount_pct    NUMERIC(5,4),
    gross_amount    NUMERIC(12,2),
    net_amount      NUMERIC(12,2),
    margin          NUMERIC(12,2),
    payment_method  TEXT,
    channel         TEXT
);

COPY etl.products FROM :'products_csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
COPY etl.customers FROM :'customers_csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
COPY etl.stores FROM :'stores_csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
COPY etl.sales FROM :'sales_csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

INSERT INTO dim_date (
    date_key, full_date, day_of_week, day_name, day_of_month, day_of_year,
    week_of_year, month, month_name, quarter, semester, year, is_weekend, is_holiday
)
SELECT
    to_char(d, 'YYYYMMDD')::int,
    d,
    (EXTRACT(DOW FROM d)::int + 1)::smallint,
    CASE EXTRACT(DOW FROM d)::int
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        ELSE 'Saturday'
    END,
    EXTRACT(DAY FROM d)::smallint,
    EXTRACT(DOY FROM d)::smallint,
    EXTRACT(WEEK FROM d)::smallint,
    EXTRACT(MONTH FROM d)::smallint,
    CASE EXTRACT(MONTH FROM d)::int
        WHEN 1 THEN 'January' WHEN 2 THEN 'February' WHEN 3 THEN 'March'
        WHEN 4 THEN 'April' WHEN 5 THEN 'May' WHEN 6 THEN 'June'
        WHEN 7 THEN 'July' WHEN 8 THEN 'August' WHEN 9 THEN 'September'
        WHEN 10 THEN 'October' WHEN 11 THEN 'November' ELSE 'December'
    END,
    EXTRACT(QUARTER FROM d)::smallint,
    CASE WHEN EXTRACT(MONTH FROM d) <= 6 THEN 1 ELSE 2 END::smallint,
    EXTRACT(YEAR FROM d)::smallint,
    EXTRACT(DOW FROM d)::int IN (0, 6),
    to_char(d, 'MM-DD') IN (
        '01-01', '01-06', '05-01', '08-15',
        '10-12', '11-01', '12-06', '12-08', '12-25'
    )
FROM generate_series('2022-01-01'::date, '2024-12-31'::date, '1 day') AS d;

INSERT INTO dim_product (
    product_sk, product_nk, product_name, category, subcategory, brand,
    supplier, unit_cost, unit_price, margin_pct
)
SELECT
    row_number() OVER (ORDER BY product_id),
    product_id,
    product_name,
    category,
    subcategory,
    brand,
    supplier,
    unit_cost,
    unit_price,
    ROUND((unit_price - unit_cost) / NULLIF(unit_price, 0) * 100, 2)
FROM etl.products;

INSERT INTO dim_customer (
    customer_sk, customer_nk, first_name, last_name, email,
    city, region, segment, loyalty_since
)
SELECT
    row_number() OVER (ORDER BY customer_id),
    customer_id,
    first_name,
    last_name,
    email,
    city,
    region,
    segment,
    loyalty_since
FROM etl.customers;

INSERT INTO dim_store (
    store_sk, store_nk, store_name, city, region, country, store_type, sqm
)
SELECT
    row_number() OVER (ORDER BY store_id),
    store_id,
    store_name,
    city,
    region,
    country,
    store_type,
    sqm
FROM etl.stores;

SELECT setval(pg_get_serial_sequence('dim_product', 'product_sk'), (SELECT MAX(product_sk) FROM dim_product));
SELECT setval(pg_get_serial_sequence('dim_customer', 'customer_sk'), (SELECT MAX(customer_sk) FROM dim_customer));
SELECT setval(pg_get_serial_sequence('dim_store', 'store_sk'), (SELECT MAX(store_sk) FROM dim_store));

INSERT INTO fact_sales (
    transaction_id, date_key, product_sk, customer_sk, store_sk,
    quantity, unit_price, discount_pct, gross_amount, net_amount,
    margin, margin_pct, payment_method, channel
)
SELECT
    s.transaction_id,
    to_char(s.sale_date, 'YYYYMMDD')::int,
    dp.product_sk,
    dc.customer_sk,
    ds.store_sk,
    s.quantity,
    s.unit_price,
    s.discount_pct,
    s.gross_amount,
    s.net_amount,
    s.margin,
    ROUND(s.margin / NULLIF(s.net_amount, 0) * 100, 2),
    s.payment_method,
    s.channel
FROM etl.sales s
JOIN dim_date d
    ON d.date_key = to_char(s.sale_date, 'YYYYMMDD')::int
JOIN dim_product dp
    ON dp.product_nk = s.product_id
JOIN dim_customer dc
    ON dc.customer_nk = s.customer_id
JOIN dim_store ds
    ON ds.store_nk = s.store_id;

DROP SCHEMA etl CASCADE;

ANALYZE dim_date;
ANALYZE dim_product;
ANALYZE dim_customer;
ANALYZE dim_store;
ANALYZE fact_sales;

DO $$
DECLARE
    n_sales bigint;
    n_products bigint;
    n_customers bigint;
    n_stores bigint;
    n_dates bigint;
    n_orphan bigint;
BEGIN
    SELECT COUNT(*) INTO n_sales FROM fact_sales;
    SELECT COUNT(*) INTO n_products FROM dim_product;
    SELECT COUNT(*) INTO n_customers FROM dim_customer;
    SELECT COUNT(*) INTO n_stores FROM dim_store;
    SELECT COUNT(*) INTO n_dates FROM dim_date;
    SELECT COUNT(*) INTO n_orphan
    FROM fact_sales f
    LEFT JOIN dim_product p ON p.product_sk = f.product_sk
    LEFT JOIN dim_customer c ON c.customer_sk = f.customer_sk
    LEFT JOIN dim_store s ON s.store_sk = f.store_sk
    LEFT JOIN dim_date d ON d.date_key = f.date_key
    WHERE p.product_sk IS NULL
       OR c.customer_sk IS NULL
       OR s.store_sk IS NULL
       OR d.date_key IS NULL;

    IF n_products <> 500 OR n_customers <> 2000 OR n_stores <> 50
       OR n_sales <> 50000 OR n_dates <> 1096 OR n_orphan <> 0 THEN
        RAISE EXCEPTION
            'Carga inesperada: sales=% products=% customers=% stores=% dates=% orphans=%',
            n_sales, n_products, n_customers, n_stores, n_dates, n_orphan;
    END IF;
END
$$;
