# Cómo dar la clase

Conéctate como estudiante, en solo lectura, y proyecta las consultas en este orden:

1. `01-explorar.md`
2. `02-filtrar.md`
3. `03-agrupar.md`
4. `04-relacionar.md`
5. `05-analizar.md`

Cada bloque trae la pregunta de negocio, qué decir y el SQL para copiar.

```bash
psql "host=34.39.202.205 port=6432 dbname=retail_dwh user=estudiante sslmode=require"
```

Ese usuario es el de toda la clase. La contraseña está en la fila `estudiante` de `clase02/student_credentials.csv`. No la dejes escrita en el archivo de la clase.

## Qué hay en la base

| Vista | Qué es | Cómo se une con las ventas |
|---|---|---|
| `curso.productos` | 500 productos, 5 categorías | `ventas.id_producto` |
| `curso.clientes` | 2 000 clientes | `ventas.id_cliente` |
| `curso.tiendas` | 50 tiendas en España | `ventas.id_tienda` |
| `curso.fechas` | todos los días de 2022 a 2024 | `ventas.id_fecha` |
| `curso.ventas` | 50 000 transacciones | |

## Tres avisos antes de empezar

- `descuento_pct` es una fracción. `0.10` significa 10 %.
- Cada categoría tiene una sola subcategoría. Alimentación es siempre Arroz, Ropa es siempre Pantalón, Hogar es Almohada, Deportes es Botella y Electrónica es Smartphone. No es un error de la consulta.
- Los estudiantes no pueden modificar datos. Si alguien prueba un `INSERT`, debe fallar. Puedes demostrarlo al final:

```sql
INSERT INTO curso.productos (nombre) VALUES ('prueba');
```
