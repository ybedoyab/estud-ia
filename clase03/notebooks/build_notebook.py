"""Genera el notebook de la clase. No incluye contraseñas."""

import json
import uuid
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CLIENTE = (AQUI.parent / "api" / "app" / "cliente.py").read_text(encoding="utf-8")
OUT = AQUI / "EstudIA_Clase03_SQL_Pandas_Airflow.ipynb"


def md(texto):
    return {"cell_type": "markdown", "id": uuid.uuid4().hex[:12], "metadata": {}, "source": _lineas(texto)}


def code(texto):
    return {
        "cell_type": "code",
        "id": uuid.uuid4().hex[:12],
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": _lineas(texto),
    }


def _lineas(texto):
    if not texto.endswith("\n"):
        texto += "\n"
    return texto.splitlines(keepends=True)


celdas = [
    md("""# EstudIA — Clase 03
## SQL, Pandas y un pipeline que se ejecuta solo

Hoy vas a consultar ventas, limpiar los datos, calcular un indicador y dejar un reporte. Al final, Airflow lo ejecutará cada 10 minutos sin abrir este cuaderno.

```text
SQL  ->  Pandas  ->  ETL  ->  pipeline  ->  Airflow  ->  reporte
```

Antes de escribir, guarda tu propia copia: **Archivo → Guardar una copia en Drive**.
Trabaja en esa copia. Esta plantilla queda igual para el resto del curso.

La clase va de 18:00 a 21:00, hora de Bogotá.
"""),
    md("""## Parte 0 — Preparación

Ejecuta esta celda una vez. Instala lo necesario para consultar PostgreSQL y publicar el pipeline. No instala Airflow: Airflow ya está en el servidor de la clase.
"""),
    code("""%pip install -q "psycopg[binary]" "SQLAlchemy>=2" pandas matplotlib requests
print("dependencias listas")
"""),
    md("""## Parte 1 — SQL analítico

La base es la misma de la clase 02.

| Vista | Qué contiene | Cómo se une |
|---|---|---|
| `curso.ventas` | 50 000 transacciones | — |
| `curso.productos` | 500 productos | `ventas.id_producto` |
| `curso.tiendas` | 50 tiendas | `ventas.id_tienda` |
| `curso.clientes` | 2 000 clientes | `ventas.id_cliente` |
| `curso.fechas` | días de 2022 a 2024 | `ventas.id_fecha` |

`importe_neto` ya trae el descuento. `descuento_pct` es una fracción: `0.10` significa 10 %.

**Pregunta.** ¿Qué combinaciones de región y categoría superan un millón de venta neta?

`HAVING` filtra el grupo ya sumado. `WHERE` no puede hacer esa suma.
"""),
    code("""CONSULTA_CATEGORIA = \"\"\"
SELECT t.region, p.categoria,
       COUNT(*) AS transacciones,
       ROUND(SUM(v.importe_neto), 2) AS venta_neta
FROM curso.ventas v
JOIN curso.productos p ON p.id_producto = v.id_producto
JOIN curso.tiendas t ON t.id_tienda = v.id_tienda
GROUP BY t.region, p.categoria
HAVING SUM(v.importe_neto) > 1000000
ORDER BY venta_neta DESC
LIMIT 15
\"\"\"
print("consulta de categorias guardada")
"""),
    md("""**Pregunta.** ¿Cuáles son los tres productos con más unidades dentro de cada categoría?

`ROW_NUMBER()` numera dentro de cada `PARTITION BY`. El filtro `puesto <= 3` va en una CTE: una ventana no se puede filtrar en el mismo `SELECT` donde se calcula.
"""),
    code("""CONSULTA_RANKING = \"\"\"
WITH unidades AS (
    SELECT p.categoria, p.nombre,
           SUM(v.cantidad) AS unidades,
           ROW_NUMBER() OVER (
               PARTITION BY p.categoria
               ORDER BY SUM(v.cantidad) DESC
           ) AS puesto
    FROM curso.ventas v
    JOIN curso.productos p ON p.id_producto = v.id_producto
    GROUP BY p.categoria, p.nombre
)
SELECT categoria, nombre, unidades, puesto
FROM unidades
WHERE puesto <= 3
ORDER BY categoria, puesto
\"\"\"
print("consulta de ranking guardada")
"""),
    md("""## Parte 2 — Conexión desde Colab

Entras con tu usuario individual, por ejemplo `estudiante21`, y con tu contraseña. Se piden una sola vez. El usuario compartido `estudiante` puede leer, pero no publica un pipeline.

Host, puerto y base ya están configurados.
"""),
    code("""import os
from getpass import getpass

API_BASE_URL = "https://34.95.210.33.sslip.io"
DB_HOST = "34.39.202.205"
DB_PORT = 6432
DB_NAME = "retail_dwh"

USUARIO = os.environ.get("ESTUDIA_USUARIO") or input("Usuario PostgreSQL: ").strip()
CONTRASENA = os.environ.get("ESTUDIA_CONTRASENA") or getpass("Contrasena: ")
if USUARIO == "estudiante":
    raise SystemExit("Usa tu usuario individual. El usuario compartido no publica pipelines.")
print("usuario cargado:", USUARIO)
"""),
    code("""import requests
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.pool import NullPool

certificado = "/tmp/estudia-lab-ca.crt"
respuesta_ca = requests.get(f"{API_BASE_URL}/certs/estudia-lab-ca.crt", timeout=30)
respuesta_ca.raise_for_status()
open(certificado, "wb").write(respuesta_ca.content)

motor = create_engine(
    URL.create(
        "postgresql+psycopg",
        username=USUARIO,
        password=CONTRASENA,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
    ),
    poolclass=NullPool,
    connect_args={
        "sslmode": "verify-full",
        "sslrootcert": certificado,
        "prepare_threshold": None,
        "connect_timeout": 20,
    },
)

def consultar(sql):
    try:
        with motor.connect() as conn:
            return pd.read_sql(text(sql), conn)
    except Exception as exc:
        mensaje = str(exc).lower()
        if "password" in mensaje or "authentication" in mensaje:
            raise SystemExit("Usuario o contrasena rechazados. Corrige la celda anterior y ejecutala de nuevo.") from None
        if "ssl" in mensaje or "certificate" in mensaje:
            raise SystemExit("Fallo la validacion TLS. La conexion no se abrio.") from None
        if "timeout" in mensaje or "could not" in mensaje:
            raise SystemExit("No hay conexion con la base. Revisa la red e intentalo otra vez.") from None
        raise SystemExit("La consulta no se pudo ejecutar: " + str(exc).splitlines()[-1]) from None

print(consultar("SELECT 1 AS conexion_ok"))
"""),
    md("""Si viste `conexion_ok`, ejecuta las consultas de la parte 1. El resultado aparece como tabla.
"""),
    code("""categorias = consultar(CONSULTA_CATEGORIA)
print("filas y columnas:", categorias.shape)
categorias
"""),
    code("""ranking = consultar(CONSULTA_RANKING)
print("filas y columnas:", ranking.shape)
ranking.head(15)
"""),
    md("""## Parte 3 — Pandas

`groupby` hace aquí lo mismo que `GROUP BY` en SQL: parte las filas y calcula un número por grupo.

**Pregunta.** En la muestra que ya bajaste, ¿qué región acumula más venta neta?
"""),
    code("""print(categorias.head())
categorias.info()
print("nulos")
print(categorias.isna().sum())
print("filas duplicadas:", int(categorias.duplicated().sum()))

por_region = (
    categorias.groupby("region", as_index=False)["venta_neta"]
    .sum()
    .sort_values("venta_neta", ascending=False)
)
por_region
"""),
    code("""import matplotlib.pyplot as plt

grafico = por_region.head(7)
plt.figure(figsize=(8, 4))
plt.barh(grafico["region"], grafico["venta_neta"])
plt.xlabel("Venta neta")
plt.title("Regiones con mas venta en la muestra")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()
"""),
    md("""## Parte 4 — El ETL

1. **Extraer** lee ventas desde PostgreSQL.
2. **Transformar** quita filas incompletas.
3. **Validar** comprueba que el resultado sirve.
4. **El reporte** agrega la venta por categoría.

La celda ya funciona. Puedes cambiar la columna de agrupación de `categoria` a `canal` y volver a ejecutarla.
"""),
    code("""def extraer_datos():
    return consultar(\"\"\"
        SELECT t.region, p.categoria, v.canal, v.metodo_pago,
               v.importe_neto, v.cantidad
        FROM curso.ventas v
        JOIN curso.productos p ON p.id_producto = v.id_producto
        JOIN curso.tiendas t ON t.id_tienda = v.id_tienda
        LIMIT 5000
    \"\"\")


def transformar_datos(df):
    limpio = df.dropna(subset=["region", "categoria", "importe_neto"]).copy()
    limpio["importe_neto"] = limpio["importe_neto"].astype(float)
    return limpio


def validar_datos(df):
    if df.empty:
        raise ValueError("La extraccion no trajo filas.")
    if df["importe_neto"].isna().any():
        raise ValueError("Quedaron importes vacios.")
    return df


def generar_reporte(df):
    return (
        df.groupby("categoria", as_index=False)
        .agg(venta_neta=("importe_neto", "sum"), unidades=("cantidad", "sum"))
        .sort_values("venta_neta", ascending=False)
    )


reporte_local = generar_reporte(validar_datos(transformar_datos(extraer_datos())))
print("filas y columnas:", reporte_local.shape)
reporte_local
"""),
    md("""## Parte 5 — Publicar el pipeline

Airflow no recibe tu código Python. Recibe la consulta, la validación y el reporte. El servidor solo sabe ejecutar esas operaciones.

`publicar()` usa el token de tu sesión. El identificador del DAG sale de tu usuario: nadie puede publicar encima del pipeline de otra persona.

Si ya habías publicado, la misma llamada reemplaza tu DAG. No crea un segundo.
"""),
    code(CLIENTE + """
sesion = iniciar_sesion(API_BASE_URL, USUARIO, CONTRASENA)
print("sesion de", sesion["usuario"], "vigente por", sesion["expires_in"] // 60, "minutos")
TOKEN = sesion["access_token"]
"""),
    code("""pipeline = EstudIAPipeline(
    nombre="Mi primer pipeline",
    intervalo_minutos=10,
    api_url=API_BASE_URL,
    token=TOKEN,
)
pipeline.agregar_tarea(
    "extraer",
    "sql",
    \"\"\"
    SELECT p.categoria, t.region,
           SUM(v.importe_neto) AS importe_neto,
           SUM(v.cantidad) AS cantidad
    FROM curso.ventas v
    JOIN curso.productos p ON p.id_producto = v.id_producto
    JOIN curso.tiendas t ON t.id_tienda = v.id_tienda
    GROUP BY p.categoria, t.region
    \"\"\",
)
pipeline.agregar_tarea("validar", "validacion", depende_de=["extraer"])
pipeline.agregar_tarea(
    "agrupar",
    "agrupacion",
    {"columnas": ["categoria"], "metrica": "sum", "campo": "importe_neto"},
    depende_de=["validar"],
)
pipeline.agregar_tarea("reporte", "reporte_csv", depende_de=["agrupar"])
pipeline.mostrar_diagrama()
pipeline.validar()
"""),
    code("""publicado = pipeline.publicar()
"""),
    md("""## Parte 6 — Ver la ejecución

La primera ejecución periódica llega en el siguiente múltiplo de 10 minutos. Esta celda también pide una ejecución inmediata y muestra el estado real que devuelve Airflow.

Vuelve a ejecutarla un minuto después si el estado todavía es `queued` o `running`.
"""),
    code("""import time

inmediata = pipeline.ejecutar_ahora()
print("ejecucion pedida:", inmediata)
for _ in range(12):
    estado = pipeline.ejecuciones()
    print(estado["ejecuciones"][:3])
    if any(item.get("estado") == "success" for item in estado["ejecuciones"]):
        break
    time.sleep(10)
"""),
    code("""print(pipeline.reporte()[:1500])
"""),
    md("""## Cierre

El resumen de abajo solo marca OK cuando la API confirma una ejecución `success` y el reporte ya existe. No se rellena a mano.
"""),
    code("""ejecuciones = pipeline.ejecuciones()["ejecuciones"]
exito = next((item for item in ejecuciones if item.get("estado") == "success"), None)
reporte_ok = False
try:
    reporte_ok = "estudiante" in pipeline.reporte().splitlines()[0]
except Exception:
    reporte_ok = False

print("ESTUDIA — CLASE 03")
print()
print("Estudiante:", USUARIO)
print("SQL:", "OK" if categorias.shape[0] else "PENDIENTE")
print("Pandas:", "OK" if por_region.shape[0] else "PENDIENTE")
print("Pipeline:", "OK" if publicado.get("estado") == "Publicado" else "PENDIENTE")
print("DAG publicado:", publicado.get("dag_id"))
print("Ejecucion:", exito.get("estado") if exito else "PENDIENTE")
print("Programacion: cada", publicado.get("intervalo_minutos"), "minutos")
print("Reporte:", "disponible" if reporte_ok else "PENDIENTE")
print("Seguimiento:", publicado.get("airflow_url"))
"""),
]

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        "colab": {"provenance": []},
    },
    "cells": celdas,
}
OUT.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(OUT, "celdas", len(celdas))
