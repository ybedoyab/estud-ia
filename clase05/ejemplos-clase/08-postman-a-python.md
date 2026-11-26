# De Postman a Python

1. Abre la colección de la clase 04.
2. Ejecuta el login. No copies el token al cuaderno.
3. Abre `GET /api/v4/ventas` con región, página y `page_size`.
4. Code, Python, Requests.
5. Borra usuario y contraseña fijos.
6. En Airflow salen de `BaseHook.get_connection("estudia_api")`.
7. Añade `timeout=20` al login y `timeout=60` al GET.
8. Si el estado no es 200, lanza un error con el código, sin imprimir el cuerpo del login.
9. Esa función es `extraer_api` dentro del DAG.

Ejemplo de la forma, sin secretos:

```python
respuesta = requests.get(
    base + "/api/v4/ventas",
    headers={"Authorization": "Bearer " + token, "Accept": "application/json"},
    params={"region": "Aragón", "page": 1, "page_size": 100, "orden": "id_transaccion", "direccion": "asc"},
    timeout=60,
)
respuesta.raise_for_status()
```
