# Guía del estudiante — Clase 05

Vas a escribir la imagen, el Compose, el primer DAG y el pipeline. Los huecos dicen `COMPLETA`. No copies la carpeta `profesor/`: esa copia es del docente.

Si no puedes instalar Docker, abre `notebooks/EstudIA_Clase05_PRACTICA.ipynb`. Ese cuaderno recorre las mismas ideas y la misma API. No enciende Airflow.

## 01 — Docker

Docker empaqueta un programa con sus librerías. Una imagen es la plantilla. Un contenedor es esa plantilla en marcha. No es una máquina virtual: comparte el núcleo del sistema y arranca en segundos.

En Windows abre Docker Desktop y espera a que diga que el motor está activo. Comprueba:

```powershell
docker --version
docker compose version
docker run --rm hello-world
docker images
docker ps
docker ps -a
```

`docker images` lista plantillas descargadas. `docker ps` lista contenedores en marcha. `docker ps -a` incluye los que ya terminaron.

Para ver extensiones en el Explorador: Vista, mostrar extensiones de archivo. Puedes editar con el Bloc de notas.

## 02 — Dockerfile

Abre `plantillas/infraestructura/Dockerfile`.

| Hueco | Escribe |
|---|---|
| FROM | `apache/airflow:3.4.0` |
| USER | `airflow` |
| pandas | `3.1.0` |
| requests | `2.34.2` |

`FROM` elige la imagen base. `USER airflow` evita dejar el proceso como root. `RUN pip` añade una capa. Las versiones van fijas para que el laboratorio no cambie mañana.

## 03 — YAML

La indentación es la estructura. Dos espacios mal puestos parten el archivo. Una lista usa `-`. Un diccionario usa `clave: valor`. `#` comenta. `${AIRFLOW_WEB_PORT:-8080}` lee una variable y, si falta, usa 8080.

## 04 — Compose

Abre `plantillas/infraestructura/docker-compose.yml`. Completa solo los huecos. No borres el resto.

| Hueco | Valor |
|---|---|
| Imagen de metadatos | `postgres:16.6` |
| Ejecutor | `LocalExecutor` |
| Paralelismo | `4` |
| Corridas activas | `1` |
| `./dags` | `/opt/airflow/dags` |
| `./logs` | `/opt/airflow/logs` |
| `./data` | `/opt/airflow/data` |
| Condición | `service_healthy` |
| API | `api-server` |
| Planificador | `scheduler` |
| Procesador | `dag-processor` |
| Dirección | `127.0.0.1` |

PostgreSQL de esta carpeta guarda metadatos de Airflow, no las 50.000 ventas. No publiques su puerto. `127.0.0.1` hace que la interfaz solo se abra en tu máquina. Si 8080 está ocupado, deja la expresión y pon `8088` en `.env`.

## 05 — Variables

En `plantillas/infraestructura/.env.example`:

```dotenv
AIRFLOW_WEB_PORT=8080
AIRFLOW_ADMIN_USER=admin
AIRFLOW_ADMIN_PASSWORD=estudia-local
```

No inventes `FERNET_KEY` ni `JWT_SECRET`. No pongas ahí tu contraseña de PostgreSQL.

## 06 — Validar y encender

```powershell
.\scripts\validar_infraestructura.ps1
.\scripts\activar_infraestructura.ps1
.\scripts\preparar.ps1
.\scripts\iniciar.ps1
.\scripts\comprobar.ps1
```

Si queda un hueco, el validador dice archivo y línea y no construye. `preparar` crea las claves locales y la imagen. `iniciar` levanta los contenedores. `comprobar` pega la URL. El triggerer puede salir down: no forma parte de este laboratorio.

Usuario `admin`, contraseña `estudia-local`. No es tu usuario de la API.

## 07 — Primer DAG

Abre `plantillas/dags/estudia_clase05_mi_primer_dag.py`.

`dag_id` es `estudia_clase05_mi_primer_dag`. `schedule=None`. `catchup=False`. La primera tarea se llama `saludar` y llama a `saludar`. La segunda se llama `finalizar` y llama a `finalizar`. Escribe esta línea, sin comentario delante:

```python
inicio >> fin
```

```powershell
.\scripts\validar_dags.ps1 primero
.\scripts\activar_dags.ps1 primero
```

El pipeline puede seguir incompleto: este comando no lo copia. En la interfaz quita la pausa, pulsa Trigger y lee los dos logs.

## 08 — Connection y API

En Postman, `POST https://34.95.210.33.sslip.io/api/v4/auth/login` con tu usuario. No compartas el token.

En Airflow, Admin, Connections, crea `estudia_api`: tipo HTTP, host `34.95.210.33.sslip.io`, schema `https`, tu usuario y tu contraseña. Puerto y Extra vacíos. No guardes el token.

## 09 — Pipeline

Abre `plantillas/dags/estudia_clase05_practica.py`.

| Hueco | Valor |
|---|---|
| Connection | `estudia_api` |
| Clave del token | `access_token` |
| Encabezado | `Authorization` |
| Rango | `3` |
| Región | `Aragón` |
| Página | `numero` |
| Tamaño | `100` |
| XCom de bronze | `extraer_api` |
| Lista del JSON | `data` |
| concat | `True` |
| Fecha | `fecha` |
| Importe | `importe_neto` |
| XCom de validar | `transformar_silver` |
| Nulos y duplicados | `id_transaccion` |
| Primer groupby | `categoria` y `sum` |
| Segundo groupby | `region` y `sum` |
| dag_id | `estudia_clase05_api_medallion` |
| schedule | `None` |
| catchup | `False` |
| max_active_runs | `1` |
| retries | `1` |

Las seis tareas, en orden: `extraer_api`, `guardar_bronze`, `transformar_silver`, `validar_datos`, `generar_gold`, `exportar_reporte`. Cada `python_callable` lleva el mismo nombre. Escribe:

```python
t1 >> t2 >> t3 >> t4 >> t5 >> t6
```

```powershell
.\scripts\validar_dags.ps1 pipeline
.\scripts\activar_dags.ps1 pipeline
```

Quita la pausa y dispara. Debes ver unas 200 filas, alcance parcial y la carpeta `data/` en tu máquina, porque montaste `./data:/opt/airflow/data`.

El DAG `estudia_clase05_fallo_controlado` falla a propósito por un id duplicado en un archivo local. No llama a la API.

Para apagar: `.\scripts\detener.ps1`.
