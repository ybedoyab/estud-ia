# Arquitectura

Laboratorio local. No crea una VM por estudiante.

```text
Postman / navegador
        |
        v
Airflow en 127.0.0.1:8080
  api-server
  scheduler
  dag-processor
  postgres de metadatos, sin puerto publicado
        |
        | HTTPS, token de un solo uso en la tarea
        v
https://34.95.210.33.sslip.io/api/v4
        |
        v
data/bronze  JSON de páginas
data/silver  CSV plano
data/gold    indicadores de esa extracción
data/reports manifiesto
```

El ejecutor es LocalExecutor. No hay Redis ni Celery. El procesador de DAGs es un servicio aparte porque Airflow 3.4 separa el parseo del scheduler.

La base `postgres:16.6` solo guarda metadatos de Airflow. La contraseña `estudia_meta_local` vive en la red de Compose y no sale al host. El dataset del curso sigue en GCP y esta clase no le abre puertos nuevos.

`/ventas` devuelve filas planas (`categoria`, `region`). `/ventas/muestra` anida `producto` y `tienda`. El pipeline de esta clase pagina `/ventas`. El cuaderno enseña la diferencia. Gold no mezcla las dos formas.

Cada ejecución escribe en un directorio con el `run_id` saneado. Un reintento reemplaza esos archivos. No usa `/tmp` del contenedor. XCom solo devuelve el identificador de la corrida.

El DAG nace con `schedule=None`, `catchup=False`, `max_active_runs=1` y una pausa. Un cron opcional se documenta y no se enciende para los 45 cursos.

Quien no usa Docker ejecuta las mismas funciones en Colab. Eso no deja un scheduler.
