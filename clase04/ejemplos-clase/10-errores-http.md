# 10. Errores HTTP

Objetivo: reconocer el código y no reintentar una escritura.

Todas las llamadas son únicas y pequeñas. Los 500 y 503 salen de rutas de demostración.

| Código | Petición | Dónde |
| --- | --- | --- |
| 200 | GET `/api/v4/health` | sin token |
| 201 | POST `/api/v4/sandbox/tareas` | Bearer, body con `titulo` |
| 204 | DELETE de esa tarea | body vacío, sin `.json()` |
| 400 | GET `/api/v4/ventas?fecha_desde=2024-12-30&fecha_hasta=2024-01-01` | Bearer |
| 401 | GET `/api/v4/productos` | Authorization: No Auth |
| 403 | GET `/api/v4/ejemplos/prohibido` | Bearer |
| 404 | GET `/api/v4/productos/999999` | Bearer |
| 405 | POST `/api/v4/ventas` | Bearer, cualquier JSON |
| 422 | GET `/api/v4/ventas?page_size=0` | Bearer |
| 429 | GET `/api/v4/ejemplos/demasiado-rapido` | Bearer, header `Retry-After: 2` |
| 500 | GET `/api/v4/ejemplos/error-interno` | Bearer |
| 503 | GET `/api/v4/ejemplos/no-disponible` | Bearer |

## En el cuaderno

`status_code` muestra el número. `raise_for_status()` lanza `HTTPError` en 4xx y 5xx. Un `try/except` deja continuar cuando el error es el ejemplo.

`requests.exceptions.Timeout` corta una espera demasiado corta. `requests.exceptions.ConnectionError` aparece si no hay conexión. El cuaderno provoca la segunda contra un puerto local cerrado, no contra la API.

Un GET de demostración se reintenta como máximo dos veces. POST, PUT, PATCH y DELETE no se reintentan.

## Si un estudiante insiste en el 500

Recuerda que `/api/v4/ejemplos/error-interno` está hecho para devolver 500. No es una caída del servicio. Health sigue en 200.
