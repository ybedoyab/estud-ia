"""Carga educativa. Lee el CSV local de la VM y no imprime contraseñas.

Escenarios, con variables de entorno:
- ESTUDIA_ESCENARIO=individual  (por defecto): reparte sesiones entre estudiante46-90.
- ESTUDIA_ESCENARIO=compartida: todas las sesiones usan estudiante46.
"""

import csv
import itertools
import os
from pathlib import Path

from locust import HttpUser, between, task

CSV = Path(os.environ.get("ESTUDIA_CUENTAS", "/home/yulcr/estudia-clase04-cuentas.csv"))


def cuentas():
    with CSV.open(encoding="utf-8", newline="") as handle:
        filas = [fila for fila in csv.DictReader(handle) if fila["usuario"].startswith("estudiante")]
    if os.environ.get("ESTUDIA_ESCENARIO") == "compartida":
        return [fila for fila in filas if fila["usuario"] == "estudiante46"]
    return filas


_ciclo = itertools.cycle(cuentas())


class Estudiante(HttpUser):
    wait_time = between(0.4, 1.2)
    host = os.environ.get("ESTUDIA_BASE", "https://34.95.210.33.sslip.io")

    def on_start(self):
        cuenta = next(_ciclo)
        respuesta = self.client.post(
            "/api/v4/auth/login",
            json={"username": cuenta["usuario"], "password": cuenta["password"]},
            name="/api/v4/auth/login",
            timeout=15,
        )
        if respuesta.status_code != 200:
            self.token = ""
            return
        self.token = respuesta.json()["access_token"]

    def _cabecera(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    @task(4)
    def productos(self):
        self.client.get(
            "/api/v4/productos",
            headers=self._cabecera(),
            params={"page": 1, "page_size": 20},
            name="/api/v4/productos",
            timeout=15,
        )

    @task(3)
    def ventas(self):
        self.client.get(
            "/api/v4/ventas",
            headers=self._cabecera(),
            params={"region": "Andalucía", "page": 1, "page_size": 20},
            name="/api/v4/ventas",
            timeout=15,
        )

    @task(2)
    def pagina(self):
        self.client.get(
            "/api/v4/ventas",
            headers=self._cabecera(),
            params={"page": 2, "page_size": 50, "orden": "importe_neto", "direccion": "desc"},
            name="/api/v4/ventas?page=2",
            timeout=15,
        )

    @task(1)
    def indicadores(self):
        self.client.get(
            "/api/v4/indicadores/ventas-por-categoria",
            headers=self._cabecera(),
            name="/api/v4/indicadores/ventas-por-categoria",
            timeout=15,
        )

    @task(1)
    def muestra(self):
        self.client.get(
            "/api/v4/ventas/muestra",
            headers=self._cabecera(),
            params={"limite": 200},
            name="/api/v4/ventas/muestra",
            timeout=15,
        )
