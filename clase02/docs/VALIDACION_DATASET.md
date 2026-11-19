# Validación del dataset

Fuente: [oleong/retail-data-warehouse](https://github.com/oleong/retail-data-warehouse), commit `191fd84ad1eb7c890f6b3a83556d7bc583c29f42`, licencia MIT.

Los CSV salen de `data/raw/generate_data.py` (semilla 42). El esquema estrella se construye en SQL con la misma lógica que `src/transform/transform.py`: `row_number()` como surrogate key y `date_key` `YYYYMMDD`. Spark, Java y el venv de generación se eliminaron después de crear los CSV. En la VM solo quedan PostgreSQL y PgBouncer.

## Tamaño y filas

| Objeto | Filas |
|---|---:|
| `public.fact_sales` / `curso.ventas` | 50 000 |
| `public.dim_customer` / `curso.clientes` | 2 000 |
| `public.dim_product` / `curso.productos` | 500 |
| `public.dim_store` / `curso.tiendas` | 50 |
| `public.dim_date` / `curso.fechas` | 1 096 |
| Base `retail_dwh` | 18 MB |

Fechas: 2022-01-01 a 2024-12-31 (2022, 2023 y 2024). Hay columnas `es_fin_de_semana` y `es_festivo` (festivos fijos de España definidos por el proyecto original).

## Llaves

| Tabla | PK | FK |
|---|---|---|
| `dim_date` | `date_key` | |
| `dim_product` | `product_sk` | |
| `dim_customer` | `customer_sk` | |
| `dim_store` | `store_sk` | |
| `fact_sales` | `transaction_id` | `date_key`, `product_sk`, `customer_sk`, `store_sk` |

La carga aborta si alguna venta queda sin dimensión. Los `JOIN` de `curso` usan esas mismas llaves con alias en español.

## Valores útiles para la clase

Categorías, 100 productos cada una: Alimentación, Deportes, Electrónica, Hogar, Ropa.

Segmentos de cliente: Estándar 1 105, Ocasional 591, Premium 304.

Canales: Tienda 25 027, Online 17 442, App 7 531.

Métodos de pago: Tarjeta 27 460, Bizum 9 046, Efectivo 7 539, PayPal 5 955.

Tiendas por región: Andalucía 15, Comunitat Valenciana 10, y 5 en Aragón, Castilla y León, Cataluña, Comunidad de Madrid y País Vasco. El tipo de tienda es Flagship, Standard o Express.

El generador elige categoría y subcategoría con el mismo índice, así que cada categoría quedó con una sola subcategoría: Ropa/Pantalón, Hogar/Almohada, Alimentación/Arroz, Deportes/Botella, Electrónica/Smartphone. No se inventaron filas para “corregirlo”. Sigue habiendo volumen suficiente para filtros, agregaciones, JOIN, fechas y ventanas.

`descuento_pct` se guarda como fracción (`0.10` = 10 %), igual que en el CSV original.
