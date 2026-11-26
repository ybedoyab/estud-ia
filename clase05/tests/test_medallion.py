import ast
import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]


def cargar_practica():
    ruta = RAIZ / "profesor" / "dags" / "estudia_clase05_practica.py"
    spec = importlib.util.spec_from_file_location("practica_clase05", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def pipeline():
    spec = importlib.util.spec_from_file_location("medallion_clase05", RAIZ / "pipeline" / "medallion.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.fixture
def datos(tmp_path, monkeypatch):
    monkeypatch.setenv("ESTUDIA_DATA", str(tmp_path))
    return tmp_path


def test_fixture_llega_a_reporte_y_no_duplica(datos):
    med = pipeline()
    extraccion = json.loads((RAIZ / "fixtures" / "ventas_ok.json").read_text(encoding="utf-8"))
    med.guardar_staging("corrida", extraccion)
    med.guardar_bronze("corrida")
    med.guardar_bronze("corrida")
    assert len(list((datos / "bronze" / "corrida").glob("pagina_*.json"))) == 1
    med.transformar_silver("corrida")
    med.transformar_silver("corrida")
    marco = pd.read_csv(datos / "silver" / "corrida" / "ventas.csv")
    assert list(marco["id_transaccion"]) == [1, 2]
    assert float(marco.loc[marco["id_transaccion"] == 2, "importe_neto"].iloc[0]) < 0
    med.validar_datos("corrida")
    med.generar_gold("corrida")
    med.exportar_reporte("corrida")
    manifiesto = json.loads((datos / "reports" / "corrida" / "manifiesto.json").read_text(encoding="utf-8"))
    assert manifiesto["alcance"] == "parcial"
    assert manifiesto["filas"] == 2
    bronze = (datos / "bronze" / "corrida" / "pagina_1.json").read_text(encoding="utf-8")
    assert "access_token" not in bronze
    assert not (datos / "staging" / "corrida" / "extraccion.json").exists()


def test_duplicado_detiene_antes_de_gold(datos):
    med = pipeline()
    extraccion = json.loads((RAIZ / "fixtures" / "validacion_falla.json").read_text(encoding="utf-8"))
    med.guardar_staging("falla", extraccion)
    med.guardar_bronze("falla")
    med.transformar_silver("falla")
    with pytest.raises(RuntimeError, match="duplicados"):
        med.validar_datos("falla")
    assert not (datos / "gold" / "falla").exists()


def test_plantilla_no_entra_a_dags_y_trae_huecos():
    plantilla = (RAIZ / "plantillas" / "dags" / "estudia_clase05_practica.py").read_text(encoding="utf-8")
    primero = (RAIZ / "plantillas" / "dags" / "estudia_clase05_mi_primer_dag.py").read_text(encoding="utf-8")
    assert "COMPLETA" in plantilla
    assert "COMPLETA" in primero
    resuelta_en_dags = (RAIZ / "dags" / "estudia_clase05_practica.py").read_text(encoding="utf-8")
    assert "COMPLETA" not in resuelta_en_dags
    assert plantilla != resuelta_en_dags
    assert not any(linea.strip() == "t1 >> t2 >> t3 >> t4 >> t5 >> t6" for linea in plantilla.splitlines())
    assert not any(linea.strip() == "inicio >> fin" for linea in primero.splitlines())


def test_practica_rellena_con_fixture(datos, monkeypatch):
    monkeypatch.setenv("ESTUDIA_FIXTURE", str(RAIZ / "fixtures" / "ventas_ok.json"))
    modulo = cargar_practica()

    class Bandeja:
        def __init__(self):
            self.caja = {}

        def xcom_pull(self, task_ids):
            return self.caja[task_ids]

    ti = Bandeja()
    contexto = {"run_id": "manual__practica", "ti": ti}
    for nombre, funcion in (
        ("extraer_api", modulo.extraer_api),
        ("guardar_bronze", modulo.guardar_bronze),
        ("transformar_silver", modulo.transformar_silver),
        ("validar_datos", modulo.validar_datos),
        ("generar_gold", modulo.generar_gold),
        ("exportar_reporte", modulo.exportar_reporte),
    ):
        ti.caja[nombre] = funcion(**contexto)
    resumen = json.loads((datos / "reports" / "manual__practica" / "resumen.json").read_text(encoding="utf-8"))
    assert resumen["transacciones"] == 2
    assert resumen["alcance"] == "parcial"


def test_archivos_python_compilan_y_no_guardan_secretos():
    prohibido = ("ey" + "J", "student_" + "credentials")
    for ruta in RAIZ.rglob("*"):
        if not ruta.is_file():
            continue
        if ruta.suffix.lower() not in {".py", ".md", ".yml", ".yaml", ".json", ".example", ".txt", ".ps1", ".sh", ".ipynb"}:
            continue
        if "dist" in ruta.parts or "__pycache__" in ruta.parts:
            continue
        texto = ruta.read_text(encoding="utf-8")
        for marca in prohibido:
            assert marca not in texto, ruta.name
        if ruta.suffix == ".py":
            ast.parse(texto)
    profesor = (RAIZ / "profesor" / "estudia_clase05_profesor.py").read_text(encoding="utf-8")
    resuelta = (RAIZ / "profesor" / "dags" / "estudia_clase05_practica.py").read_text(encoding="utf-8")
    assert "COMPLETA" not in profesor
    assert "COMPLETA" not in resuelta
    assert "t1 >> t2 >> t3 >> t4 >> t5 >> t6" in resuelta
