# Arquitectura

Proyecto GCP: `drafty-autopilot-fx`, cuenta `fastex.999@gmail.com`, región `southamerica-east1`.

Hay dos VM y no comparten base de datos.

| VM | Tipo | IP | Función |
|---|---|---|---|
| `estudia-postgres-lab` | e2-medium | pública `34.39.202.205`, interna `10.20.0.2` | PostgreSQL 16 y PgBouncer. La clase 02 no se modifica. |
| `estudia-airflow-clase03` | e2-standard-2, 8 GB, disco 30 GB | pública `34.95.210.33`, interna `10.20.0.3` | Airflow 3.4.0, FastAPI y Caddy |

```text
Colab
  |  SQL por TLS al puerto 6432, con el usuario individual
  |  HTTPS a la API, con un token de 4 horas
API FastAPI
  |  comprueba la contraseña abriendo una sesión real en PostgreSQL
  |  no guarda esa contraseña
  |  escribe un JSON validado y un DAG generado
Airflow 3.4.0, LocalExecutor
  |  metadata en Postgres 16, contenedor propio de esta VM
  |  lee curso.* con el rol airflow_lectura, solo SELECT
  |  escribe el CSV en el directorio de ese estudiante
```

El certificado HTTPS lo emite Let's Encrypt para `34.95.210.33.sslip.io` y `airflow.34.95.210.33.sslip.io`. Caddy lo renueva solo.

Los DAG de estudiantes se pausan a las 21:00, hora de Bogotá. `catchup` está apagado: al volver a encender la VM no se reponen las corridas que no ocurrieron.

Airflow usa un pool `clase03` de 6 ranuras y paralelismo 8, para que las corridas de la clase no se amontonen todas a la vez.
