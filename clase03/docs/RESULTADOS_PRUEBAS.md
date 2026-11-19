# Resultados de las pruebas — 19 de noviembre de 2026

Medidas sobre el entorno desplegado. No son simulaciones.

## Servicios

| Comprobación | Resultado |
|---|---|
| `GET https://34.95.210.33.sslip.io/health` | `{"ok": true, "servicio": "estudia-clase03"}` |
| `https://airflow.34.95.210.33.sslip.io` | HTTP 200, certificado de Let's Encrypt |
| Login del docente en la API de Airflow | HTTP 200, sin mostrar la contraseña |
| PostgreSQL educativo | `curso.ventas` sigue en 50 000 filas |
| DAG docente `estudia_clase03_demo` | activo |
| DAG de prueba `estudiante80`–`estudiante99` | pausados después de la carga |

## Notebook

El archivo se ejecutó con nbclient y el kernel local `estudia-clase03`, usando la cuenta de prueba `estudiante90`. No se abrió la interfaz web de Google Colab: no hay sesión de Drive autenticada en esta máquina, y no se inventó un enlace.

Salida real de la celda final:

```text
Estudiante: estudiante90
SQL: OK
Pandas: OK
Pipeline: OK
DAG publicado: estudia_estudiante90_pipeline
Ejecucion: success
Programacion: cada 10 minutos
Reporte: disponible
```

La contraseña no apareció en el notebook ni en la salida.

## Ejecuciones

| DAG | Corrida | Estado |
|---|---|---|
| `estudia_estudiante90_pipeline` | `scheduled__2026-11-19T21:50:00+00:00` | success |
| `estudia_estudiante90_pipeline` | `manual__2026-11-19T21:56:52.452204+00:00` | success |
| `estudia_clase03_demo` | `scheduled__2026-11-19T21:50:00+00:00` | success |
| `estudia_clase03_demo` | `manual__2026-11-19T22:03:44.248528+00:00` | failed, con el texto de demostración |
| `estudia_clase03_demo` | `manual__2026-11-19T22:05:13.090599+00:00` | success, después de volver la variable a `0` |

El CSV del docente quedó en `/opt/airflow/reportes/docente/reporte_ventas.csv` (6 líneas). El de la prueba, en el directorio de `estudiante90`, con la columna `estudiante` igual a `estudiante90`.

## Autenticación

PASS. Contraseña incorrecta 401. Usuario `estudiante` 403. Login individual 200. Sin token 401. Token vencido 401. El noveno intento fallido, hecho desde la VM para no bloquear la red del docente, devolvió 429.

## Seguridad

PASS.

- El token de `estudiante90` ve `estudia_estudiante90_pipeline`. El de `estudiante91` ve el suyo.
- El reporte de A contiene `estudiante90` y no `estudiante91`.
- Python arbitrario, `DELETE` y una consulta de más de 4 000 caracteres: 422.
- Una entrega inválida no borró el DAG ya publicado.
- `airflow_lectura` no puede crear tablas: transacción de solo lectura.
- `SELECT pg_sleep(20)` se canceló a los 15 segundos (`57014`).
- La contraseña de prueba no aparece en los logs de FastAPI.

## Carga

PASS. 20 publicaciones (`estudiante80`–`estudiante99`) en 63,2 segundos, las cuatro a la vez. Las 20 ejecuciones pedidas después terminaron en success.

Memoria de la VM en ese momento: 1 985 MB usados de 7 934, 5 948 MB disponibles. El scheduler quedó cerca de 586 MB. No hubo caída ni agotamiento de memoria.

Esas 20 cuentas quedan pausadas para no ocupar el pool `clase03` durante la clase. Las cuentas `estudiante01`–`estudiante45` no se usaron y no se les cambió la contraseña.

## Lo que no se probó en un navegador

La pantalla de Colab. El cuaderno sí recorrió el mismo código que esa pantalla va a ejecutar: SQL, Pandas, `publicar()` y la consulta del estado real.
