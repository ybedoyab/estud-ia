# Medallion

| Capa | Qué guarda | Qué no guarda |
|---|---|---|
| bronze | JSON de cada página, filtros, número de página, `page_size`, conteos, alcance | login, token, headers |
| silver | CSV con `id_transaccion`, `fecha`, `cantidad`, `importe_neto`, `categoria`, `region` | diccionarios anidados |
| gold | importe por categoría, importe por región, transacciones, promedio | el censo de 50.000 |
| reports | los mismos indicadores y `manifiesto.json` | contraseñas |

`/ventas` es plano. `/ventas/muestra` trae `producto` y `tienda` dentro. Este pipeline usa dos páginas planas, 100 filas cada una como máximo.

El alcance queda en `parcial` mientras `filas` sea menor que `total_records`.

La escritura pasa por un archivo temporal y `os.replace`, en el volumen `data/`, no en `/tmp`.
