# 13. Integración con Airflow

Objetivo: nombrar el pipeline sin obligar a publicarlo.

## La cadena

`extraer_api` → `guardar_raw` → `normalizar` → `validar` → `generar_reporte`

Es lo mismo que el cuaderno, en otro sitio: pedir la muestra, conservar el JSON, abrir las columnas, revisar la clave y escribir el agregado.

El ejemplo del docente está en `clase04/examples/airflow/estudia_clase04_demo_api.py`. Usa esos nombres de tarea. `schedule` es `None` y el DAG nace en pausa. La contraseña no está en el archivo: iría en una conexión de Airflow llamada `estudia_clase04_api`.

## Qué no decir

No digas que ese DAG está desplegado. No está cargado en el scheduler. Ver el archivo en el repositorio no lo ejecuta.

Tampoco pidas 45 DAG nuevos. La clase de hoy termina en el cuaderno.

## Frase de cierre

«Si cierro Colab, la sesión de Python se apaga. Un pipeline repetiría la extracción sin volver a copiar el token en el chat. Hoy no lo vamos a publicar.»
