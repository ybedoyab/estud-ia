import csv
import os
from pathlib import Path

import requests

fila = next(
    item
    for item in csv.DictReader(open("/cuentas.csv", encoding="utf-8"))
    if item["usuario"] == "estudiante46"
)
os.environ["ESTUDIA_USUARIO"] = fila["usuario"]
os.environ["ESTUDIA_PASSWORD"] = fila["password"]
base = "https://34.95.210.33.sslip.io"
login = requests.post(
    base + "/api/v4/auth/login",
    json={"username": fila["usuario"], "password": fila["password"]},
    timeout=20,
)
login.raise_for_status()
token = login.json()["access_token"]
headers = {"Authorization": "Bearer " + token}
destino = Path("/curso/examples/json")
destino.mkdir(parents=True, exist_ok=True)


def guardar(nombre, ruta, params=None):
    respuesta = requests.get(base + ruta, headers=headers, params=params, timeout=30)
    respuesta.raise_for_status()
    (destino / nombre).write_text(respuesta.text, encoding="utf-8")
    print(nombre, respuesta.status_code, len(respuesta.content))


guardar("productos_pagina.json", "/api/v4/productos", {"page": 1, "page_size": 5})
guardar("venta_anidada.json", "/api/v4/ventas/1")
guardar("ventas_pagina.json", "/api/v4/ventas", {"region": "Aragón", "page": 1, "page_size": 2})
guardar("resumen.json", "/api/v4/indicadores/resumen")
guardar("ventas_por_categoria.json", "/api/v4/indicadores/ventas-por-categoria")
print(Path("/curso/examples/json/resumen.json").read_text(encoding="utf-8"))

import nbformat
from nbclient import NotebookClient

nb = nbformat.read("/curso/notebooks/EstudIA_Clase04_APIs_REST_Postman.ipynb", as_version=4)
cliente = NotebookClient(
    nb,
    timeout=180,
    kernel_name="python3",
    resources={"metadata": {"path": "/tmp"}},
)
cliente.execute()
print("notebook_ok", len(nb.cells))
