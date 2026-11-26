# EstudIA — Clase 05

Airflow local con Docker y un pipeline Medallion sobre la API de la clase 04.

La interfaz queda en [http://127.0.0.1:8080](http://127.0.0.1:8080). No hace falta Git ni Python instalados en el portátil: Docker Desktop basta. Si Docker no se puede instalar, el camino es `notebooks/EstudIA_Clase05_PRACTICA.ipynb`.

## Versiones fijadas

| Pieza | Versión |
|---|---|
| Airflow | `apache/airflow:3.4.0` |
| Metadatos | `postgres:16.6`, LocalExecutor |
| Pandas | 2.2.3 |
| Requests | 2.32.3 |

No se usa la etiqueta `latest`. No hay Redis ni Celery.

## Orden

```powershell
cd clase05
.\scripts\preparar.ps1
.\scripts\iniciar.ps1
.\scripts\comprobar.ps1
```

En Linux o macOS: `./scripts/preparar.sh`, `./scripts/iniciar.sh`, `./scripts/comprobar.sh`.

Usuario de la interfaz: `admin`. Contraseña: `AIRFLOW_ADMIN_PASSWORD` de `.env` (`estudia-local` si no la cambias). Esa clave solo abre Airflow en tu máquina.

Connection `estudia_api`: tipo HTTP, host `34.95.210.33.sslip.io`, schema `https`, login y contraseña de PostgreSQL. El DAG `estudia_clase05_api_medallion` nace en pausa.

Para apagar: `.\scripts\detener.ps1`.

El ZIP para quien no clona el repositorio se arma con `.\scripts\empaquetar.ps1`. No incluye la solución de `profesor/`.
