# Resultados de las pruebas

Fecha: 26 de noviembre de 2026. Máquina Windows. Motor de Docker Desktop apagado.

## Lo que sí corrió

| Prueba | Resultado |
|---|---|
| `pytest tests/test_medallion.py` | 5 passed |
| Fixture correcto, dos pasadas | 2 filas, el importe negativo se conserva, un solo `pagina_1.json` |
| Fixture con id duplicado | falla antes de crear gold |
| DAG de práctica vacío | se importa y se detiene en `COMPLETA` sin llamar a la red |
| DAG de práctica rellenado, con fixture | 2 transacciones, alcance parcial |
| Pipeline del profesor contra la API, usuario `estudiante` | 200 filas, alcance parcial, `total_records` 5018, sin token en bronze ni en el manifiesto |
| Cuaderno del profesor con nbclient | salud `estudia-clase04`, login bearer 14400, 2 páginas, 200 filas, promedio 1545.01, todo Aragón |
| Copia rellenada del cuaderno de práctica, modo respaldo | 2 filas, alcance `respaldo`, importe negativo conservado |
| `GET /api/v4/health` | 200, `estudia-clase04` |
| `GET /health` | 200, `estudia-clase03` |
| `docker compose config` | válido. Servicios: postgres, airflow-init, airflow-apiserver, airflow-scheduler, airflow-dag-processor |

El escaneo de `clase05/` no encontró un JWT ni el archivo de contraseñas de estudiantes. La contraseña del usuario compartido no se imprimió.

## Lo que no corrió

El motor de Docker no estaba encendido. No se construyó la imagen, no se migró la base, no arrancaron los contenedores y no se abrió `http://127.0.0.1:8080`. No se midió el tamaño de la descarga ni la RAM real del laboratorio. No se probó la interfaz gráfica de Airflow, Docker Desktop, Windows con WSL2 ni Colab en el navegador.

El DAG resuelto no se copió a la VM de la clase 03. No se crearon recursos de GCP ni se cambió el tamaño de las VM.

Newman no participa en esta clase.
