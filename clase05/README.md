# EstudIA — Clase 05

Práctica para construir Docker, Airflow y un pipeline Medallion. Los archivos con huecos están en `plantillas/`. La raíz de este repositorio ya trae la infraestructura y los DAG resueltos para el docente. El ZIP del estudiante no los incluye.

La interfaz, cuando el entorno ya está arriba, queda en [http://127.0.0.1:8080](http://127.0.0.1:8080). Si ese puerto está ocupado, cambia `AIRFLOW_WEB_PORT`. No hace falta Git ni Python en el portátil. Si Docker no se puede instalar, el camino es `notebooks/EstudIA_Clase05_PRACTICA.ipynb`. Completar ese cuaderno no despliega contenedores.

## Versiones fijadas

| Pieza | Versión |
|---|---|
| Airflow | `apache/airflow:3.4.0` |
| Metadatos | `postgres:16.6`, LocalExecutor |
| Pandas | 3.1.0 |
| Requests | 2.34.2 |

No se usa `latest`. No hay Redis ni Celery.

## Orden del estudiante

1. Completar `plantillas/infraestructura/`.
2. `.\scripts\validar_infraestructura.ps1`
3. `.\scripts\activar_infraestructura.ps1`
4. `.\scripts\preparar.ps1`, `.\scripts\iniciar.ps1`, `.\scripts\comprobar.ps1`
5. Completar `plantillas/dags/`.
6. `.\scripts\validar_dags.ps1` y `.\scripts\activar_dags.ps1`

En Linux o macOS los mismos nombres terminan en `.sh`.

Usuario de la interfaz: `admin`. Contraseña inicial: `estudia-local`. Esa clave solo abre Airflow en tu máquina. No es el usuario de PostgreSQL ni el de la API.

Connection `estudia_api`: tipo HTTP, host `34.95.210.33.sslip.io`, schema `https`, tu login y tu contraseña de PostgreSQL. El DAG nace en pausa.

Para apagar: `.\scripts\detener.ps1`. No uses `docker compose down -v` durante la práctica: borra los metadatos.

El ZIP estudiantil se arma con `.\scripts\empaquetar.ps1`. No incluye `profesor/`.
