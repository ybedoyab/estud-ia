# Guía del docente

Proyecta el notebook del estudiante y dicta desde esta guía. La API ya está desplegada. Swagger sirve para mostrar el contrato, no para reemplazar Postman.

## Antes de entrar

1. `./clase04/infra/status.ps1`
2. Si el contenedor está parado, `./clase04/infra/start.ps1`.
3. PostgreSQL tiene que estar encendido. Sin esa VM la API responde 503 en `/api/v4/health`.
4. Abre `https://34.95.210.33.sslip.io/api/v4/docs` y `https://34.95.210.33.sslip.io/health`. La segunda debe seguir diciendo `estudia-clase03`.

No leas contraseñas en voz alta y no dejes un token en una diapositiva. El usuario compartido `estudiante` entra a esta API y sigue sin poder publicar DAG.

## Secuencia de 180 minutos

| Minuto | Qué hacer |
|---|---|
| 0–15 | Cliente, servidor, URL, método y código. Un GET a JSONPlaceholder. |
| 15–35 | Postman a mano: login, body JSON, copiar el token a Bearer. |
| 35–55 | GET de productos y un producto por path. Mostrar 404 con un id inexistente. |
| 55–75 | Query: región Andalucía y categoría Electrónica. Nombrar los filtros que sí existen. |
| 75–95 | Dos páginas. Mostrar `total_records`, `has_next` y que el orden por `id_transaccion` no repite filas. |
| 95–110 | `page_size=0` es 422. Fechas cruzadas son 400. Sin token es 401. |
| 110–125 | 403, 429, 500 y 503 con las rutas `/api/v4/ejemplos/`. Leer `Retry-After`. No saturar el servidor. |
| 125–145 | `GET /api/v4/ventas/1` y comparar `DataFrame` con `json_normalize`. |
| 145–165 | Muestra de 200, indicador por categoría, gráfico y guardado de JSON y CSV. |
| 165–175 | POST, PUT, PATCH y DELETE solo en `/api/v4/sandbox/tareas`. POST a `/api/v4/ventas` da 405. |
| 175–180 | El dibujo del DAG `extraer_api → guardar_raw → normalizar → validar → generar_reporte`. No se ejecuta en el servidor. |

## Qué no prometer

- El token de esta clase no publica DAG ni entra al admin de Airflow.
- Dos alumnos con `estudiante` no ven las tareas de sandbox del otro.
- El reporte de facturación puede apagar las VM un poco después de 40.000 COP. El disco y la IP se siguen cobrando.
