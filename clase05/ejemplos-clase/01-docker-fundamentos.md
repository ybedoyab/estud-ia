# Docker, en una frase

Una imagen es la receta. Un contenedor es esa receta en ejecución. Compose describe varios contenedores que se hablan por una red interna.

En esta clase la imagen de Airflow es `apache/airflow:3.4.0`. No se escribe `latest`, porque mañana esa etiqueta podría ser otra versión.

Pregunta: "¿El contenedor de postgres de Compose es la base de las 50.000 ventas?" Respuesta: no. Solo guarda usuarios, DAGs y el estado de las tareas de este portátil.

Lo que no hacemos: contenedor privilegiado, montar `docker.sock`, publicar el puerto 5432.
