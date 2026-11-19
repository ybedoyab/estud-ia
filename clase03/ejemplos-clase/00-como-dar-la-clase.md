# Cómo dar la clase 03

Tres horas. El cuaderno es `clase03/notebooks/EstudIA_Clase03_SQL_Pandas_Airflow.ipynb`. Súbelo a Colab o ábrelo si ya está en Drive, y pide a cada estudiante: **Archivo → Guardar una copia en Drive**.

Proyecta también Airflow en `https://airflow.34.95.210.33.sslip.io`. El usuario docente y su contraseña están solo en la VM, en `/root/estudia-clase03/secrets.env`, campo `AIRFLOW_ADMIN_PASSWORD`. No la pongas en una diapositiva.

## 18:00 — SQL

Di: «Hoy el resultado no se queda en la pantalla. Va a quedar programado».

Abre la parte 1 del cuaderno. Muestra las dos consultas, pero todavía no las ejecutes: aún no hay conexión. Explica `HAVING` contra `WHERE`, y por qué el `ROW_NUMBER` se filtra en la CTE.

Deja 15 minutos para que relean los JOIN de la clase 02. Si alguien se adelanta, que pase a la parte 2.

## 18:30 — Conexión

Ejecuta la celda de credenciales con tu usuario de prueba, no con el de un estudiante. La contraseña no debe verse: `getpass` la oculta.

La celda siguiente imprime `conexion_ok`. Si falla:

- Contraseña: que vuelva a ejecutar la celda de credenciales.
- TLS: el cuaderno descarga el certificado público solo. Si Colab no llega a la API, revisa que `https://34.95.210.33.sslip.io/health` responda `ok`.
- Base caída: en la otra VM, `sudo systemctl status postgresql pgbouncer`.

Luego ejecuta las dos consultas y enseña la tabla.

## 18:45 — Pandas

Ejecuta `head`, nulos, duplicados y el `groupby` por región. Muestra el gráfico. Di la equivalencia en voz alta: «esto es el GROUP BY que ya escribieron, ahora sobre la tabla que bajaron».

## 19:10 — Descanso

Deja el cuaderno en la parte 4. No publiques todavía.

## 19:20 — ETL

Ejecuta las cuatro funciones. El reporte local debe mostrar categorías y venta neta. Quien termine puede cambiar `categoria` por `canal` y volver a correr la celda.

## 19:55 — El DAG

Di: «si cierro Colab, esto se apaga. Airflow no». Muestra el diagrama que imprime `mostrar_diagrama()`. Recalca que al servidor no viaja código libre: viajan la consulta, la validación y el reporte.

## 20:20 — Publicar

Ejecuta `publicar()`. En el navegador de Airflow debe aparecer `estudia_<usuario>_pipeline` en estado activo. Si tarda, espera un minuto y vuelve a publicar: la API no da por publicado un DAG que Airflow no ha reconocido.

## 20:40 — Reloj y errores

En Airflow abre el DAG docente `estudia_clase03_demo`. Corre cada 5 minutos.

Para mostrar un fallo sin tocar la base:

```bash
cd /opt/estudia-clase03/airflow
sudo docker compose exec airflow-apiserver airflow variables set estudia_demo_forzar_error 1
```

La siguiente corrida falla en `validar` con el mensaje de demostración. Enseña el log. Luego:

```bash
sudo docker compose exec airflow-apiserver airflow variables set estudia_demo_forzar_error 0
```

La corrida siguiente vuelve a terminar bien.

## 20:55 — Cierre

Cada estudiante ejecuta la celda final. Solo marca OK lo que la API confirma. A las 21:00 la VM pausa los DAG de estudiantes. Las tareas que ya empezaron terminan. La infraestructura sigue encendida hasta que tú la detengas con `clase03/infra/stop.sh`.

## Si alguien no entra

- Usuario `estudiante` a secas: no sirve para publicar. Necesita `estudianteNN`.
- Colab reinició: hay que volver a ejecutar desde la celda de credenciales. El token dura 4 horas, pero la memoria de la sesión se pierde.
- Publicó algo inválido: el mensaje llega en español a la celda y no borra los DAG de los demás.
- Airflow tarda en ver el archivo: la API espera hasta unos 90 segundos. Si se rinde, que publique otra vez.
