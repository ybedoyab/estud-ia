# Clase 04 — APIs REST, Postman y extracción

Los estudiantes consumen una API de solo lectura. No la implementan y no modifican las ventas.

La URL pública, ya comprobada, es `https://34.95.210.33.sslip.io/api/v4`. Swagger está en `https://34.95.210.33.sslip.io/api/v4/docs`.

El login usa el mismo usuario y la misma contraseña de PostgreSQL. El token dura cuatro horas, va en `Authorization: Bearer` y solo autoriza lectura (`retail:read`). El usuario compartido `estudiante` puede entrar. Cada login abre una sesión distinta.

## Materiales

| Pieza | Ruta |
|---|---|
| API | `clase04/backend/` |
| Colección de Postman | `clase04/postman/` |
| Notebook | `clase04/notebooks/EstudIA_Clase04_APIs_REST_Postman.ipynb` |
| JSON de respaldo | `clase04/examples/json/` |
| Extractor de ejemplo | `clase04/examples/python/extraer_ventas.py` |
| DAG docente, no desplegado | `clase04/examples/airflow/estudia_clase04_demo_api.py` |
| Guías | `clase04/docs/` |
| Encendido | `clase04/infra/start.ps1` |

## Operación

Desde esta máquina, con `gcloud` autenticado como `fastex.999@gmail.com`:

```powershell
./clase04/infra/status.ps1
./clase04/infra/start.ps1
./clase04/infra/stop.ps1
./clase04/infra/smoke_test.ps1
```

Eso solo enciende o apaga el contenedor de la clase 04. PostgreSQL y Airflow siguen su propio ciclo. El tope de 40.000 COP del proyecto sigue activo: si el gasto del mes llega al tope, las dos VM se detienen.

La base `estudia-postgres-lab` estaba apagada y se encendió para esta clase. Con las VM apagadas se sigue cobrando disco e IP.
