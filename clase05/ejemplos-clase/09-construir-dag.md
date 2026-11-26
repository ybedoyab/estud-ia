# El DAG

Los estudiantes no reciben el grafo ya unido. Escriben los operadores en `plantillas/dags/estudia_clase05_practica.py` y esta línea:

```python
t1 >> t2 >> t3 >> t4 >> t5 >> t6
```

Identificador: `estudia_clase05_api_medallion`. `schedule=None`, `catchup=False`, `max_active_runs=1`, un reintento, nace en pausa.

Tareas: `extraer_api`, `guardar_bronze`, `transformar_silver`, `validar_datos`, `generar_gold`, `exportar_reporte`.

`.\scripts\validar_dags.ps1` rechaza huecos. `.\scripts\activar_dags.ps1` comprueba la sintaxis dentro del contenedor y solo entonces copia el archivo a `dags/`.

La solución de referencia está en `profesor/dags/estudia_clase05_practica.py`. No se entrega en el ZIP. No la dejes junto a otra copia con el mismo `dag_id`.
