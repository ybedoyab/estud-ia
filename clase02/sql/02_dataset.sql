-- Esquema estrella de oleong/retail-data-warehouse (MIT).
-- Fuente: sql/retail_dwh_ddl.sql del commit 191fd84ad1eb7c890f6b3a83556d7bc583c29f42.
-- Las tablas viven en public y no se exponen a los estudiantes.

CREATE SCHEMA IF NOT EXISTS public;

DROP TABLE IF EXISTS fact_sales CASCADE;
DROP TABLE IF EXISTS dim_product CASCADE;
DROP TABLE IF EXISTS dim_customer CASCADE;
DROP TABLE IF EXISTS dim_store CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;

CREATE TABLE dim_date (
    date_key       INT          NOT NULL,
    full_date      DATE         NOT NULL,
    day_of_week    SMALLINT,
    day_name       VARCHAR(10),
    day_of_month   SMALLINT,
    day_of_year    SMALLINT,
    week_of_year   SMALLINT,
    month          SMALLINT,
    month_name     VARCHAR(12),
    quarter        SMALLINT,
    semester       SMALLINT,
    year           SMALLINT,
    is_weekend     BOOLEAN,
    is_holiday     BOOLEAN,
    CONSTRAINT pk_dim_date PRIMARY KEY (date_key)
);

COMMENT ON TABLE dim_date IS
    'Date dimension — one row per calendar day 2022-01-01 to 2024-12-31.';

CREATE TABLE dim_product (
    product_sk    SERIAL       NOT NULL,
    product_nk    INT          NOT NULL,
    product_name  VARCHAR(200),
    category      VARCHAR(100),
    subcategory   VARCHAR(100),
    brand         VARCHAR(100),
    supplier      VARCHAR(100),
    unit_cost     NUMERIC(10,2),
    unit_price    NUMERIC(10,2),
    margin_pct    NUMERIC(6,2),
    CONSTRAINT pk_dim_product PRIMARY KEY (product_sk),
    CONSTRAINT uq_product_nk  UNIQUE     (product_nk)
);

COMMENT ON TABLE dim_product IS
    'Product dimension — SCD Type 1 (overwrite on each pipeline run).';

CREATE TABLE dim_customer (
    customer_sk    SERIAL      NOT NULL,
    customer_nk    INT         NOT NULL,
    first_name     VARCHAR(100),
    last_name      VARCHAR(100),
    email          VARCHAR(200),
    city           VARCHAR(100),
    region         VARCHAR(100),
    segment        VARCHAR(50),
    loyalty_since  DATE,
    CONSTRAINT pk_dim_customer PRIMARY KEY (customer_sk),
    CONSTRAINT uq_customer_nk  UNIQUE     (customer_nk)
);

CREATE TABLE dim_store (
    store_sk    SERIAL      NOT NULL,
    store_nk    INT         NOT NULL,
    store_name  VARCHAR(200),
    city        VARCHAR(100),
    region      VARCHAR(100),
    country     VARCHAR(100),
    store_type  VARCHAR(50),
    sqm         INT,
    CONSTRAINT pk_dim_store PRIMARY KEY (store_sk),
    CONSTRAINT uq_store_nk  UNIQUE     (store_nk)
);

CREATE TABLE fact_sales (
    transaction_id  BIGINT        NOT NULL,
    date_key        INT           NOT NULL,
    product_sk      INT           NOT NULL,
    customer_sk     INT           NOT NULL,
    store_sk        INT           NOT NULL,
    quantity        INT,
    unit_price      NUMERIC(10,2),
    discount_pct    NUMERIC(5,4),
    gross_amount    NUMERIC(12,2),
    net_amount      NUMERIC(12,2),
    margin          NUMERIC(12,2),
    margin_pct      NUMERIC(6,2),
    payment_method  VARCHAR(50),
    channel         VARCHAR(50),
    CONSTRAINT pk_fact_sales   PRIMARY KEY (transaction_id),
    CONSTRAINT fk_date         FOREIGN KEY (date_key)    REFERENCES dim_date     (date_key),
    CONSTRAINT fk_product      FOREIGN KEY (product_sk)  REFERENCES dim_product  (product_sk),
    CONSTRAINT fk_customer     FOREIGN KEY (customer_sk) REFERENCES dim_customer (customer_sk),
    CONSTRAINT fk_store        FOREIGN KEY (store_sk)    REFERENCES dim_store    (store_sk)
);

COMMENT ON TABLE fact_sales IS
    'Fact table — one row per sales transaction line. ~50 000 rows for the demo.';

CREATE INDEX idx_fact_date     ON fact_sales (date_key);
CREATE INDEX idx_fact_product  ON fact_sales (product_sk);
CREATE INDEX idx_fact_customer ON fact_sales (customer_sk);
CREATE INDEX idx_fact_store    ON fact_sales (store_sk);
CREATE INDEX idx_fact_channel  ON fact_sales (channel);
CREATE INDEX idx_fact_payment  ON fact_sales (payment_method);
