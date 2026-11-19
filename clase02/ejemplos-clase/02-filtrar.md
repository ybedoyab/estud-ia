# 2. Filtrar y ordenar

Objetivo: quedarse solo con las filas que responden la pregunta.

`WHERE` se evalúa fila por fila. `AND` exige las dos condiciones. `OR` basta con una.

## Precio dentro de un rango

**Pregunta:** ¿qué alimentos cuestan entre 5 y 30?

`BETWEEN` incluye los dos extremos.

```sql
SELECT nombre, precio_unitario
FROM curso.productos
WHERE categoria = 'Alimentación'
  AND precio_unitario BETWEEN 5 AND 30
ORDER BY precio_unitario;
```

## Varias regiones, excluyendo un segmento

**Pregunta:** ¿qué clientes de Andalucía o Cataluña no son ocasionales?

`IN` es una lista. `<>` significa “distinto de”. También se puede escribir `NOT (segmento = 'Ocasional')`.

```sql
SELECT ciudad, segmento
FROM curso.clientes
WHERE region IN ('Andalucía', 'Cataluña')
  AND segmento <> 'Ocasional'
LIMIT 20;
```

## Texto parecido

**Pregunta:** ¿qué productos tienen “arroz” en el nombre, o empiezan por “Smartphone”?

`LIKE` distingue mayúsculas. `ILIKE` no. `%` significa “cualquier texto”.

```sql
SELECT nombre, categoria
FROM curso.productos
WHERE nombre ILIKE '%arroz%'
   OR nombre LIKE 'Smartphone%';
```

## Nulos

**Pregunta:** ¿qué clientes no tienen ninguna compra pagada con Bizum?

Un `LEFT JOIN` conserva al cliente aunque no haya venta. Si no hubo cruce, `id_transaccion` queda `NULL`. `IS NULL` es la forma de preguntar por ese vacío. `= NULL` no funciona.

```sql
SELECT c.id_cliente, c.nombre, c.segmento
FROM curso.clientes c
LEFT JOIN curso.ventas v
    ON v.id_cliente = c.id_cliente
   AND v.metodo_pago = 'Bizum'
WHERE v.id_transaccion IS NULL
LIMIT 20;
```

Si quitan el filtro de Bizum y buscan clientes sin ninguna venta, el resultado puede ser vacío. Cero filas también es una respuesta: casi todos compraron algo.

## Las tiendas más grandes

**Pregunta:** ¿cuáles son las diez tiendas con más metros?

`DESC` ordena de mayor a menor. Si hay empate en metros, `nombre ASC` desempatan por nombre.

```sql
SELECT nombre, ciudad, metros_cuadrados
FROM curso.tiendas
ORDER BY metros_cuadrados DESC, nombre ASC
LIMIT 10;
```
