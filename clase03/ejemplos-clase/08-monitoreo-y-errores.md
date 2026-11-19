# 8. Monitoreo y errores

Objetivo: leer un fallo controlado y ver la corrida siguiente en verde.

Concepto: cada tarea tiene estado, duración y log. Un reintento vuelve a ejecutar la tarea, no todo el DAG, salvo que la dependencia lo exija.

Qué decir: «el error de demostración no borra ventas. Es una bandera que yo enciendo».

Demostración: poner la variable `estudia_demo_forzar_error` en `1`, esperar la corrida del DAG docente, abrir el log de `validar`, volver la variable a `0`.

Resultado esperado: una corrida `failed` con el texto «Error de demostracion controlado por el docente» y, después, una corrida `success`.

Pregunta: ¿en qué tarea se detuvo y qué tareas no llegaron a empezar?

Error frecuente: buscar el error en PostgreSQL. La base no se modificó.

Corrección: el log de la tarea `validar` tiene el mensaje. Quitar la variable hace que el siguiente ciclo escriba de nuevo el CSV.

Transición: la celda final del cuaderno recoge SQL, Pandas, publicación, ejecución y reporte. Lo que no esté confirmado queda en `PENDIENTE`.
