# Guía del estudiante

Vas a consumir una API. No vas a programarla ni a cambiar las ventas.

## Postman, a mano

1. Crea una petición POST.
2. La URL es `https://34.95.210.33.sslip.io/api/v4/auth/login`.
3. En Body, elige raw y JSON:

```json
{"username": "estudiante01", "password": "tu contraseña de PostgreSQL"}
```

4. Envíala. El código debe ser 200. En la respuesta hay `access_token`, `token_type` igual a `bearer` y `expires_in` igual a 14400.
5. Copia el token. En la siguiente petición abre Authorization, elige Bearer Token y pégalo. No lo pongas en la URL.
6. Crea un GET a `https://34.95.210.33.sslip.io/api/v4/productos?page=1&page_size=20`.
7. Cambia el path a `/api/v4/productos/1` para pedir un producto concreto.
8. Prueba `/api/v4/ventas?region=Andalucía&categoria=Electrónica&page=1&page_size=20`.
9. Quita el token y vuelve a pedir productos. Tiene que responder 401.

En el entorno de Postman marca `password` y `access_token` como secretos. No exportes el entorno con esos valores y no lo subas al repositorio. Si usas la colección, el test del login guarda el token en la variable `access_token` y no lo escribe en la consola.

La colección está en `clase04/postman/EstudIA_Clase04.postman_collection.json`. El entorno, sin contraseña, está al lado. Importar la colección no reemplaza el paso anterior: primero tienes que haber visto el body, el header y el código.

## Python

```python
response = requests.get(
    url,
    headers={"Authorization": f"Bearer {token}"},
    params={"page": 1, "page_size": 20},
    timeout=15,
)
response.raise_for_status()
datos = response.json()
```

`timeout` corta la espera. `raise_for_status` no deja seguir si el código es de error. `params` arma la query string. El token va en el header, nunca en un print.

Si el código es 429, lee `Retry-After`, espera esos segundos y reintenta solo un GET. No reintentes POST, PUT, PATCH ni DELETE.

Para la práctica usa `/api/v4/ventas/muestra?limite=200`. No bajes las 50.000 ventas.

El notebook está en `clase04/notebooks/EstudIA_Clase04_APIs_REST_Postman.ipynb`. Si la API no responde, los JSON de `clase04/examples/json/` permiten seguir con datos guardados. Dilo: no son una consulta en vivo.
