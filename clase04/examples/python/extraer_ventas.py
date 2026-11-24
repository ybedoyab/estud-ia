"""Ejemplo de extractor. La contraseña llega por entorno o por getpass, nunca queda en el archivo."""

import os
from getpass import getpass

import pandas as pd
import requests

BASE = os.environ.get("ESTUDIA_BASE", "https://34.95.210.33.sslip.io")


def sesion(usuario: str, password: str) -> str:
    respuesta = requests.post(
        f"{BASE}/api/v4/auth/login",
        json={"username": usuario, "password": password},
        timeout=15,
    )
    respuesta.raise_for_status()
    return respuesta.json()["access_token"]


def ventas(token: str, pagina: int, tamano: int = 100) -> dict:
    respuesta = requests.get(
        f"{BASE}/api/v4/ventas",
        headers={"Authorization": f"Bearer {token}"},
        params={"region": "Andalucía", "page": pagina, "page_size": tamano},
        timeout=15,
    )
    respuesta.raise_for_status()
    return respuesta.json()


def extraer(token: str, paginas: int = 2) -> pd.DataFrame:
    marcos = []
    for numero in range(1, paginas + 1):
        cuerpo = ventas(token, numero)
        marcos.append(pd.DataFrame(cuerpo["data"]))
        if not cuerpo["pagination"]["has_next"]:
            break
    return pd.concat(marcos, ignore_index=True) if marcos else pd.DataFrame()


if __name__ == "__main__":
    usuario = os.environ.get("ESTUDIA_USUARIO") or input("Usuario: ")
    password = os.environ.get("ESTUDIA_PASSWORD") or getpass("Contraseña: ")
    token = sesion(usuario, password)
    marco = extraer(token)
    print(marco.shape)
    print(marco.head(3).to_string(index=False))
