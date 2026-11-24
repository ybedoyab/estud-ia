# 2. OpenAPI, Swagger y el contrato

Objetivo: leer una operación en el contrato real, sin adivinar nombres de campos.

## Dónde está

- Especificación: `GET https://34.95.210.33.sslip.io/api/v4/openapi.json`
- Swagger: `https://34.95.210.33.sslip.io/api/v4/docs`

OpenAPI es el documento. Swagger UI es la página que lo muestra y deja probarlo. Postman es un cliente. No son sinónimos.

## Qué abrir en Swagger

1. `GET /api/v4/productos`. Los query params `page` y `page_size` no son obligatorios.
2. `GET /api/v4/productos/{id_producto}`. El id del path sí es obligatorio.
3. `POST /api/v4/auth/login`. El cuerpo tiene `$ref` a `LoginBody`. `username` y `password` están en `required`.
4. `GET /api/v4/ventas`. `region`, `categoria`, fechas, `page` y `page_size` salen como opcionales.

Un esquema dice tipos, campos y restricciones. En esta API el estado de una tarea solo admite `pendiente`, `en_progreso` y `hecha`.

## Authorize

El botón **Authorize** aparece porque el contrato declara el esquema `HTTPBearer`, un JWT. Health y login no lo piden. El resto sí.

Pega el `access_token` sin la palabra Bearer. No cambia los permisos: solo documenta el header que la API ya exigía.

## Pregunta

«¿Qué código de respuesta está escrito en el login además del 200?»

422, cuando el cuerpo no cumple el esquema.

## Si no tienen Postman

Se quedan en Swagger. En Colab, la sección 02 lista título, versión, rutas y el `$ref` del login sin volcar el archivo entero. El ejercicio 02 pide un GET, un POST, un requerido, un opcional y un código. `ver_solucion("02")` está en el cuaderno.
