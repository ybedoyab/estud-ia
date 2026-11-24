"""Detiene las VM de EstudIA cuando el gasto del mes alcanza el presupuesto."""

import base64
import json
import urllib.error
import urllib.request

import functions_framework

PROJECT = "drafty-autopilot-fx"
ZONE = "southamerica-east1-a"
INSTANCES = ("estudia-postgres-lab", "estudia-airflow-clase03")


def _token() -> str:
    request = urllib.request.Request(
        "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
        headers={"Metadata-Flavor": "Google"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)["access_token"]


def _detener(nombre: str, token: str) -> None:
    url = (
        "https://compute.googleapis.com/compute/v1/projects/"
        f"{PROJECT}/zones/{ZONE}/instances/{nombre}/stop"
    )
    request = urllib.request.Request(
        url,
        data=b"{}",
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            print(nombre, response.status)
    except urllib.error.HTTPError as exc:
        detalle = exc.read().decode("utf-8", errors="replace")[:300]
        print(nombre, exc.code, detalle)


@functions_framework.cloud_event
def apagar(cloud_event):
    aviso = json.loads(base64.b64decode(cloud_event.data["message"]["data"]))
    costo = float(aviso.get("costAmount") or 0)
    tope = float(aviso.get("budgetAmount") or 0)
    if tope <= 0 or costo < tope:
        print(f"sin apagar costo={costo} tope={tope}")
        return
    print(f"apagando costo={costo} tope={tope}")
    token = _token()
    for nombre in INSTANCES:
        _detener(nombre, token)
