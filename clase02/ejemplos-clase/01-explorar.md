# 1. Explorar

Objetivo: que vean las cinco vistas y dejen de pedir `SELECT *` para todo.

## Ver una muestra del catálogo

**Pregunta:** ¿qué productos hay?

`SELECT *` devuelve todas las columnas. `LIMIT` corta el resultado. Sin `LIMIT`, una tabla grande llena la pantalla y no aporta más.

```sql
SELECT *
FROM curso.productos
LIMIT 10;
```

Repite la misma idea con `curso.clientes`, `curso.tiendas`, `curso.fechas` y `curso.ventas`.

## Elegir columnas y ponerles un nombre

**Pregunta:** ¿cómo se llama cada producto y a qué precio se vende?

El alias con `AS` cambia el título de la columna solo en el resultado. No cambia la tabla.

```sql
SELECT
    nombre AS producto,
    categoria,
    precio_unitario AS precio
FROM curso.productos
LIMIT 10;
```

## Valores distintos

**Pregunta:** ¿cuáles son las categorías, sin repetirlas?

`DISTINCT` quita duplicados. Aquí deben aparecer cinco: Alimentación, Deportes, Electrónica, Hogar y Ropa.

```sql
SELECT DISTINCT categoria
FROM curso.productos
ORDER BY categoria;
```

`ORDER BY` se ve mejor en el bloque de agregaciones, pero ya sirve para que la lista no salga en un orden arbitrario.
