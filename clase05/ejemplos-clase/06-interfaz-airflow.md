# Interfaz

URL: http://127.0.0.1:8080

Usuario: `admin`

Contraseña inicial: `estudia-local`

En Airflow 3 la pantalla la sirve el api-server. No hay un contenedor aparte llamado webserver. El health puede marcar el triggerer como down. Este laboratorio no lo arranca y las tareas igual corren.

DAGs que deben aparecer, en pausa:

- `estudia_clase05_api_medallion`
- `estudia_clase05_fallo_controlado`

Graph muestra las flechas. Grid muestra el estado de cada corrida. Logs abre la salida de una tarea.

Quitar la pausa es el interruptor del DAG. Trigger lanza una corrida manual.
