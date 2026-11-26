# Entrega clase 05

Material para armar las diapositivas. Lo no probado en pantalla está dicho como no probado.

## Versiones

| Pieza | Valor |
|---|---|
| Airflow | `apache/airflow:3.4.0` |
| Ejecutor | LocalExecutor |
| Metadatos | `postgres:16.6`, sin puerto publicado, clave local `estudia_meta_local` |
| Pandas | 3.1.0 |
| Requests | 2.34.2 |
| Interfaz | `http://127.0.0.1:8080` |
| API | `https://34.95.210.33.sslip.io/api/v4` |

No hay imagen `latest`, ni Redis, ni Celery.

## Comandos

Windows, dentro de `clase05` o de la carpeta descomprimida:

```powershell
docker --version
docker compose version
docker run --rm hello-world
.\scripts\validar_infraestructura.ps1
.\scripts\activar_infraestructura.ps1
.\scripts\preparar.ps1
.\scripts\iniciar.ps1
.\scripts\comprobar.ps1
.\scripts\validar_dags.ps1
.\scripts\activar_dags.ps1
.\scripts\detener.ps1
```

Linux y macOS: `./scripts/preparar.sh`, `./scripts/iniciar.sh`, `./scripts/comprobar.sh`, `./scripts/detener.sh`.

Health esperado: `http://127.0.0.1:8080/api/v2/monitor/health`.

Si 8080 está ocupado: `AIRFLOW_WEB_PORT=8088` en `.env`.

Borrar metadatos locales, a propósito: `docker compose down -v`.

ZIP: `.\scripts\empaquetar.ps1`. Sale en `clase05/dist/EstudIA_Clase05_laboratorio.zip` y no incluye `profesor/`.

## Pantallas

1. Docker Desktop en marcha.
2. PowerShell con `hello-world`.
3. Navegador en `http://127.0.0.1:8080`, usuario `admin`, contraseña `estudia-local`.
4. Lista de DAGs: `estudia_clase05_api_medallion` y `estudia_clase05_fallo_controlado`, en pausa.
5. Admin, Connections, formulario de abajo.
6. Graph con las seis tareas.
7. Grid en success.
8. Log sin token.
9. `data/reports/<run_id>/manifiesto.json` con `alcance: parcial` y `filas: 200`.
10. El DAG de fallo en `failed` después de `up_for_retry`.

## Connection `estudia_api`

| Campo | Valor |
|---|---|
| Connection Id | `estudia_api` |
| Connection Type | HTTP |
| Host | `34.95.210.33.sslip.io` |
| Schema | `https` |
| Login | `estudiante` o `estudianteNN` |
| Password | la de PostgreSQL |
| Port | vacío |

## Práctica y solucionario

Los estudiantes completan `plantillas/infraestructura/` y `plantillas/dags/`. El ZIP no trae el Dockerfile ni el Compose resueltos en la raíz. El docente los tiene en la raíz de `clase05/` y en `profesor/infraestructura/`. Las respuestas están en `profesor/SOLUCIONARIO.md`.

Primer DAG: `estudia_clase05_mi_primer_dag`, tareas `saludar` y `finalizar`, línea `inicio >> fin`.

## DAG

`estudia_clase05_api_medallion`

Los estudiantes escriben los seis operadores y la línea `t1 >> t2 >> t3 >> t4 >> t5 >> t6`.

`extraer_api → guardar_bronze → transformar_silver → validar_datos → generar_gold → exportar_reporte`

`schedule=None`, `catchup=False`, `max_active_runs=1`, un reintento, nace en pausa.

Huecos principales: `apache/airflow:3.4.0`, `airflow`, pandas `3.1.0`, requests `2.34.2`, `postgres:16.6`, `LocalExecutor`, comandos `api-server`, `scheduler` y `dag-processor`, `127.0.0.1`, volúmenes `/opt/airflow/dags`, `/opt/airflow/logs` y `/opt/airflow/data`, Connection `estudia_api`, `access_token`, `Authorization`, `Aragón`, `page_size` 100, dos páginas, `data`, `fecha`, `importe_neto`, `id_transaccion`, `categoria`, `region`, `sum`.

## Rutas de datos

```text
data/bronze/<run_id>/pagina_1.json
data/bronze/<run_id>/pagina_2.json
data/bronze/<run_id>/cobertura.json
data/silver/<run_id>/ventas.csv
data/gold/<run_id>/por_categoria.csv
data/gold/<run_id>/por_region.csv
data/gold/<run_id>/resumen.json
data/reports/<run_id>/manifiesto.json
```

Resultado medido contra la API el 26 de noviembre de 2026, con el usuario compartido: 200 filas, alcance parcial, 5018 registros en el filtro de Aragón. El manifiesto no llevó el token.

`/ventas` es plano. `/ventas/muestra` anida `producto` y `tienda`. El pipeline usa `/ventas`.

## Lo que sí corrió en Docker

Docker Desktop 4.92, motor 29.8.0. La imagen ocupa 3.22 GB en disco y Postgres 16.6 ocupa 617 MB. En marcha, los cuatro contenedores usaron alrededor de 1 GB de los 7.44 GiB de la VM.

`preparar`, `iniciar`, el health de `127.0.0.1:8080`, la corrida del profesor y el apagado se probaron por consola. La corrida dejó 200 filas, alcance parcial y 5018 en el filtro. El health marca el triggerer como down: este laboratorio no lo usa.

## Lo que no se vio en pantalla

No se abrió el navegador en `http://127.0.0.1:8080` ni la ventana de Docker Desktop. El cuaderno del profesor se ejecutó con nbclient, no dentro de colab.google.com. El DAG no se instaló en la VM de la clase 03.

La práctica nueva se probó descomprimiendo el ZIP en una carpeta aparte, completando las plantillas y levantando ese proyecto en `127.0.0.1:8088`. El primer DAG terminó en success con los dos logs. El pipeline devolvió 200 filas, alcance parcial y 5018 registros en el filtro. El fallo controlado llegó a `failed` en el intento 2. Tras `docker compose stop` y un nuevo arranque, el manifiesto y la corrida seguían. No se usó `down -v`.
