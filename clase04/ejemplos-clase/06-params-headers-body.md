# 6. Params, headers y body

Objetivo: ver que el token, el identificador y el filtro no viajan en el mismo sitio.

## Header

En una petición ya autenticada, la pestaña **Headers** muestra `Authorization`. No leas el valor en voz alta. En el cuaderno se imprime `Authorization: Bearer <oculto>`.

`Accept: application/json` pide la representación. `Content-Type: application/json` solo acompaña a un body.

## Path

GET `https://34.95.210.33.sslip.io/api/v4/productos/1`

Sin params y sin body. Esperado: 200, `Pantalón Modelo 0001`, categoría Ropa.

## Query

GET `https://34.95.210.33.sslip.io/api/v4/ventas`

Pestaña **Params**:

| Clave | Valor |
| --- | --- |
| region | Aragón |
| categoria | Hogar |
| fecha_desde | 2024-01-01 |
| fecha_hasta | 2024-12-30 |
| page | 1 |
| page_size | 2 |
| orden | id_transaccion |
| direccion | asc |

Esperado: 200, `pagination.total_records` mayor que cero y filas con `id_transaccion`.

Regiones reales: Andalucía, Aragón, Castilla y León, Cataluña, Comunidad de Madrid, Comunitat Valenciana, País Vasco.

Categorías reales: Alimentación, Deportes, Electrónica, Hogar, Ropa.

## La frase

«`/productos/1` es un recurso. `/ventas?region=Aragón&page=1&page_size=2` es una página de un listado.»

## Si falla

401: falta el Bearer. 422: `page_size` fuera de 1 a 100. Lista vacía con 200: la región o la tilde no coinciden; no es un fallo de red.

## Sin Postman

Swagger, mismos campos en Try it out. Colab, secciones 04 y 05, con `params={...}`.
