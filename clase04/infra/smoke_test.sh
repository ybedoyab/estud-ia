#!/bin/bash
# Comprueba la API con una cuenta sintética. Imprime códigos y un JSON sin secretos.
set -euo pipefail
python3 - <<'PY'
import csv
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://34.95.210.33.sslip.io"
cuentas = list(csv.DictReader(Path("/home/yulcr/estudia-clase04-cuentas.csv").open(encoding="utf-8")))
usuario = next(fila for fila in cuentas if fila["usuario"] == "estudiante46")

def llamar(method, path, body=None, token=None, ok=(200,)):
    datos = None if body is None else json.dumps(body).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(BASE + path, data=datos, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            crudo = response.read()
            print(method, path, response.status)
            return response.status, json.loads(crudo) if crudo else {}
    except urllib.error.HTTPError as exc:
        print(method, path, exc.code)
        if exc.code not in ok:
            raise SystemExit(1)
        return exc.code, {}

_, salud = llamar("GET", "/api/v4/health")
assert salud["servicio"] == "estudia-clase04"
_, clase03 = llamar("GET", "/health")
assert clase03["servicio"] == "estudia-clase03"
_, sesion = llamar("POST", "/api/v4/auth/login", {"username": usuario["usuario"], "password": usuario["password"]})
token = sesion["access_token"]
assert sesion["scope"] == "retail:read"
_, yo = llamar("GET", "/api/v4/auth/me", token=token)
print("usuario", yo["usuario"], "identidad", yo["identidad"])
_, productos = llamar("GET", "/api/v4/productos?page=1&page_size=1", token=token)
print("primer_producto", productos["data"][0]["id_producto"], productos["data"][0]["nombre"])
_, venta = llamar("GET", "/api/v4/ventas/1", token=token)
print(json.dumps(venta, ensure_ascii=False))
_, pagina = llamar("GET", "/api/v4/ventas?region=Arag%C3%B3n&page=1&page_size=2", token=token)
print("pagina", pagina["pagination"])
codigo, _ = llamar("POST", "/api/v4/ventas", {"x": 1}, token=token, ok=(405,))
assert codigo == 405
ataque = "/api/v4/ventas?region=" + urllib.parse.quote("' OR 1=1 --") + "&page=1&page_size=5"
_, inyeccion = llamar("GET", ataque, token=token)
assert all(fila["region"] == "' OR 1=1 --" for fila in inyeccion["data"])
print("inyeccion_filas", len(inyeccion["data"]))
_, alta = llamar("POST", "/api/v4/sandbox/tareas", {"titulo": "humo", "detalle": "prueba", "estado": "pendiente", "prioridad": 1}, token=token, ok=(201,))
print("sandbox", alta["id_tarea"])
print("smoke_ok")
PY
