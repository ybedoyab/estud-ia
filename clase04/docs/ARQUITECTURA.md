# Arquitectura de la clase 04

## Decisión

Se eligió un contenedor FastAPI independiente en la VM `estudia-airflow-clase03`, detrás del Caddy que ya termina HTTPS. La ruta pública es `https://34.95.210.33.sslip.io/api/v4`.

Cloud Run quedaría aislado, pero PostgreSQL solo escucha en la red interna `10.20.0.2:6432`. Llegar desde Cloud Run exigiría un conector de red y otro servicio de pago. La VM, un `e2-standard-2` con unos 5,7 GB libres antes del contenedor, alcanza para un proceso adicional de 256 MB y 1 CPU. Se probó primero con media CPU: el login mejoró al subir el límite, y las listas siguieron por encima de dos segundos en el percentil 95. No se creó otra base ni se cambió el tamaño de las máquinas.

## Qué no cambia

La API de la clase 03 sigue en el mismo dominio, fuera de `/api/v4`. Su login, sus DAG y el bloqueo del usuario compartido `estudiante` para publicar pipelines no se modificaron. `/health` sigue respondiendo `estudia-clase03`.

## Recorrido de una consulta

```text
Postman o Colab
  → HTTPS (Caddy, Let's Encrypt)
  → contenedor clase04, un solo worker
  → JWT con audiencia estudia-clase04
  → pool de hasta 6 conexiones
  → PgBouncer (pool_mode transaction, puerto 6432)
  → PostgreSQL retail_dwh
  → vistas curso.productos, curso.tiendas, curso.fechas, curso.ventas
```

El login abre una conexión corta con el usuario del estudiante, solo para comprobar la contraseña. Las consultas de datos usan la cuenta `clase04_lectura`. Esa cuenta no hereda `rol_estudiante`: tiene `SELECT` sobre las cuatro vistas educativas y no puede leer `curso.clientes`.

## Sesión y sandbox

Cada login firma un JWT de cuatro horas con `jti` propio. Dos personas con el usuario `estudiante` obtienen dos sesiones. El sandbox guarda tareas en memoria, separadas por ese `jti`, con un máximo de 30 y el mismo vencimiento del token. Como el proceso es uno solo, no hace falta un almacén compartido. Si el contenedor se reinicia, las tareas ficticias desaparecen. No tocan `retail_dwh`.

PgBouncer está en modo transacción. El pool de la API desactiva las sentencias preparadas de psycopg para no romper ese modo.
