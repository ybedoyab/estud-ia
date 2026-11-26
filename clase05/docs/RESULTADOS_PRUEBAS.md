# Resultados de las pruebas

Fecha: 26 de noviembre de 2026. Windows, Docker Desktop 4.92.0, motor 29.8.0, contenedores linux/amd64. La VM de Docker tenía 7.44 GiB y 16 CPU.

## Laboratorio Docker

| Prueba | Resultado |
|---|---|
| `docker compose config` | válido. Servicios: postgres, airflow-init, airflow-apiserver, airflow-scheduler, airflow-dag-processor |
| Construcción | imagen `apache/airflow:3.4.0` más pandas 3.1.0 y requests 2.34.2, que ya venían en esa imagen |
| Tamaño en disco | Airflow 3.22 GB. Las cuatro etiquetas comparten capas. Postgres 16.6 ocupa 617 MB |
| `airflow db migrate` | terminó |
| `http://127.0.0.1:8080/api/v2/monitor/health` | respondió. Metadatos, scheduler y dag processor en healthy. Triggerer en down, porque este laboratorio no lo arranca |
| Importación | sin errores. Los dos DAG nacen en pausa |
| Práctica sin rellenar | `extraer_api` falla con el aviso de `COMPLETA` y no llama a la API |
| Fallo controlado | `id_transaccion duplicado`. Se vio `up_for_retry` y luego `failed`, con `attempt=2.log` |
| DAG del profesor, API real, usuario `estudiante` | success. 200 filas, alcance parcial, 5018 en el filtro, promedio 1545.00865. Sin token en `data/` ni en el log |
| Misma corrida, limpiada y relanzada | otra vez success, siguen 2 páginas y 200 filas |
| `detener` y `iniciar` | el manifiesto y la Connection siguieron. PostgreSQL no publica puerto en el host |
| RAM observada | api-server 298 MiB, scheduler 463 MiB, dag processor 223 MiB, postgres 63 MiB |

El health se consultó con `curl`. No se abrió el navegador ni se hizo clic en la interfaz.

## Lo demás, ya medido antes de encender Docker

| Prueba | Resultado |
|---|---|
| `pytest tests/test_medallion.py` | 5 passed |
| Cuaderno del profesor con nbclient | salud `estudia-clase04`, login bearer 14400, 200 filas |
| Copia rellenada del cuaderno de práctica, modo respaldo | 2 filas, alcance `respaldo` |
| `GET /api/v4/health` | 200, `estudia-clase04` |
| `GET /health` | 200, `estudia-clase03` |

No se midió el ZIP de descarga comprimido, aparte del tamaño que las imágenes ocupan en disco. No se probó Colab en el navegador ni la ventana de Docker Desktop. El DAG no se copió a la VM de la clase 03. No se crearon recursos de GCP.
