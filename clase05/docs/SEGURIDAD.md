# Seguridad

Hay cuatro identidades distintas:

| Quién | Dónde | Para qué |
|---|---|---|
| `admin` / `estudia-local` | Airflow en 127.0.0.1 | Abrir la interfaz local |
| `estudiante` o `estudianteNN` | Connection `estudia_api` | Login de la API de la clase 04 |
| `airflow` / `estudia_meta_local` | PostgreSQL de Compose, sin puerto | Metadatos de Airflow |
| Dataset del curso | GCP, ya existente | Lectura. Esta clase no cambia permisos |

La Connection guarda usuario y contraseña cifrados con `FERNET_KEY`, que `preparar` escribe en `.env` y no se versiona. El mismo archivo guarda `JWT_SECRET`, la clave con la que el scheduler habla con el API server. Sin esa clave compartida las tareas fallan antes de ejecutar el Python. El archivo `config/simple_auth_passwords.json` tampoco. Airflow 3.4 abre ese archivo en modo de escritura, así que el volumen no puede ser de solo lectura. Sigue estando solo en el portátil.

Cada corrida pide un token con POST y lo descarta al terminar la extracción. No se imprime, no va en XCom y no se escribe en bronze. Un fallo de login registra el código HTTP, no el cuerpo.

La interfaz no escucha en `0.0.0.0`. Los contenedores no son privilegiados y no montan el socket de Docker.

El DAG de fallo lee `fixtures/validacion_falla.json`. No altera la API ni las ventas.

No actives la misma programación en todos los portátiles: serían decenas de extracciones iguales contra una API compartida.
