"""Genera la colección y el entorno de Postman sin secretos."""

import json
from pathlib import Path

SALIDA = Path(__file__).resolve().parent
BASE = "{{base_url}}"


def peticion(nombre, method, path, body=None, auth=None, tests="", query=None):
    url = f"{BASE}{path}"
    if query:
        url += "?" + "&".join(f"{clave}={valor}" for clave, valor in query)
    item = {
        "name": nombre,
        "request": {
            "method": method,
            "header": [{"key": "Content-Type", "value": "application/json"}] if body is not None else [],
            "url": url,
        },
        "event": [],
    }
    if body is not None:
        item["request"]["body"] = {"mode": "raw", "raw": json.dumps(body, ensure_ascii=False, indent=2)}
    if auth is not None:
        item["request"]["auth"] = auth
    if tests:
        item["event"].append({
            "listen": "test",
            "script": {"type": "text/javascript", "exec": tests.strip().splitlines()},
        })
    return item


SIN_AUTH = {"type": "noauth"}
BEARER = {
    "type": "bearer",
    "bearer": [{"key": "token", "value": "{{access_token}}", "type": "string"}],
}
GUARDA_TOKEN = """
pm.test("login 200", function () { pm.response.to.have.status(200); });
const cuerpo = pm.response.json();
pm.test("trae token y alcance", function () {
    pm.expect(cuerpo).to.have.property("token_type", "bearer");
    pm.expect(cuerpo).to.have.property("scope", "retail:read");
    pm.expect(cuerpo.expires_in).to.eql(14400);
});
pm.environment.set("access_token", cuerpo.access_token);
pm.collectionVariables.set("access_token", cuerpo.access_token);
"""
JSON_OK = """
pm.test("respuesta JSON", function () {
    pm.response.to.be.success;
    pm.response.to.have.jsonBody();
});
"""
PAGINACION = """
pm.test("200 y paginacion", function () {
    pm.response.to.have.status(200);
    const pagina = pm.response.json().pagination;
    pm.expect(pagina).to.include.all.keys("page", "page_size", "total_records", "total_pages", "has_next");
});
if (pm.response.json().data && pm.response.json().data.length) {
    pm.environment.set("id_producto", String(pm.response.json().data[0].id_producto || pm.environment.get("id_producto")));
}
"""

carpetas = [
    ("00. Health Check", [
        peticion("Salud clase 04", "GET", "/api/v4/health", auth=SIN_AUTH, tests='pm.test("200", () => pm.response.to.have.status(200));'),
        peticion("Salud clase 03 sigue viva", "GET", "/health", auth=SIN_AUTH, tests='pm.test("clase 03", () => pm.expect(pm.response.json().servicio).to.eql("estudia-clase03"));'),
    ]),
    ("01. Autenticacion", [
        peticion(
            "Login",
            "POST",
            "/api/v4/auth/login",
            {"username": "{{username}}", "password": "{{password}}"},
            SIN_AUTH,
            GUARDA_TOKEN,
        ),
        peticion("Quien soy", "GET", "/api/v4/auth/me", tests='pm.test("identidad", () => pm.expect(pm.response.json()).to.have.property("sesion"));'),
        peticion("Sin token", "GET", "/api/v4/productos", auth=SIN_AUTH, tests='pm.test("401", () => pm.response.to.have.status(401));'),
    ]),
    ("02. Primer GET", [
        peticion("Listar productos", "GET", "/api/v4/productos", query=[("page", "{{page}}"), ("page_size", "{{page_size}}")], tests=PAGINACION),
        peticion("Listar categorias", "GET", "/api/v4/categorias", tests=JSON_OK),
    ]),
    ("03. Path parameters", [
        peticion("Producto por id", "GET", "/api/v4/productos/{{id_producto}}", tests=JSON_OK),
        peticion("Transaccion anidada", "GET", "/api/v4/ventas/1", tests='pm.test("anidada", () => { const c = pm.response.json(); pm.expect(c.producto).to.be.an("object"); pm.expect(c.tienda).to.be.an("object"); });'),
        peticion("Producto inexistente", "GET", "/api/v4/productos/999999", tests='pm.test("404", () => pm.response.to.have.status(404));'),
    ]),
    ("04. Query parameters y filtros", [
        peticion(
            "Ventas de Electronica en Andalucia",
            "GET",
            "/api/v4/ventas",
            query=[("region", "Andalucía"), ("categoria", "Electrónica"), ("page", "1"), ("page_size", "20")],
            tests=PAGINACION,
        ),
    ]),
    ("05. Paginacion", [
        peticion("Pagina 1", "GET", "/api/v4/ventas", query=[("page", "1"), ("page_size", "20"), ("orden", "id_transaccion")], tests=PAGINACION),
        peticion("Pagina 2", "GET", "/api/v4/ventas", query=[("page", "2"), ("page_size", "20"), ("orden", "id_transaccion")], tests=PAGINACION),
        peticion("page_size invalido", "GET", "/api/v4/ventas", query=[("page_size", "0")], tests='pm.test("422", () => pm.response.to.have.status(422));'),
    ]),
    ("06. JSON anidado", [
        peticion("Muestra de 200", "GET", "/api/v4/ventas/muestra", query=[("limite", "200")], tests=JSON_OK),
    ]),
    ("07. Indicadores", [
        peticion("Resumen", "GET", "/api/v4/indicadores/resumen", tests=JSON_OK),
        peticion("Por categoria", "GET", "/api/v4/indicadores/ventas-por-categoria", tests=JSON_OK),
        peticion("Por region", "GET", "/api/v4/indicadores/ventas-por-region", tests=JSON_OK),
        peticion("Por periodo", "GET", "/api/v4/indicadores/ventas-por-periodo", query=[("granularidad", "mes")], tests=JSON_OK),
    ]),
    ("08. Sandbox CRUD", [
        peticion("Listar tareas", "GET", "/api/v4/sandbox/tareas", tests=JSON_OK),
        peticion(
            "Crear tarea",
            "POST",
            "/api/v4/sandbox/tareas",
            {"titulo": "Practicar POST", "detalle": "Tarea ficticia de la sesion", "estado": "pendiente", "prioridad": 2},
            tests='pm.test("201", () => pm.response.to.have.status(201)); pm.environment.set("id_tarea", pm.response.json().id_tarea);',
        ),
        peticion(
            "Reemplazar tarea",
            "PUT",
            "/api/v4/sandbox/tareas/{{id_tarea}}",
            {"titulo": "Practicar PUT", "detalle": "Reemplazo completo", "estado": "en_progreso", "prioridad": 1},
            tests='pm.test("200", () => pm.response.to.have.status(200));',
        ),
        peticion(
            "Actualizar estado",
            "PATCH",
            "/api/v4/sandbox/tareas/{{id_tarea}}",
            {"estado": "hecha"},
            tests='pm.test("200", () => pm.response.to.have.status(200));',
        ),
        peticion("Eliminar tarea", "DELETE", "/api/v4/sandbox/tareas/{{id_tarea}}", tests='pm.test("204", () => pm.response.to.have.status(204));'),
    ]),
    ("09. Manejo de errores", [
        peticion("Fechas cruzadas", "GET", "/api/v4/ventas", query=[("fecha_desde", "2024-12-01"), ("fecha_hasta", "2024-01-01")], tests='pm.test("400", () => pm.response.to.have.status(400));'),
        peticion("Prohibido", "GET", "/api/v4/ejemplos/prohibido", tests='pm.test("403", () => pm.response.to.have.status(403));'),
        peticion("Demasiado rapido", "GET", "/api/v4/ejemplos/demasiado-rapido", tests='pm.test("429", () => { pm.response.to.have.status(429); pm.expect(pm.response.headers.get("Retry-After")).to.eql("2"); });'),
        peticion("Error interno de ejemplo", "GET", "/api/v4/ejemplos/error-interno", tests='pm.test("500", () => pm.response.to.have.status(500));'),
        peticion("No disponible de ejemplo", "GET", "/api/v4/ejemplos/no-disponible", tests='pm.test("503", () => pm.response.to.have.status(503));'),
        peticion("Escritura sobre ventas", "POST", "/api/v4/ventas", {"importe_neto": 1}, tests='pm.test("405", () => pm.response.to.have.status(405));'),
    ]),
]

coleccion = {
    "info": {
        "name": "EstudIA Clase 04",
        "description": "API educativa de solo lectura. El login guarda el token en la variable access_token y no lo imprime.",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    },
    "auth": BEARER,
    "variable": [
        {"key": "base_url", "value": "https://34.95.210.33.sslip.io"},
        {"key": "access_token", "value": ""},
        {"key": "id_producto", "value": "1"},
        {"key": "id_tarea", "value": ""},
        {"key": "page", "value": "1"},
        {"key": "page_size", "value": "20"},
    ],
    "item": [{"name": nombre, "item": items} for nombre, items in carpetas],
}
entorno = {
    "name": "EstudIA Clase 04",
    "values": [
        {"key": "base_url", "value": "https://34.95.210.33.sslip.io", "enabled": True},
        {"key": "username", "value": "", "enabled": True},
        {"key": "password", "value": "", "type": "secret", "enabled": True},
        {"key": "access_token", "value": "", "type": "secret", "enabled": True},
        {"key": "id_producto", "value": "1", "enabled": True},
        {"key": "id_tarea", "value": "", "enabled": True},
        {"key": "page", "value": "1", "enabled": True},
        {"key": "page_size", "value": "20", "enabled": True},
    ],
    "_postman_variable_scope": "environment",
}

(SALIDA / "EstudIA_Clase04.postman_collection.json").write_text(json.dumps(coleccion, ensure_ascii=False, indent=2), encoding="utf-8")
(SALIDA / "EstudIA_Clase04.postman_environment.json").write_text(json.dumps(entorno, ensure_ascii=False, indent=2), encoding="utf-8")
print("postman_ok")
