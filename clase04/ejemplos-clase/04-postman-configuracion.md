# 4. Configurar Postman a mano

Objetivo: construir una petición sin importar nada. La colección llega al cierre.

## Secuencia en la interfaz

1. Abre Postman y pulsa **New → HTTP Request**. No uses Import.
2. El selector de la izquierda dice **GET**. Cámbialo cuando haga falta.
3. Pega la URL en la barra.
4. Para el login, abre **Body → raw** y, a la derecha, elige **JSON**.
5. Escribe el JSON. Postman añade `Content-Type: application/json`.
6. Pulsa **Send**.
7. Arriba de la respuesta lee **Status**, **Time** y **Size**. Abajo está el body.
8. Copia `access_token` desde el body. No lo compartas.
9. En la petición siguiente abre **Authorization → Bearer Token** y pega el valor en **Token**.
10. Los filtros van en la pestaña **Params**, una clave por fila. No los concatenes a mano si puedes evitarlo.
11. El CRUD del sandbox usa la misma autorización y cambia método, URL y body.
12. Un 401, 404 o 422 se lee en Status y en `detail`. No significa que la base se haya caído.

## URLs de esta secuencia

- GET `https://jsonplaceholder.typicode.com/posts/1`
- GET `https://34.95.210.33.sslip.io/api/v4/health`
- POST `https://34.95.210.33.sslip.io/api/v4/auth/login`

El environment y la colección están en `clase04/postman/`. El environment trae la URL y deja `password` y `access_token` vacíos. Importarlos no sustituye este recorrido.

## Si algo sale mal

- 422 en el login: no está en raw JSON, o faltó un campo.
- 401 en `/auth/me`: el token se pegó con comillas o con la palabra Bearer.
- Could not send request: prueba primero `/api/v4/health` en el navegador.

## Si no tienen Postman

No instalen nada a mitad de la clase. Swagger hace Try it out. Colab hace las mismas llamadas. Los JSON de ejemplo van dentro del cuaderno, marcados como respaldo, y no reemplazan una respuesta en vivo.
