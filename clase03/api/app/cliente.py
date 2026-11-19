"""Cliente que usan el notebook y las pruebas. No contiene secretos."""

from __future__ import annotations

import os

import requests


class ErrorEstudIA(RuntimeError):
    pass


class EstudIAPipeline:
    def __init__(self, nombre, intervalo_minutos=10, api_url=None, token=None):
        self.nombre = nombre
        self.intervalo_minutos = intervalo_minutos
        self.api_url = (api_url or os.environ.get("ESTUDIA_API_URL", "")).rstrip("/")
        self.token = token or os.environ.get("ESTUDIA_TOKEN", "")
        self.tareas = []
        self.publicacion = None

    def agregar_tarea(self, tarea_id, tipo, configuracion=None, depende_de=None):
        tarea = {"id": tarea_id, "tipo": tipo, "depende_de": list(depende_de or [])}
        configuracion = configuracion or {}
        if tipo == "sql":
            consulta = configuracion if isinstance(configuracion, str) else configuracion.get("consulta", "")
            tarea["consulta"] = consulta
        elif tipo == "transformacion":
            tarea["operacion"] = configuracion.get("operacion", "quitar_nulos")
        elif tipo == "agrupacion":
            tarea["columnas"] = configuracion.get("columnas", [])
            tarea["metrica"] = configuracion.get("metrica", "sum")
            tarea["campo"] = configuracion.get("campo", "importe_neto")
        self.tareas.append(tarea)
        return self

    def definicion(self):
        return {
            "nombre": self.nombre,
            "intervalo_minutos": self.intervalo_minutos,
            "tareas": self.tareas,
        }

    def mostrar_diagrama(self):
        print(self.nombre)
        for tarea in self.tareas:
            origen = ", ".join(tarea["depende_de"]) or "inicio"
            print(f"  {origen} -> {tarea['id']} ({tarea['tipo']})")
        return self.definicion()

    def _cabeceras(self):
        if not self.token:
            raise ErrorEstudIA("Primero inicia sesion. No hay token de estudiante.")
        return {"Authorization": f"Bearer {self.token}"}

    def validar(self):
        respuesta = requests.post(
            f"{self.api_url}/pipelines/validate",
            json=self.definicion(),
            headers=self._cabeceras(),
            timeout=30,
        )
        if respuesta.status_code >= 400:
            raise ErrorEstudIA(_detalle(respuesta))
        return respuesta.json()

    def publicar(self):
        respuesta = requests.post(
            f"{self.api_url}/pipelines/publish",
            json=self.definicion(),
            headers=self._cabeceras(),
            timeout=120,
        )
        if respuesta.status_code >= 400:
            raise ErrorEstudIA(_detalle(respuesta))
        self.publicacion = respuesta.json()
        datos = self.publicacion
        print("Pipeline validado correctamente.")
        print()
        print(f"Estudiante: {datos.get('estudiante')}")
        print(f"DAG: {datos.get('dag_id')}")
        print(f"Estado: {datos.get('estado')}")
        print(f"Programacion: cada {datos.get('intervalo_minutos')} minutos")
        print(f"Proxima ejecucion: {datos.get('proxima_ejecucion')}")
        print(f"URL: {datos.get('url')}")
        return datos

    def ejecutar_ahora(self):
        respuesta = requests.post(
            f"{self.api_url}/pipelines/me/trigger",
            headers=self._cabeceras(),
            timeout=60,
        )
        if respuesta.status_code >= 400:
            raise ErrorEstudIA(_detalle(respuesta))
        return respuesta.json()

    def ejecuciones(self):
        respuesta = requests.get(
            f"{self.api_url}/pipelines/me/runs",
            headers=self._cabeceras(),
            timeout=30,
        )
        if respuesta.status_code >= 400:
            raise ErrorEstudIA(_detalle(respuesta))
        return respuesta.json()

    def reporte(self):
        respuesta = requests.get(
            f"{self.api_url}/pipelines/me/report",
            headers=self._cabeceras(),
            timeout=30,
        )
        if respuesta.status_code >= 400:
            raise ErrorEstudIA(_detalle(respuesta))
        return respuesta.text


def iniciar_sesion(api_url, usuario, contrasena):
    respuesta = requests.post(
        f"{api_url.rstrip('/')}/auth/login",
        json={"username": usuario, "password": contrasena},
        timeout=30,
    )
    if respuesta.status_code >= 400:
        raise ErrorEstudIA(_detalle(respuesta))
    datos = respuesta.json()
    os.environ["ESTUDIA_TOKEN"] = datos["access_token"]
    os.environ["ESTUDIA_USUARIO"] = datos["usuario"]
    return datos


def _detalle(respuesta):
    try:
        cuerpo = respuesta.json()
    except Exception:
        cuerpo = {}
    mensaje = cuerpo.get("detail") or cuerpo.get("mensaje") or respuesta.text
    return f"HTTP {respuesta.status_code}: {mensaje}"
