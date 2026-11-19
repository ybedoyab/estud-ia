# 5. Construir el pipeline

Objetivo: convertir las funciones en tareas con dependencias.

Concepto: una tarea no empieza hasta que terminan las que tiene en `depende_de`. El servidor no ejecuta Python arbitrario.

Qué decir: «ustedes describen el trabajo. El servidor tiene una lista corta de operaciones permitidas: SQL de lectura, validar, agrupar y escribir el CSV».

Demostración: `EstudIAPipeline`, cuatro `agregar_tarea` y `mostrar_diagrama`.

Resultado esperado: el diagrama imprime `extraer -> validar -> agrupar -> reporte`. `validar()` responde sin error.

Pregunta: ¿qué pasa si `reporte` no depende de `agrupar`?

Error frecuente: pedir un tipo `python` o meter un `DELETE` en la consulta.

Corrección: el mensaje de la API dice que el tipo o la sentencia no están permitidos. Se cambia la definición y se vuelve a validar. No se crea ningún DAG.

Transición: «validar no lo deja corriendo. Publicar sí».
