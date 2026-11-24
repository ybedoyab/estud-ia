# Guía del docente

El guion de las tres horas está en `clase04/ejemplos-clase/00-como-dar-la-clase.md`. Síguelo de 18:00 a 21:00, con la pausa de las 19:05 a las 19:15. Esta página no propone otro orden.

El cuaderno único es `clase04/notebooks/EstudIA_Clase04_APIs_REST_Postman.ipynb`. Súbelo a Drive. Los estudiantes guardan una copia y ejecutan hacia abajo.

## Tres caminos, los mismos recursos

- Postman, construyendo cada petición. La colección se importa al final.
- Swagger: `https://34.95.210.33.sslip.io/api/v4/docs`. El botón Authorize pide el token del login.
- Colab, para quien no pueda instalar nada. Cubre login, métodos, filtros, sandbox, páginas, errores y Pandas.

## Antes de entrar

1. `GET https://34.95.210.33.sslip.io/api/v4/health` debe decir `estudia-clase04`.
2. `GET https://34.95.210.33.sslip.io/health` debe seguir diciendo `estudia-clase03`.
3. Si el contenedor está parado, `./clase04/infra/start.ps1`. PostgreSQL tiene que estar encendido: sin esa VM, health responde 503.
4. Abre Swagger, entra con un usuario de prueba, pulsa Authorize y prueba `GET /api/v4/productos`. No proyectes el token.
5. Deja Postman en una petición en blanco. No importes la colección todavía.

## Orden de la sesión

| Hora | Bloque | Dónde seguir |
|---|---|---|
| 18:00 | A. Qué es una API, REST y SOAP | `01-fundamentos-api-rest-soap.md` |
| 18:25 | B. OpenAPI y Swagger | `02-openapi-swagger-contratos.md` |
| 18:45 | C. Métodos HTTP | `03-metodos-http.md` y `04-postman-configuracion.md` |
| 19:05 | Pausa de diez minutos | |
| 19:15 | D. Login y Bearer | `05-login-bearer-token.md` |
| 19:40 | E. GET, headers y query | `06-params-headers-body.md` |
| 20:05 | E. Sandbox | `07-crud-sandbox.md` |
| 20:25 | F. Páginas, JSON y Pandas | `08-paginacion.md` y `09-json-pandas-colab.md` |
| 20:45 | Errores controlados | `10-errores-http.md` |
| 20:55 | Reto, archivos y Airflow | `11`, `12` y `13` |

## Qué no prometer

- El token no publica DAG ni entra al admin de Airflow.
- Dos personas con `estudiante` no ven el sandbox de la otra. Un login nuevo no cierra la sesión ajena.
- Tres páginas no son las 50.000 ventas.
- El DAG `estudia_clase04_demo_api` no está cargado en el scheduler.
- El tope de 40.000 COP puede detener las VM. El disco y la IP se siguen cobrando.
- Si health falla, no rellenes la clase con datos mudos. El respaldo del cuaderno se activa a propósito y marca cada resultado.
