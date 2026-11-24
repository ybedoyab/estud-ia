# 11. Extracción, validación y exportación

Objetivo: guardar la página que sí se pidió, con metadatos, y sin secretos.

## Qué se guarda

En la carpeta `salida_clase04` del cuaderno:

- `ventas_parcial.json`: el JSON original de las páginas pedidas.
- `ventas_normalizadas.csv`: la misma extracción abierta con `json_normalize`.
- `metadatos_extraccion.json`: fecha en UTC, filtros, páginas solicitadas, páginas recibidas, identificadores únicos, `extraccion: parcial`, `total_pages` conocido y códigos de error observados.

No entran el token ni la contraseña. La celda lo comprueba antes de dar la descarga por buena.

## Descarga

En Colab, `google.colab.files.download`. Fuera de Colab la celda dice la ruta local y no falla.

## Validar antes de fiarse

- `id_transaccion` sin nulos.
- Sin duplicados de esa clave en la muestra pedida.
- `importe_neto` convertible a número.
- `has_next` o `total_pages` leídos en voz alta, para no tratar tres páginas como el censo.

Si el modo es respaldo, los archivos llevan el prefijo `RESPALDO_` y el metadato `origen` lo dice. No se archivan como si fueran la extracción de hoy.

## Airflow, solo como idea

Esos tres archivos son la versión manual de guardar el crudo, normalizar y dejar constancia. El paso siguiente está en el ejemplo 13. Nadie publica un DAG en esta sección.
