"""Cuaderno de práctica y cuaderno resuelto de la clase 05."""

import json
import uuid
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RESPALDO = {
    "data": [
        {
            "id_transaccion": 1,
            "fecha": "2024-01-02",
            "cantidad": 1,
            "importe_neto": 10.5,
            "categoria": "Ropa",
            "region": "Aragón",
        },
        {
            "id_transaccion": 2,
            "fecha": "2024-01-03",
            "cantidad": 4,
            "importe_neto": -2.0,
            "categoria": "Hogar",
            "region": "Aragón",
        },
    ],
    "pagination": {"page": 1, "page_size": 100, "total_records": 10, "total_pages": 1, "has_next": False},
}


def lineas(texto: str) -> list[str]:
    if not texto.endswith("\n"):
        texto += "\n"
    return texto.splitlines(keepends=True)


def md(texto: str) -> dict:
    return {"cell_type": "markdown", "id": uuid.uuid4().hex[:12], "metadata": {}, "source": lineas(texto)}


def code(texto: str) -> dict:
    return {
        "cell_type": "code",
        "id": uuid.uuid4().hex[:12],
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": lineas(texto),
    }


PREPARACION = '''
import json
import os
from getpass import getpass
from pathlib import Path

import pandas as pd
import requests

BASE = "https://34.95.210.33.sslip.io"
RAIZ = Path(os.environ.get("ESTUDIA_DATA", "salida_clase05"))
USAR_RESPALDO = os.environ.get("ESTUDIA_FORZAR_RESPALDO") == "1"
RESPALDO = json.loads("""__RESPALDO__""")
token = None

def listo(valor):
    if isinstance(valor, str) and "COMPLETA" in valor:
        raise RuntimeError("Completa el campo. Es el mismo valor que escribiste en Postman y en el DAG.")

def exigir(respuesta, codigo):
    if respuesta.status_code != codigo:
        raise RuntimeError("Esperaba " + str(codigo) + " y llego " + str(respuesta.status_code))
    return respuesta

usuario = os.environ.get("ESTUDIA_USUARIO") or input("Usuario PostgreSQL: ")
password = os.environ.get("ESTUDIA_PASSWORD") or getpass("Contrasena: ")
print("usuario listo", usuario)
'''.replace("__RESPALDO__", json.dumps(RESPALDO, ensure_ascii=False))

PASOS = [
    (
        """## 00 — Leer la infraestructura, sin desplegarla

Completa estos textos. No levantan contenedores: solo comprueban que reconoces la imagen, el ejecutor, el comando, el puerto y el volumen. En Docker haras lo mismo dentro de los archivos.
""",
        '''
imagen = "COMPLETA"
ejecutor = "COMPLETA"
comando_scheduler = "COMPLETA"
escucha_en = "COMPLETA"
volumen_dags = "COMPLETA"
dependencia = "COMPLETA"
listo(imagen)
listo(ejecutor)
listo(comando_scheduler)
listo(escucha_en)
listo(volumen_dags)
listo(dependencia)
esperado = {
    "imagen": "apache/airflow:3.4.0",
    "ejecutor": "LocalExecutor",
    "comando_scheduler": "scheduler",
    "escucha_en": "127.0.0.1",
    "volumen_dags": "/opt/airflow/dags",
    "dependencia": "t1 >> t2 >> t3 >> t4 >> t5 >> t6",
}
if imagen != esperado["imagen"] or ejecutor != esperado["ejecutor"]:
    raise RuntimeError("Revisa imagen y ejecutor.")
if comando_scheduler != esperado["comando_scheduler"] or escucha_en != esperado["escucha_en"]:
    raise RuntimeError("Revisa el comando del scheduler y la direccion.")
if volumen_dags != esperado["volumen_dags"] or dependencia != esperado["dependencia"]:
    raise RuntimeError("Revisa el volumen y la cadena de operadores.")
print("infraestructura leida")
''',
        '''
imagen = "apache/airflow:3.4.0"
ejecutor = "LocalExecutor"
comando_scheduler = "scheduler"
escucha_en = "127.0.0.1"
volumen_dags = "/opt/airflow/dags"
dependencia = "t1 >> t2 >> t3 >> t4 >> t5 >> t6"
listo(imagen)
listo(ejecutor)
listo(comando_scheduler)
listo(escucha_en)
listo(volumen_dags)
listo(dependencia)
print("infraestructura leida", imagen, ejecutor, dependencia)
''',
        "Esto no crea contenedores. Quien instalo Docker escribe los mismos valores en las plantillas.",
    ),
    (
        """## 01 — La misma API

Comprueba salud antes de armar el pipeline. Si no responde, el docente puede autorizar el respaldo. Ese modo no es Airflow y no es la API.
""",
        '''
url_salud = "COMPLETA"
listo(url_salud)
try:
    salud = requests.get(url_salud, timeout=20)
    exigir(salud, 200)
    print(salud.json())
except Exception:
    if not USAR_RESPALDO:
        raise
    print("RESPALDO")
''',
        '''
url_salud = BASE + "/api/v4/health"
listo(url_salud)
if USAR_RESPALDO:
    print("RESPALDO")
else:
    try:
        salud = requests.get(url_salud, timeout=20)
        exigir(salud, 200)
        print(salud.json())
    except Exception:
        USAR_RESPALDO = True
        print("RESPALDO")
''',
        "Health no pide token. Si falla, no inventes filas: usa el respaldo marcado.",
    ),
    (
        """## 01 — Login, como en Postman

POST `/api/v4/auth/login`. Body JSON con usuario y contraseña. Authorization: No Auth. No imprimas el token.
""",
        '''
url_login = "COMPLETA"
listo(url_login)
if USAR_RESPALDO:
    token = "respaldo"
    print("RESPALDO sin login")
else:
    alta = requests.post(url_login, json={"username": usuario, "password": password}, timeout=20)
    exigir(alta, 200)
    token = alta.json()["access_token"]
    print("tipo", alta.json()["token_type"], "expira", alta.json()["expires_in"], "autenticado", bool(token))
''',
        '''
url_login = BASE + "/api/v4/auth/login"
listo(url_login)
if USAR_RESPALDO:
    token = "respaldo"
    print("RESPALDO sin login")
else:
    alta = requests.post(url_login, json={"username": usuario, "password": password}, timeout=20)
    exigir(alta, 200)
    token = alta.json()["access_token"]
    print("tipo", alta.json()["token_type"], "expira", alta.json()["expires_in"], "autenticado", bool(token))
''',
        "El token se queda en memoria. En Airflow sale de la Connection `estudia_api` y tampoco viaja por XCom.",
    ),
    (
        """## 02 — Ventas planas, con paginación

GET `/api/v4/ventas`. Params: región Aragón, `page_size` 100, páginas 1 y 2, orden `id_transaccion`. El encabezado es `Bearer` y el token. `/ventas` trae `categoria` y `region` en la misma fila. `/ventas/muestra` las anida y no se usa para este gold.
""",
        '''
ruta = "COMPLETA"
region = "COMPLETA"
page_size = "COMPLETA"
paginas = "COMPLETA"
prefijo = "COMPLETA"
listo(ruta)
listo(region)
listo(page_size)
listo(paginas)
listo(prefijo)
paginas_json = []
if USAR_RESPALDO:
    paginas_json = [{"numero": 1, "cuerpo": RESPALDO}]
    print("RESPALDO")
else:
    for numero in range(1, int(paginas) + 1):
        respuesta = requests.get(
            BASE + ruta,
            headers={"Authorization": prefijo + " " + token, "Accept": "application/json"},
            params={"region": region, "page": numero, "page_size": int(page_size), "orden": "id_transaccion", "direccion": "asc"},
            timeout=60,
        )
        exigir(respuesta, 200)
        paginas_json.append({"numero": numero, "cuerpo": respuesta.json()})
        if not respuesta.json()["pagination"]["has_next"]:
            break
print("paginas", len(paginas_json), "filas", sum(len(p["cuerpo"]["data"]) for p in paginas_json))
''',
        '''
ruta = "/api/v4/ventas"
region = "Aragón"
page_size = "100"
paginas = "2"
prefijo = "Bearer"
listo(ruta)
listo(region)
listo(page_size)
listo(paginas)
listo(prefijo)
paginas_json = []
if USAR_RESPALDO:
    paginas_json = [{"numero": 1, "cuerpo": RESPALDO}]
    print("RESPALDO")
else:
    for numero in range(1, int(paginas) + 1):
        respuesta = requests.get(
            BASE + ruta,
            headers={"Authorization": prefijo + " " + token, "Accept": "application/json"},
            params={"region": region, "page": numero, "page_size": int(page_size), "orden": "id_transaccion", "direccion": "asc"},
            timeout=60,
        )
        exigir(respuesta, 200)
        paginas_json.append({"numero": numero, "cuerpo": respuesta.json()})
        if not respuesta.json()["pagination"]["has_next"]:
            break
print("paginas", len(paginas_json), "filas", sum(len(p["cuerpo"]["data"]) for p in paginas_json))
print("alcance parcial: total_records", paginas_json[-1]["cuerpo"]["pagination"]["total_records"])
''',
        "Dos páginas de 100 no son las 50000 ventas. total_records es el filtro completo.",
    ),
    (
        """## 03 — Bronze, silver, validación y gold

Bronze guarda el JSON de cada página. Silver deja las columnas planas. Si hay un id duplicado, el pipeline se detiene. Un importe negativo se conserva. Gold agrupa la extracción, no el censo.
""",
        '''
columna_categoria = "COMPLETA"
columna_region = "COMPLETA"
regla = "COMPLETA"
cadena = "COMPLETA"
listo(columna_categoria)
listo(columna_region)
listo(regla)
listo(cadena)
if regla != "rechazar":
    raise RuntimeError("La regla es rechazar duplicados.")
if cadena != "t1 >> t2 >> t3 >> t4 >> t5 >> t6":
    raise RuntimeError("Escribe la linea t1 >> t2 >> t3 >> t4 >> t5 >> t6.")
bronze = RAIZ / "bronze" / "notebook"
bronze.mkdir(parents=True, exist_ok=True)
for pagina in paginas_json:
    (bronze / f"pagina_{pagina['numero']}.json").write_text(json.dumps(pagina["cuerpo"], ensure_ascii=False), encoding="utf-8")
marco = pd.concat([pd.DataFrame(p["cuerpo"]["data"]) for p in paginas_json], ignore_index=True)
marco = marco[["id_transaccion", "fecha", "cantidad", "importe_neto", columna_categoria, columna_region]].copy()
marco["importe_neto"] = pd.to_numeric(marco["importe_neto"], errors="coerce")
if marco["id_transaccion"].duplicated().any():
    raise RuntimeError("Hay duplicados. No se borran.")
por_categoria = marco.groupby(columna_categoria, as_index=False)["importe_neto"].sum()
por_region = marco.groupby(columna_region, as_index=False)["importe_neto"].sum()
resumen = {
    "transacciones": int(marco.shape[0]),
    "importe_promedio": float(marco["importe_neto"].mean()),
    "alcance": "respaldo" if USAR_RESPALDO else "parcial",
    "nota": "No es el total de 50000 ventas.",
}
reporte = RAIZ / "reports" / "notebook"
reporte.mkdir(parents=True, exist_ok=True)
por_categoria.to_csv(reporte / "por_categoria.csv", index=False)
(reporte / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False), encoding="utf-8")
print(resumen)
print(por_categoria.head(3).to_string(index=False))
print(por_region.head(3).to_string(index=False))
''',
        '''
columna_categoria = "categoria"
columna_region = "region"
regla = "rechazar"
cadena = "t1 >> t2 >> t3 >> t4 >> t5 >> t6"
listo(columna_categoria)
listo(columna_region)
listo(regla)
listo(cadena)
if regla != "rechazar":
    raise RuntimeError("La regla es rechazar duplicados.")
if cadena != "t1 >> t2 >> t3 >> t4 >> t5 >> t6":
    raise RuntimeError("Escribe la linea t1 >> t2 >> t3 >> t4 >> t5 >> t6.")
bronze = RAIZ / "bronze" / "notebook"
bronze.mkdir(parents=True, exist_ok=True)
for pagina in paginas_json:
    (bronze / f"pagina_{pagina['numero']}.json").write_text(json.dumps(pagina["cuerpo"], ensure_ascii=False), encoding="utf-8")
marco = pd.concat([pd.DataFrame(p["cuerpo"]["data"]) for p in paginas_json], ignore_index=True)
marco = marco[["id_transaccion", "fecha", "cantidad", "importe_neto", columna_categoria, columna_region]].copy()
marco["importe_neto"] = pd.to_numeric(marco["importe_neto"], errors="coerce")
if marco["id_transaccion"].duplicated().any():
    raise RuntimeError("Hay duplicados. No se borran.")
por_categoria = marco.groupby(columna_categoria, as_index=False)["importe_neto"].sum()
por_region = marco.groupby(columna_region, as_index=False)["importe_neto"].sum()
resumen = {
    "transacciones": int(marco.shape[0]),
    "importe_promedio": float(marco["importe_neto"].mean()),
    "alcance": "respaldo" if USAR_RESPALDO else "parcial",
    "nota": "No es el total de 50000 ventas.",
}
reporte = RAIZ / "reports" / "notebook"
reporte.mkdir(parents=True, exist_ok=True)
por_categoria.to_csv(reporte / "por_categoria.csv", index=False)
(reporte / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False), encoding="utf-8")
print(resumen)
print(por_categoria.head(3).to_string(index=False))
print(por_region.head(3).to_string(index=False))
''',
        "Bronze es el JSON original. Silver es la tabla. Gold suma la muestra. La cadena es la de las tareas del DAG.",
    ),
]


def cuaderno(resuelto: bool) -> dict:
    titulo = (
        """# EstudIA — Clase 05 — Profesor

Misma práctica que el cuaderno de los estudiantes. Aquí las URLs, los params y la cadena ya están escritos.

Esto ejecuta funciones de Python. No levanta Airflow ni Docker.
"""
        if resuelto
        else """# EstudIA — Clase 05
## La misma práctica, sin Docker

Si no pudiste instalar Docker, empieza por reconocer imagen, puerto y volumen. Después recorre el mismo pipeline. Donde dice `COMPLETA`, escribe el valor de la práctica.

Guardar una copia en Drive y ejecutar hacia abajo. La contraseña no se imprime. Completar estos textos no despliega contenedores ni deja Airflow encendido.
"""
    )
    celdas = [md(titulo), md("## Preparación\n\nPide el usuario de PostgreSQL. Sirve `estudianteNN` o `estudiante`."), code(PREPARACION)]
    for titulo_paso, estudiante, profesor, nota in PASOS:
        celdas.append(md(titulo_paso))
        celdas.append(code(profesor if resuelto else estudiante))
        if resuelto:
            celdas.append(md("**Qué acaba de pasar.** " + nota))
    celdas.append(md(
        """## Dependencias

```mermaid
flowchart LR
  extraer_api --> guardar_bronze --> transformar_silver --> validar_datos --> generar_gold --> exportar_reporte
```

Ejecutar estas funciones en un cuaderno no deja un scheduler encendido. Airflow, en Docker, es el que guarda el DAG, los logs y los reintentos.
"""
    ))
    celdas.append(code(
        '''
try:
    from google.colab import files
    for ruta in (RAIZ / "reports" / "notebook").glob("*"):
        files.download(str(ruta))
except ImportError:
    print("archivos en", RAIZ / "reports" / "notebook")
'''
    ))
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "cells": celdas,
    }


def main() -> None:
    (AQUI / "EstudIA_Clase05_PRACTICA.ipynb").write_text(
        json.dumps(cuaderno(False), ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    (AQUI / "EstudIA_Clase05_PROFESOR.ipynb").write_text(
        json.dumps(cuaderno(True), ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print("notebooks listos")


if __name__ == "__main__":
    main()
