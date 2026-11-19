# 6. Publicar en Airflow

Objetivo: que el DAG quede registrado a nombre de quien inició sesión.

Concepto: el token dice quién es el estudiante. El DAG se llama `estudia_estudianteNN_pipeline`. Volver a publicar actualiza ese mismo archivo.

Qué decir: «no elijan el identificador. Si pudieran, alguien publicaría encima del trabajo de otra persona».

Demostración: `pipeline.publicar()`.

Resultado esperado: el texto con estudiante, DAG, estado `Publicado`, cada 10 minutos, la próxima hora y dos URL.

Pregunta: ¿qué URL abre el estado y cuál abre la pantalla del docente?

Error frecuente: publicar sin haber iniciado sesión, o con el usuario compartido.

Corrección: volver a la celda de credenciales, iniciar sesión y publicar otra vez.

Transición: «publicado no es lo mismo que ya ejecutado. El reloj de Airflow dispara la corrida».
