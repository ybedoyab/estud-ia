"""API de la clase 03. Autentica contra PostgreSQL y publica DAGs declarativos."""

from __future__ import annotations

import hmac
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
import psycopg
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel, Field

from app.validacion import EntregaInvalida, dag_id, usuario_permitido, validar_pipeline

API_DIR = Path(__file__).resolve().parent
DAGS = Path(os.environ.get("ESTUDIA_DAGS", "/data/dags"))
SPECS = Path(os.environ.get("ESTUDIA_SPECS", "/data/specs"))
REPORTES = Path(os.environ.get("ESTUDIA_REPORTES", "/data/reportes"))
JWT_SECRET = os.environ.get("ESTUDIA_JWT_SECRET", "")
JWT_HORAS = int(os.environ.get("ESTUDIA_JWT_HORAS", "4"))
ADMIN_TOKEN = os.environ.get("ESTUDIA_ADMIN_TOKEN", "")
AIRFLOW_URL = os.environ.get("AIRFLOW_API_URL", "http://airflow-apiserver:8080").rstrip("/")
AIRFLOW_USER = os.environ.get("AIRFLOW_ADMIN_USER", "docente")
AIRFLOW_PASSWORD = os.environ.get("AIRFLOW_ADMIN_PASSWORD", "")
PUBLIC_API = os.environ.get("PUBLIC_API_URL", "").rstrip("/")
PUBLIC_AIRFLOW = os.environ.get("PUBLIC_AIRFLOW_URL", "").rstrip("/")
PGHOST = os.environ.get("ESTUDIA_PGHOST", "10.20.0.2")
PGPORT = int(os.environ.get("ESTUDIA_PGPORT", "6432"))
PGDATABASE = os.environ.get("ESTUDIA_PGDATABASE", "retail_dwh")
MAX_FALLOS = 8
VENTANA_FALLOS = 900
_fallos: dict[str, list[float]] = {}
_airflow_token = {"valor": "", "expira": 0.0}

app = FastAPI(title="EstudIA clase 03", docs_url=None, redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://colab.research.google.com",
        "https://colab.google.com",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


class LoginBody(BaseModel):
    username: str = Field(max_length=32)
    password: str = Field(max_length=200)


class PipelineBody(BaseModel):
    nombre: str
    intervalo_minutos: int = 10
    tareas: list[dict]


def _ahora() -> float:
    return time.time()


def _registrar_fallo(ip: str) -> None:
    marca = _ahora()
    recientes = [item for item in _fallos.get(ip, []) if marca - item < VENTANA_FALLOS]
    recientes.append(marca)
    _fallos[ip] = recientes
    if len(recientes) > MAX_FALLOS:
        raise HTTPException(status_code=429, detail="Demasiados intentos. Espera unos minutos.")


def _exigir_cupo(ip: str) -> None:
    marca = _ahora()
    recientes = [item for item in _fallos.get(ip, []) if marca - item < VENTANA_FALLOS]
    _fallos[ip] = recientes
    if len(recientes) > MAX_FALLOS:
        raise HTTPException(status_code=429, detail="Demasiados intentos. Espera unos minutos.")


def _autenticar_postgres(usuario: str, contrasena: str) -> None:
    try:
        with psycopg.connect(
            host=PGHOST,
            port=PGPORT,
            dbname=PGDATABASE,
            user=usuario,
            password=contrasena,
            sslmode="require",
            connect_timeout=8,
            autocommit=True,
        ) as conn:
            actual = conn.execute("SELECT current_user").fetchone()[0]
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Usuario o contrasena incorrectos.") from None
    if actual != usuario:
        raise HTTPException(status_code=401, detail="Usuario o contrasena incorrectos.")


def _token(usuario: str) -> str:
    if not JWT_SECRET:
        raise HTTPException(status_code=500, detail="La API no tiene configurada la firma de sesion.")
    expira = datetime.now(timezone.utc) + timedelta(hours=JWT_HORAS)
    return jwt.encode(
        {"sub": usuario, "scope": "estudiante", "exp": expira},
        JWT_SECRET,
        algorithm="HS256",
    )


def estudiante_actual(request: Request) -> str:
    cabecera = request.headers.get("authorization", "")
    if not cabecera.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Falta el token de sesion.")
    try:
        datos = jwt.decode(cabecera[7:].strip(), JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token expiro. Vuelve a iniciar sesion.") from None
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="El token no es valido.") from None
    usuario = str(datos.get("sub") or "")
    if datos.get("scope") != "estudiante" or not usuario_permitido(usuario):
        raise HTTPException(status_code=401, detail="El token no es valido.")
    return usuario


def _airflow_headers() -> dict[str, str]:
    if _airflow_token["expira"] < _ahora() + 30:
        respuesta = _airflow(
            "POST",
            "/auth/token",
            json={"username": AIRFLOW_USER, "password": AIRFLOW_PASSWORD},
            auth=False,
        )
        _airflow_token["valor"] = respuesta["access_token"]
        _airflow_token["expira"] = _ahora() + 600
    return {"Authorization": f"Bearer {_airflow_token['valor']}"}


def _airflow(method: str, path: str, json=None, auth: bool = True):
    import httpx

    headers = _airflow_headers() if auth else {}
    try:
        respuesta = httpx.request(
            method,
            f"{AIRFLOW_URL}{path}",
            json=json,
            headers=headers,
            timeout=20,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Airflow no responde.") from exc
    if respuesta.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Airflow respondio {respuesta.status_code}.")
    if not respuesta.content:
        return {}
    return respuesta.json()


def _escribir_dag(usuario: str) -> str:
    identificador = dag_id(usuario)
    contenido = (
        "from datetime import datetime, timedelta\n"
        "from airflow import DAG\n"
        "from airflow.operators.python import PythonOperator\n"
        "from estudia_runtime import ejecutar_tarea\n\n"
        f"USUARIO = {usuario!r}\n"
        f"DAG_ID = {identificador!r}\n\n"
        "with DAG(\n"
        "    dag_id=DAG_ID,\n"
        "    description='Pipeline individual de la clase 03',\n"
        "    start_date=datetime(2026, 11, 19),\n"
        "    schedule=None,\n"
        "    catchup=False,\n"
        "    max_active_runs=1,\n"
        "    default_args={'retries': 1, 'retry_delay': timedelta(minutes=1)},\n"
        "    tags=['clase03', 'estudiante', USUARIO],\n"
        "    is_paused_upon_creation=True,\n"
        ") as dag:\n"
        "    ejecutar_tarea(usuario=USUARIO)\n"
    )
    # The schedule is applied by the runtime from the spec via timetable in the generated file.
    destino = DAGS / f"{identificador}.py"
    destino.write_text(_dag_completo(usuario, identificador), encoding="utf-8")
    return identificador


def _dag_completo(usuario: str, identificador: str) -> str:
    return f'''from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.timetables.trigger import CronTriggerTimetable
from estudia_runtime import ejecutar_tarea, intervalo_de

USUARIO = {usuario!r}
MINUTOS = intervalo_de(USUARIO)

with DAG(
    dag_id={identificador!r},
    description="Pipeline individual de la clase 03",
    start_date=datetime(2026, 11, 19),
    schedule=CronTriggerTimetable(f"*/{{MINUTOS}} * * * *", timezone="America/Bogota"),
    catchup=False,
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=4),
    default_args={{
        "retries": 1,
        "retry_delay": timedelta(minutes=1),
        "execution_timeout": timedelta(minutes=3),
    }},
    tags=["clase03", "estudiante", USUARIO],
    is_paused_upon_creation=True,
) as dag:
    PythonOperator(
        task_id="pipeline",
        python_callable=ejecutar_tarea,
        op_kwargs={{"usuario": USUARIO}},
        pool="clase03",
    )
'''


def _esperar_dag(identificador: str) -> None:
    for _ in range(18):
        try:
            _airflow("GET", f"/api/v2/dags/{identificador}")
            return
        except HTTPException:
            time.sleep(5)
    raise HTTPException(status_code=504, detail="Airflow todavia no reconoce el DAG. Vuelve a publicar en un minuto.")


def _activar(identificador: str) -> None:
    _airflow("PATCH", f"/api/v2/dags/{identificador}", json={"is_paused": False})


def _proxima(minutos: int) -> str:
    zona = timezone(timedelta(hours=-5))
    ahora = datetime.now(zona)
    resto = minutos - (ahora.minute % minutos)
    if resto == minutos and ahora.second == 0:
        resto = minutos
    proxima = (ahora + timedelta(minutes=resto)).replace(second=0, microsecond=0)
    return proxima.strftime("%Y-%m-%d %H:%M America/Bogota")


@app.get("/health")
def health():
    return {"ok": True, "servicio": "estudia-clase03"}


@app.get("/certs/estudia-lab-ca.crt")
def certificado():
    ruta = API_DIR / "estudia-lab-ca.crt"
    if not ruta.is_file():
        raise HTTPException(status_code=404, detail="El certificado publico no esta disponible.")
    return FileResponse(ruta, media_type="application/x-pem-file", filename="estudia-lab-ca.crt")


@app.post("/auth/login")
def login(body: LoginBody, request: Request):
    ip = request.client.host if request.client else "desconocida"
    _exigir_cupo(ip)
    usuario = body.username.strip()
    if usuario == "estudiante":
        raise HTTPException(
            status_code=403,
            detail="El usuario compartido no puede publicar un pipeline individual.",
        )
    if not usuario_permitido(usuario):
        _registrar_fallo(ip)
        raise HTTPException(status_code=401, detail="Usuario o contrasena incorrectos.")
    try:
        _autenticar_postgres(usuario, body.password)
    except HTTPException:
        _registrar_fallo(ip)
        raise
    return {
        "access_token": _token(usuario),
        "token_type": "bearer",
        "expires_in": JWT_HORAS * 3600,
        "usuario": usuario,
    }


@app.get("/students/me")
def yo(usuario: str = Depends(estudiante_actual)):
    return {"usuario": usuario, "dag_id": dag_id(usuario)}


@app.post("/pipelines/validate")
def validar(body: PipelineBody, usuario: str = Depends(estudiante_actual)):
    try:
        limpio = validar_pipeline(body.model_dump())
    except EntregaInvalida as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"ok": True, "estudiante": usuario, "pipeline": limpio}


@app.post("/pipelines/publish")
def publicar(body: PipelineBody, usuario: str = Depends(estudiante_actual)):
    try:
        limpio = validar_pipeline(body.model_dump())
    except EntregaInvalida as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    SPECS.mkdir(parents=True, exist_ok=True)
    DAGS.mkdir(parents=True, exist_ok=True)
    spec = SPECS / f"{usuario}.json"
    temporal = spec.with_suffix(".json.tmp")
    temporal.write_text(json.dumps(limpio, ensure_ascii=False, indent=2), encoding="utf-8")
    temporal.replace(spec)
    identificador = _escribir_dag(usuario)
    _esperar_dag(identificador)
    _activar(identificador)
    return {
        "estudiante": usuario,
        "dag_id": identificador,
        "estado": "Publicado",
        "intervalo_minutos": limpio["intervalo_minutos"],
        "proxima_ejecucion": _proxima(limpio["intervalo_minutos"]),
        "url": f"{PUBLIC_API}/pipelines/me",
        "airflow_url": f"{PUBLIC_AIRFLOW}/dags/{identificador}/grid",
    }


@app.get("/pipelines/me")
def mi_pipeline(usuario: str = Depends(estudiante_actual)):
    identificador = dag_id(usuario)
    try:
        dag = _airflow("GET", f"/api/v2/dags/{identificador}")
    except HTTPException:
        raise HTTPException(status_code=404, detail="Todavia no has publicado un pipeline.") from None
    return {
        "estudiante": usuario,
        "dag_id": identificador,
        "pausado": dag.get("is_paused"),
        "url": f"{PUBLIC_AIRFLOW}/dags/{identificador}/grid",
    }


@app.post("/pipelines/me/trigger")
def disparar(usuario: str = Depends(estudiante_actual)):
    identificador = dag_id(usuario)
    logical = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    corrida = _airflow(
        "POST",
        f"/api/v2/dags/{identificador}/dagRuns",
        json={"logical_date": logical, "conf": {}},
    )
    return {"dag_id": identificador, "run_id": corrida.get("dag_run_id") or corrida.get("run_id"), "estado": corrida.get("state")}


@app.get("/pipelines/me/runs")
def corridas(usuario: str = Depends(estudiante_actual)):
    identificador = dag_id(usuario)
    datos = _airflow("GET", f"/api/v2/dags/{identificador}/dagRuns?limit=10&order_by=-logical_date")
    corridas_raw = datos.get("dag_runs") or datos.get("dagRuns") or []
    return {
        "dag_id": identificador,
        "ejecuciones": [
            {
                "run_id": item.get("dag_run_id") or item.get("run_id"),
                "estado": item.get("state"),
                "inicio": item.get("start_date"),
                "fin": item.get("end_date"),
            }
            for item in corridas_raw
        ],
    }


@app.get("/pipelines/me/runs/{run_id}")
def corrida(run_id: str, usuario: str = Depends(estudiante_actual)):
    if "/" in run_id or ".." in run_id:
        raise HTTPException(status_code=422, detail="Identificador de ejecucion no valido.")
    identificador = dag_id(usuario)
    return _airflow("GET", f"/api/v2/dags/{identificador}/dagRuns/{run_id}")


@app.get("/pipelines/me/report")
def reporte(usuario: str = Depends(estudiante_actual)):
    ruta = REPORTES / usuario / "reporte_ventas.csv"
    if not ruta.is_file():
        raise HTTPException(status_code=404, detail="El reporte todavia no existe. Espera la primera ejecucion.")
    return PlainTextResponse(ruta.read_text(encoding="utf-8"))


@app.get("/pipelines/me/logs")
def logs(usuario: str = Depends(estudiante_actual)):
    identificador = dag_id(usuario)
    datos = _airflow("GET", f"/api/v2/dags/{identificador}/dagRuns?limit=1&order_by=-logical_date")
    corridas_raw = datos.get("dag_runs") or []
    if not corridas_raw:
        return {"logs": "Todavia no hay ejecuciones."}
    run_id = corridas_raw[0].get("dag_run_id")
    try:
        tarea = _airflow(
            "GET",
            f"/api/v2/dags/{identificador}/dagRuns/{run_id}/taskInstances/pipeline/logs/1",
        )
    except HTTPException:
        return {"run_id": run_id, "estado": corridas_raw[0].get("state"), "logs": "El log todavia no esta disponible."}
    return {"run_id": run_id, "estado": corridas_raw[0].get("state"), "logs": tarea}


@app.post("/admin/pause-all")
def pausar(request: Request):
    recibido = request.headers.get("x-admin-token", "")
    if not ADMIN_TOKEN or not hmac.compare_digest(recibido, ADMIN_TOKEN):
        raise HTTPException(status_code=401, detail="No autorizado.")
    pausados = []
    for spec in SPECS.glob("estudiante*.json"):
        usuario = spec.stem
        if not usuario_permitido(usuario):
            continue
        identificador = dag_id(usuario)
        try:
            _airflow("PATCH", f"/api/v2/dags/{identificador}", json={"is_paused": True})
            pausados.append(identificador)
        except HTTPException:
            continue
    return {"pausados": pausados}
