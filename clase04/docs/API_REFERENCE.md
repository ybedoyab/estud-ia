# Referencia de la API

Base: `https://34.95.210.33.sslip.io`

Contrato OpenAPI: `https://34.95.210.33.sslip.io/api/v4/openapi.json`

Documentación interactiva: `https://34.95.210.33.sslip.io/api/v4/docs`

No existe `id_venta`. La clave real de cada fila es `id_transaccion`.

## Públicos

| Método | Ruta | Resultado |
|---|---|---|
| GET | `/api/v4/health` | `{"ok": true, "servicio": "estudia-clase04"}` |
| GET | `/api/v4/docs` | Swagger de esta API |
| GET | `/api/v4/openapi.json` | Contrato OpenAPI |
| GET | `/health` | Sigue siendo la clase 03 |

## Sesión

`POST /api/v4/auth/login`

```json
{"username": "estudiante01", "password": "<la de PostgreSQL>"}
```

```json
{
  "access_token": "<no se publica>",
  "token_type": "bearer",
  "expires_in": 14400,
  "usuario": "estudiante46",
  "scope": "retail:read"
}
```

El ejemplo de usuario de arriba es la forma. En la prueba real el usuario fue `estudiante46` y `expires_in` fue 14400. El token no se copia en este documento.

`GET /api/v4/auth/me` devuelve usuario, alcance, `sesion` (el `jti`) e `identidad`: `individual` o `compartida`.

## Lectura

Todas piden `Authorization: Bearer <token>`.

| Método | Ruta | Notas |
|---|---|---|
| GET | `/api/v4/productos` | `categoria`, `q`, `page`, `page_size` hasta 100 |
| GET | `/api/v4/productos/{id_producto}` | 404 si no existe |
| GET | `/api/v4/categorias` | Cinco categorías reales |
| GET | `/api/v4/tiendas` | `region`, paginación |
| GET | `/api/v4/tiendas/{id_tienda}` | |
| GET | `/api/v4/ventas` | Filtros y orden |
| GET | `/api/v4/ventas/{id_transaccion}` | JSON anidado |
| GET | `/api/v4/ventas/muestra?limite=200` | Entre 100 y 300 filas, orden fijo |
| GET | `/api/v4/indicadores/resumen` | |
| GET | `/api/v4/indicadores/ventas-por-categoria` | |
| GET | `/api/v4/indicadores/ventas-por-region` | |
| GET | `/api/v4/indicadores/ventas-por-periodo?granularidad=mes` | También `trimestre` |

Filtros de ventas: `region`, `categoria`, `canal`, `metodo_pago`, `fecha_desde`, `fecha_hasta`, `id_producto`, `id_tienda`.

Orden permitido: `id_transaccion`, `fecha`, `importe_neto`, `cantidad`. Dirección `asc` o `desc`. El desempate siempre es `id_transaccion`.

`fecha_desde` posterior a `fecha_hasta` responde 400. Un `page_size` de 0 o un orden desconocido responde 422: FastAPI rechaza el tipo antes de consultar.

## Sandbox

`/api/v4/sandbox/tareas` acepta GET, POST (201), PUT, PATCH y DELETE (204). Los objetos pertenecen a la sesión del token, no al usuario. No se escriben en PostgreSQL.

## Errores de práctica

Estas rutas no tocan la base. Exigen token.

| Ruta | Código |
|---|---|
| `/api/v4/ejemplos/prohibido` | 403 |
| `/api/v4/ejemplos/demasiado-rapido` | 429 y `Retry-After: 2` |
| `/api/v4/ejemplos/error-interno` | 500 |
| `/api/v4/ejemplos/no-disponible` | 503 |

`POST /api/v4/ventas` responde 405. La API no tiene un cuerpo SQL.
