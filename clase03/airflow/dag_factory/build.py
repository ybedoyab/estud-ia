"""Contrato de la fabrica.

La API escribe el DAG a partir de una definicion ya validada. El archivo
generado solo llama a estudia_runtime. No incorpora codigo del estudiante.
"""

ESQUEMA = {
    "nombre": "texto corto",
    "intervalo_minutos": [5, 10, 15],
    "tareas": ["sql", "validacion", "transformacion", "agrupacion", "reporte_csv"],
}
