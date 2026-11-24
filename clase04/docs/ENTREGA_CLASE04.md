# Entrega para armar la clase 04

Todo lo que sigue se comprobó el 24 de noviembre de 2026, salvo que una línea diga lo contrario.

## URL

- Base: `https://34.95.210.33.sslip.io`
- API: `https://34.95.210.33.sslip.io/api/v4`
- Swagger: `https://34.95.210.33.sslip.io/api/v4/docs`
- OpenAPI: `https://34.95.210.33.sslip.io/api/v4/openapi.json`
- Salud de esta clase: `GET /api/v4/health` → `{"ok": true, "servicio": "estudia-clase04"}`
- Salud de la clase 03, sin cambios: `GET /health` → `{"ok": true, "servicio": "estudia-clase03"}`

El certificado es de Let's Encrypt, vigente hasta el 17 de febrero de 2027.

## Login en Postman

POST `https://34.95.210.33.sslip.io/api/v4/auth/login`

Body, raw, JSON:

```json
{"username": "estudiante01", "password": "<contraseña de PostgreSQL>"}
```

Respuesta real, con el token sustituido. El usuario de la prueba fue `estudiante46`; la forma es la misma para `estudiante01` y para `estudiante`.

```json
{
  "access_token": "<omitido>",
  "token_type": "bearer",
  "expires_in": 14400,
  "usuario": "estudiante46",
  "scope": "retail:read"
}
```

En Authorization elige Bearer Token y pega el `access_token`. La colección guarda ese valor en la variable `access_token` y no lo imprime.

`GET /api/v4/auth/me` con el usuario compartido real respondió identidad `compartida`. Dos logins seguidos produjeron dos sesiones.

## Ejemplos reales

Path: `GET /api/v4/productos/1` → `Pantalón Modelo 0001`, categoría Ropa.

Query y página, `GET /api/v4/ventas?region=Aragón&page=1&page_size=2`:

```json
{
  "data": [
    {
      "id_transaccion": 1,
      "fecha": "2024-07-11",
      "cantidad": 1,
      "importe_neto": 156.94,
      "categoria": "Electrónica",
      "region": "Aragón"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 2,
    "total_records": 5018,
    "total_pages": 2509,
    "has_next": true
  }
}
```

La respuesta completa de esa página está en `clase04/examples/json/ventas_pagina.json`. La segunda fila es la transacción 11.

JSON anidado, `GET /api/v4/ventas/1`:

```json
{
  "id_transaccion": 1,
  "fecha": "2024-07-11",
  "cantidad": 1,
  "importe_neto": 156.94,
  "descuento_pct": 0.0,
  "canal": "Tienda",
  "metodo_pago": "Tarjeta",
  "producto": {
    "id_producto": 425,
    "nombre": "Smartphone Modelo 0425",
    "categoria": "Electrónica",
    "marca": "BrandA"
  },
  "tienda": {
    "id_tienda": 34,
    "nombre": "RetailCo Zaragoza 04",
    "region": "Aragón",
    "ciudad": "Zaragoza"
  }
}
```

No hay `id_venta`. La clave es `id_transaccion`.

Resumen de las 50.000 ventas: importe neto 67.568.665,1; cantidad 249.600; ticket promedio 1.351,37; fechas del 2022-01-01 al 2024-12-30.

## Métodos HTTP

| Método | Dónde | Código comprobado |
|---|---|---|
| GET | `/api/v4/productos` | 200 |
| POST | `/api/v4/auth/login` | 200 |
| POST | `/api/v4/sandbox/tareas` | 201 |
| PUT | `/api/v4/sandbox/tareas/{id}` | 200 |
| PATCH | `/api/v4/sandbox/tareas/{id}` | 200 |
| DELETE | `/api/v4/sandbox/tareas/{id}` | 204 |

## Códigos comprobados

| Código | Cómo se obtuvo |
|---|---|
| 200 | GET de productos, ventas y salud |
| 201 | POST del sandbox |
| 204 | DELETE del sandbox |
| 400 | `fecha_desde` posterior a `fecha_hasta` |
| 401 | Sin token, token ilegible o contraseña incorrecta |
| 403 | `GET /api/v4/ejemplos/prohibido` |
| 404 | Producto 999999, o tarea de otra sesión |
| 405 | `POST /api/v4/ventas` |
| 422 | `page_size=0` |
| 429 | `GET /api/v4/ejemplos/demasiado-rapido`, header `Retry-After: 2` |
| 500 | `GET /api/v4/ejemplos/error-interno` |
| 503 | `GET /api/v4/ejemplos/no-disponible` |

422 es la validación de FastAPI. 400 es una petición bien formada que no tiene sentido, como un rango de fechas al revés.

## Python que hay que mostrar

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

El notebook tiene 30 celdas y `nbclient` las ejecutó todas contra la API. No se abrió Colab en el navegador.

## Arquitectura

```text
Postman / Colab
  → HTTPS 34.95.210.33.sslip.io
  → Caddy
  → contenedor clase04 (1 CPU, 256 MB, un worker)
  → PgBouncer 10.20.0.2:6432
  → vistas curso de retail_dwh
```

La cuenta `clase04_lectura` solo puede leer productos, tiendas, fechas y ventas. No lee clientes.

## Carga

Dos pasadas de 10 minutos con 45 usuarios y cero fallos. La que vale para la clase es la de 1 CPU.

Con cuentas distintas, 11.753 peticiones y 19,6 por segundo: login p95 770 ms, muestra p95 1.600 ms, productos p95 2.500 ms, ventas p95 2.700 ms. Con 45 sesiones de la misma cuenta sintética, productos p95 2.600 ms y cero fallos.

El p95 de los GET sencillos de listado quedó por encima de dos segundos. La muestra y el login sí entran. El detalle está en `clase04/docs/RESULTADOS_PRUEBAS.md`.

## Encendido y apagado

```powershell
./clase04/infra/start.ps1
./clase04/infra/status.ps1
./clase04/infra/stop.ps1
```

Eso no apaga PostgreSQL ni Airflow. El tope de 40.000 COP del proyecto sigue pudiendo detener las dos VM. El disco y la IP se cobran igual.

## Rutas de los materiales

- `clase04/README.md`
- `clase04/docs/GUIA_ESTUDIANTE.md`
- `clase04/docs/GUIA_DOCENTE.md`
- `clase04/docs/API_REFERENCE.md`
- `clase04/docs/ARQUITECTURA.md`
- `clase04/docs/SEGURIDAD.md`
- `clase04/docs/RESULTADOS_PRUEBAS.md`
- `clase04/postman/EstudIA_Clase04.postman_collection.json`
- `clase04/postman/EstudIA_Clase04.postman_environment.json`
- `clase04/notebooks/EstudIA_Clase04_APIs_REST_Postman.ipynb`
- `clase04/examples/json/`
- `clase04/examples/python/extraer_ventas.py`
- `clase04/examples/airflow/estudia_clase04_demo_api.py`

## Limitaciones

- El DAG de ejemplo no está cargado en Airflow.
- Newman no se ejecutó. La colección se generó y las mismas llamadas se comprobaron con scripts.
- El sandbox se pierde si el contenedor reinicia. Hay un solo worker.
- Google Colab no se abrió en el navegador.
- No hay capturas de Postman ni de Swagger.

## Secuencia de 180 minutos

Está en `clase04/docs/GUIA_DOCENTE.md`.
