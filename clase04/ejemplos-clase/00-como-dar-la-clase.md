# Cómo dar la clase 04

Tres horas, de 18:00 a 21:00. El cuaderno único es `clase04/notebooks/EstudIA_Clase04_APIs_REST_Postman.ipynb`. Súbelo a Drive y pide **Archivo → Guardar una copia en Drive**. No hace falta clonar el repositorio.

Hay tres caminos y los tres recorren los mismos recursos:

- Postman, armando cada petición a mano. La colección se importa al final, no al principio.
- Swagger, en el navegador: `https://34.95.210.33.sslip.io/api/v4/docs`.
- Colab, con el cuaderno. Quien no pueda instalar nada hace Swagger más Colab y, si la API no responde, el modo respaldo del propio cuaderno.

La API es `https://34.95.210.33.sslip.io/api/v4`. El contrato es `https://34.95.210.33.sslip.io/api/v4/openapi.json`.

## Antes de las 18:00

Checklist:

- `GET https://34.95.210.33.sslip.io/api/v4/health` devuelve `{"ok": true, "servicio": "estudia-clase04"}`.
- `GET https://34.95.210.33.sslip.io/health` sigue devolviendo `estudia-clase03`.
- Abre Swagger. Pulsa **Authorize**, pega un token de prueba y cierra el cuadro. `GET /api/v4/productos` debe salir 200. Cierra sesión de ese token en tu máquina; no lo proyectes.
- Ten a mano un usuario de prueba, no el de un estudiante. La contraseña no va a la diapositiva ni al chat.
- El usuario compartido de la demo es `estudiante`. Cada login abre una sesión distinta. No invalida a los demás.
- Postman instalado en el proyector. Crea una petición en blanco. No importes todavía la colección.
- Ten el cuaderno abierto en Colab, sin ejecutar el login hasta que llegues a esa sección.
- Si health no responde, no inventes datos. Di que la API no está y, solo entonces, autoriza en el cuaderno `USAR_RESPALDO = True`.

## 18:00 — Fundamentos

Pantalla: el navegador, sin Postman todavía. Escribe en la pizarra o en un documento compartido esta URL y pártela con ellos:

`https://34.95.210.33.sslip.io/api/v4/productos/1`

Di: «Una API es un contrato que permite que dos sistemas intercambien información sin que uno tenga que conocer cómo está programado el otro. El cliente pide. El servidor responde. Nosotros somos el cliente. La API es el servidor. La petición y la respuesta son el viaje.»

Sigue, en este orden:

1. Una base de datos guarda y responde SQL. Una pantalla la usa una persona. La API es la puerta entre programas. Hoy no abrimos PostgreSQL.
2. HTTP es el idioma de la petición. HTTPS es ese idioma dentro de un canal cifrado. Por eso la URL empieza por `https://` y por eso no pegamos la contraseña en un chat.
3. En REST un recurso tiene URL. El método dice qué queremos hacer. Cada petición se explica sola: el servidor no recuerda la anterior. JSON es habitual en REST; REST no obliga a usarlo.
4. SOAP es otro contrato. El mensaje va en un sobre XML y las operaciones se describen en un WSDL. SOAP no exige HTTP: el sobre puede viajar por otro protocolo. No vamos a llamar uno. Solo hay que reconocerlo para no confundirlo con una ruta REST.
5. GraphQL deja elegir la forma de la respuesta. gRPC usa un contrato binario. Hoy no se practican.
6. Un endpoint es un método más una ruta. `GET /api/v4/productos` y `POST /api/v4/auth/login` son endpoints distintos.
7. En la URL, `https` es el esquema, el host es `34.95.210.33.sslip.io`, el path es `/api/v4/productos/1` y lo que iría tras `?` son parámetros de consulta.

Pregunta: «Si les doy la contraseña de PostgreSQL, ¿están hablando con la API o con la base?». Deben responder que la contraseña solo se usa una vez, en el login de la API. Después no viaja SQL.

Sin Postman: escuchan esta explicación y abren el cuaderno en la sección 00. No ejecutan todavía el login.

## 18:25 — El contrato

Pantalla: Swagger, `https://34.95.210.33.sslip.io/api/v4/docs`.

Di: «El contrato dice qué se puede pedir, con qué datos y qué forma tiene la respuesta. OpenAPI es ese documento. Swagger es la página que lo enseña. Postman es el cliente donde vamos a armar las peticiones. No son tres nombres para la misma cosa.»

Haz esto:

1. Abre `GET /api/v4/openapi.json` en otra pestaña solo un segundo. No recorras miles de líneas. Vuelve a Swagger.
2. Despliega `GET /api/v4/productos`. Señala `parameters`, cuáles son opcionales y la respuesta 200.
3. Despliega `POST /api/v4/auth/login`. El cuerpo apunta a `LoginBody`. `username` y `password` son requeridos.
4. Menciona que un esquema describe tipos y campos obligatorios. Eso es JSON Schema dentro de OpenAPI.
5. Aún no pulses Authorize. El token llega en el bloque de autenticación.

Pregunta: «¿Qué campo del login puedo omitir?». Ninguno. `region`, en cambio, sí se puede omitir al listar ventas.

Si Swagger no carga, usa el cuaderno, sección 02: lee el mismo `openapi.json` y lista rutas sin imprimirlo entero.

Sin Postman: se quedan en Swagger. En Colab ejecutan hasta la sección 02.

## 18:45 — Los métodos, todavía en la pizarra

Di, antes de tocar Postman: «GET pide. POST crea o arranca una acción. PUT reemplaza el recurso entero. PATCH cambia solo lo que envías. DELETE elimina. HEAD pide encabezados sin cuerpo. OPTIONS pregunta qué métodos admite la URL. GET es segura: no debería modificar. PUT y DELETE son idempotentes: repetirlas deja el mismo resultado. POST no lo es.»

Escribe la diferencia en una frase: «PUT manda la tarea completa. PATCH manda un solo campo.»

Códigos, en tres familias: 2xx salió bien, 4xx la petición no se acepta, 5xx falló el servidor. No provoques un 500 real. Los 500 y 503 de esta clase son rutas de ejemplo.

## 18:50 — La primera petición, a mano

Pantalla: Postman, petición nueva. No abras la colección.

1. Método **GET**.
2. URL: `https://jsonplaceholder.typicode.com/posts/1`.
3. No hay headers, ni params, ni body.
4. Pestaña **Params** vacía. Pestaña **Body** en none.
5. Pulsa **Send**.
6. Esperado: Status **200**. Mira Time, Size y el JSON del body. Señala `Content-Type: application/json`.

Pregunta: «¿Esto es la base de EstudIA?». No. Es otra API, para ver el viaje.

Repite el gesto con la nuestra, todavía sin token:

1. GET `https://34.95.210.33.sslip.io/api/v4/health`.
2. Send.
3. Esperado: 200 y `{"ok": true, "servicio": "estudia-clase04"}`.

Si sale un error de conexión, para la clase y revisa health antes de seguir. No pases a los filtros.

Sin Postman: en Swagger, `GET /api/v4/health`, **Try it out**, **Execute**. En Colab, la sección 01 hace la llamada pública y muestra texto, JSON y DataFrame.

## 19:05 — Pausa

Diez minutos. Deja health en la pantalla. No pidas todavía el login.

## 19:15 — Login a mano

Pantalla: Postman, petición nueva.

Di: «Autenticación es demostrar quién eres. Autorización es lo que esa identidad puede hacer. Vamos a comprobar usuario y contraseña. La API devuelve un token de acceso. Ese token es un JWT firmado, de tipo Bearer, con alcance `retail:read` y cuatro horas de vida. No es una conexión a PostgreSQL. La API lee la base con otra cuenta, de solo lectura, y tú no envías SQL.»

1. Método **POST**.
2. URL: `https://34.95.210.33.sslip.io/api/v4/auth/login`.
3. Pestaña **Body** → **raw** → **JSON**.
4. Escribe, con tu usuario de prueba:

```json
{"username": "estudiante", "password": "la contraseña de PostgreSQL"}
```

5. Pestaña **Authorization**: **No Auth**. El login no lleva token.
6. Header `Content-Type: application/json`. Postman lo pone al elegir JSON.
7. **Send**.
8. Esperado: Status **200**. En el body: `token_type` bearer, `expires_in` 14400, `scope` retail:read y `usuario`. Hay un `access_token`.
9. Copia el token desde el body. No lo leas en voz alta, no lo pegues en el chat y no lo dejes en una captura.
10. Nueva petición GET `https://34.95.210.33.sslip.io/api/v4/auth/me`.
11. Pestaña **Authorization** → **Bearer Token**. Pega el token en el campo Token. No escribas la palabra Bearer.
12. **Send**. Esperado: 200, el mismo usuario, `identidad` `compartida` si usaste `estudiante`, e `individual` si usaste `estudianteNN`.

Pregunta: «¿Dos personas con el usuario `estudiante` se pisan?». No. Cada login crea su propia sesión.

Si responde 401: usuario o contraseña mal. Si responde 422: el JSON no tiene los dos campos o no elegiste raw JSON. Si el token se pegó con comillas o con la palabra Bearer, `/auth/me` da 401: bórralo y pega solo el valor.

Sin Postman: en Swagger ejecuta el POST de login, copia el token, pulsa **Authorize**, pégalo y cierra. Luego ejecuta `GET /api/v4/auth/me`. En Colab, sección 03, con `getpass`. El cuaderno no imprime el token.

## 19:40 — GET, path, query y headers

Sigue en la misma petición autenticada de Postman. El token ya está en Authorization.

1. GET `https://34.95.210.33.sslip.io/api/v4/productos`.
2. Pestaña **Params**: `page` = `1`, `page_size` = `5`.
3. **Send**. Esperado: 200, `data` y `pagination`.
4. Cambia la URL a `https://34.95.210.33.sslip.io/api/v4/productos/1`. Quita los params. **Send**. Esperado: 200, Pantalón Modelo 0001, categoría Ropa.
5. Pregunta a un estudiante otro id. Escríbelo en el path, no en el body.
6. Nueva URL: `https://34.95.210.33.sslip.io/api/v4/ventas`.
7. **Params**: `region` = `Aragón`, `categoria` = `Hogar`, `fecha_desde` = `2024-01-01`, `fecha_hasta` = `2024-12-30`, `page` = `1`, `page_size` = `2`.
8. **Send**. Esperado: 200, `total_records` mayor que cero, `has_next` true si hay más de dos, y filas con `id_transaccion`.

Di la diferencia en voz alta: «`/productos/1` nombra un recurso. `?region=Aragón&page=1` filtra un listado. El header Authorization no se muestra en el proyector: solo decimos que va como Bearer y que el valor está oculto.»

Si 401: el token no está en Authorization. Si 422: `page_size` no es un entero entre 1 y 100. Si la región vuelve vacía, revisa la tilde de Aragón.

Sin Postman: los mismos clics en Swagger, con Authorize ya hecho. En Colab, secciones 04 y 05.

## 20:05 — El sandbox

Di: «Las ventas no se crean ni se borran. POST, PUT, PATCH y DELETE se practican en tareas ficticias. Esa memoria es de la sesión, no de PostgreSQL, y se pierde cuando expira el token.»

En Postman, con el mismo Bearer:

1. GET `https://34.95.210.33.sslip.io/api/v4/sandbox/tareas`. Esperado: 200 y `data`.
2. POST a la misma URL. **Body → raw → JSON**:

```json
{"titulo": "Practicar POST", "detalle": "Tarea ficticia de la sesion", "estado": "pendiente", "prioridad": 2}
```

3. **Send**. Esperado: **201** y un `id_tarea`. Cópialo. No inventes uno.
4. GET `https://34.95.210.33.sslip.io/api/v4/sandbox/tareas/` más ese id. Esperado: 200.
5. PUT a esa URL. Body completo:

```json
{"titulo": "Practicar PUT", "detalle": "Reemplazo completo", "estado": "en_progreso", "prioridad": 1}
```

6. Esperado: 200 y el título nuevo. PUT sin `titulo` responde 422.
7. PATCH a la misma URL. Body: `{"estado": "hecha"}`. Esperado: 200, estado `hecha`, título intacto.
8. DELETE a la misma URL. Esperado: **204**, body vacío. No busques JSON.
9. GET otra vez. Esperado: 404.

Para el aislamiento, haz un segundo POST de login en otra pestaña, con el mismo usuario. No reemplaces el primer token. Con el segundo token, el GET de la tarea del primero da 404. Pregunta: «¿Por qué, si el usuario es el mismo?». Porque cada token es una sesión.

Sin Postman: la misma secuencia en Swagger. En Colab, la sección 06 crea el id, no lo hardcodea, y no interpreta el 204 como JSON.

## 20:25 — Páginas, JSON y Pandas

Postman, una sola página, para ver el sobre:

GET `https://34.95.210.33.sslip.io/api/v4/ventas` con Params `region=Aragón`, `page=1`, `page_size=50`.

Di: «`total_records` y `total_pages` dicen cuánto hay. `has_next` dice si esta página no es la última. Pedir tres páginas no es bajarse las 50.000. Aunque los id salgan seguidos, la extracción sigue siendo parcial.»

Luego GET `https://34.95.210.33.sslip.io/api/v4/ventas/1`. Señala los objetos `producto` y `tienda`, y el campo `id_transaccion`. No existe `id_venta`.

A partir de aquí el análisis es de Colab, secciones 07 a 09. Proyecta el cuaderno:

- tres páginas, no más;
- `json_normalize` frente a un DataFrame que deja los diccionarios dentro;
- muestra de 200 con `limite=200`;
- media de la muestra y ticket promedio global en dos frases distintas. No son la misma población.

Sin Postman: Swagger muestra una página y la venta 1. El recorrido de páginas, la tabla y el gráfico se hacen en Colab.

## 20:45 — Errores, sin derribar nada

Una petición por código. No pulses Send en bucle.

| Qué enviar | Esperado |
| --- | --- |
| GET `/api/v4/health` | 200 |
| POST del sandbox | 201 |
| DELETE de esa tarea | 204 |
| GET `/api/v4/ventas?fecha_desde=2024-12-30&fecha_hasta=2024-01-01` | 400 |
| GET `/api/v4/productos` con Authorization en No Auth | 401 |
| GET `/api/v4/ejemplos/prohibido` | 403 |
| GET `/api/v4/productos/999999` | 404 |
| POST `/api/v4/ventas` con un JSON cualquiera | 405 |
| GET `/api/v4/ventas?page_size=0` | 422 |
| GET `/api/v4/ejemplos/demasiado-rapido` | 429 y header `Retry-After` |
| GET `/api/v4/ejemplos/error-interno` | 500 |
| GET `/api/v4/ejemplos/no-disponible` | 503 |

Di: «Un 429 pide esperar. Reintentar tiene sentido en un GET, una o dos veces, mirando `Retry-After`. No se reintenta un POST: podrías crear dos tareas.»

Sin Postman: los mismos Try it out en Swagger. Colab, sección 10, ya los recorre y explica `raise_for_status`, Timeout y ConnectionError.

## 20:55 — Cierre

En Colab, secciones 11 y 12. Cada estudiante deja una muestra de su región, el CSV, el JSON y el gráfico. El resumen final solo puede decir OK en lo que esa ejecución hizo. Si alguien está en respaldo, los OK de la API quedan en NO. Eso es correcto.

Di el puente, sin abrir Airflow: «extraer, guardar el JSON, normalizar, validar y generar el reporte es un pipeline. El DAG de ejemplo del repositorio no está cargado en el scheduler. Nadie tiene que publicarlo hoy.»

Solo ahora, si sobra un minuto, importa `clase04/postman/EstudIA_Clase04.postman_collection.json` y el environment. El environment trae la URL y deja la contraseña vacía. Quien llegue tarde a esa importación no perdió la clase: ya construyó las peticiones.

A las 21:00 cierra. No lances pruebas de carga. No pidas que bajen las 50.000 ventas.
