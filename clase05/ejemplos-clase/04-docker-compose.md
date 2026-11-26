# Compose de esta clase

Servicios:

| Servicio | Comando | Puerto en el portátil |
|---|---|---|
| postgres | Postgres 16.6 | ninguno |
| airflow-init | `airflow db migrate` | ninguno, se apaga al terminar |
| airflow-apiserver | `api-server` | `127.0.0.1:8080` |
| airflow-scheduler | `scheduler` | ninguno |
| airflow-dag-processor | `dag-processor` | ninguno |

No está Redis. No está Celery. No está el triggerer: las tareas de esta clase no se aplazan.

Los volúmenes `dags`, `logs` y `data` se ven en la carpeta del laboratorio. `postgres-db` se queda dentro de Docker.

`preparar` construye la imagen propia. Airflow 3.4.0 ya trae pandas 3.1.0 y requests 2.34.2; el Dockerfile deja esas versiones fijas.
