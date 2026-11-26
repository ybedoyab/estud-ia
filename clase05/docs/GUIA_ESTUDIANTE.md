# Guía del estudiante

Vas a levantar Airflow en tu portátil y a convertir una petición de Postman en un pipeline. No vas a modificar las 50.000 ventas.

Si Docker no instala, abre `notebooks/EstudIA_Clase05_PRACTICA.ipynb` en Colab. Ese cuaderno no es Airflow: recorre las mismas funciones una vez.

## 1. Docker Desktop

1. Comprueba que Windows muestra virtualización activa en el Administrador de tareas, pestaña Rendimiento.
2. Instala WSL2 si el instalador de Docker lo pide. La guía de Microsoft es la de "Install WSL".
3. Descarga Docker Desktop desde [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/).
4. Instálalo y reinicia si lo pide.
5. Ábrelo y espera a que diga que el motor está en marcha.
6. En PowerShell:

```powershell
docker --version
docker compose version
docker run --rm hello-world
```

Hace falta unos 8 GB de RAM en el equipo. En Docker Desktop, Settings, Resources, deja al menos 4 GB para la máquina virtual.

## 2. Laboratorio

Descomprime el ZIP en una carpeta corta, por ejemplo `C:\estudia-clase05`. En PowerShell:

```powershell
cd C:\estudia-clase05
.\scripts\preparar.ps1
.\scripts\iniciar.ps1
.\scripts\comprobar.ps1
```

Abre [http://127.0.0.1:8080](http://127.0.0.1:8080). Usuario `admin`. Contraseña la de `.env`, de salida `estudia-local`.

Si el puerto 8080 está ocupado, cambia `AIRFLOW_WEB_PORT=8088` en `.env` y vuelve a iniciar.

## 3. Connection

Admin, Connections, añade:

| Campo | Valor |
|---|---|
| Connection Id | `estudia_api` |
| Connection Type | HTTP |
| Host | `34.95.210.33.sslip.io` |
| Schema | `https` |
| Login | tu usuario PostgreSQL |
| Password | tu contraseña de PostgreSQL |
| Port | vacío |

Esa contraseña no es la de `admin` ni la de la base de metadatos de Airflow.

## 4. El DAG

En DAGs verás `estudia_clase05_api_medallion`, en pausa. Ábrelo y mira el grafo:

`extraer_api → guardar_bronze → transformar_silver → validar_datos → generar_gold → exportar_reporte`

Edita `dags/estudia_clase05_practica.py` y sustituye cada `COMPLETA`:

| Campo | Valor |
|---|---|
| `RUTA_VENTAS` | `/api/v4/ventas` |
| `REGION` | `Aragón` |
| `PAGE_SIZE` | `100` |
| `PAGINAS` | `2` |
| `PREFIJO_AUTH` | `Bearer` |
| `COLUMNA_CATEGORIA` | `categoria` |
| `COLUMNA_REGION` | `region` |
| `REGLA_DUPLICADOS` | `rechazar` |
| `CADENA` | `extraer_api>guardar_bronze>transformar_silver>validar_datos>generar_gold>exportar_reporte` |

Quita la pausa y pulsa Trigger. Dos páginas no son las 50.000 ventas. El informe queda en `data/reports/`.

`estudia_clase05_fallo_controlado` falla a propósito con un JSON local. Sirve para ver `up_for_retry` y `failed`. No toca la API.

Para apagar: `.\scripts\detener.ps1`.
