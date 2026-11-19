"""Prueba la autenticación real contra la API. No imprime contraseñas."""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _entorno import API, cuentas

RESULTADOS = []


def marcar(nombre, ok, detalle=""):
    RESULTADOS.append((nombre, ok, detalle))
    print(("PASS" if ok else "FAIL"), nombre, detalle)


def main():
    personas = cuentas()
    usuario = "estudiante90"
    buena = personas[usuario]
    sesion = requests.Session()

    mala = sesion.post(f"{API}/auth/login", json={"username": usuario, "password": "no-es-la-clave"}, timeout=30)
    marcar("contrasena incorrecta", mala.status_code == 401, str(mala.status_code))

    compartido = sesion.post(
        f"{API}/auth/login",
        json={"username": "estudiante", "password": "cualquiera"},
        timeout=30,
    )
    marcar("usuario compartido rechazado", compartido.status_code == 403, str(compartido.status_code))

    buena_resp = sesion.post(
        f"{API}/auth/login",
        json={"username": usuario, "password": buena},
        timeout=30,
    )
    marcar("login individual", buena_resp.status_code == 200 and buena_resp.json().get("usuario") == usuario, str(buena_resp.status_code))
    token = buena_resp.json().get("access_token", "")

    sin_token = sesion.get(f"{API}/students/me", timeout=30)
    marcar("sin token", sin_token.status_code == 401, str(sin_token.status_code))

    secreto = None
    from _entorno import secreto as leer
    firma = leer("ESTUDIA_JWT_SECRET")
    vencido = jwt.encode(
        {"sub": usuario, "scope": "estudiante", "exp": datetime.now(timezone.utc) - timedelta(minutes=5)},
        firma,
        algorithm="HS256",
    )
    expirado = sesion.get(f"{API}/students/me", headers={"Authorization": f"Bearer {vencido}"}, timeout=30)
    marcar("token expirado", expirado.status_code == 401, str(expirado.status_code))

    yo = sesion.get(f"{API}/students/me", headers={"Authorization": f"Bearer {token}"}, timeout=30)
    marcar("identidad del token", yo.status_code == 200 and yo.json().get("usuario") == usuario, str(yo.status_code))

    from _entorno import ssh
    remoto = ssh(
        "python3 - << 'PY'\n"
        "import json, urllib.request\n"
        "url = 'https://34.95.210.33.sslip.io/auth/login'\n"
        "ultimo = 0\n"
        "for _ in range(10):\n"
        "    req = urllib.request.Request(url, data=json.dumps({'username':'estudiante99','password':'intento-fallido'}).encode(), headers={'Content-Type':'application/json'})\n"
        "    try:\n"
        "        urllib.request.urlopen(req, timeout=20)\n"
        "        ultimo = 200\n"
        "    except Exception as exc:\n"
        "        ultimo = getattr(exc, 'code', 0)\n"
        "        if ultimo == 429:\n"
        "            break\n"
        "print(ultimo)\n"
        "PY"
    ).strip()
    marcar("limite de intentos", remoto == "429", remoto)
    print("AUTH", "PASS" if all(ok for _, ok, _ in RESULTADOS) else "FAIL")
    return 0 if all(ok for _, ok, _ in RESULTADOS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
