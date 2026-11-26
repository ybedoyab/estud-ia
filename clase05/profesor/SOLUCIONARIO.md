# Solucionario — Clase 05

La infraestructura que ya fue probada sigue en la raíz de `clase05/`: `Dockerfile`, `docker-compose.yml` y `.env.example`. Las mismas copias están en `profesor/infraestructura/`. Los DAG resueltos están en `profesor/dags/`. El cuaderno resuelto es `notebooks/EstudIA_Clase05_PROFESOR.ipynb`.

Puedes ejecutar la raíz mientras los estudiantes siguen en `plantillas/`. No pongas esta carpeta en el ZIP.

## Dockerfile

| Campo | Respuesta |
|---|---|
| FROM | `apache/airflow:3.4.0` |
| USER | `airflow` |
| pandas | `3.1.0` |
| requests | `2.34.2` |

## Compose

| Campo | Respuesta |
|---|---|
| EXECUTOR | `LocalExecutor` |
| PARALLELISM | `4` |
| MAX_ACTIVE_RUNS_PER_DAG | `1` |
| ./dags | `/opt/airflow/dags` |
| ./logs | `/opt/airflow/logs` |
| ./data | `/opt/airflow/data` |
| condition | `service_healthy` |
| image | `postgres:16.6` |
| airflow-apiserver | `api-server` |
| puerto del host | `127.0.0.1` |
| airflow-scheduler | `scheduler` |
| airflow-dag-processor | `dag-processor` |

## Entorno

`AIRFLOW_WEB_PORT=8080`, `AIRFLOW_ADMIN_USER=admin`, `AIRFLOW_ADMIN_PASSWORD=estudia-local`.

`preparar` sustituye los marcadores de `FERNET_KEY` y `JWT_SECRET`. No se dictan esas claves.

## Primer DAG

`dag_id="estudia_clase05_mi_primer_dag"`, `schedule=None`, `catchup=False`, tareas `saludar` y `finalizar`, línea `inicio >> fin`.

## Pipeline

| Campo | Respuesta |
|---|---|
| Connection | `estudia_api` |
| JSON del token | `access_token` |
| Header | `Authorization` |
| range | `range(1, 3)` |
| region | `Aragón` |
| page | `numero` |
| page_size | `100` |
| XCom bronze | `extraer_api` |
| DataFrame | `data` |
| ignore_index | `True` |
| fecha | `fecha` |
| importe | `importe_neto` |
| XCom validar | `transformar_silver` |
| nulos y duplicados | `id_transaccion` |
| groupby | `categoria` + `sum`, `region` + `sum` |
| dag_id | `estudia_clase05_api_medallion` |
| schedule | `None` |
| catchup | `False` |
| max_active_runs | `1` |
| retries | `1` |
| dependencia | `t1 >> t2 >> t3 >> t4 >> t5 >> t6` |

## Comandos

```powershell
.\scripts\validar_infraestructura.ps1
.\scripts\activar_infraestructura.ps1
.\scripts\preparar.ps1
.\scripts\iniciar.ps1
.\scripts\comprobar.ps1
.\scripts\validar_dags.ps1
.\scripts\activar_dags.ps1
.\scripts\detener.ps1
```

## Resultado de referencia

200 filas, 5.018 registros filtrados de Aragón, alcance parcial, promedio cercano a 1545. Puede cambiar si cambian los datos.

## Errores

| Síntoma | Qué hacer |
|---|---|
| PENDIENTE archivo:línea | Completar ese hueco. No construir. |
| YAML inválido | Revisar la indentación y volver a `docker compose config`. |
| Puerto ocupado | `AIRFLOW_WEB_PORT=8088` y reiniciar. |
| Login 401 en Airflow | La clave de la interfaz es `estudia-local`, no la de PostgreSQL. |
| Tareas en cola | El DAG sigue en pausa. |
| Triggerer down | Esperado. No forma parte del laboratorio. |
| Id duplicado | El fixture de fallo. No se borra la fila. |
