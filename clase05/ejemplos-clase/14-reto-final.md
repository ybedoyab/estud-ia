# Reto

Con el DAG en success:

1. Abre `data/reports/<run_id>/manifiesto.json` y señala `alcance`.
2. Compara `filas` con `total_records` del filtro. Explica por qué no son 50.000.
3. Di qué columna usarías si alguien te pasa la muestra anidada en vez de `/ventas`.
4. Dispara el DAG de fallo y lee la frase del log.
5. Apaga Compose con `detener` y vuelve a iniciar. Los DAG siguen ahí porque el volumen de metadatos se conservó.

Quien esté en Colab entrega el resumen impreso por el cuaderno y los archivos de `salida_clase05/reports/notebook`. Esa entrega no demuestra un scheduler.
