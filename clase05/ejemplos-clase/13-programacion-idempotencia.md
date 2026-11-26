# Programación e idempotencia

Deja `schedule=None`.

Si en una demostración con un solo equipo quieres un cron, cambia solo esa copia a algo holgado, por ejemplo cada hora, y vuelve a `None` al terminar. `catchup=False` evita correr el pasado. No lo actives en los 45 portátiles a la vez.

La misma corrida escribe siempre en `data/<capa>/<run_id>/`. Un reintento reemplaza el archivo. No agrega otra copia de las filas.

XCom transporta el `run_id`, no el dataframe ni el token.
