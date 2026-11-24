from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

from app.config import recargar
from app.limite import reiniciar as reiniciar_limite
from app.main import app
from app.sandbox import reiniciar as reiniciar_sandbox
from app.seguridad import AUDIENCIA, EMISOR


@pytest.fixture(autouse=True)
def _limpio(monkeypatch):
    recargar()
    reiniciar_limite()
    reiniciar_sandbox()
    monkeypatch.setattr("app.routers.auth.autenticar_postgres", lambda usuario, contrasena: None)
    yield
    reiniciar_limite()
    reiniciar_sandbox()


@pytest.fixture
def cliente():
    with TestClient(app) as prueba:
        yield prueba


def _entrar(cliente, usuario="estudiante01"):
    respuesta = cliente.post("/api/v4/auth/login", json={"username": usuario, "password": "no-se-guarda"})
    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert "access_token" in cuerpo
    return cuerpo["access_token"]


def test_openapi_muestra_bearer_sin_cambiar_el_login(cliente):
    esquema = cliente.get("/api/v4/openapi.json").json()
    bearer = esquema["components"]["securitySchemes"]["HTTPBearer"]
    assert bearer["scheme"] == "bearer"
    assert "security" not in esquema["paths"]["/api/v4/auth/login"]["post"]
    assert "security" not in esquema["paths"]["/api/v4/health"]["get"]
    assert esquema["paths"]["/api/v4/productos"]["get"]["security"] == [{"HTTPBearer": []}]
    login = esquema["components"]["schemas"]["LoginBody"]
    assert login["required"] == ["username", "password"]


def test_health(cliente):
    respuesta = cliente.get("/api/v4/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"ok": True, "servicio": "estudia-clase04"}
    assert respuesta.headers["x-request-id"]


def test_login_y_me(cliente):
    token = _entrar(cliente)
    yo = cliente.get("/api/v4/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert yo.status_code == 200
    cuerpo = yo.json()
    assert cuerpo["usuario"] == "estudiante01"
    assert cuerpo["scope"] == "retail:read"
    assert cuerpo["identidad"] == "individual"
    assert cuerpo["expires_in"] > 14000


def test_usuario_compartido_dos_sesiones(cliente):
    primero = _entrar(cliente, "estudiante")
    segundo = _entrar(cliente, "estudiante")
    assert primero != segundo
    uno = cliente.get("/api/v4/auth/me", headers={"Authorization": f"Bearer {primero}"}).json()
    dos = cliente.get("/api/v4/auth/me", headers={"Authorization": f"Bearer {segundo}"}).json()
    assert uno["identidad"] == "compartida"
    assert uno["sesion"] != dos["sesion"]


def test_usuario_desconocido_no_consulta_postgres(cliente, monkeypatch):
    def fallar(usuario, contrasena):
        raise AssertionError("no debio consultar postgres")

    monkeypatch.setattr("app.routers.auth.autenticar_postgres", fallar)
    respuesta = cliente.post("/api/v4/auth/login", json={"username": "postgres", "password": "x"})
    assert respuesta.status_code == 401


def test_token_de_otra_audiencia(cliente):
    ajeno = jwt.encode(
        {
            "iss": "estudia",
            "aud": "clase03",
            "sub": "estudiante01",
            "scope": "estudiante",
            "jti": "abc",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc),
        },
        "otro-secreto",
        algorithm="HS256",
    )
    respuesta = cliente.get("/api/v4/productos", headers={"Authorization": f"Bearer {ajeno}"})
    assert respuesta.status_code == 401


def test_token_expirado(cliente):
    vencido = jwt.encode(
        {
            "iss": EMISOR,
            "aud": AUDIENCIA,
            "sub": "estudiante01",
            "scope": "retail:read",
            "jti": "sesion-vieja",
            "iat": datetime.now(timezone.utc) - timedelta(hours=5),
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        },
        "secreto-de-prueba-clase04",
        algorithm="HS256",
    )
    respuesta = cliente.get("/api/v4/auth/me", headers={"Authorization": f"Bearer {vencido}"})
    assert respuesta.status_code == 401


def test_productos_y_filtros(cliente, monkeypatch):
    capturado = {}

    def falso(categoria, q, page, page_size):
        capturado.update(categoria=categoria, q=q, page=page, page_size=page_size)
        return {"data": [{"id_producto": 1, "nombre": "Pantalón Modelo 0001"}], "pagination": {}}

    monkeypatch.setattr("app.routers.datos.productos", falso)
    token = _entrar(cliente)
    respuesta = cliente.get(
        "/api/v4/productos",
        headers={"Authorization": f"Bearer {token}"},
        params={"categoria": "Ropa", "q": "Pantalón", "page": 1, "page_size": 20},
    )
    assert respuesta.status_code == 200
    assert capturado["q"] == "Pantalón"
    assert respuesta.json()["data"][0]["id_producto"] == 1


def test_filtro_inyeccion_queda_como_parametro(cliente, monkeypatch):
    capturado = {}

    def falso(filtros, orden, direccion, page, page_size):
        capturado["filtros"] = filtros
        return {"data": [], "pagination": {"page": 1, "page_size": 20, "total_records": 0, "total_pages": 0, "has_next": False}}

    monkeypatch.setattr("app.routers.datos.ventas", falso)
    token = _entrar(cliente)
    ataque = "' OR 1=1 --"
    respuesta = cliente.get(
        "/api/v4/ventas",
        headers={"Authorization": f"Bearer {token}"},
        params={"region": ataque, "page": 1, "page_size": 20},
    )
    assert respuesta.status_code == 200
    assert capturado["filtros"]["region"] == ataque


def test_validacion_422_y_fechas_400(cliente, monkeypatch):
    monkeypatch.setattr(
        "app.routers.datos.ventas",
        lambda *args, **kwargs: {"data": [], "pagination": {}},
    )
    token = _entrar(cliente)
    cabecera = {"Authorization": f"Bearer {token}"}
    assert cliente.get("/api/v4/ventas", headers=cabecera, params={"page_size": 0}).status_code == 422
    assert cliente.get("/api/v4/ventas", headers=cabecera, params={"orden": "email"}).status_code == 422
    cruzadas = cliente.get(
        "/api/v4/ventas",
        headers=cabecera,
        params={"fecha_desde": "2024-12-01", "fecha_hasta": "2024-01-01"},
    )
    assert cruzadas.status_code == 400


def test_no_encontrado_y_metodo(cliente, monkeypatch):
    monkeypatch.setattr("app.routers.datos.producto", lambda id_producto: None)
    token = _entrar(cliente)
    cabecera = {"Authorization": f"Bearer {token}"}
    assert cliente.get("/api/v4/productos/999999", headers=cabecera).status_code == 404
    assert cliente.post("/api/v4/ventas", headers=cabecera, json={"x": 1}).status_code == 405


def test_ejemplos_de_error(cliente):
    token = _entrar(cliente)
    cabecera = {"Authorization": f"Bearer {token}"}
    limite = cliente.get("/api/v4/ejemplos/demasiado-rapido", headers=cabecera)
    assert limite.status_code == 429
    assert limite.headers["retry-after"] == "2"
    assert cliente.get("/api/v4/ejemplos/error-interno", headers=cabecera).status_code == 500
    assert cliente.get("/api/v4/ejemplos/no-disponible", headers=cabecera).status_code == 503
    assert cliente.get("/api/v4/ejemplos/prohibido", headers=cabecera).status_code == 403


def test_sandbox_aislado_por_sesion(cliente):
    uno = _entrar(cliente, "estudiante")
    dos = _entrar(cliente, "estudiante")
    alta = cliente.post(
        "/api/v4/sandbox/tareas",
        headers={"Authorization": f"Bearer {uno}"},
        json={"titulo": "Repasar GET", "detalle": "solo esta sesion", "estado": "pendiente", "prioridad": 2},
    )
    assert alta.status_code == 201
    id_tarea = alta.json()["id_tarea"]
    assert cliente.get("/api/v4/sandbox/tareas", headers={"Authorization": f"Bearer {dos}"}).json()["data"] == []
    assert cliente.get(f"/api/v4/sandbox/tareas/{id_tarea}", headers={"Authorization": f"Bearer {dos}"}).status_code == 404
    parche = cliente.patch(
        f"/api/v4/sandbox/tareas/{id_tarea}",
        headers={"Authorization": f"Bearer {uno}"},
        json={"estado": "hecha"},
    )
    assert parche.status_code == 200
    assert parche.json()["estado"] == "hecha"
    reemplazo = cliente.put(
        f"/api/v4/sandbox/tareas/{id_tarea}",
        headers={"Authorization": f"Bearer {uno}"},
        json={"titulo": "Repasar PUT", "detalle": "", "estado": "en_progreso", "prioridad": 1},
    )
    assert reemplazo.status_code == 200
    assert reemplazo.json()["titulo"] == "Repasar PUT"
    borrado = cliente.delete(f"/api/v4/sandbox/tareas/{id_tarea}", headers={"Authorization": f"Bearer {uno}"})
    assert borrado.status_code == 204
    assert borrado.content == b""
