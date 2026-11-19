import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from app.validacion import EntregaInvalida, sql_es_segura, usuario_permitido, validar_pipeline


def pipeline(**cambios):
    base = {
        "nombre": "Practica",
        "intervalo_minutos": 10,
        "tareas": [
            {"id": "extraer", "tipo": "sql", "consulta": "SELECT categoria FROM curso.productos"},
            {"id": "validar", "tipo": "validacion", "depende_de": ["extraer"]},
            {"id": "reporte", "tipo": "reporte_csv", "depende_de": ["validar"]},
        ],
    }
    base.update(cambios)
    return base


def test_usuario_individual():
    assert usuario_permitido("estudiante21")
    assert not usuario_permitido("estudiante")
    assert not usuario_permitido("postgres")


def test_rechaza_escritura():
    with pytest.raises(EntregaInvalida):
        sql_es_segura("DELETE FROM curso.ventas")
    with pytest.raises(EntregaInvalida):
        sql_es_segura("SELECT 1; DROP TABLE curso.ventas")
    with pytest.raises(EntregaInvalida):
        sql_es_segura("SELECT pg_read_file('/etc/passwd') FROM curso.ventas")


def test_rechaza_python_y_shell_en_tipo():
    datos = pipeline()
    datos["tareas"][0]["tipo"] = "python"
    with pytest.raises(EntregaInvalida):
        validar_pipeline(datos)


def test_acepta_select():
    limpio = validar_pipeline(pipeline())
    assert limpio["intervalo_minutos"] == 10
    assert limpio["tareas"][0]["consulta"].lower().startswith("select")
