# Validaciones

Antes de gold se exige:

- las seis columnas;
- `id_transaccion` no nulo;
- sin ids repetidos;
- fechas que se puedan leer;
- el mismo número de filas que la cobertura de bronze;
- alcance `parcial` o `completo`.

Si un id está repetido, la tarea falla. No se borran filas y no se cambia un nulo por cero.

Un importe negativo se conserva. El fixture de fallo trae uno a propósito y el error que debe verse es el duplicado, no el signo.

El DAG `estudia_clase05_fallo_controlado` usa `fixtures/validacion_falla.json`. No llama a la API.
