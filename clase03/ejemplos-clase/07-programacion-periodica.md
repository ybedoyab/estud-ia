# 7. Programación periódica

Objetivo: ver una corrida que nadie lanzó a mano.

Concepto: el horario es un cron en `America/Bogota`. `catchup=False` evita que, al encender la máquina, Airflow intente recuperar todas las corridas perdidas. A las 21:00 los DAG de estudiantes se pausan; lo que ya está en curso termina.

Qué decir: «cada 10 minutos es el ritmo de la clase. El de demostración va cada 5 para que lo veamos antes de irnos».

Demostración: DAG `estudia_clase03_demo` en la interfaz, y la celda que pide una corrida inmediata del pipeline del estudiante.

Resultado esperado: en la lista de ejecuciones aparece `success` o, mientras espera, `queued` o `running`.

Pregunta: ¿a qué hora sería la próxima corrida de un DAG de 10 minutos si ahora son las 20:43?

Error frecuente: creer que apagar Colab detiene el DAG. No lo detiene. Pausar el DAG, o apagar la VM, sí.

Corrección: la pausa de las 21:00 es automática. Para detener la VM después de clase se usa `clase03/infra/stop.sh`.

Transición: «cuando una corrida falla, el log dice en qué tarea y por qué».
