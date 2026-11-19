# 4. ETL

Objetivo: partir el trabajo en extraer, transformar, validar y reportar.

Concepto: cada función tiene una entrada y una salida. Validar es decidir si el resultado sirve antes de publicarlo.

Qué decir: «si la extracción viene vacía, prefiero un error claro antes que un CSV en blanco».

Demostración: la celda con `extraer_datos`, `transformar_datos`, `validar_datos` y `generar_reporte`.

Resultado esperado: una fila por categoría, con `venta_neta` y `unidades`.

Pregunta: ¿qué cambiarían para agrupar por canal en lugar de por categoría?

Error frecuente: transformar antes de extraer, o usar una columna que la consulta no trajo.

Corrección: el orden de la última línea del cuaderno es extraer, transformar, validar, reportar.

Transición: «esto vive mientras la celda está abierta. El siguiente paso es dejarlo encargado».
