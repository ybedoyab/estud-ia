"""Genera el notebook del estudiante y el del profesor. No incluye contraseñas."""

import json
import uuid
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CLIENTE = (AQUI.parent / "api" / "app" / "cliente.py").read_text(encoding="utf-8")
ESTUDIANTE = AQUI / "EstudIA_Clase03_SQL_Pandas_Airflow.ipynb"
PROFESOR = AQUI / "EstudIA_Clase03_PROFESOR.ipynb"


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


def cuaderno(celdas, destino):
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
    destino.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    print(destino.name, "celdas", len(celdas))


PIP = '''%pip install -q "psycopg[binary]" "SQLAlchemy>=2" pandas matplotlib requests
print("dependencias listas")
'''

CREDENCIALES = '''import os
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
'''

CONEXION = '''import requests
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
'''

SESION = CLIENTE + '''
sesion = iniciar_sesion(API_BASE_URL, USUARIO, CONTRASENA)
print("sesion de", sesion["usuario"], "vigente por", sesion["expires_in"] // 60, "minutos")
TOKEN = sesion["access_token"]
'''

SQL_CATEGORIA = '''CONSULTA_CATEGORIA = """
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
"""
print("consulta de categorias guardada")
'''

SQL_RANKING = '''CONSULTA_RANKING = """
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
"""
print("consulta de ranking guardada")
'''

PANDAS = '''print(categorias.head())
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
'''

GRAFICO = '''import matplotlib.pyplot as plt

grafico = por_region.head(7)
plt.figure(figsize=(8, 4))
plt.barh(grafico["region"], grafico["venta_neta"])
plt.xlabel("Venta neta")
plt.title("Regiones con mas venta en la muestra")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()
'''

ETL = '''def extraer_datos():
    return consultar("""
        SELECT t.region, p.categoria, v.canal, v.metodo_pago,
               v.importe_neto, v.cantidad
        FROM curso.ventas v
        JOIN curso.productos p ON p.id_producto = v.id_producto
        JOIN curso.tiendas t ON t.id_tienda = v.id_tienda
        LIMIT 5000
    """)


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
'''

PIPELINE = '''pipeline = EstudIAPipeline(
    nombre="Mi primer pipeline",
    intervalo_minutos=10,
    api_url=API_BASE_URL,
    token=TOKEN,
)
pipeline.agregar_tarea(
    "extraer",
    "sql",
    """
    SELECT p.categoria, t.region,
           SUM(v.importe_neto) AS importe_neto,
           SUM(v.cantidad) AS cantidad
    FROM curso.ventas v
    JOIN curso.productos p ON p.id_producto = v.id_producto
    JOIN curso.tiendas t ON t.id_tienda = v.id_tienda
    GROUP BY p.categoria, t.region
    """,
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
'''

estudiante = [
    md("""# EstudIA — Clase 03
## SQL, Pandas y un pipeline que se ejecuta solo

Hoy vas a consultar ventas, limpiar los datos, calcular un indicador y dejar un reporte. Al final, Airflow lo ejecutará cada 10 minutos sin abrir este cuaderno.

```text
SQL  ->  Pandas  ->  ETL  ->  pipeline  ->  Airflow  ->  reporte
```

Guarda tu copia: **Archivo → Guardar una copia en Drive**. Trabaja en esa copia.

Las celdas de conexión ya están listas: ejecútalas. Las consultas, el ETL y las tareas del pipeline las escribes tú, mientras las armamos en clase.
"""),
    md("""## Parte 0 — Preparación

Ejecuta esta celda una vez. Instala lo necesario para consultar PostgreSQL. No instala Airflow: Airflow ya está en el servidor de la clase.
"""),
    code(PIP),
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

Escribe la consulta en la celda. Necesitas `JOIN`, `GROUP BY` y `HAVING`. `HAVING` filtra el grupo ya sumado. `WHERE` no puede usar esa suma.
"""),
    code('''CONSULTA_CATEGORIA = """
SELECT

FROM

"""
print("consulta de categorias guardada")
'''),
    md("""**Pregunta.** ¿Cuáles son los tres productos con más unidades dentro de cada categoría?

Escribe una CTE. `ROW_NUMBER()` numera dentro de cada `PARTITION BY`. El filtro `puesto <= 3` va fuera, en el `SELECT` final: una ventana no se puede filtrar en el mismo `SELECT` donde se calcula.
"""),
    code('''CONSULTA_RANKING = """
WITH unidades AS (
    SELECT

    FROM

)
SELECT

FROM unidades
WHERE
"""
print("consulta de ranking guardada")
'''),
    md("""## Parte 2 — Conexión desde Colab

Esta parte sí está escrita. Ejecútala. Entras con tu usuario individual, por ejemplo `estudiante21`, y con tu contraseña. Se piden una sola vez.

Host, puerto y base ya están configurados. El usuario compartido `estudiante` puede leer, pero no publica un pipeline.
"""),
    code(CREDENCIALES),
    code(CONEXION),
    md("""Si viste `conexion_ok`, ejecuta las dos consultas que escribiste. El resultado aparece como tabla.
"""),
    code('''categorias = consultar(CONSULTA_CATEGORIA)
print("filas y columnas:", categorias.shape)
categorias
'''),
    code('''ranking = consultar(CONSULTA_RANKING)
print("filas y columnas:", ranking.shape)
ranking.head(15)
'''),
    md("""## Parte 3 — Pandas

`groupby` hace aquí lo mismo que `GROUP BY` en SQL: parte las filas y calcula un número por grupo.

Completa la agrupación. La pregunta es: en la muestra que ya bajaste, ¿qué región acumula más venta neta?
"""),
    code('''print(categorias.head())
categorias.info()
print("nulos")
print(categorias.isna().sum())
print("filas duplicadas:", int(categorias.duplicated().sum()))

por_region = (
    categorias.groupby("COMPLETA", as_index=False)["COMPLETA"]
    .sum()
    .sort_values("COMPLETA", ascending=False)
)
por_region
'''),
    code('''import matplotlib.pyplot as plt

grafico = por_region.head(7)
plt.figure(figsize=(8, 4))
plt.barh(grafico["COMPLETA"], grafico["COMPLETA"])
plt.xlabel("Venta neta")
plt.title("Regiones con mas venta en la muestra")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()
'''),
    md("""## Parte 4 — El ETL

Escribe el cuerpo de las cuatro funciones.

1. **Extraer** lee ventas desde PostgreSQL. Trae región, categoría, canal, método de pago, importe neto y cantidad. Limita a 5 000 filas.
2. **Transformar** quita filas sin región, categoría o importe, y deja el importe como número.
3. **Validar** rechaza un resultado vacío o con importes vacíos.
4. **El reporte** suma el importe y la cantidad por categoría, de mayor a menor venta.

La última línea ya llama a las cuatro en orden. No la cambies.
"""),
    code('''def extraer_datos():
    return consultar("""
        SELECT
        FROM
    """)


def transformar_datos(df):
    return df


def validar_datos(df):
    return df


def generar_reporte(df):
    return df


reporte_local = generar_reporte(validar_datos(transformar_datos(extraer_datos())))
print("filas y columnas:", reporte_local.shape)
reporte_local
'''),
    md("""## Parte 5 — El pipeline

Hasta aquí el trabajo vive en Colab. Un DAG es ese mismo trabajo, partido en tareas, con un orden y un horario.

`EstudIAPipeline` es el DAG. `intervalo_minutos` es la programación: 5, 10 o 15. `agregar_tarea` es una task. `depende_de` dice cuál tarea espera a cuál.

Ejecuta la celda siguiente. Carga la herramienta. No hace falta reescribirla.
"""),
    code(SESION),
    md("""Ahora escribe tu DAG. Cuatro tareas, en este orden:

1. `extraer`, tipo `sql`. La consulta debe leer `curso.` y devolver al menos `categoria` e `importe_neto`.
2. `validar`, tipo `validacion`. Depende de `extraer`.
3. `agrupar`, tipo `agrupacion`. Columnas, métrica (`sum`) y campo. Depende de `validar`.
4. `reporte`, tipo `reporte_csv`. Depende de `agrupar`.

El identificador del DAG lo pone el servidor a partir de tu usuario. Tú no lo eliges.
"""),
    code('''pipeline = EstudIAPipeline(
    nombre="",
    intervalo_minutos=0,
    api_url=API_BASE_URL,
    token=TOKEN,
)
pipeline.agregar_tarea(
    "",
    "",
    """
    """,
)
pipeline.agregar_tarea(
    "",
    "",
    depende_de=[],
)
pipeline.agregar_tarea(
    "",
    "",
    {"columnas": [], "metrica": "", "campo": ""},
    depende_de=[],
)
pipeline.agregar_tarea(
    "",
    "",
    depende_de=[],
)
pipeline.mostrar_diagrama()
pipeline.validar()
'''),
    md("""Cuando `validar()` no marque error, publica. Si ya habías publicado, esta llamada reemplaza tu DAG. No crea un segundo.
"""),
    code('''publicado = pipeline.publicar()
'''),
    md("""## Parte 6 — Ver la ejecución

La primera ejecución periódica llega en el siguiente múltiplo de tus minutos. Esta celda también pide una ejecución inmediata y muestra el estado real que devuelve Airflow.

Vuelve a ejecutarla un minuto después si el estado todavía es `queued` o `running`.

En el navegador, entra a https://airflow.34.95.210.33.sslip.io con tu mismo usuario y tu misma contraseña. Solo ves tu DAG.
"""),
    code('''import time

inmediata = pipeline.ejecutar_ahora()
print("ejecucion pedida:", inmediata)
for _ in range(12):
    estado = pipeline.ejecuciones()
    print(estado["ejecuciones"][:3])
    if any(item.get("estado") == "success" for item in estado["ejecuciones"]):
        break
    time.sleep(10)
'''),
    code('''print(pipeline.reporte()[:1500])
'''),
    md("""## Cierre

El resumen solo marca OK cuando la API confirma una ejecución `success` y el reporte ya existe. No se rellena a mano.
"""),
    code('''ejecuciones = pipeline.ejecuciones()["ejecuciones"]
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
'''),
]

profesor = [
    md("""# EstudIA — Clase 03 — Cuaderno del profesor

Misma estructura que el de los estudiantes. Aquí las respuestas ya están escritas y, debajo de cada bloque, qué hace cada línea.

Proyecta el cuaderno del estudiante. Dicta o escribe con ellos. Este archivo es tu guía, no la plantilla que ellos copian.

Archivo de los estudiantes: `EstudIA_Clase03_SQL_Pandas_Airflow.ipynb`.
"""),
    md("""## Parte 0 — Preparación

Diles que ejecuten la celda. `%pip` instala paquetes en la sesión de Colab. No instala Airflow.
"""),
    code(PIP),
    md("""## Parte 1 — Primera consulta

**Pregunta.** ¿Qué combinaciones de región y categoría superan un millón de venta neta?

Líneas:

1. `SELECT t.region, p.categoria` — la región sale de la tienda (`t`) y la categoría del producto (`p`).
2. `COUNT(*) AS transacciones` — cuántas filas de venta cayeron en ese grupo.
3. `ROUND(SUM(v.importe_neto), 2) AS venta_neta` — suma lo que sí se cobró, con el descuento ya aplicado, y deja dos decimales.
4. `FROM curso.ventas v` — la tabla de hechos. `v` es el alias.
5. `JOIN curso.productos ...` — trae la categoría. Sin este JOIN, `ventas` no tiene `categoria`.
6. `JOIN curso.tiendas ...` — trae la región de la tienda, no la del cliente.
7. `GROUP BY t.region, p.categoria` — una fila por cada pareja región-categoría.
8. `HAVING SUM(v.importe_neto) > 1000000` — filtra grupos. `WHERE` iría antes de agrupar y no puede usar esta suma.
9. `ORDER BY venta_neta DESC` — primero el grupo que más vendió.
10. `LIMIT 15` — solo las primeras 15 parejas. En la base hay 35 que pasan el millón.

Resultado esperado: 15 filas, con columnas `region`, `categoria`, `transacciones`, `venta_neta`.
"""),
    code(SQL_CATEGORIA),
    md("""## Parte 1 — Ranking

**Pregunta.** ¿Cuáles son los tres productos con más unidades dentro de cada categoría?

Líneas:

1. `WITH unidades AS (` — la CTE calcula el ranking. El filtro va después, afuera.
2. `SELECT p.categoria, p.nombre` — el producto se identifica por categoría y nombre. En este catálogo cada categoría tiene una sola subcategoría, así que varios nombres se parecen.
3. `SUM(v.cantidad) AS unidades` — unidades vendidas de ese producto.
4. `ROW_NUMBER() OVER (` — numera filas. No las borra.
5. `PARTITION BY p.categoria` — la numeración vuelve a empezar en cada categoría.
6. `ORDER BY SUM(v.cantidad) DESC` — el puesto 1 es el que más unidades tiene.
7. `) AS puesto` — el número queda en la columna `puesto`.
8. `JOIN` y `GROUP BY p.categoria, p.nombre` — una fila por producto antes de numerar.
9. `SELECT ... FROM unidades WHERE puesto <= 3` — aquí sí se puede filtrar el puesto, porque ya existe como columna de la CTE.
10. `ORDER BY categoria, puesto` — deja juntos los tres de cada categoría.

Resultado esperado: 15 filas. Cinco categorías por tres puestos.
"""),
    code(SQL_RANKING),
    md("""## Parte 2 — Conexión

Esta celda sí va escrita en el cuaderno de ellos. Explícala, no pidas que la reescriban.

1. `API_BASE_URL`, `DB_HOST`, `DB_PORT`, `DB_NAME` — datos públicos. No son la contraseña.
2. `input` pide el usuario. `getpass` pide la contraseña sin mostrarla.
3. Si escriben `estudiante` sin número, la celda se detiene. Esa cuenta no publica un DAG.
4. La siguiente celda baja el certificado público y abre la conexión con `sslmode=verify-full`.
5. `NullPool` y `prepare_threshold=None` evitan un fallo conocido con PgBouncer.
6. `consultar` ejecuta SQL y devuelve un DataFrame. Si la contraseña está mal, el mensaje no la imprime.
7. `SELECT 1 AS conexion_ok` solo comprueba que la sesión entró.
"""),
    code(CREDENCIALES),
    code(CONEXION),
    md("""Cuando `conexion_ok` aparezca, ejecuta las dos consultas que escribieron.
"""),
    code('''categorias = consultar(CONSULTA_CATEGORIA)
print("filas y columnas:", categorias.shape)
categorias
'''),
    code('''ranking = consultar(CONSULTA_RANKING)
print("filas y columnas:", ranking.shape)
ranking.head(15)
'''),
    md("""## Parte 3 — Pandas

`categorias` ya es la tabla de la primera consulta. Pandas no vuelve a PostgreSQL.

1. `head()` — las primeras filas, para ver los nombres de columna.
2. `info()` — tipo de cada columna y cuántos valores no nulos hay.
3. `isna().sum()` — nulos por columna. En esta consulta no debería haber.
4. `duplicated().sum()` — filas repetidas. El `GROUP BY` ya dejó una fila por grupo, así que sale 0.
5. `groupby("region", as_index=False)` — equivale al `GROUP BY t.region`. `as_index=False` deja `region` como columna, no como índice.
6. `["venta_neta"].sum()` — suma la venta de las categorías de esa región.
7. `sort_values(..., ascending=False)` — la región de arriba es la que más vendió en la muestra de 15 filas. No es el total de la base: la consulta ya había cortado en 15.

En el gráfico, `barh` usa la región en el eje vertical y la venta en el horizontal. `invert_yaxis` deja la más grande arriba. `head(7)` muestra como máximo siete regiones.
"""),
    code(PANDAS),
    code(GRAFICO),
    md("""## Parte 4 — ETL

Cuatro funciones. La última línea las llama en orden: extraer, transformar, validar, reportar.

`extraer_datos`

1. `consultar` recibe el SQL y baja las filas a un DataFrame.
2. Trae región de la tienda, categoría del producto, canal, método de pago, importe y cantidad.
3. Los dos `JOIN` son los mismos de la primera consulta.
4. `LIMIT 5000` — la clase no necesita las 50 000 ventas. El servidor, más tarde, también corta en 5 000.

`transformar_datos`

1. `dropna(subset=[...])` — bota la fila si le falta región, categoría o importe. No bota una fila solo porque otra columna esté vacía.
2. `.copy()` — trabaja sobre una copia, no sobre la vista que devuelve `dropna`.
3. `astype(float)` — el importe queda como número para poder sumarlo.

`validar_datos`

1. Si el DataFrame está vacío, lanza un error y el reporte no se genera.
2. Si quedó algún importe vacío, también se detiene.
3. Si pasa, devuelve el mismo DataFrame.

`generar_reporte`

1. `groupby("categoria")` — una fila por categoría.
2. `agg(venta_neta=..., unidades=...)` — dos cálculos en la misma agrupación.
3. `sort_values` — la categoría que más vendió queda primera.

Resultado esperado: una fila por categoría presente en las 5 000 filas, con `venta_neta` y `unidades`.
"""),
    code(ETL),
    md("""## Parte 5 — Del ETL al DAG

Diles esto antes de escribir:

- Un **DAG** es el pipeline completo.
- Una **task** es una de las funciones: extraer, validar, agrupar, reportar.
- `depende_de` es la flecha. `validar` no empieza hasta que `extraer` termina.
- `intervalo_minutos` es el horario. En Airflow queda como un cron en hora de Bogotá. `catchup` está apagado: no recupera horas perdidas.
- El servidor no ejecuta el Python que escriben en Colab. Ejecuta la consulta, la validación, la agrupación y el CSV. Por eso el tipo de la tarea es un nombre de una lista corta, no código libre.

La celda de la herramienta solo se ejecuta. `iniciar_sesion` comprueba el usuario contra PostgreSQL y guarda un token de cuatro horas. `EstudIAPipeline` todavía no publica nada.
"""),
    code(SESION),
    md("""La celda que ellos deben completar, ya resuelta:

1. `nombre` — un título visible. No es el identificador del DAG.
2. `intervalo_minutos=10` — cada diez minutos. También acepta 5 o 15. Cero no sirve.
3. `api_url` y `token` — a dónde se envía y quién lo envía. Salen de las celdas anteriores.
4. Primera tarea, id `extraer`, tipo `sql`. La consulta agrupa por categoría y región y devuelve `importe_neto` y `cantidad`. Esas columnas las usa la tarea de agrupar.
5. Segunda, id `validar`, tipo `validacion`, `depende_de=["extraer"]`. Revisa que la consulta haya traído filas.
6. Tercera, id `agrupar`, tipo `agrupacion`. `columnas` es el `GROUP BY`, `metrica` es `sum` y `campo` es la columna que se suma.
7. Cuarta, id `reporte`, tipo `reporte_csv`. Escribe el archivo con el usuario y la fecha.
8. `mostrar_diagrama()` — imprime el orden en la celda. Aún no toca Airflow.
9. `validar()` — la API revisa la consulta y las dependencias. Si hay un `DELETE` o un tipo inventado, aquí se rechaza y no se crea el DAG.

En Airflow eso queda como un DAG `estudia_estudianteNN_pipeline`, con una task llamada `pipeline` que recorre estas cuatro en orden. La programación es `*/10 * * * *` en `America/Bogota`.
"""),
    code(PIPELINE),
    md("""`publicar()` envía el JSON, espera a que Airflow vea el archivo y solo entonces dice `Publicado`. Devuelve el DAG, el horario, la próxima hora y el enlace.

Si publican otra vez, se reemplaza el mismo DAG.
"""),
    code('''publicado = pipeline.publicar()
'''),
    md("""## Parte 6 — La corrida

1. `ejecutar_ahora()` pide una corrida manual. No reemplaza el horario.
2. El ciclo consulta el estado real cada 10 segundos, hasta doce veces.
3. Para cuando aparece `success`. `queued` o `running` significan que todavía va.
4. `reporte()` lee el CSV de ese estudiante. La primera columna es su usuario.

En la interfaz, cada quien entra con `estudianteNN` y la misma contraseña. La lista muestra solo su DAG. Tú entras como `docente` y ves todos.

El DAG de demostración, `estudia_clase03_demo`, corre cada cinco minutos. Para el fallo controlado, pon la variable `estudia_demo_forzar_error` en `1` y luego vuelve a `0`.
"""),
    code('''import time

inmediata = pipeline.ejecutar_ahora()
print("ejecucion pedida:", inmediata)
for _ in range(12):
    estado = pipeline.ejecuciones()
    print(estado["ejecuciones"][:3])
    if any(item.get("estado") == "success" for item in estado["ejecuciones"]):
        break
    time.sleep(10)
'''),
    code('''print(pipeline.reporte()[:1500])
'''),
    md("""## Cierre

La celda final no tiene respuestas escritas a mano. Marca OK solo si la tabla de SQL tiene filas, Pandas agrupó, la API dice `Publicado`, hay una corrida `success` y el reporte contiene la palabra `estudiante`.
"""),
    code('''ejecuciones = pipeline.ejecuciones()["ejecuciones"]
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
'''),
]

cuaderno(estudiante, ESTUDIANTE)
cuaderno(profesor, PROFESOR)
