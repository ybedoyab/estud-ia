# El DAG

Identificador: `estudia_clase05_api_medallion`.

Archivo de práctica: `dags/estudia_clase05_practica.py`. También está en `plantillas/` por si hay que empezar de cero. Sustituir `COMPLETA` no rompe el import: el DAG aparece igual. La corrida se detiene hasta que los campos estén escritos.

Tareas, en este orden:

`extraer_api > guardar_bronze > transformar_silver > validar_datos > generar_gold > exportar_reporte`

`schedule=None`, `catchup=False`, `max_active_runs=1`, un reintento, nace en pausa.

La solución de referencia está en `profesor/estudia_clase05_profesor.py`. No se entrega en el ZIP. Para probarla en local, aparta el archivo de práctica y copia el del profesor a `dags/`. No los dejes juntos: los dos usan el mismo `dag_id`.
