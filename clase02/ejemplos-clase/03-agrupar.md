# 3. Agregar y agrupar

Objetivo: pasar de filas sueltas a un resumen.

`WHERE` filtra filas. `GROUP BY` las junta. `HAVING` filtra los grupos ya calculados.

## Precio por categoría

**Pregunta:** ¿qué categoría es más cara, en promedio?

`COUNT(*)` cuenta filas. `AVG`, `MIN` y `MAX` miran `precio_unitario`. `ROUND(..., 2)` deja dos decimales.

```sql
SELECT
    categoria,
    COUNT(*) AS productos,
    ROUND(AVG(precio_unitario), 2) AS precio_medio,
    MIN(precio_unitario) AS precio_min,
    MAX(precio_unitario) AS precio_max
FROM curso.productos
GROUP BY categoria
ORDER BY precio_medio DESC;
```

Deben salir cinco filas, una por categoría, con 100 productos cada una.

## Venta por canal

**Pregunta:** ¿por dónde entra más dinero: tienda, web o app?

`SUM` suma el importe. `importe_neto` ya tiene el descuento aplicado. `importe_bruto` no.

```sql
SELECT
    canal,
    COUNT(*) AS transacciones,
    SUM(cantidad) AS unidades,
    ROUND(SUM(importe_neto), 2) AS venta_neta
FROM curso.ventas
GROUP BY canal
HAVING SUM(importe_neto) > 0
ORDER BY venta_neta DESC;
```

`HAVING` va después de agrupar. Aquí los tres canales venden, así que no desaparece ninguno. Sirve para mostrar la diferencia con `WHERE`: `WHERE` no puede usar el `SUM`.

## Más caros que el promedio

**Pregunta:** ¿qué productos cuestan más que el precio medio de todo el catálogo?

La subconsulta devuelve un solo número. La consulta de fuera compara cada producto contra ese número.

```sql
SELECT nombre, categoria, precio_unitario
FROM curso.productos
WHERE precio_unitario > (
    SELECT AVG(precio_unitario)
    FROM curso.productos
)
ORDER BY precio_unitario DESC
LIMIT 10;
```
