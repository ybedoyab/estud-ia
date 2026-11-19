# Guía docente

El guion hora por hora está en `ejemplos-clase/00-como-dar-la-clase.md`. Esta página es solo la contingencia y lo que hay que proyectar.

Proyecta, en este orden: el cuaderno, una consulta con filas, el gráfico, la salida de `publicar()`, y Airflow en `https://airflow.34.95.210.33.sslip.io`.

| Si pasa esto | Qué hacer |
|---|---|
| Colab no llega a la API | Abre `/health`. Si no responde, `docker compose ps` en la VM de Airflow. |
| Un estudiante no autentica | Que use `estudianteNN` y vuelva a escribir la contraseña. El compartido está bloqueado a propósito. |
| Airflow tarda en ver el DAG | La API espera cerca de 90 segundos. Se puede publicar otra vez: actualiza el mismo DAG. |
| Alguien manda SQL de escritura | La celda muestra el rechazo. Los demás DAG siguen. |
| Quieres un fallo en la pantalla | Variable `estudia_demo_forzar_error=1` en el DAG docente. Luego vuelve a `0`. |
| Se acaba la clase | A las 21:00 se pausan los DAG de estudiantes. Después, `infra/stop.sh` apaga la VM y conserva disco, historial y reportes. |

El ejemplo docente `estudia_clase03_demo` no modifica `retail_dwh`.
