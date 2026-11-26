# Cómo dar la clase 05

Los estudiantes escriben código. No descargan un Compose resuelto. La raíz del repositorio docente ya funciona: no la proyectes como atajo. Ellos abren `plantillas/`.

Quien no instala Docker sigue en `notebooks/EstudIA_Clase05_PRACTICA.ipynb`. Di en cada bloque que ese cuaderno no enciende contenedores.

## 18:00 — API

Di: hay tres credenciales distintas. `admin` / `estudia-local` abre Airflow en el portátil. El usuario PostgreSQL abre la API. La base de metadatos de Docker no se toca.

Abre Postman. `POST https://34.95.210.33.sslip.io/api/v4/auth/login`, sin auth, JSON con el usuario asignado. Esperas 200 y un `access_token`. Luego `GET /api/v4/auth/me` con Bearer. No se comparte el token.

Colab: la primera celda de login usa `getpass()`.

## 18:10 — Qué es Docker

Di: una imagen es la plantilla y un contenedor es esa plantilla en marcha. No es una máquina virtual. Docker Desktop incluye el motor. Compose describe varios contenedores. WSL2 es la capa de Linux en Windows.

Pregunta: ¿`docker ps` muestra imágenes o contenedores? Respuesta: contenedores en marcha. `docker images` muestra plantillas. `docker ps -a` incluye los detenidos.

## 18:20 — Instalar

Windows: virtualización activa, WSL2, instalador de Docker Desktop, reinicio si lo pide, abrir la aplicación y esperar al motor.

```powershell
docker --version
docker compose version
docker run --rm hello-world
```

Error frecuente: el cliente existe y el motor no. Se espera a Docker Desktop. A las 19:05, quien siga instalando pasa a Colab.

## 18:45 — Dockerfile, YAML, Compose y .env

Archivo: `plantillas/infraestructura/Dockerfile`.

Di: `FROM` elige la base, `USER airflow` evita root, `RUN` crea una capa. No usamos `latest`.

Respuestas: `apache/airflow:3.4.0`, `airflow`, `3.1.0`, `2.34.2`.

Archivo: `plantillas/infraestructura/docker-compose.yml`. Muestra una línea corrida de indentación y di que Compose la rechaza.

Respuestas, en este orden: `LocalExecutor`, `"4"`, `"1"`, `/opt/airflow/dags`, `/opt/airflow/logs`, `/opt/airflow/data`, `service_healthy`, `postgres:16.6`, `api-server`, `127.0.0.1`, `scheduler`, `dag-processor`.

Di: LocalExecutor corre las tareas en el mismo equipo. Celery las reparte con una cola; aquí no hay Redis. PostgreSQL de este Compose es metadatos, no las ventas. `127.0.0.1` no publica la interfaz en la red. El volumen `./data` es el disco que el pipeline usará más tarde.

Archivo: `plantillas/infraestructura/.env.example`. Respuestas: `8080`, `admin`, `estudia-local`. No se inventan FERNET ni JWT. No se escribe la clave de PostgreSQL.

Colab: la celda de infraestructura pide los mismos textos y dice que no despliega.

## 19:15 — Validar y desplegar

```powershell
.\scripts\validar_infraestructura.ps1
.\scripts\activar_infraestructura.ps1
.\scripts\preparar.ps1
.\scripts\iniciar.ps1
.\scripts\comprobar.ps1
```

Di: validar no construye si queda un hueco. Activar copia los archivos a la raíz. Preparar crea las claves y la imagen. Iniciar arranca Postgres, migra metadatos y levanta api-server, scheduler y dag-processor.

```powershell
docker compose ps
docker compose logs --tail=50 airflow-scheduler
```

Error: puerto ocupado. Se cambia `AIRFLOW_WEB_PORT=8088` y se vuelve a iniciar. El triggerer down no es un fallo.

Interfaz: `http://127.0.0.1:8080`, `admin`, `estudia-local`. Muestra DAGs, Graph, Grid, Runs y Connections.

## 19:30 — Primer DAG

Archivo: `plantillas/dags/estudia_clase05_mi_primer_dag.py`.

Respuestas: `estudia_clase05_mi_primer_dag`, `None`, `False`, `saludar`, `saludar`, `finalizar`, `finalizar`, y la línea `inicio >> fin`.

```powershell
.\scripts\validar_dags.ps1 primero
.\scripts\activar_dags.ps1 primero
```

Ese argumento no mira el pipeline. Puede seguir con `COMPLETA` y no entra en `dags/`. En Linux o macOS: `./scripts/validar_dags.sh primero` y `./scripts/activar_dags.sh primero`. Quita la pausa, Trigger, y lee los dos logs. No hace falta la API.

## 19:40 — Connection

Admin, Connections. Id `estudia_api`, tipo HTTP, host `34.95.210.33.sslip.io`, schema `https`, login y contraseña de cada estudiante. En el DAG, `BaseHook.get_connection("estudia_api")`. No se imprime `password`.

## 19:50 — HTTP y paginación

En el mismo archivo de práctica: `access_token`, `Authorization`, `range(1, 3)`, región `Aragón`, `page` igual a `numero`, `page_size` `100`.

Di: dos páginas de 100 son 200 filas. Aragón tiene más registros; el alcance queda parcial. No se bajan las 50.000 ventas. `/ventas` es plano. `/ventas/muestra` es anidado y no se usa aquí.

## 20:05 — Medallion

Bronze guarda el JSON original. No se guarda el login. Silver: `data`, `ignore_index=True`, columna `fecha`, columna `importe_neto`. Validación: `id_transaccion` nulo y `id_transaccion` duplicado. No se borran filas ni se cambian negativos por cero. Gold: `categoria` con `sum`, `region` con `sum`.

## 20:20 — Operadores, dependencias y XCom

Los estudiantes escriben los seis operadores y esta línea:

```python
t1 >> t2 >> t3 >> t4 >> t5 >> t6
```

`dag_id` `estudia_clase05_api_medallion`, `schedule=None`, `catchup=False`, `max_active_runs=1`, `retries` `1`.

XCom: bronze tira de `extraer_api` y validar tira de `transformar_silver`. Solo viaja el `run_id`. Los archivos viajan por `./data`, el volumen que escribieron en Compose.

```powershell
.\scripts\validar_dags.ps1 pipeline
.\scripts\activar_dags.ps1 pipeline
```

En Linux o macOS: `./scripts/validar_dags.sh pipeline` y `./scripts/activar_dags.sh pipeline`. Sin argumento, los dos scripts siguen revisando los dos DAG. Un hueco del pipeline no impide el primer DAG, y un hueco del pipeline impide copiar solo ese archivo a `dags/`.

## 20:35 — Ejecutar

Abre `estudia_clase05_api_medallion`, quita la pausa, Trigger. Revisa Graph, Grid, logs y `data/bronze`, `data/silver`, `data/gold`, `data/reports`. Referencia de la corrida probada: 200 filas, 5.018 en el filtro, alcance parcial, promedio cerca de 1545. Los números pueden moverse si cambian los datos.

## 20:45 — Fallo y horario

El DAG `estudia_clase05_fallo_controlado` usa un archivo local con un id repetido. Muestra Failed y el reintento. Un duplicado no debe convertirse en un indicador.

`schedule=None` es manual. `*/10 * * * *` sería cada diez minutos: no lo actives en los 45 equipos.

```powershell
.\scripts\detener.ps1
```

`stop` apaga. `down` borra contenedores y conserva volúmenes. `down -v` borra también los metadatos. En la práctica se usa `stop`.

## Cierre

Pregunta: ¿por qué el JSON de ventas aparece en la carpeta `data` de tu portátil? Respuesta: porque el Compose monta `./data` dentro del contenedor.
