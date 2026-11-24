# 7. CRUD del sandbox

Objetivo: practicar POST, PUT, PATCH y DELETE sin tocar las ventas.

Base: `https://34.95.210.33.sslip.io/api/v4/sandbox/tareas`

Authorization: Bearer de tu sesión. El sandbox no escribe en PostgreSQL. Vive en la memoria de esa sesión y caduca con el token. Hay un máximo de 30 tareas por sesión.

## Secuencia

1. **GET** la colección. Esperado: 200 y `data`.
2. **POST** la misma URL. Body raw JSON:

```json
{"titulo": "Practicar POST", "detalle": "Tarea ficticia de la sesion", "estado": "pendiente", "prioridad": 2}
```

Esperado: **201** y `id_tarea`. Usa ese id.

3. **GET** `/api/v4/sandbox/tareas/{id_tarea}`. Esperado: 200.
4. **PUT** a esa URL. Hay que reenviar el recurso:

```json
{"titulo": "Practicar PUT", "detalle": "Reemplazo completo", "estado": "en_progreso", "prioridad": 1}
```

Esperado: 200. Sin `titulo`, 422.

5. **PATCH** con un solo campo: `{"estado": "hecha"}`. Esperado: 200, título anterior intacto.
6. **DELETE**. Esperado: **204** y body vacío. No llames `.json()` sobre esa respuesta.
7. **GET** del mismo id. Esperado: 404.

`estado` solo puede ser `pendiente`, `en_progreso` o `hecha`. `prioridad` va de 1 a 5. `titulo` admite hasta 80 caracteres.

## Aislamiento

Repite el login en otra petición y guarda el segundo token aparte. Con ese token, el GET de la tarea anterior responde 404. El usuario puede ser el mismo, incluida la cuenta `estudiante`. Cada token es una sesión.

## Sin Postman

La sección 06 del cuaderno hace esta secuencia, toma el id de la respuesta y compara dos sesiones. Swagger permite los mismos Try it out si Authorize usa el token de cada sesión por separado.
