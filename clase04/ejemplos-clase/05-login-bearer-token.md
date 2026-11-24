# 5. Login y Bearer token

Objetivo: entrar con el usuario de PostgreSQL y usar el token sin mostrarlo.

## Postman

Método **POST**. URL:

`https://34.95.210.33.sslip.io/api/v4/auth/login`

**Authorization:** No Auth.

**Body → raw → JSON:**

```json
{"username": "estudiante", "password": "<contraseña de PostgreSQL>"}
```

También vale `estudianteNN`. No uses la cuenta de otra persona.

**Send.** Esperado, con el token omitido:

```json
{
  "access_token": "<omitido>",
  "token_type": "bearer",
  "expires_in": 14400,
  "usuario": "estudiante",
  "scope": "retail:read"
}
```

Ese token es un JWT firmado en HS256. Trae emisor, audiencia, expiración, alcance y un identificador de sesión. No trae la contraseña.

Luego **GET** `https://34.95.210.33.sslip.io/api/v4/auth/me`.

**Authorization → Bearer Token.** Pega solo el token.

Esperado: 200, el mismo usuario, `scope` retail:read e `identidad` `compartida` o `individual`.

## Qué decir

«Autenticación es quién eres. Autorización es el alcance `retail:read`: puedes leer, no publicar DAGs ni escribir ventas. Una API key sería una clave fija de la aplicación. OAuth 2.0 es otro marco de tokens y consentimientos. Aquí el propio login entrega el JWT. HTTPS protege la contraseña en el camino. Esta sesión no es una conexión abierta a PostgreSQL.»

El usuario `estudiante` admite varias sesiones a la vez. Un login nuevo no cierra el de al lado.

## Swagger

Ejecuta el POST, copia el token, pulsa **Authorize** y cierra el cuadro. Prueba `/auth/me`.

## Colab

Sección 03. `input` y `getpass`. La celda imprime usuario, tipo, segundos, alcance y el resultado de `/auth/me`. No imprime el token.

## Si falla

401: credencial incorrecta. 422: el cuerpo no cumple `LoginBody`. No reintentes el login en un bucle.
