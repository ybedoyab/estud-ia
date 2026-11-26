# Guía del docente

El guion de las tres horas está en `clase05/ejemplos-clase/00-como-dar-la-clase.md`. Esta página no cambia ese orden.

## Qué proyectar

- Postman, colección EstudIA Clase 04, petición de ventas.
- Docker Desktop.
- [http://127.0.0.1:8080](http://127.0.0.1:8080) en tu máquina, usuario `admin`.
- Swagger: [https://34.95.210.33.sslip.io/api/v4/docs](https://34.95.210.33.sslip.io/api/v4/docs).
- Colab con `notebooks/EstudIA_Clase05_PRACTICA.ipynb` para quien no tenga Docker.

La solución está en `profesor/estudia_clase05_profesor.py` y en `notebooks/EstudIA_Clase05_PROFESOR.ipynb`. No van en el ZIP.

## Antes de entrar

1. `GET https://34.95.210.33.sslip.io/api/v4/health` debe decir `estudia-clase04`.
2. `GET https://34.95.210.33.sslip.io/health` debe seguir diciendo `estudia-clase03`.
3. Tu Airflow local ya inició y el DAG de práctica aparece en pausa.
4. La Connection `estudia_api` está creada en tu instancia, no en la de los estudiantes.
5. No actives un cron en los 45 equipos. `schedule` se queda en `None`.

## Si Docker no arranca

A las 19:05, quien siga en el instalador pasa a Colab. No esperes al cierre.

## Lo que no está desplegado

El DAG resuelto no se copió a la VM de la clase 03. Esa instancia sigue sirviendo a la clase anterior. La demostración de Airflow de esta sesión es local.

## Horario

| Hora | Bloque |
|---|---|
| 18:00–18:10 | Repaso de API y autenticación en Postman |
| 18:10–18:20 | Docker, imágenes y contenedores |
| 18:20–18:45 | Instalación de Docker |
| 18:45–19:05 | Dockerfile, YAML, Compose y .env |
| 19:05–19:15 | Descanso |
| 19:15–19:30 | Validación, construcción y despliegue |
| 19:30–19:40 | Primer DAG de dos tareas |
| 19:40–19:50 | Connections y autenticación individual |
| 19:50–20:05 | Extracción HTTP y paginación |
| 20:05–20:20 | Bronze, Silver, validación y Gold |
| 20:20–20:35 | Operadores, dependencias y XCom |
| 20:35–20:45 | Ejecutar el DAG y comprobar resultados |
| 20:45–20:55 | Fallos, reintentos y programación |
| 20:55–21:00 | Cierre |

El guion hablado está en `ejemplos-clase/00-como-dar-la-clase.md`. Las respuestas están en `profesor/SOLUCIONARIO.md`.
