# Guía del estudiante

Vas a consumir una API. No vas a programarla ni a cambiar las ventas. El usuario y la contraseña son los de PostgreSQL. Sirve `estudianteNN` o el compartido `estudiante`.

Hay tres formas de hacer el mismo recorrido. Elige una. Si no puedes instalar programas, usa la segunda y la tercera.

## 1. Postman, a mano

No importes la colección al empezar.

1. New → HTTP. Deja el método en GET.
2. URL: `https://jsonplaceholder.typicode.com/posts/1`. Send. El status debe ser 200.
3. Cambia la URL a `https://34.95.210.33.sslip.io/api/v4/health`. Send. Debe decir `estudia-clase04`.
4. Cambia el método a POST. URL: `https://34.95.210.33.sslip.io/api/v4/auth/login`.
5. Body → raw → JSON:

```json
{"username": "estudiante01", "password": "tu contraseña de PostgreSQL"}
```

6. Authorization de esta petición: No Auth. Send.
7. El status debe ser 200. Anota `token_type` (`bearer`), `expires_in` (14400) y `scope` (`retail:read`). Copia `access_token` y no lo pegues en el chat.
8. Nueva petición GET a `https://34.95.210.33.sslip.io/api/v4/auth/me`. Authorization → Bearer Token. Pega solo el token. Send.
9. GET `https://34.95.210.33.sslip.io/api/v4/productos`. En Params: `page` = 1, `page_size` = 5.
10. Cambia la URL a `https://34.95.210.33.sslip.io/api/v4/productos/1`.
11. GET `https://34.95.210.33.sslip.io/api/v4/ventas` con Params `region=Aragón`, `categoria=Hogar`, `page=1`, `page_size=2`.
12. El sandbox está en `https://34.95.210.33.sslip.io/api/v4/sandbox/tareas`: GET, POST, GET del id que te devuelva, PUT, PATCH y DELETE. El DELETE responde 204 y no trae JSON.
13. Quita el token y pide productos. Tiene que responder 401.

Al final de la clase puedes importar `clase04/postman/EstudIA_Clase04.postman_collection.json` y el environment. El environment no trae contraseña. No lo exportes después de escribirla.

## 2. Swagger, sin instalar nada

Abre `https://34.95.210.33.sslip.io/api/v4/docs`.

1. Ejecuta `GET /api/v4/health`. No pide token.
2. Abre `POST /api/v4/auth/login`, pulsa Try it out y envía tu usuario y contraseña.
3. Copia el `access_token`. Pulsa **Authorize**, pégalo sin la palabra Bearer y cierra el cuadro.
4. Prueba productos, una venta, el sandbox y los ejemplos de error en el mismo orden que Postman.

Health y login no usan Authorize. El resto de las operaciones sí. El contrato completo, si quieres verlo como archivo, es `https://34.95.210.33.sslip.io/api/v4/openapi.json`.

## 3. Colab

Abre `clase04/notebooks/EstudIA_Clase04_APIs_REST_Postman.ipynb`, guárdalo en tu Drive y ejecuta las celdas en orden. No hace falta clonar el repositorio ni instalar Postman, Docker, PostgreSQL o Airflow.

La contraseña se pide con `getpass` y no queda escrita. El token se queda en memoria. Las secciones van de la 00 a la 13: salud, una API pública, el contrato, login, GET, filtros, sandbox, páginas, JSON anidado, Pandas, errores, archivos, reto y el esquema de un pipeline.

Si una celda te pide completar algo, el enunciado trae el objetivo y una pista. Después de intentarlo puedes ejecutar `ver_solucion("02")`, `ver_solucion("04")`, `ver_solucion("06")`, `ver_solucion("08")` o `ver_solucion("12")`.

No bajes las 50.000 ventas. La práctica pide unas pocas páginas y una muestra de 200. Si `has_next` es verdadero, la extracción es parcial aunque no veas ids repetidos.

El resumen final solo marca OK lo que tu ejecución hizo de verdad.

## Si la API no responde

No disimules el fallo. La celda de salud lo imprime. Si el docente lo autoriza, cambia `USAR_RESPALDO` a `True` y vuelve a ejecutar esa celda. Los resultados dirán `RESPALDO` y no cuentan como consulta en vivo. Esos ejemplos viajan dentro del cuaderno: no dependen de que tengas el repositorio. No los mezcles con una tabla que sí vino de la API.

## Errores que vas a provocar a propósito

Un 429 trae `Retry-After`. Puedes esperar y repetir un GET una o dos veces. No reintentes POST, PUT, PATCH ni DELETE. Un 500 de `/api/v4/ejemplos/error-interno` es una demostración, no una caída.
