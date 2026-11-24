"""Construye el notebook único de la clase 04.

Los ejemplos de respaldo quedan dentro del cuaderno para que funcione en Colab
sin clonar el repositorio. No contienen contraseñas ni tokens.
"""

import json
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook


def md(texto):
    return new_markdown_cell(texto.strip("\n") + "\n")


def code(texto):
    return new_code_cell(texto.strip("\n") + "\n")


def respaldo_embebido():
    carpeta = Path(__file__).resolve().parents[1] / "examples" / "json"
    productos = json.loads((carpeta / "productos_pagina.json").read_text(encoding="utf-8"))
    ventas = json.loads((carpeta / "ventas_pagina.json").read_text(encoding="utf-8"))
    venta = json.loads((carpeta / "venta_anidada.json").read_text(encoding="utf-8"))
    resumen = json.loads((carpeta / "resumen.json").read_text(encoding="utf-8"))
    por_categoria = json.loads((carpeta / "ventas_por_categoria.json").read_text(encoding="utf-8"))
    muestra = []
    for fila in ventas["data"]:
        muestra.append(
            {
                "id_transaccion": fila["id_transaccion"],
                "fecha": fila["fecha"],
                "cantidad": fila["cantidad"],
                "importe_neto": fila["importe_neto"],
                "producto": {
                    "id_producto": fila["id_producto"],
                    "nombre": "ejemplo guardado",
                    "categoria": fila["categoria"],
                },
                "tienda": {"id_tienda": fila["id_tienda"], "region": fila["region"]},
            }
        )
    return {
        "aviso": "Ejemplos guardados de respuestas reales, sin credenciales. No son la sesión en vivo.",
        "productos": productos,
        "ventas_aragon": ventas,
        "venta": venta,
        "resumen": resumen,
        "por_categoria": por_categoria,
        "muestra": {"data": muestra, "total": len(muestra), "nota": "Extracto didáctico, no las 200 filas de la API."},
        "openapi": {
            "openapi": "3.1.0",
            "info": {"title": "EstudIA clase 04", "version": "1.0.0"},
            "aviso": "Extracto didáctico. En modo API el cuaderno lee openapi.json en vivo.",
            "paths": {
                "/api/v4/health": {"get": {"responses": {"200": {}}}},
                "/api/v4/auth/login": {
                    "post": {
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {"schema": {"$ref": "#/components/schemas/LoginBody"}}
                            },
                        },
                        "responses": {"200": {}, "422": {}},
                    }
                },
                "/api/v4/productos": {"get": {"responses": {"200": {}}}},
                "/api/v4/productos/{id_producto}": {
                    "get": {
                        "parameters": [{"name": "id_producto", "in": "path", "required": True}],
                        "responses": {"200": {}, "404": {}},
                    }
                },
                "/api/v4/ventas": {
                    "get": {
                        "parameters": [
                            {"name": "region", "in": "query", "required": False},
                            {"name": "categoria", "in": "query", "required": False},
                            {"name": "page", "in": "query", "required": False},
                            {"name": "page_size", "in": "query", "required": False},
                        ],
                        "responses": {"200": {}, "400": {}, "422": {}},
                    }
                },
                "/api/v4/sandbox/tareas": {"get": {"responses": {"200": {}}}, "post": {"responses": {"201": {}}}},
            },
            "components": {
                "schemas": {
                    "LoginBody": {
                        "required": ["username", "password"],
                        "properties": {"username": {"type": "string"}, "password": {"type": "string"}},
                    },
                    "TareaBody": {
                        "required": ["titulo"],
                        "properties": {
                            "titulo": {"type": "string"},
                            "detalle": {"type": "string"},
                            "estado": {"type": "string"},
                            "prioridad": {"type": "integer"},
                        },
                    },
                },
                "securitySchemes": {
                    "HTTPBearer": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
                },
            },
        },
    }


RESPALDO = json.dumps(respaldo_embebido(), ensure_ascii=False)

celdas = []

celdas.append(md("""
# EstudIA 2026 — Clase 04: APIs REST

Este cuaderno se abre en Google Colab. No hace falta clonar el repositorio, ni instalar Postman, Docker, PostgreSQL o Airflow.

Hay tres formas equivalentes de hacer el laboratorio. Este archivo es la vía de Python. Postman y Swagger recorren los mismos recursos.

1. **Postman**, si lo tienes instalado: armas cada petición a mano.
2. **Swagger UI**, en el navegador, sin instalar nada: [documentación interactiva](https://34.95.210.33.sslip.io/api/v4/docs).
3. **Este cuaderno**: login, métodos HTTP, parámetros, paginación, errores, JSON y Pandas.

Guarda una copia con **Archivo → Guardar una copia en Drive** y ejecuta las celdas de arriba hacia abajo. No te saltes el login: el token vive solo en la memoria de esta sesión.
"""))

celdas.append(md("""
## Cómo está organizada la clase

**Bloque A.** Qué es una API, en qué se diferencia de una base de datos y de una pantalla, y cómo se hablan un cliente y un servidor.

**Bloque B.** El contrato: OpenAPI, los esquemas y la diferencia entre la especificación, Swagger y Postman.

**Bloque C.** Los métodos HTTP, los parámetros y los códigos de respuesta.

**Bloque D.** Autenticación, token y la diferencia entre esta sesión y una conexión directa a PostgreSQL.

**Bloque E.** La misma práctica en las tres herramientas.

**Bloque F.** Paginación, JSON anidado, Pandas, errores y el puente hacia Airflow.

Si la API no responde, el cuaderno lo dice. No rellena la práctica con datos inventados. El modo respaldo, más abajo, solo se activa si tú o el docente lo piden, y cada resultado de ese modo lleva la marca `RESPALDO`.
"""))

celdas.append(md("""
## 00 — Preparación

`requests` envía la petición HTTP. `pandas` convierte registros en tabla. `getpass` oculta la contraseña. `json` lee el contrato y guarda archivos.

Colab ya trae estas librerías. Si una importación falla, crea una celda nueva y ejecuta `!pip install requests pandas matplotlib`. No instales Docker ni un servidor.
"""))

celdas.append(code("""
import json
import os
from datetime import datetime, timezone
from getpass import getpass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import requests

try:
    from IPython.display import display
except ImportError:
    display = print

BASE = "https://34.95.210.33.sslip.io"
pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 120)

hecho = {
    "api_accesible": False,
    "autenticacion": False,
    "consulta": False,
    "paginacion": False,
    "normalizados": False,
    "validaciones": False,
    "grafico": False,
    "archivos": False,
}
errores_observados = []
token = None
usuario = None
MODO = "sin_conexion"
api_responde = False

SOLUCIONES = {
    "02": (
        "Un GET documentado es /api/v4/productos. "
        "Un POST es /api/v4/auth/login. "
        "En el esquema al que apunta el $ref del login, username y password son requeridos. "
        "region es un parámetro de query opcional de /api/v4/ventas. "
        "200 aparece entre las respuestas de esas operaciones."
    ),
    "04": "El path /api/v4/productos/2 pide el producto con identificador 2. El 2 viaja en la URL, no en el cuerpo.",
    "05": (
        "region=Aragón y categoria=Hogar viajan en la query string. "
        "params={'region': 'Aragón', 'categoria': 'Hogar', 'page': 1, 'page_size': 2} "
        "no modifica la ruta /api/v4/ventas."
    ),
    "06": (
        "POST crea y devuelve id_tarea. PUT reemplaza titulo, detalle, estado y prioridad. "
        "PATCH envía solo {'estado': 'hecha'}. DELETE responde 204 sin JSON. "
        "Otra sesión del mismo usuario no ve esa tarea."
    ),
    "08": "La clave de cada venta es id_transaccion. No existe id_venta en esta API.",
    "12": (
        "Elige una región real, por ejemplo Aragón. Pide pocas páginas, valida id_transaccion "
        "y calcula un indicador solo sobre esa muestra. Márcalo como extracción parcial."
    ),
}

def ver_solucion(numero):
    texto = SOLUCIONES.get(str(numero))
    if texto is None:
        print("No hay una solución con ese número.")
        return
    print("Solución del ejercicio", numero)
    print(texto)

def comprobar(condicion, mensaje):
    if condicion:
        print("Comprobación correcta:", mensaje)
        return
    raise AssertionError("Revisa el ejercicio: " + mensaje)

def llamar(metodo, ruta, *, params=None, cuerpo=None, token_sesion=None, timeout=25):
    if MODO != "api":
        raise RuntimeError("Esta llamada pertenece a la API en vivo y el cuaderno está en otro modo.")
    headers = {"Accept": "application/json"}
    if cuerpo is not None:
        headers["Content-Type"] = "application/json"
    if token_sesion:
        headers["Authorization"] = "Bearer " + token_sesion
    return requests.request(
        metodo,
        BASE + ruta,
        params=params,
        json=cuerpo,
        headers=headers,
        timeout=timeout,
    )

print("Librerías listas. La base es", BASE)
"""))

celdas.append(md("""
Primero comprobamos si la API está viva. `GET /api/v4/health` no pide token. Si falla, verás el error. No lo vamos a tapar con una tabla ficticia.
"""))

celdas.append(code("""
try:
    salud = requests.get(BASE + "/api/v4/health", timeout=20)
    salud.raise_for_status()
    api_responde = True
    print("status", salud.status_code)
    print(salud.json())
except requests.exceptions.Timeout:
    api_responde = False
    print("La API no respondió a tiempo (Timeout). Revisa tu conexión antes de seguir.")
except requests.exceptions.ConnectionError as exc:
    api_responde = False
    print("No hubo conexión con la API (ConnectionError).")
    print(type(exc).__name__)
except requests.HTTPError as exc:
    api_responde = False
    print("La API respondió con error:", exc.response.status_code)
"""))

celdas.append(md("""
El modo respaldo usa ejemplos guardados dentro de este cuaderno. Sirve cuando no puedes llegar a la API y el docente lo autoriza. Esos ejemplos salen de respuestas reales ya anonimizadas: no traen contraseñas ni tokens.

No actives el respaldo si la celda anterior mostró `estudia-clase04`. Mezclar las dos fuentes haría pasar un archivo viejo por una consulta de hoy.
"""))

celdas.append(code('''
respaldo = json.loads(r"""__RESPALDO_JSON__""")
print(respaldo["aviso"])
'''.replace("__RESPALDO_JSON__", RESPALDO) + '''


USAR_RESPALDO = False  # TODO: cámbialo a True solo si /health falló y el docente autoriza el respaldo.
if os.environ.get("ESTUDIA_FORZAR_RESPALDO") == "1":
    USAR_RESPALDO = True

if USAR_RESPALDO:
    MODO = "respaldo"
    print("RESPALDO activo. Ningún resultado siguiente se presenta como respuesta en vivo de la API.")
    if api_responde:
        print("La API sí había respondido. Se ignora a propósito para esta corrida de respaldo.")
elif api_responde:
    MODO = "api"
    hecho["api_accesible"] = True
    print("Modo API. Los resultados salen de", BASE)
else:
    MODO = "sin_conexion"
    raise RuntimeError(
        "Sin conexión y sin respaldo. No sigas con datos simulados. "
        "Revisa la red o, con autorización, cambia USAR_RESPALDO a True y ejecuta de nuevo esta celda."
    )
'''))

celdas.append(md("""
## Bloque A — Qué es una API

Una API es un contrato que permite que dos sistemas intercambien información sin que uno tenga que conocer cómo está programado el otro. El cliente pide un recurso. El servidor decide si puede entregarlo y responde con una representación de ese recurso.

Una base de datos guarda los datos y responde SQL a quien tiene permiso de conectarse. Una interfaz gráfica es la pantalla que usa una persona. La API no es ninguna de las dos: es la puerta acordada entre programas. Esta clase no abre PostgreSQL. Entra por HTTPS a una API que, por dentro, lee esa base con una cuenta técnica de solo lectura.

En cada intercambio hay cuatro piezas: el **cliente** (Postman, el navegador o este cuaderno), el **servidor** (la API de EstudIA), la **petición** y la **respuesta**.

**HTTP** es el protocolo de esas peticiones. **HTTPS** es HTTP dentro de un canal cifrado. La URL de la clase empieza por `https://`: la contraseña y el token no viajan en claro.

Una **API REST** trata la información como recursos. Cada recurso tiene una URL. El método HTTP dice qué quieres hacer con él. El servidor no recuerda la petición anterior: cada llamada lleva lo necesario para entenderse. Eso es comunicación sin estado. REST no exige JSON. JSON es el formato habitual de esta API y de muchas otras; el contrato podría haber elegido otro.

Una **API SOAP** define operaciones en un contrato WSDL. El mensaje va en un sobre XML, con encabezado y cuerpo. SOAP es un protocolo de mensajes, no un estilo de URLs, y no está atado siempre a HTTP: el sobre puede viajar por otros protocolos. Aquí no vamos a llamar un servicio SOAP. Nos basta reconocer el sobre y el WSDL para no confundirlos con REST.

**GraphQL** deja que el cliente pida la forma exacta de la respuesta en una consulta. **gRPC** usa contratos binarios y suele trabajar sobre HTTP/2. No los practicamos en esta sesión.

Un **endpoint** es una operación concreta: un método más una ruta. `GET /api/v4/productos` y `POST /api/v4/auth/login` son endpoints distintos aunque vivan en el mismo servidor.

La URL se parte así:

`https://34.95.210.33.sslip.io/api/v4/productos/1?page=1`

- `https` es el esquema.
- `34.95.210.33.sslip.io` es el host.
- `/api/v4/productos/1` es el path. El `1` identifica un producto.
- Lo que va después de `?` son parámetros de consulta, no parte del nombre del recurso.
"""))

celdas.append(md("""
## 01 — Primera petición HTTP

Antes de autenticarnos, mira una API pública pequeña. JSONPlaceholder no es EstudIA y no pide contraseña. Sirve para ver el viaje de ida y vuelta.
"""))

celdas.append(code("""
publica = requests.get("https://jsonplaceholder.typicode.com/posts/1", timeout=20)
print("URL", publica.url)
print("método", publica.request.method)
print("status", publica.status_code)
for nombre in ("Content-Type", "Date", "Content-Length"):
    print("header", nombre, publica.headers.get(nombre))
"""))

celdas.append(md("""
`response.text` es el cuerpo, todavía como texto. `response.json()` lo convierte en diccionarios y listas de Python. Un `DataFrame` es otra cosa: una tabla. Las tres representaciones conviven; no son el mismo objeto.
"""))

celdas.append(code("""
print("tipo de text", type(publica.text).__name__)
print(publica.text[:180])
objeto = publica.json()
print("tipo de json", type(objeto).__name__, "claves", sorted(objeto))
tabla_publica = pd.DataFrame([objeto])
print("tipo de DataFrame", type(tabla_publica).__name__, "forma", tabla_publica.shape)
tabla_publica
"""))

celdas.append(md("""
## Bloque B — Contratos y documentación

El **contrato de una API** dice qué se puede pedir, con qué datos y qué forma tiene la respuesta. No es el código del servidor ni la base de datos.

Un **esquema** describe una estructura: qué campos existen, de qué tipo son y cuáles son obligatorios. **JSON Schema** es el lenguaje que usa OpenAPI para eso. Puede declarar tipos, campos requeridos, longitudes y valores permitidos.

**OpenAPI** es el documento que reúne rutas, operaciones, parámetros, cuerpos, respuestas, esquemas y mecanismos de seguridad. La especificación de esta clase está en `GET /api/v4/openapi.json`.

**Swagger UI** es una página que lee ese documento y deja probar los endpoints. **Postman** es una aplicación donde armas y guardas peticiones. Los tres no son lo mismo: OpenAPI es el contrato, Swagger es una vista interactiva de ese contrato, Postman es un cliente.

Para leer una operación busca, en este orden, `paths`, el método, `parameters`, `requestBody`, `responses` y, si el cuerpo dice `$ref`, el esquema dentro de `components.schemas`. Un campo listado en `required` es obligatorio. Si `required` es falso o no está, el parámetro es opcional. El tipo sale de `schema` o de `properties`.

Abre Swagger en el navegador: <https://34.95.210.33.sslip.io/api/v4/docs>. Elige `GET /api/v4/productos`. Ahí ves parámetros y respuestas sin escribir código. El botón **Authorize** pide el token Bearer que devuelve el login. Health y login no lo necesitan; el resto de las operaciones sí. Pega solo el token, sin la palabra `Bearer` y sin compartirlo en el chat del curso.
"""))

celdas.append(md("""
## 02 — Leer OpenAPI desde Colab

Pedimos el contrato real y mostramos solo el índice: título, versión, rutas, métodos, parámetros y esquemas. No imprimimos el documento entero.
"""))

celdas.append(code("""
if MODO == "api":
    especificacion = llamar("GET", "/api/v4/openapi.json", timeout=30)
    comprobar(especificacion.status_code == 200, "openapi.json responde 200")
    spec = especificacion.json()
    print("Contrato en vivo")
else:
    spec = respaldo["openapi"]
    print("RESPALDO: este contrato es un extracto guardado, no openapi.json en vivo.")

print("título", spec["info"]["title"])
print("versión de la API", spec["info"]["version"])
print("versión de OpenAPI", spec["openapi"])
print("esquemas de seguridad", list(spec.get("components", {}).get("securitySchemes", {})))
print("--- endpoints ---")
for ruta in sorted(spec["paths"]):
    metodos = [metodo.upper() for metodo in spec["paths"][ruta] if metodo in {"get", "post", "put", "patch", "delete"}]
    print(", ".join(metodos), ruta)

login = spec["paths"]["/api/v4/auth/login"]["post"]
referencia = login["requestBody"]["content"]["application/json"]["schema"]["$ref"]
nombre_esquema = referencia.rsplit("/", 1)[-1]
esquema_login = spec["components"]["schemas"][nombre_esquema]
print("login $ref", referencia)
print("login requeridos", esquema_login.get("required"))
print("login propiedades", list(esquema_login.get("properties", {})))
print("login respuestas", list(login.get("responses", {})))
print("--- query de /api/v4/ventas ---")
for parametro in spec["paths"]["/api/v4/ventas"]["get"].get("parameters", []):
    obligatorio = "requerido" if parametro.get("required") else "opcional"
    print(parametro["name"], parametro.get("in"), obligatorio)
"""))

celdas.append(md("""
### Ejercicio 02

**Objetivo.** Localizar en el contrato un GET, un POST, un dato requerido, uno opcional y un código de respuesta.

**Concepto.** Paths, `required` y `responses`. No memorices los nombres: léelos en la lista que acaba de imprimirse.

**Instrucción.** Puedes cambiar los valores. Tienen que existir en la especificación que cargó la celda anterior.

**Resultado esperado.** La comprobación confirma las cinco piezas. Si cambias un path por otro que no está, la celda se detiene con un mensaje claro.

**Pista.** El login es POST y su cuerpo apunta a un esquema. `region` no es obligatorio para listar ventas.

Cuando quieras ver la respuesta comentada, ejecuta `ver_solucion("02")` en una celda nueva, después de intentar la tuya.
"""))

celdas.append(code("""
# TODO: sustituye estos hallazgos por otros que veas en el contrato, si quieres practicar la búsqueda.
hallazgo_get = "/api/v4/productos"
hallazgo_post = "/api/v4/auth/login"
hallazgo_requerido = "username"
hallazgo_opcional = "region"
hallazgo_codigo = "200"

operacion_get = spec["paths"].get(hallazgo_get, {})
operacion_post = spec["paths"].get(hallazgo_post, {})
comprobar("get" in operacion_get, hallazgo_get + " admite GET")
comprobar("post" in operacion_post, hallazgo_post + " admite POST")
comprobar(hallazgo_requerido in esquema_login.get("required", []), hallazgo_requerido + " es requerido en el login")
consulta_ventas = spec["paths"]["/api/v4/ventas"]["get"]["parameters"]
opcional = [item["name"] for item in consulta_ventas if not item.get("required")]
comprobar(hallazgo_opcional in opcional, hallazgo_opcional + " es un query param opcional")
codigos = []
for operaciones in spec["paths"].values():
    for operacion in operaciones.values():
        if isinstance(operacion, dict):
            codigos.extend(operacion.get("responses", {}))
comprobar(hallazgo_codigo in codigos, "el código " + hallazgo_codigo + " está documentado")
"""))

celdas.append(md("""
## Bloque C — HTTP

El método dice la intención.

- **GET** pide una representación. No lleva cuerpo.
- **POST** crea un recurso o arranca una acción. El login es un POST.
- **PUT** reemplaza el recurso completo por la representación que envías.
- **PATCH** cambia solo los campos que envías.
- **DELETE** elimina el recurso.
- **HEAD** pide los encabezados, sin el cuerpo. **OPTIONS** pregunta qué métodos admite la URL. Los mencionamos para reconocerlos; la práctica usa los cinco primeros.

Una operación **segura** no debe cambiar datos. GET, HEAD y OPTIONS se consideran seguras. Una operación **idempotente** puede repetirse y el resultado final coincide con haberla hecho una vez: GET, HEAD, OPTIONS, PUT y DELETE. POST no es idempotente: enviarlo dos veces puede crear dos recursos. PATCH no siempre es idempotente; depende de qué campo cambie.

PUT y PATCH no son intercambiables. En el sandbox, PUT exige el recurso completo (`titulo` es obligatorio en el esquema). PATCH acepta un solo campo, por ejemplo `estado`.

Los **headers** viajan aparte del cuerpo. `Authorization` lleva el token. `Content-Type` dice cómo está escrito el cuerpo que envías. `Accept` dice qué representación aceptas de vuelta. Aquí pedimos `application/json`.

Un **path parameter** es parte de la ruta: `/productos/1`. Un **query parameter** va después de `?`: `/ventas?region=Aragón&page=1`. El **body** es el JSON del POST, PUT o PATCH. GET no lo usa.

Los códigos se leen por familias. **2xx** la petición se atendió: 200 OK, 201 creado, 204 sin cuerpo. **4xx** el cliente pidió algo que el servidor no acepta: falta token, falta un campo, la ruta no existe. **5xx** falló el servidor. Un 500 de esta clase, en los endpoints de ejemplo, es una demostración controlada, no una caída real.
"""))

celdas.append(md("""
## Bloque D — Autenticación

**Autenticación** responde quién eres. **Autorización** responde qué puedes hacer después de identificarte. El login comprueba usuario y contraseña contra PostgreSQL y, si coinciden, entrega un **access token**. Ese token es un **JWT** firmado (HS256): el servidor puede verificar la firma, el emisor, la audiencia, la expiración y el alcance sin guardar la contraseña dentro del token.

Lo enviamos como **Bearer token**, en el header `Authorization`. No va en la URL y no se imprime. Dura cuatro horas (`expires_in` es 14400 segundos). El alcance de esta clase es `retail:read`: leer el catálogo y las ventas. No publica DAGs ni administra el servidor.

Cada login crea una sesión propia (`jti`), también para el usuario compartido `estudiante`. Dos personas con esa cuenta pueden trabajar a la vez. El sandbox de una sesión no se ve desde la otra. Cerrar tu cuaderno no invalida la sesión de tu compañero.

Una **API key** sería una clave fija de la aplicación, distinta de la contraseña de cada persona. **OAuth 2.0** es un marco en el que un proveedor entrega tokens con alcances, a menudo después de una pantalla de consentimiento. Esta API no es un servidor OAuth: entrega ella misma un JWT de alcance fijo después del usuario y la contraseña.

Esta sesión autenticada no es una conexión a PostgreSQL. Tú no envías SQL. La API abre su propia conexión de solo lectura, con otra cuenta, y solo para las consultas que el contrato permite. HTTPS protege la contraseña en el camino. Por eso no la escribimos en el cuaderno ni en los archivos de salida.
"""))

celdas.append(md("""
## 03 — Login

Usa tu usuario de PostgreSQL: `estudianteNN` o el compartido `estudiante`. La contraseña es la misma de la clase 02. `getpass` no la muestra. Si alguien automatiza el cuaderno, puede definir `ESTUDIA_USUARIO` y `ESTUDIA_PASSWORD` en el entorno; esos valores no forman parte del archivo.

El cuaderno guarda el token en la variable `token` y muestra usuario, tipo, expiración, alcance y si la autenticación quedó hecha.
"""))

celdas.append(code("""
if MODO != "api":
    print("RESPALDO: no se envía usuario ni contraseña. No hay sesión autenticada.")
    usuario = "respaldo"
    token = None
else:
    usuario = os.environ.get("ESTUDIA_USUARIO") or input("Usuario PostgreSQL: ")
    password = os.environ.get("ESTUDIA_PASSWORD") or getpass("Contraseña: ")
    login = llamar(
        "POST",
        "/api/v4/auth/login",
        cuerpo={"username": usuario, "password": password},
    )
    if login.status_code != 200:
        print("El login no entró. Código", login.status_code)
        print("Revisa usuario y contraseña. No se imprime el cuerpo para no arrastrar datos de acceso.")
        raise RuntimeError("Login rechazado")
    sesion = login.json()
    token = sesion["access_token"]
    print("usuario", sesion["usuario"])
    print("tipo", sesion["token_type"])
    print("expira_en_segundos", sesion["expires_in"])
    print("scope", sesion["scope"])
    print("autenticado", sesion["token_type"] == "bearer" and bool(token))
    yo = llamar("GET", "/api/v4/auth/me", token_sesion=token)
    comprobar(yo.status_code == 200, "auth/me responde 200")
    identidad = yo.json()
    print("identidad", identidad["identidad"])
    print("scope_confirmado", identidad["scope"])
    print("sesion_activa", bool(identidad["sesion"]))
    hecho["autenticacion"] = True
    del sesion
"""))

celdas.append(md("""
## 04 — GET

`requests.get` arma una petición GET. Con el token en el header, pedimos el catálogo y después un producto concreto. `/api/v4/productos/1` usa un path parameter: el identificador va dentro de la ruta.

El producto 1 de este laboratorio es un pantalón de la categoría Ropa, si el catálogo no ha cambiado.
"""))

celdas.append(code("""
if MODO != "api":
    print("RESPALDO: catálogo de ejemplo, no es la respuesta de esta sesión.")
    productos = respaldo["productos"]
    producto_1 = respaldo["productos"]["data"][0]
else:
    listado = llamar("GET", "/api/v4/productos", params={"page": 1, "page_size": 5}, token_sesion=token)
    comprobar(listado.status_code == 200, "el listado de productos responde 200")
    productos = listado.json()
    uno = llamar("GET", "/api/v4/productos/1", token_sesion=token)
    comprobar(uno.status_code == 200, "el producto 1 responde 200")
    producto_1 = uno.json()
    hecho["consulta"] = True

print("registros en la página", len(productos["data"]))
print("paginación", productos["pagination"])
print("producto 1", producto_1["id_producto"], producto_1["nombre"], producto_1["categoria"])
"""))

celdas.append(md("""
### Ejercicio 04

**Objetivo.** Pedir otro producto cambiando solo el identificador.

**Concepto.** Path parameter.

**Instrucción.** Cambia `id_elegido`. Tiene que ser un entero de un producto que exista. El 2 es un valor real del catálogo.

**Resultado esperado.** Código 200 y el mismo identificador que pediste.

**Pista.** La ruta es `/api/v4/productos/` más el número, sin query string. `ver_solucion("04")` explica la URL.
"""))

celdas.append(code("""
id_elegido = 2  # TODO: cámbialo por otro identificador que hayas visto.

if MODO != "api":
    print("RESPALDO: no se consulta otro id en vivo.")
    print("En la API, la ruta sería /api/v4/productos/" + str(id_elegido))
else:
    otro_producto = llamar("GET", "/api/v4/productos/" + str(id_elegido), token_sesion=token)
    print("status", otro_producto.status_code)
    if otro_producto.status_code == 200:
        ficha = otro_producto.json()
        comprobar(ficha["id_producto"] == id_elegido, "el id devuelto coincide con el pedido")
        print(ficha["nombre"], ficha["categoria"])
    else:
        raise AssertionError("Ese identificador no devolvió 200. Prueba con 1 o con 2.")
"""))

celdas.append(md("""
## 05 — Headers y query parameters

El header `Authorization` va en la petición y no se imprime. Los filtros de ventas no se escriben en el path: van en `params` y `requests` construye la query string.

`/productos/1` identifica un solo recurso. `/ventas?region=Aragón&page=1&page_size=2` pide una página de un listado. El primero es un path parameter. El segundo son query parameters. Región, categoría y fechas de abajo son valores reales del laboratorio.
"""))

celdas.append(code("""
print("Authorization: Bearer <oculto>")
print("Accept: application/json")

filtro_region = "Aragón"  # TODO: puedes cambiarla por Andalucía, Cataluña, Comunidad de Madrid, Comunitat Valenciana, Castilla y León o País Vasco.
filtro_categoria = "Hogar"  # TODO: Alimentación, Deportes, Electrónica, Hogar o Ropa.

if MODO != "api":
    print("RESPALDO: página guardada de Aragón, no es tu filtro en vivo.")
    pagina_filtro = respaldo["ventas_aragon"]
else:
    pagina_filtro = llamar(
        "GET",
        "/api/v4/ventas",
        params={
            "region": filtro_region,
            "categoria": filtro_categoria,
            "fecha_desde": "2024-01-01",
            "fecha_hasta": "2024-12-30",
            "page": 1,
            "page_size": 2,
            "orden": "id_transaccion",
            "direccion": "asc",
        },
        token_sesion=token,
    )
    comprobar(pagina_filtro.status_code == 200, "el filtro de ventas responde 200")
    pagina_filtro = pagina_filtro.json()

print("path de un recurso: /api/v4/productos/1")
print("query de un listado: /api/v4/ventas?region=" + filtro_region + "&categoria=" + filtro_categoria + "&page=1&page_size=2")
print("total_records", pagina_filtro["pagination"]["total_records"])
print("has_next", pagina_filtro["pagination"]["has_next"])
print("filas recibidas", len(pagina_filtro["data"]))
"""))

celdas.append(md("""
## 06 — POST, PUT, PATCH y DELETE

Estas cuatro operaciones se practican solo en `/api/v4/sandbox/tareas`. Son tareas ficticias de tu sesión. No se escriben en PostgreSQL y desaparecen al expirar el token. El análisis de ventas sigue siendo de solo lectura.

El esquema real exige `titulo` para crear o reemplazar. `detalle`, `estado` y `prioridad` tienen valores por defecto. `estado` solo admite `pendiente`, `en_progreso` o `hecha`. `prioridad` va de 1 a 5. El identificador `id_tarea` lo devuelve el POST: no lo inventes.

Un DELETE correcto responde **204** y el cuerpo va vacío. No llames `.json()` sobre ese cuerpo.

Después creamos una segunda sesión con el mismo usuario. La tarea de la primera no aparece en la segunda. Si entraste con `estudiante`, las dos sesiones son de la cuenta compartida y pueden convivir.
"""))

celdas.append(code("""
if MODO != "api":
    print("RESPALDO: el CRUD de ejemplo no llama al sandbox ni demuestra el aislamiento real.")
    bolsa = {}
    creada = {"id_tarea": "ejemplo", "titulo": "Practicar POST", "detalle": "ficticia", "estado": "pendiente", "prioridad": 2}
    bolsa[creada["id_tarea"]] = creada
    reemplazada = {"id_tarea": "ejemplo", "titulo": "Practicar PUT", "detalle": "reemplazo", "estado": "en_progreso", "prioridad": 1}
    bolsa["ejemplo"] = reemplazada
    bolsa["ejemplo"]["estado"] = "hecha"
    del bolsa["ejemplo"]
    print("RESPALDO pasos simulados: listar, crear, leer, reemplazar, actualizar, borrar. Quedan", len(bolsa), "tareas.")
else:
    print("1 GET listar")
    lista_inicial = llamar("GET", "/api/v4/sandbox/tareas", token_sesion=token)
    comprobar(lista_inicial.status_code == 200, "el listado del sandbox responde 200")
    otra = llamar(
        "POST",
        "/api/v4/auth/login",
        cuerpo={"username": usuario, "password": password},
    )
    comprobar(otra.status_code == 200, "la segunda sesión también entra")
    token_b = otra.json()["access_token"]
    del otra
    yo_a = llamar("GET", "/api/v4/auth/me", token_sesion=token).json()
    yo_b = llamar("GET", "/api/v4/auth/me", token_sesion=token_b).json()
    print("mismo_usuario", yo_a["usuario"] == yo_b["usuario"] == usuario)
    print("identidad", yo_a["identidad"])
    print("sesiones_distintas", yo_a["sesion"] != yo_b["sesion"])
    if yo_a["sesion"] == yo_b["sesion"]:
        raise RuntimeError("Las dos sesiones quedaron con el mismo identificador.")
    print("2 POST crear")
    alta = llamar(
        "POST",
        "/api/v4/sandbox/tareas",
        cuerpo={
            "titulo": "Practicar POST",
            "detalle": "Tarea ficticia de la sesion",
            "estado": "pendiente",
            "prioridad": 2,
        },
        token_sesion=token,
    )
    comprobar(alta.status_code == 201, "crear responde 201")
    tarea = alta.json()
    id_tarea = tarea["id_tarea"]
    print("id recibido", bool(id_tarea), "estado", tarea["estado"])
    print("3 GET de la tarea creada")
    lectura = llamar("GET", "/api/v4/sandbox/tareas/" + id_tarea, token_sesion=token)
    comprobar(lectura.status_code == 200, "la sesión dueña lee su tarea")
    ajena = llamar("GET", "/api/v4/sandbox/tareas/" + id_tarea, token_sesion=token_b)
    print("la otra sesión recibe", ajena.status_code)
    comprobar(ajena.status_code == 404, "la otra sesión no ve la tarea")
    print("4 PUT reemplazar")
    # TODO: el reemplazo debe incluir los campos del recurso, no solo el que cambió.
    reemplazo = llamar(
        "PUT",
        "/api/v4/sandbox/tareas/" + id_tarea,
        cuerpo={
            "titulo": "Practicar PUT",
            "detalle": "Reemplazo completo",
            "estado": "en_progreso",
            "prioridad": 1,
        },
        token_sesion=token,
    )
    comprobar(reemplazo.status_code == 200, "PUT responde 200")
    comprobar(reemplazo.json()["titulo"] == "Practicar PUT", "PUT sustituyó el título")
    print("5 PATCH un solo campo")
    ajuste = llamar(
        "PATCH",
        "/api/v4/sandbox/tareas/" + id_tarea,
        cuerpo={"estado": "hecha"},
        token_sesion=token,
    )
    comprobar(ajuste.status_code == 200, "PATCH responde 200")
    comprobar(ajuste.json()["estado"] == "hecha", "PATCH cambió solo el estado")
    comprobar(ajuste.json()["titulo"] == "Practicar PUT", "PATCH conservó el resto")
    print("6 DELETE")
    borrado = llamar("DELETE", "/api/v4/sandbox/tareas/" + id_tarea, token_sesion=token)
    print("status", borrado.status_code, "bytes", len(borrado.content))
    comprobar(borrado.status_code == 204, "DELETE responde 204")
    comprobar(len(borrado.content) == 0, "el 204 llega sin cuerpo")
    print("7 GET después de borrar")
    despues = llamar("GET", "/api/v4/sandbox/tareas/" + id_tarea, token_sesion=token)
    print("status", despues.status_code)
    comprobar(despues.status_code == 404, "la tarea ya no está en la sesión")
    del token_b
    del password
"""))

celdas.append(md("""
Si el PATCH te confundió con el PUT, ejecuta `ver_solucion("06")`. La idea: PUT reescribe la tarea; PATCH manda únicamente `estado`.
"""))

celdas.append(md("""
## 07 — Paginación

`/api/v4/ventas` no entrega las 50.000 filas de una vez. Cada respuesta trae `page`, `page_size`, `total_records`, `total_pages` y `has_next`. El orden por defecto es `id_transaccion` ascendente, con ese mismo campo como desempate.

La función de abajo pide tres páginas de 50 filas: 150 registros como máximo. Es una **extracción parcial intencional**. Aunque los identificadores salgan seguidos o no haya duplicados, eso no demuestra que ya tengas todas las ventas. Para saber si falta información se miran `has_next` y `total_pages`.
"""))

celdas.append(code("""
def extraer_parcial(region, paginas=3, page_size=50):
    pedidas = []
    recibidas = []
    por_pagina = []
    filas = []
    meta = None
    for numero in range(1, paginas + 1):
        pedidas.append(numero)
        if MODO != "api":
            break
        respuesta = llamar(
            "GET",
            "/api/v4/ventas",
            params={
                "region": region,
                "page": numero,
                "page_size": page_size,
                "orden": "id_transaccion",
                "direccion": "asc",
            },
            token_sesion=token,
        )
        comprobar(respuesta.status_code == 200, "la página " + str(numero) + " responde 200")
        cuerpo = respuesta.json()
        meta = cuerpo["pagination"]
        recibidas.append(meta["page"])
        por_pagina.append(len(cuerpo["data"]))
        filas.extend(cuerpo["data"])
        if not meta["has_next"]:
            break
    return {
        "filas": filas,
        "paginas_pedidas": pedidas,
        "paginas_recibidas": recibidas,
        "por_pagina": por_pagina,
        "meta": meta,
    }

if MODO != "api":
    print("RESPALDO: no se recorren páginas en vivo.")
    extraccion = {
        "filas": respaldo["ventas_aragon"]["data"],
        "paginas_pedidas": [1],
        "paginas_recibidas": [1],
        "por_pagina": [len(respaldo["ventas_aragon"]["data"])],
        "meta": respaldo["ventas_aragon"]["pagination"],
    }
    print("RESPALDO total_pages del ejemplo", extraccion["meta"]["total_pages"], ". Esto no es tu extracción.")
else:
    extraccion = extraer_parcial(filtro_region, paginas=3, page_size=50)
    hecho["paginacion"] = True

identificadores = [fila["id_transaccion"] for fila in extraccion["filas"]]
print("páginas pedidas", extraccion["paginas_pedidas"])
print("páginas recibidas", extraccion["paginas_recibidas"])
print("registros por página", extraccion["por_pagina"])
print("identificadores únicos", len(set(identificadores)), "de", len(identificadores))
if extraccion["meta"]:
    print("total_records del filtro", extraccion["meta"]["total_records"])
    print("total_pages", extraccion["meta"]["total_pages"])
    print("has_next de la última página pedida", extraccion["meta"]["has_next"])
print("Tipo de extracción: parcial. Tres páginas no equivalen al total, aunque no veas duplicados.")
"""))

celdas.append(md("""
## 08 — JSON anidado

`GET /api/v4/ventas/1` no devuelve una fila plana. Trae la venta y, dentro, los objetos `producto` y `tienda`.

Una **lista** es una secuencia ordenada. Un **diccionario** asocia claves con valores. Un **objeto anidado** es un diccionario dentro de otro. `pd.DataFrame` sobre esa venta deja `producto` y `tienda` como celdas con diccionarios. `pd.json_normalize` abre esas claves en columnas `producto.nombre`, `tienda.region` y similares.

### Ejercicio 08

**Objetivo.** Nombrar la clave de la venta.

**Concepto.** Identificador del recurso, no de las tablas internas.

**Instrucción.** Escribe el nombre del campo. La pista está en el JSON, no en un `id_venta` imaginario.

**Resultado esperado.** La comprobación acepta `id_transaccion`.

**Pista.** `ver_solucion("08")`.
"""))

celdas.append(code("""
clave_venta = "id_transaccion"  # TODO: confirma que este es el campo identificador.

if MODO != "api":
    print("RESPALDO: venta de ejemplo embebida, no es GET /ventas/1 de esta sesión.")
    venta = respaldo["venta"]
else:
    respuesta_venta = llamar("GET", "/api/v4/ventas/1", token_sesion=token)
    comprobar(respuesta_venta.status_code == 200, "la venta 1 responde 200")
    venta = respuesta_venta.json()

print("raíz", type(venta).__name__)
print("producto", type(venta["producto"]).__name__, venta["producto"])
print("tienda", type(venta["tienda"]).__name__, venta["tienda"])
print("lista de una venta", type([venta]).__name__)
como_tabla = pd.DataFrame([venta])
plana = pd.json_normalize(venta)
print("columnas DataFrame", list(como_tabla.columns))
print("columnas normalizadas", list(plana.columns))
comprobar(clave_venta in venta, "la clave elegida existe en la venta")
comprobar(clave_venta == "id_transaccion", "la clave de la transacción es id_transaccion")
print("id_transaccion", venta["id_transaccion"])
plana
"""))

celdas.append(md("""
## 09 — Pandas sobre una muestra

`GET /api/v4/ventas/muestra?limite=200` devuelve entre 100 y 300 ventas, ordenadas por `id_transaccion`. No son las 50.000. Los indicadores de `/api/v4/indicadores/resumen` sí describen toda la población. Una media calculada aquí no se compara con el ticket promedio global como si fueran el mismo conjunto.

Después de normalizar verás `head`, `shape`, `info`, nulos, duplicados de `id_transaccion`, la media de `importe_neto` y un `groupby` por categoría.
"""))

celdas.append(code("""
if MODO != "api":
    print("RESPALDO: la muestra embebida tiene pocas filas. No son las 200 de la API ni las 50.000 ventas.")
    registros = respaldo["muestra"]["data"]
    indicadores = respaldo["resumen"]
else:
    muestra = llamar("GET", "/api/v4/ventas/muestra", params={"limite": 200}, token_sesion=token)
    comprobar(muestra.status_code == 200, "la muestra responde 200")
    registros = muestra.json()["data"]
    indicadores = llamar("GET", "/api/v4/indicadores/resumen", token_sesion=token).json()

df = pd.json_normalize(registros)
df["importe_neto"] = pd.to_numeric(df["importe_neto"])
print("head")
display(df.head())
print("shape", df.shape)
df.info()
print("nulos")
print(df.isna().sum())
print("duplicados de id_transaccion", int(df.duplicated(subset="id_transaccion").sum()))
print("media de importe_neto en la muestra", float(df["importe_neto"].mean()))
por_categoria = (
    df.groupby("producto.categoria", as_index=False)["importe_neto"]
    .sum()
    .sort_values("importe_neto", ascending=False)
)
print(por_categoria)
print("Ticket promedio global, otra población:", indicadores["ticket_promedio"])
print("Transacciones globales:", indicadores["transacciones"])
print("No compares la media de esta muestra con el ticket global como si midieran lo mismo.")
if MODO == "api":
    hecho["normalizados"] = True
    if int(df.duplicated(subset="id_transaccion").sum()) == 0 and df["id_transaccion"].notna().all():
        hecho["validaciones"] = True
"""))

celdas.append(code("""
fig, ax = plt.subplots(figsize=(8, 4))
por_categoria.sort_values("importe_neto").plot.barh(
    x="producto.categoria",
    y="importe_neto",
    ax=ax,
    legend=False,
    title="Importe neto por categoría en la muestra",
)
ax.set_xlabel("importe_neto")
fig.tight_layout()
fig.savefig("muestra_por_categoria.png", dpi=120)
plt.show()
if MODO == "api":
    hecho["grafico"] = True
    print("Gráfico generado con la muestra en vivo.")
else:
    print("RESPALDO: el gráfico usa el ejemplo embebido, no la muestra de 200.")
"""))

celdas.append(md("""
## 10 — Errores

Estos códigos salen de peticiones pequeñas y de endpoints de demostración. No vamos a tumbar el servidor ni a repetir escrituras.

| Código | Qué lo provoca aquí |
| --- | --- |
| 200 | un GET válido, por ejemplo health o productos |
| 201 | el POST del sandbox |
| 204 | el DELETE del sandbox, sin JSON |
| 400 | `fecha_desde` posterior a `fecha_hasta` |
| 401 | productos sin token |
| 403 | `/api/v4/ejemplos/prohibido` |
| 404 | un producto que no existe |
| 405 | POST a `/api/v4/ventas`, que es de solo lectura |
| 422 | un `page_size` que el esquema no acepta |
| 429 | `/api/v4/ejemplos/demasiado-rapido`, con `Retry-After` |
| 500 | `/api/v4/ejemplos/error-interno` |
| 503 | `/api/v4/ejemplos/no-disponible` |

`status_code` es el número. `raise_for_status()` lanza `HTTPError` cuando el código es 4xx o 5xx. El `try/except` deja seguir el cuaderno después de un error que estamos provocando a propósito.

`Timeout` significa que esperamos más de lo indicado. `ConnectionError` significa que ni siquiera se completó la conexión. Un reintento tiene sentido en un GET fallido, pocas veces, y debe respetar `Retry-After`. No reintentamos POST, PUT, PATCH ni DELETE: repetirlos puede crear o borrar dos veces.
"""))

celdas.append(code("""
def anotar(codigo, respuesta):
    errores_observados.append(int(codigo))
    detalle = ""
    if respuesta.content:
        try:
            cuerpo = respuesta.json()
            detalle = cuerpo.get("detail", "")
        except ValueError:
            detalle = "(el cuerpo no es JSON)"
    if not isinstance(detalle, str):
        detalle = "respuesta estructurada"
    print(codigo, detalle[:160])

if MODO != "api":
    print("RESPALDO: no se provocan errores contra la API.")
else:
    anotar(200, llamar("GET", "/api/v4/health"))
    demo = llamar(
        "POST",
        "/api/v4/sandbox/tareas",
        cuerpo={"titulo": "Codigo 201", "estado": "pendiente", "prioridad": 3},
        token_sesion=token,
    )
    anotar(demo.status_code, demo)
    id_demo = demo.json()["id_tarea"]
    vacio = llamar("DELETE", "/api/v4/sandbox/tareas/" + id_demo, token_sesion=token)
    print(vacio.status_code, "bytes", len(vacio.content))
    errores_observados.append(vacio.status_code)
    anotar(400, llamar(
        "GET",
        "/api/v4/ventas",
        params={"fecha_desde": "2024-12-30", "fecha_hasta": "2024-01-01", "page_size": 1},
        token_sesion=token,
    ))
    anotar(401, requests.get(BASE + "/api/v4/productos", timeout=20))
    anotar(403, llamar("GET", "/api/v4/ejemplos/prohibido", token_sesion=token))
    anotar(404, llamar("GET", "/api/v4/productos/999999", token_sesion=token))
    anotar(405, llamar("POST", "/api/v4/ventas", cuerpo={"no": "se escribe"}, token_sesion=token))
    anotar(422, llamar("GET", "/api/v4/ventas", params={"page_size": 0}, token_sesion=token))
    limitado = llamar("GET", "/api/v4/ejemplos/demasiado-rapido", token_sesion=token)
    anotar(limitado.status_code, limitado)
    print("Retry-After", limitado.headers.get("Retry-After"))
    anotar(500, llamar("GET", "/api/v4/ejemplos/error-interno", token_sesion=token))
    anotar(503, llamar("GET", "/api/v4/ejemplos/no-disponible", token_sesion=token))

    try:
        requests.get(BASE + "/api/v4/productos/999999", headers={"Authorization": "Bearer " + token}, timeout=20).raise_for_status()
    except requests.HTTPError as exc:
        print("HTTPError controlado", exc.response.status_code)

    try:
        requests.get(BASE + "/api/v4/health", timeout=0.001)
        print("La salud respondió antes de 0.001 s. Timeout no saltó en este intento.")
    except requests.exceptions.Timeout:
        print("Timeout controlado: la espera superó 0.001 s.")
    except requests.exceptions.ConnectionError:
        print("ConnectionError al cortar la espera.")

    try:
        requests.get("http://127.0.0.1:9", timeout=2)
    except requests.exceptions.ConnectionError:
        print("ConnectionError controlado contra un puerto local cerrado. No es la API.")

    print("Reintento limitado de un GET de demostración. No se reintenta ninguna escritura.")
    espera = 0
    for intento in (1, 2):
        if espera:
            import time
            time.sleep(min(espera, 2))
        prueba = llamar("GET", "/api/v4/ejemplos/no-disponible", token_sesion=token)
        print("intento", intento, prueba.status_code)
        if prueba.status_code < 500:
            break
        espera = int(prueba.headers.get("Retry-After", "1"))
    print("Reintentos agotados. No se sigue llamando.")
    print("códigos vistos", sorted(set(errores_observados)))
"""))

celdas.append(md("""
## 11 — Guardar resultados

Se guardan el JSON original de la extracción parcial, el CSV normalizado y un archivo de metadatos: páginas pedidas y recibidas, identificadores únicos, fecha, filtros, si la extracción fue parcial y los errores observados.

La celda de descarga usa `google.colab.files.download`. Fuera de Colab no hay botón; los archivos quedan en la carpeta `salida_clase04`. Ni el token ni la contraseña entran en esos archivos.
"""))

celdas.append(code("""
carpeta = Path("salida_clase04")
carpeta.mkdir(exist_ok=True)
origen = "api" if MODO == "api" else "respaldo"
marca = "en_vivo" if MODO == "api" else "RESPALDO"

ventas_json = carpeta / ("ventas_parcial.json" if MODO == "api" else "RESPALDO_ventas_parcial.json")
ventas_csv = carpeta / ("ventas_normalizadas.csv" if MODO == "api" else "RESPALDO_ventas_normalizadas.csv")
meta_json = carpeta / ("metadatos_extraccion.json" if MODO == "api" else "RESPALDO_metadatos_extraccion.json")

plano_extraccion = pd.json_normalize(extraccion["filas"])
ventas_json.write_text(json.dumps(extraccion["filas"], ensure_ascii=False), encoding="utf-8")
plano_extraccion.to_csv(ventas_csv, index=False)
metadatos = {
    "origen": origen,
    "aviso": "Resultados de la API en vivo." if MODO == "api" else "RESPALDO. No mezclar con una extracción en vivo.",
    "fecha_extraccion": datetime.now(timezone.utc).isoformat(),
    "filtros": {"region": filtro_region, "categoria": filtro_categoria},
    "paginas_solicitadas": extraccion["paginas_pedidas"],
    "paginas_recibidas": extraccion["paginas_recibidas"],
    "identificadores_unicos": len(set(identificadores)),
    "extraccion": "parcial",
    "total_pages_conocido": None if not extraccion["meta"] else extraccion["meta"]["total_pages"],
    "errores_observados": errores_observados,
}
meta_json.write_text(json.dumps(metadatos, ensure_ascii=False, indent=2), encoding="utf-8")

secreto = token or ""
for archivo in (ventas_json, ventas_csv, meta_json):
    texto = archivo.read_text(encoding="utf-8")
    if secreto and secreto in texto:
        raise RuntimeError("Un archivo de salida contiene el token. No se descarga.")
    if "password" in texto.lower() and "ESTUDIA_PASSWORD" in texto:
        raise RuntimeError("Un archivo de salida parece contener la contraseña.")
    print(marca, archivo.name, archivo.stat().st_size, "bytes")

if MODO == "api":
    hecho["archivos"] = True
"""))

celdas.append(code("""
try:
    from google.colab import files
    for archivo in sorted(Path("salida_clase04").glob("*")):
        if archivo.is_file():
            files.download(str(archivo))
except ImportError:
    print("No estás en Colab. Los archivos quedaron en", Path("salida_clase04").resolve())
"""))

celdas.append(md("""
## 12 — Reto final

Elige una región o una categoría. La celda usa `filtro_region`, que puedes cambiar en la sección 05 y volver a ejecutar desde allí. Pide dos páginas de 50 filas, valida la clave, calcula el importe neto total de **esa muestra** y dibuja el gráfico.

El resumen final marca OK solo lo que esta ejecución dejó hecho contra la API. Una celda que no corrió, o que corrió en respaldo, queda en NO.
"""))

celdas.append(code("""
print("Reto. Región:", filtro_region, ". Categoría de referencia:", filtro_categoria)

if MODO != "api":
    print("RESPALDO: el reto no consulta la API y no marca OK.")
    reto = pd.json_normalize(respaldo["ventas_aragon"]["data"])
else:
    reto_crudo = extraer_parcial(filtro_region, paginas=2, page_size=50)
    reto = pd.json_normalize(reto_crudo["filas"])
    ids = reto["id_transaccion"]
    print("páginas", reto_crudo["paginas_pedidas"], reto_crudo["paginas_recibidas"])
    print("únicos", int(ids.nunique()), "duplicados", int(ids.duplicated().sum()), "nulos", int(ids.isna().sum()))
    indicador = float(pd.to_numeric(reto["importe_neto"]).sum())
    print("importe_neto de esta muestra parcial", round(indicador, 2))
    print("Sigue siendo una extracción parcial. total_pages =", reto_crudo["meta"]["total_pages"])
    fig, ax = plt.subplots(figsize=(8, 4))
    (
        reto.groupby("categoria")["importe_neto"]
        .sum()
        .sort_values()
        .plot.barh(ax=ax, title="Reto: importe neto por categoría, muestra parcial")
    )
    fig.tight_layout()
    fig.savefig(Path("salida_clase04") / "reto_por_categoria.png", dpi=120)
    plt.show()
    hecho["grafico"] = True
    hecho["validaciones"] = bool(ids.nunique() == len(reto) and ids.notna().all())
    hecho["consulta"] = True
    hecho["paginacion"] = True
    hecho["normalizados"] = "categoria" in reto.columns

nombres = [
    ("api_accesible", "API accesible"),
    ("autenticacion", "Autenticación correcta"),
    ("consulta", "Consulta ejecutada"),
    ("paginacion", "Paginación comprobada"),
    ("normalizados", "Datos normalizados"),
    ("validaciones", "Validaciones realizadas"),
    ("grafico", "Gráfico generado"),
    ("archivos", "Archivos guardados"),
]
print("--- resumen ---")
print("modo", MODO)
for clave, etiqueta in nombres:
    print(etiqueta + ":", "OK" if hecho[clave] else "NO")
"""))

celdas.append(md("""
`ver_solucion("12")` recuerda el criterio del reto: muestra pequeña, clave `id_transaccion`, indicador calculado solo sobre esas filas y la palabra parcial bien visible.
"""))

celdas.append(md("""
## 13 — De la práctica a un pipeline

Lo que hiciste a mano cabe en cinco pasos:

`extraer_api` → `guardar_raw` → `normalizar` → `validar` → `generar_reporte`

El archivo de ejemplo del docente, `clase04/examples/airflow/estudia_clase04_demo_api.py`, usa esos nombres. `schedule` está en `None` y el DAG nace en pausa. **No está cargado en el scheduler de Airflow.** Verlo en el repositorio no significa que esté publicado ni que vaya a ejecutarse solo.

No tienes que crear un DAG en esta clase. La sesión de Colab termina cuando cierras el cuaderno. Un pipeline serviría para repetir la extracción sin volver a copiar el token a mano, con la credencial guardada en una conexión de Airflow y fuera del código.
"""))

celdas.append(code("""
print("extraer_api -> guardar_raw -> normalizar -> validar -> generar_reporte")
print("El DAG de ejemplo no está desplegado en el scheduler.")
print("modo de esta corrida:", MODO)
"""))

nb = new_notebook(
    cells=celdas,
    metadata={
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    },
)
destino = Path(__file__).resolve().parent / "EstudIA_Clase04_APIs_REST_Postman.ipynb"
nbformat.write(nb, destino)
print("celdas", len(nb.cells), destino.name)
