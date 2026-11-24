# 8. Paginación

Objetivo: pedir un subconjunto y decir en voz alta que es parcial.

## Petición

GET `https://34.95.210.33.sslip.io/api/v4/ventas`

Params: `region=Aragón`, `page=1`, `page_size=50`, `orden=id_transaccion`, `direccion=asc`.

`page_size` máximo: 100. No pidas las 50.000 filas.

## Qué leer en el JSON

- `page` y `page_size`: lo que pediste y lo que el servidor usó.
- `total_records` y `total_pages`: el tamaño del filtro, no de la página.
- `has_next`: si queda alguna página después de esta.

En Aragón, con `page_size=2`, el laboratorio tiene miles de filas y `has_next` en true. Tres páginas de 50 siguen siendo una parte.

## Qué no concluir

Que no haya duplicados, o que los `id_transaccion` se vean consecutivos, no demuestra que la extracción esté completa. La completitud se lee en `has_next` y en `total_pages`.

## Colab

La sección 07 recorre tres páginas, anota cuáles se pidieron, cuáles volvieron, cuántas filas trajo cada una y cuántos id distintos hay. El texto dice que la extracción es parcial.

## Si falla

422 si `page_size` es 0 o mayor que 100. 400 si `fecha_desde` es posterior a `fecha_hasta`.
