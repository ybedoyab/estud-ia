# 9. JSON anidado y Pandas en Colab

Objetivo: abrir la venta 1, normalizarla y analizar una muestra de 200 sin confundirla con las 50.000.

## Venta anidada

GET `https://34.95.210.33.sslip.io/api/v4/ventas/1`

La raíz es un diccionario. `producto` y `tienda` son diccionarios dentro. Una lista aparecería si pidiéramos una página de ventas.

La clave es `id_transaccion`. No hay `id_venta`.

`pd.DataFrame([venta])` deja los objetos anidados como celdas. `pd.json_normalize(venta)` abre `producto.nombre` y `tienda.region`.

El cuaderno, sección 08, lo muestra con la venta en vivo. `ver_solucion("08")` recuerda la clave.

## Muestra

GET `https://34.95.210.33.sslip.io/api/v4/ventas/muestra?limite=200`

`limite` solo acepta de 100 a 300. La sección 09 convierte `data` con `json_normalize` y recorre:

- `head` y `shape`
- `info`
- `isna().sum()`
- `duplicated(subset="id_transaccion").sum()`
- `importe_neto` medio
- `groupby("producto.categoria")`, `sum` y `sort_values`
- un gráfico de barras horizontales

Al lado, `GET /api/v4/indicadores/resumen` trae el ticket promedio de las 50.000 transacciones. Esa cifra y la media de la muestra no describen la misma población.

## Sin conexión

Si el docente autoriza el respaldo, el cuaderno usa ejemplos embebidos y los marca `RESPALDO`. Esos archivos no se mezclan con una tabla que sí vino de la API.
