"""Ejecuta el notebook con el mismo cliente que usarán los estudiantes."""

import os
import sys
import tempfile
from pathlib import Path

import nbformat
from nbclient import NotebookClient

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _entorno import cuentas

RAIZ = Path(__file__).resolve().parents[1]
NOTEBOOK = RAIZ / "notebooks" / "EstudIA_Clase03_SQL_Pandas_Airflow.ipynb"


def main():
    password = cuentas()["estudiante90"]
    os.environ["ESTUDIA_USUARIO"] = "estudiante90"
    os.environ["ESTUDIA_CONTRASENA"] = password
    os.environ["MPLBACKEND"] = "Agg"
    original = NOTEBOOK.read_text(encoding="utf-8")
    if password in original:
        print("FAIL el notebook de plantilla contiene la contrasena de prueba")
        return 1
    nb = nbformat.reads(original, as_version=4)
    with tempfile.TemporaryDirectory() as carpeta:
        cliente = NotebookClient(
            nb,
            timeout=600,
            kernel_name="estudia-clase03",
            resources={"metadata": {"path": carpeta}},
        )
        cliente.execute()
    texto = ""
    for celda in nb.cells:
        for salida in celda.get("outputs", []):
            texto += str(salida.get("text", ""))
            texto += str(salida.get("data", ""))
    if password in texto:
        print("FAIL la contrasena aparecio en la salida del notebook")
        return 1
    marcadores = ["conexion_ok", "Pipeline validado correctamente", "ESTUDIA — CLASE 03", "Ejecucion: success", "Reporte: disponible"]
    faltan = [item for item in marcadores if item not in texto]
    if faltan:
        print("FAIL faltan resultados:", ", ".join(faltan))
        print(texto[-2000:])
        return 1
    print("PASS notebook estudiante90")
    print("\n".join(linea for linea in texto.splitlines() if linea.startswith("ESTUDIA") or linea.startswith("Estudiante") or linea.startswith("SQL") or linea.startswith("Pandas") or linea.startswith("Pipeline") or linea.startswith("DAG") or linea.startswith("Ejecucion") or linea.startswith("Programacion") or linea.startswith("Reporte") or linea.startswith("Seguimiento")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
