# Seguridad

## Cuenta de datos

`clase04_lectura` es `LOGIN`, sin superusuario, sin crear roles y con límite de 12 conexiones. `SELECT` sobre `curso.ventas` es verdadero. `INSERT` sobre ventas, `UPDATE` sobre productos y `SELECT` sobre `curso.clientes` son falsos. La comprobación se hizo con `has_table_privilege` el 24 de noviembre de 2026.

Los estudiantes no se modificaron. Las cuentas `estudiante46` a `estudiante90` son sintéticas, de solo lectura, y sus contraseñas quedaron solo en la VM.

## Token

HS256, emisor y audiencia `estudia-clase04`, alcance `retail:read`, `jti` nuevo en cada login, vencimiento a las cuatro horas. Un JWT de la clase 03 no pasa esta API: la prueba unitaria lo rechaza con 401. El secreto está en `/opt/estudia-clase04/infra/secrets.env`, modo 600, y no está en el repositorio.

La contraseña de PostgreSQL se usa una vez, en el login, y no se escribe en el JWT, en los logs ni en las respuestas.

## Límites

Los fallos de login se cuentan por IP, no por nombre de usuario. El usuario compartido puede abrir varias sesiones. El cupo de consultas va por `jti`: una sesión ruidosa no bloquea al resto del salón.

Las consultas son parametrizadas. El filtro `region=' OR 1=1 --` devolvió 0 filas y código 200. `POST /api/v4/ventas` devolvió 405.

Dos tokens del mismo `estudiante46` no comparten el sandbox: la segunda sesión recibió 404 al pedir la tarea de la primera. Lo mismo se comprobó con el usuario real `estudiante`: dos logins, dos `jti`, identidad `compartida`.

## TLS

El certificado de `34.95.210.33.sslip.io` lo emite Let's Encrypt (YE1). Vigencia comprobada: desde el 19 de noviembre de 2026 hasta el 17 de febrero de 2027. Caddy sigue siendo el único puerto público de la API. No se abrió PostgreSQL.

## Lo que el diseño no cubre

El sandbox vive en el proceso. Un reinicio lo borra. Con más de un worker haría falta otro almacén; el contenedor arranca con `--workers 1`.

La cuenta técnica podría leer cualquier columna de las cuatro vistas. La API no selecciona clientes, correos ni teléfonos, y la vista `curso.clientes` no tiene privilegio para esta cuenta.
