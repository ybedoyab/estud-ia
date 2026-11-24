"""Construye el notebook de la clase 04."""

import json
from pathlib import Path


def md(texto):
    return {"cell_type": "markdown", "metadata": {}, "source": _lineas(texto)}


def code(texto):
    return {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": _lineas(texto),
    }


def _lineas(texto):
    texto = texto.strip("\n") + "\n"
    return [linea + "\n" for linea in texto.split("\n")[:-1]]


celdas = [
md("""
# EstudIA 2026 — Clase 04: APIs REST y Postman

En esta clase no vamos a construir la API. Vamos a consumirla, entender cada parte de una petición HTTP y convertir el JSON en una tabla de Pandas.

La API de EstudIA está en `https://34.95.210.33.sslip.io/api/v4`. Usa el mismo usuario y la misma contraseña de PostgreSQL. El token dura cuatro horas y solo permite leer.
"""),
md("""
## 1. Librerías

`requests` hace la petición. `pandas` convierte el JSON en tabla. No instales paquetes si el entorno ya los trae: Colab incluye ambos.
"""),
code("""
import os
from getpass import getpass
from pathlib import Path

import pandas as pd
import requests

BASE = "https://34.95.210.33.sslip.io"
pd.set_option("display.max_columns", 20)
"""),
md("""
## 2. Una API pública, sin autenticación

Una API es un acuerdo: el cliente pide un recurso y el servidor responde. REST organiza esos recursos en URLs y usa los métodos de HTTP.

`GET` pide una representación. No envía un cuerpo. Esta llamada a JSONPlaceholder no usa token: sirve para ver el viaje antes de entrar a EstudIA.
"""),
code("""
publica = requests.get("https://jsonplaceholder.typicode.com/posts/1", timeout=15)
print(publica.status_code)
print(dict(publica.headers))
publica.json()
"""),
md("""
## 3. Qué significa cada pieza

- `status_code` es el código HTTP. 200 quiere decir que la petición llegó y el servidor pudo responder.
- `headers` describen la respuesta: tipo de contenido, tamaño, identificadores. No son el dato de negocio.
- `.json()` convierte el cuerpo en un diccionario de Python. Si el cuerpo no es JSON, aquí falla: por eso más adelante usamos `raise_for_status()` y un `try`.
"""),
md("""
## 4 y 5. Iniciar sesión

El cuerpo lleva usuario y contraseña. La contraseña se pide con `getpass`, así no queda visible en la celda. Si el profesor automatiza el notebook, puede pasar `ESTUDIA_USUARIO` y `ESTUDIA_PASSWORD` por el entorno; en clase esos valores no se escriben en el archivo.
"""),
code("""
usuario = os.environ.get("ESTUDIA_USUARIO") or input("Usuario PostgreSQL: ")
password = os.environ.get("ESTUDIA_PASSWORD") or getpass("Contraseña: ")
login = requests.post(
    f"{BASE}/api/v4/auth/login",
    json={"username": usuario, "password": password},
    timeout=15,
)
login.raise_for_status()
token = login.json()["access_token"]
print(f"Sesión iniciada para {login.json()['usuario']}. El token queda en memoria y no se imprime.")
"""),
md("""
## 6 y 7. Bearer, línea por línea

```python
response = requests.get(
    url,
    headers={"Authorization": f"Bearer {token}"},
    params={"page": 1, "page_size": 20},
    timeout=15,
)
response.raise_for_status()
datos = response.json()
```

- `requests.get` abre una petición GET. No modifica datos.
- `url` es el recurso, por ejemplo los productos.
- `headers` lleva el token. `Bearer` significa «quien presenta esta credencial». El servidor comprueba la firma, la expiración, el emisor, la audiencia y el alcance `retail:read`.
- `params` se convierte en query string: `?page=1&page_size=20`. No van en el path.
- `timeout=15` corta la espera a 15 segundos. Sin eso, un servidor colgado deja la celda bloqueada.
- `raise_for_status()` lanza una excepción si el código es 400 o mayor. Así no seguimos trabajando con una página de error.
- `response.json()` entrega el diccionario. En las listas paginadas los registros están en `datos["data"]`.
"""),
code("""
def consultar(ruta, params=None):
    response = requests.get(
        f"{BASE}{ruta}",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()

productos = consultar("/api/v4/productos", {"page": 1, "page_size": 20})
pd.DataFrame(productos["data"]).head()
"""),
md("## 8 y 9. Un producto por su identificador\n\nEl identificador va en el path, no en la query. Cambia el número y observa un 404 cuando el recurso no existe."),
code("""
id_producto = int(productos["data"][0]["id_producto"])
detalle = consultar(f"/api/v4/productos/{id_producto}")
detalle
"""),
md("## 10. Filtros\n\nLos filtros que existen en el dataset son `region`, `categoria`, `canal`, `metodo_pago`, `fecha_desde`, `fecha_hasta`, `id_producto` e `id_tienda`. Las regiones son las de las tiendas: Andalucía, Aragón, Castilla y León, Cataluña, Comunidad de Madrid, Comunitat Valenciana y País Vasco."),
code("""
filtro = consultar(
    "/api/v4/ventas",
    {"region": "Andalucía", "categoria": "Electrónica", "page": 1, "page_size": 20},
)
print(filtro["pagination"])
pd.DataFrame(filtro["data"]).head()
"""),
md("""
## 11 y 12. Varias páginas

`has_next` dice si queda otra página. El orden por `id_transaccion` es estable, así que la página 2 no repite la 1. Si una página fallara, el hueco aparecería al comparar los identificadores.
"""),
code("""
def extraer_paginas(paginas=3, page_size=50):
    marcos = []
    vistos = []
    for page in range(1, paginas + 1):
        cuerpo = consultar(
            "/api/v4/ventas",
            {"region": "Andalucía", "page": page, "page_size": page_size, "orden": "id_transaccion"},
        )
        ids = [fila["id_transaccion"] for fila in cuerpo["data"]]
        vistos.extend(ids)
        marcos.append(pd.DataFrame(cuerpo["data"]))
        if not cuerpo["pagination"]["has_next"]:
            break
    marco = pd.concat(marcos, ignore_index=True)
    duplicados = marco["id_transaccion"].duplicated().sum()
    print(f"filas={len(marco)} duplicados={duplicados} paginas_pedidas={paginas}")
    return marco

ventas = extraer_paginas()
ventas.head()
"""),
md("""
## 13. JSON anidado

El detalle de una transacción trae `producto` y `tienda` como objetos. `pd.DataFrame` deja esos objetos como celdas. `pd.json_normalize` los aplana en columnas `producto.nombre` y `tienda.region`.

La muestra pide entre 100 y 300 filas. No hace falta bajar las 50.000 ventas.
"""),
code("""
anidada = consultar("/api/v4/ventas/1")
anidada
"""),
code("""
muestra = consultar("/api/v4/ventas/muestra", {"limite": 200})
plana = pd.json_normalize(muestra["data"])
tabla = pd.DataFrame(muestra["data"])
print("DataFrame conserva objetos:", "producto" in tabla.columns)
print("json_normalize abre columnas:", [col for col in plana.columns if "." in col])
plana.head(3)
"""),
md("## 14 y 15. Indicadores con Pandas\n\nCompara el cálculo local con el indicador que ya agrega la API."),
code("""
por_categoria = plana.groupby("producto.categoria", as_index=False)["importe_neto"].sum()
por_categoria
"""),
code("""
indicador = pd.DataFrame(consultar("/api/v4/indicadores/ventas-por-categoria")["data"])
indicador
"""),
md("## 16. Gráfico"),
code("""
por_categoria.sort_values("importe_neto").plot.barh(
    x="producto.categoria",
    y="importe_neto",
    title="Importe neto de la muestra por categoría",
    legend=False,
)
"""),
md("## 17. Guardar el JSON original y un CSV limpio\n\nEl JSON es la evidencia de lo que entregó la API. El CSV es la tabla ya aplanada."),
code("""
Path("clase04_muestra.json").write_text(
    __import__("json").dumps(muestra, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
plana.to_csv("clase04_muestra.csv", index=False)
print("archivos escritos: clase04_muestra.json, clase04_muestra.csv")
"""),
md("""
## 18. Errores controlados

La API tiene rutas de ejemplo para 403, 429, 500 y 503. No hace falta repetir una llamada hasta tumbar el servidor.

Ante un 429 se lee `Retry-After` y se espera esa cantidad de segundos, como máximo una vez. No reintentamos POST, PUT, PATCH ni DELETE: un reintento podría crear dos tareas.
"""),
code("""
import time

def demostrar(ruta):
    response = requests.get(
        f"{BASE}{ruta}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    print(ruta, response.status_code, response.headers.get("Retry-After"))
    return response

limite = demostrar("/api/v4/ejemplos/demasiado-rapido")
if limite.status_code == 429:
    espera = min(int(limite.headers.get("Retry-After", "1")), 5)
    time.sleep(espera)
    print(f"Espere {espera} s, como indica Retry-After. No se reintenta la escritura.")

for ruta in ("/api/v4/ejemplos/prohibido", "/api/v4/ejemplos/error-interno", "/api/v4/ejemplos/no-disponible"):
    demostrar(ruta)

try:
    requests.get(
        f"{BASE}/api/v4/ventas",
        headers={"Authorization": f"Bearer {token}"},
        params={"page_size": 0},
        timeout=15,
    ).raise_for_status()
except requests.HTTPError as exc:
    print("validacion", exc.response.status_code)
"""),
md("""
## 19. Cómo entraría esto en un DAG

El extractor de arriba es la primera tarea. Las siguientes no vuelven a pedir la contraseña: leen el archivo que guardó la anterior.

```text
extraer_api → guardar_raw → normalizar → validar → generar_reporte
```

En Airflow la contraseña vive en una Connection, no en el código del DAG. El ejemplo docente está en `clase04/examples/airflow/estudia_clase04_demo_api.py` y no está programado en el servidor.

Si esta celda no pudo hablar con la API, usa los JSON de `clase04/examples/json/` y dilo en voz alta: son datos guardados, no una consulta en vivo.
"""),
code("""
respaldo = Path("examples/json/venta_anidada.json")
if not respaldo.exists():
    respaldo = Path("clase04/examples/json/venta_anidada.json")
if respaldo.exists():
    print("Hay un JSON de respaldo en", respaldo)
else:
    print("No hay respaldo local. La práctica en vivo usa la API.")
"""),
]

notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    },
    "cells": celdas,
}
destino = Path(__file__).resolve().parents[1] / "notebooks" / "EstudIA_Clase04_APIs_REST_Postman.ipynb"
destino.parent.mkdir(parents=True, exist_ok=True)
destino.write_text(json.dumps(notebook, ensure_ascii=False, indent=2), encoding="utf-8")
print(destino)
