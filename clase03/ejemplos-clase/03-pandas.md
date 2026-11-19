# 3. Pandas

Objetivo: reconocer en un DataFrame lo mismo que ya hicieron con SQL.

Concepto: `groupby` equivale a `GROUP BY`. `isna` muestra huecos. `duplicated` cuenta filas repetidas.

Qué decir: «la suma ya no la hace PostgreSQL. La hace la tabla que acabamos de bajar».

Demostración: `head`, `info`, `isna`, `duplicated`, `groupby("region")` y el gráfico de barras.

Resultado esperado: una fila por región presente en la muestra, ordenada por venta neta, y un gráfico con las primeras siete.

Pregunta: ¿qué región queda arriba y coincide con lo que vieron en SQL?

Error frecuente: agrupar y olvidar `reset_index` o `as_index=False`, y luego el gráfico no encuentra la columna `region`.

Corrección: usen la celda del cuaderno, que deja `region` como columna.

Transición: «ahora separamos esa cuenta en funciones con nombre. Eso es un ETL».
