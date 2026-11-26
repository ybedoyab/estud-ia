# Ejecución y logs

Trigger manual sobre el DAG de práctica, después de quitar la pausa y de rellenar `COMPLETA`.

En Grid:

- `success` cuando la tarea terminó;
- `up_for_retry` cuando va a intentarlo otra vez;
- `failed` cuando se agotó el reintento.

El log de `extraer_api` puede mostrar el código HTTP. No debe mostrar el token ni la contraseña.

El fallo controlado se reintenta una vez, a los 20 segundos, y vuelve a fallar porque el fixture no cambia.

Apagar el entorno no borra `data/` ni el volumen de metadatos. `docker compose down -v` sí borra los metadatos locales.
