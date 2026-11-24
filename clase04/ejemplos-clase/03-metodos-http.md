# 3. Métodos HTTP

Objetivo: decir el método correcto antes de pulsar Send.

## Qué explicar, en este orden

- GET pide una representación y no lleva cuerpo.
- POST crea o dispara una acción. El login es un POST.
- PUT reemplaza el recurso. En el sandbox hay que enviar `titulo`.
- PATCH envía solo lo que cambia, por ejemplo `{"estado": "hecha"}`.
- DELETE elimina. Si sale bien, responde 204 y el cuerpo va vacío.
- HEAD pide encabezados. OPTIONS pregunta métodos permitidos. No los practicamos.

GET es segura. GET, PUT y DELETE son idempotentes. POST no lo es: dos envíos pueden crear dos tareas. No reintentes una escritura.

## Headers, path, query y body

- `Authorization: Bearer <token>` es un header. El valor no se proyecta.
- `Content-Type: application/json` describe el cuerpo que envías.
- `Accept: application/json` pide JSON de vuelta.
- `/productos/1` es un path parameter.
- `?region=Aragón&page=1&page_size=2` son query parameters.
- El JSON va en el body, solo en POST, PUT y PATCH.

## Códigos

2xx se atendió. 4xx no se aceptó la petición. 5xx falló el servidor. Los 500 y 503 de `/api/v4/ejemplos/` son demostraciones.

## Pregunta

«¿Por qué PUT de una tarea sin título no es un PATCH?»

Porque PUT sustituye el recurso y el esquema exige `titulo`. PATCH puede mandar un solo campo.

## Si no tienen Postman

La explicación es la misma. La práctica está en Swagger y en las secciones 04 a 06 y 10 del cuaderno.
