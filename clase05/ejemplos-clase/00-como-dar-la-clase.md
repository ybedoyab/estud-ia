# Cómo dar la clase

Tres horas, de 18:00 a 21:00. La pausa es de 19:05 a 19:15. Quien no tenga Docker a esa hora pasa a Colab y no espera.

No actives un cron en los 45 equipos. El DAG se dispara a mano.

## 18:00 — Repaso de la API

Di: "La API de la clase pasada sigue siendo de lectura. Hoy esa petición va a vivir dentro de un pipeline."

Abre:

- Salud: `https://34.95.210.33.sslip.io/api/v4/health`. Esperado: `estudia-clase04`.
- Swagger: `https://34.95.210.33.sslip.io/api/v4/docs`.
- Postman, carpeta de ventas, `GET {{base_url}}/api/v4/ventas` con región Aragón.

Pregunta: "¿El token va en la URL?" Respuesta: no, va en Authorization.

Si salud no responde, no sigas con datos inventados. El cuaderno tiene respaldo marcado `RESPALDO`.

## 18:15 — Qué es Docker

Di: "Un contenedor es un proceso empaquetado con sus librerías. Airflow necesita varios procesos. Compose los levanta juntos."

Abre `ejemplos-clase/01-docker-fundamentos.md` y el `docker-compose.yml`. Señala api-server, scheduler, dag-processor y postgres. Di que postgres de esta pantalla no es la base del curso.

## 18:30 — Instalación

Proyecta la descarga oficial: `https://www.docker.com/products/docker-desktop/`.

En PowerShell, y que lo copien:

```powershell
docker --version
docker compose version
docker run --rm hello-world
```

Esperado: el cliente de Docker, Compose, y "Hello from Docker!".

Luego, dentro de la carpeta descomprimida:

```powershell
.\scripts\preparar.ps1
```

Eso crea `.env`, una clave Fernet y la imagen. Puede tardar porque baja `apache/airflow:3.4.0` y `postgres:16.6`.

Errores frecuentes:

- "Docker Desktop no responde": abrir la aplicación y esperar.
- Virtualización apagada: activarla en la BIOS o en Windows.
- WSL2 ausente: instalarlo con `wsl --install` y reiniciar.
- Poca memoria: en Docker Desktop, Resources, 4 GB como mínimo.

A quien se quede atascado, dile que abra el cuaderno de práctica. No lo dejes en el instalador después de la pausa.

## 19:05 — Pausa

Diez minutos. Deja tu `preparar` terminado.

## 19:15 — Levantar Airflow

```powershell
.\scripts\iniciar.ps1
.\scripts\comprobar.ps1
```

Abre `http://127.0.0.1:8080`. Usuario `admin`. Contraseña `estudia-local`, salvo que la hayan cambiado en `.env`.

Di: "Esta contraseña no entra a PostgreSQL del curso. Solo abre esta pantalla."

Si 8080 está ocupado, `AIRFLOW_WEB_PORT=8088` en `.env`, detener e iniciar otra vez. La URL pasa a `http://127.0.0.1:8088`.

Esperado en DAGs: `estudia_clase05_api_medallion` y `estudia_clase05_fallo_controlado`, los dos en pausa.

## 19:35 — Connection

Admin, Connections, signo más.

| Campo | Qué escribir |
|---|---|
| Connection Id | `estudia_api` |
| Connection Type | HTTP |
| Host | `34.95.210.33.sslip.io` |
| Schema | `https` |
| Login | el usuario PostgreSQL |
| Password | la contraseña de ese usuario |
| Port | vacío |

Test no siempre existe en HTTP. No pegues el token en ningún campo. Guarda.

## 19:50 — De Postman al DAG

En Postman abre el código, Python Requests. Di: "Eso es el borrador. Le quitamos la contraseña fija, le ponemos timeout y `raise_for_status`, y la credencial sale de la Connection."

Abre `dags/estudia_clase05_practica.py`. Rellena en voz alta:

- `RUTA_VENTAS = "/api/v4/ventas"`
- `REGION = "Aragón"`
- `PAGE_SIZE = "100"`
- `PAGINAS = "2"`
- `PREFIJO_AUTH = "Bearer"`
- `COLUMNA_CATEGORIA = "categoria"`
- `COLUMNA_REGION = "region"`
- `REGLA_DUPLICADOS = "rechazar"`
- `CADENA = "extraer_api>guardar_bronze>transformar_silver>validar_datos>generar_gold>exportar_reporte"`

El grafo ya muestra esas flechas. La cadena escrita evita que disparen la tarea con los huecos vacíos.

## 20:10 — Medallion

Abre `data/` cuando haya corrido, o explica las carpetas antes.

- Bronze: `pagina_1.json`, `pagina_2.json`, `cobertura.json`. Sin token.
- Silver: `ventas.csv` con columnas planas.
- Gold: sumas de esa extracción.
- Reports: `manifiesto.json` con `alcance` parcial.

Di: "Dos páginas de Aragón no son el censo. El manifiesto lo dice."

`/ventas/muestra` anida producto y tienda. No la metas en este groupby.

## 20:25 — Ejecución

Quita la pausa del DAG de práctica y pulsa Trigger. En Graph verás el orden. En Logs, códigos y conteos, no el token.

Esperado: las seis tareas en success. En `data/reports/<run_id>/manifiesto.json`, `filas` cerca de 200 y `alcance` parcial.

## 20:45 — Fallo, reintento y programación

Dispara `estudia_clase05_fallo_controlado`. Esperado: `up_for_retry` y luego `failed`. El log dice que el id está duplicado. El importe negativo del fixture no es la causa.

Di: "`catchup=False` evita que un DAG nuevo salga a correr el pasado. `max_active_runs=1` evita dos corridas a la vez. No pongan un cron igual en toda el aula."

Para apagar:

```powershell
.\scripts\detener.ps1
```

## 20:55 — Cierre

Repite las tres rutas: Docker local, Colab si no hubo Docker, y la API que sigue siendo de lectura. El ZIP y el cuaderno de práctica se suben a Drive después, fuera de esta sesión. La solución de `profesor/` no se entrega.
