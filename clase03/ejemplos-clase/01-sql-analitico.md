# 1. SQL analítico

Objetivo: retomar JOIN, GROUP BY, HAVING, CTE y ranking con las ventas reales.

Concepto: una agregación responde por grupo; la ventana numera dentro del grupo.

Qué decir: «HAVING mira el resultado del grupo. Por eso puede usar SUM. WHERE todavía no lo conoce».

Demostración: las consultas `CONSULTA_CATEGORIA` y `CONSULTA_RANKING` del cuaderno.

Resultado esperado: la primera devuelve filas de región y categoría por encima de un millón. La segunda devuelve tres productos por categoría. En este catálogo cada categoría tiene una sola subcategoría, así que los nombres se parecen: Alimentación es arroz, Ropa es pantalón.

Pregunta: ¿qué región y categoría aparecen primeras?

Error frecuente: filtrar `puesto <= 3` en el mismo SELECT del `ROW_NUMBER`. PostgreSQL responde que la columna no existe.

Corrección: envolver el cálculo en `WITH` y filtrar fuera.

Transición: «estas consultas van a salir de Colab. Primero hay que entrar a la base».
