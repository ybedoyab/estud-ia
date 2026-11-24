# Resultados

Fecha de la comprobación: 24 de noviembre de 2026.

## Unitarias

13 pruebas de pytest, en local, sin base de datos, el 24 de noviembre de 2026 por la noche. Cubren login, dos sesiones del usuario compartido, rechazo de un JWT ajeno, token vencido, 400, 401, 403, 404, 405, 422, 429, 500, 503, el aislamiento del sandbox y el esquema Bearer de OpenAPI. Resultado: 13 passed. Health y login quedan fuera de `security`. `GET /api/v4/productos` lo exige. `LoginBody` sigue pidiendo `username` y `password`.

## Humo contra la URL pública

`GET /api/v4/health` → 200, servicio `estudia-clase04`.

`GET /health` → 200, servicio `estudia-clase03`.

Login de `estudiante46` → 200, `expires_in` 14400, alcance `retail:read`.

`GET /api/v4/productos?page=1&page_size=1` → el primer producto es `1`, `Pantalón Modelo 0001`.

`GET /api/v4/ventas/1` → la transacción real del 2024-07-11, producto 425, tienda 34.

`GET /api/v4/ventas?region=Aragón&page=1&page_size=2` → 5018 registros, 2509 páginas, `has_next` verdadero.

`POST /api/v4/ventas` → 405.

Filtro `' OR 1=1 --` → 200 y 0 filas.

## Seguridad de sesión

| Caso | Código |
|---|---|
| Contraseña incorrecta | 401 |
| Sin token | 401 |
| Token ilegible | 401 |
| Producto 999999 | 404 |
| `page_size=0` | 422 |
| Fechas cruzadas | 400 |
| `/api/v4/ejemplos/prohibido` | 403 |
| `/api/v4/ejemplos/demasiado-rapido` | 429 |
| `/api/v4/ejemplos/error-interno` | 500 |
| `/api/v4/ejemplos/no-disponible` | 503 |
| Segunda sesión pide la tarea de la primera | 404 |
| Usuario real `estudiante`, dos logins | 200, sesiones distintas, identidad `compartida` |

## Notebook

La versión anterior, de 30 celdas, se ejecutó con `nbclient` y la cuenta `estudiante46` dentro de un contenedor en la VM.

La versión de 48 celdas se ejecutó el 24 de noviembre de 2026 por la noche, con `nbclient` y el intérprete local, contra la API pública y el usuario compartido `estudiante`. Terminaron las 48 celdas. Identidad `compartida`, sesiones distintas, códigos 200, 201, 204, 400, 401, 403, 404, 405, 422, 429, 500 y 503, y el resumen final en OK. Las salidas y los archivos no contenían token ni contraseña.

Una copia del mismo cuaderno, fuera del repositorio, se ejecutó en modo respaldo. Terminó, etiquetó los resultados como `RESPALDO` y dejó el resumen en NO. No se mezcló con la corrida en vivo.

No se abrió Google Colab en el navegador. No se usó Postman gráfico. Newman no está instalado y no se ejecutó. No se repitió la prueba de 45 usuarios: el único cambio de la API fue el esquema de seguridad en el documento OpenAPI.

## OpenAPI público

`GET /api/v4/openapi.json` respondió 200. El esquema `HTTPBearer` está declarado. No aparece en health ni en el login. Sí aparece en productos. `GET /api/v4/health` y `GET /health` siguieron en 200 después de recrear el contenedor, sin regenerar secretos.

## Carga

Locust 2.32.4, 45 usuarios, rampa de 9 por segundo, 10 minutos, espera entre 0,4 y 1,2 segundos. Cero fallos en los dos escenarios. El contenedor tenía 1 CPU y el pool 8 conexiones. Durante la pasada anterior, con media CPU, las conexiones activas de `clase04_lectura` se mantuvieron entre 6 y 8 y el contenedor no pasó de una cuarta parte del host.

Cuentas individuales `estudiante46` a `estudiante90`, 11.753 peticiones, 19,6 por segundo:

| Ruta | p50 | p95 | Fallos |
|---|---:|---:|---:|
| POST /api/v4/auth/login | 370 ms | 770 ms | 0 |
| GET /api/v4/productos | 1.300 ms | 2.500 ms | 0 |
| GET /api/v4/ventas/muestra | 930 ms | 1.600 ms | 0 |
| GET /api/v4/indicadores/ventas-por-categoria | 1.200 ms | 2.000 ms | 0 |
| GET /api/v4/ventas | 1.700 ms | 2.700 ms | 0 |
| GET /api/v4/ventas?page=2 | 2.500 ms | 3.700 ms | 0 |

Misma cuenta `estudiante46` en las 45 sesiones, 9.996 peticiones, 16,7 por segundo. El p95 de productos fue 2.600 ms y el de la muestra 1.700 ms. Tampoco hubo fallos.

El objetivo de p95 menor a dos segundos se cumple en la muestra y en el login. No se cumple en el listado de productos ni en el de ventas. Subir el contenedor de media CPU a una CPU no corrigió esa cola: el proceso quedó cerca del 28 % del host, así que el tiempo está del lado de la espera por PostgreSQL en la VM `e2-medium`. No se cambió el tamaño de esa máquina.
