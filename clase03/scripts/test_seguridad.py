"""Aislamiento, payloads rechazados y rol de solo lectura. No imprime secretos."""

import sys
from pathlib import Path

import psycopg
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _entorno import API, DB_HOST, DB_NAME, DB_PORT, cuentas, secreto, ssh

RESULTADOS = []


def marcar(nombre, ok, detalle=""):
    RESULTADOS.append((nombre, ok))
    print(("PASS" if ok else "FAIL"), nombre, detalle)


def login(usuario, password):
    respuesta = requests.post(
        f"{API}/auth/login",
        json={"username": usuario, "password": password},
        timeout=30,
    )
    respuesta.raise_for_status()
    return respuesta.json()["access_token"]


def publicar(token, cuerpo):
    return requests.post(
        f"{API}/pipelines/publish",
        json=cuerpo,
        headers={"Authorization": f"Bearer {token}"},
        timeout=120,
    )


def pipeline_ok():
    return {
        "nombre": "Aislamiento",
        "intervalo_minutos": 15,
        "tareas": [
            {
                "id": "extraer",
                "tipo": "sql",
                "consulta": "SELECT p.categoria, SUM(v.importe_neto) AS importe_neto FROM curso.ventas v JOIN curso.productos p ON p.id_producto = v.id_producto GROUP BY p.categoria",
                "depende_de": [],
            },
            {"id": "validar", "tipo": "validacion", "depende_de": ["extraer"]},
            {"id": "reporte", "tipo": "reporte_csv", "depende_de": ["validar"]},
        ],
    }


def main():
    personas = cuentas()
    token_a = login("estudiante90", personas["estudiante90"])
    token_b = login("estudiante91", personas["estudiante91"])
    cab_a = {"Authorization": f"Bearer {token_a}"}
    cab_b = {"Authorization": f"Bearer {token_b}"}

    publicado_b = publicar(token_b, pipeline_ok())
    marcar("publicacion de B", publicado_b.status_code == 200, str(publicado_b.status_code))

    propio = requests.get(f"{API}/pipelines/me", headers=cab_a, timeout=30)
    ajeno = requests.get(f"{API}/pipelines/me", headers=cab_b, timeout=30)
    marcar(
        "cada quien ve su DAG",
        propio.json().get("dag_id") == "estudia_estudiante90_pipeline"
        and ajeno.json().get("dag_id") == "estudia_estudiante91_pipeline",
        f"{propio.status_code}/{ajeno.status_code}",
    )

    reporte_a = requests.get(f"{API}/pipelines/me/report", headers=cab_a, timeout=30)
    reporte_b = requests.get(f"{API}/pipelines/me/report", headers=cab_b, timeout=30)
    texto_a = reporte_a.text if reporte_a.status_code == 200 else ""
    marcar("reporte de A no es el de B", "estudiante90" in texto_a and "estudiante91" not in texto_a, str(reporte_a.status_code))
    marcar("B no recibe el reporte de A", reporte_b.status_code in {200, 404} and "estudiante90" not in reporte_b.text, str(reporte_b.status_code))

    shell = publicar(token_a, {
        "nombre": "malo",
        "intervalo_minutos": 10,
        "tareas": [
            {"id": "extraer", "tipo": "sql", "consulta": "SELECT 1 FROM curso.ventas", "depende_de": []},
            {"id": "romper", "tipo": "python", "codigo": "import os; os.system('id')", "depende_de": ["extraer"]},
            {"id": "reporte", "tipo": "reporte_csv", "depende_de": ["romper"]},
        ],
    })
    marcar("python arbitrario rechazado", shell.status_code == 422, str(shell.status_code))

    escritura = publicar(token_a, {
        "nombre": "escritura",
        "intervalo_minutos": 10,
        "tareas": [
            {"id": "extraer", "tipo": "sql", "consulta": "DELETE FROM curso.ventas", "depende_de": []},
            {"id": "validar", "tipo": "validacion", "depende_de": ["extraer"]},
            {"id": "reporte", "tipo": "reporte_csv", "depende_de": ["validar"]},
        ],
    })
    marcar("SQL de escritura rechazado", escritura.status_code == 422, str(escritura.status_code))

    larga = "SELECT p.categoria FROM curso.productos p WHERE " + " OR ".join(["p.categoria = 'Ropa'"] * 400)
    demasiado = publicar(token_a, {
        "nombre": "larga",
        "intervalo_minutos": 10,
        "tareas": [
            {"id": "extraer", "tipo": "sql", "consulta": larga, "depende_de": []},
            {"id": "validar", "tipo": "validacion", "depende_de": ["extraer"]},
            {"id": "reporte", "tipo": "reporte_csv", "depende_de": ["validar"]},
        ],
    })
    marcar("consulta demasiado larga rechazada", demasiado.status_code == 422, str(demasiado.status_code))

    ruta = requests.get(f"{API}/pipelines/me/runs/..%2Festudiante91", headers=cab_a, timeout=30)
    marcar("ruta fuera de alcance", ruta.status_code in {401, 404, 422}, str(ruta.status_code))

    sigue = requests.get(f"{API}/pipelines/me", headers=cab_a, timeout=30)
    marcar("una entrega mala no borra el DAG", sigue.status_code == 200 and sigue.json().get("dag_id") == "estudia_estudiante90_pipeline", str(sigue.status_code))

    try:
        with psycopg.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
            user="airflow_lectura", password=secreto("ESTUDIA_PGPASSWORD"),
            sslmode="require", connect_timeout=15, autocommit=True,
        ) as conn:
            conn.execute("CREATE TABLE public.estudia_no_debe (id int)")
            marcar("rol de lectura no escribe", False, "pudo crear una tabla")
    except Exception as exc:
        mensaje = str(exc).lower()
        marcar(
            "rol de lectura no escribe",
            "read-only" in mensaje or "permission denied" in mensaje or "cannot execute" in mensaje,
            type(exc).__name__,
        )
    try:
        with psycopg.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
            user="airflow_lectura", password=secreto("ESTUDIA_PGPASSWORD"),
            sslmode="require", connect_timeout=15, autocommit=True,
        ) as conn:
            conn.execute("SELECT pg_sleep(20)")
            marcar("consulta larga cancelada", False, "pg_sleep termino")
    except Exception as exc:
        marcar("consulta larga cancelada", getattr(exc, "sqlstate", "") == "57014", type(exc).__name__)

    logs = ssh("cd /opt/estudia-clase03/airflow && sudo docker compose logs --no-color fastapi | tail -c 200000")
    password = personas["estudiante90"]
    marcar("la contrasena no esta en los logs", password not in logs and "ESTUDIA_PGPASSWORD" not in logs)

    print("SEGURIDAD", "PASS" if all(ok for _, ok in RESULTADOS) else "FAIL")
    return 0 if all(ok for _, ok in RESULTADOS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
