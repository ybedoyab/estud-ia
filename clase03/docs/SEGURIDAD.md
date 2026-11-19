# Seguridad

La API no recibe código Python ni comandos. Recibe un JSON con una consulta `SELECT` o `WITH`, una validación, una transformación de una lista cerrada y un reporte CSV.

La consulta se rechaza si trae otra sentencia, si escribe, si nombra `pg_catalog`, `public` o `pgbouncer`, o si no lee el esquema `curso`. Además corre con el rol `airflow_lectura`, que solo tiene `SELECT`, con `statement_timeout` de 15 segundos y transacción de solo lectura. El resultado se corta en 5 000 filas.

El token identifica al estudiante. El DAG y el CSV quedan bajo ese usuario. Un token ajeno, vencido o ausente no entra. El usuario `estudiante`, sin número, recibe un rechazo explícito y no publica.

Las contraseñas de PostgreSQL no se guardan en la API ni se escriben en el cuaderno. El intento de login falla igual si el usuario no existe o si la contraseña está mal, salvo el usuario compartido, que ya es público. Hay un tope de intentos por IP.

Los secretos de servicio están en `/root/estudia-clase03/secrets.env`, modo 600. No están en git. El cuaderno solo tiene el host, el puerto, el nombre de la base y la URL pública.

La interfaz completa de Airflow queda para el docente, con usuario `docente`. Los estudiantes miran su estado por la API. El simple auth manager de Airflow no alcanza para dar a 45 personas una cuenta limitada y segura dentro de la interfaz; por eso no se crearon usuarios de Airflow para ellos.

La metadata de Airflow es un Postgres distinto, dentro de la VM de Airflow. No está en `retail_dwh`.
