# Arquitectura del laboratorio

Los estudiantes se conectan por internet al puerto **6432** de una VM de Compute Engine. PgBouncer termina TLS y abre, solo en localhost, la conexión real contra PostgreSQL. El puerto **5432** no está publicado.

```text
Internet
   |
   | TCP + TLS (sslmode=require)
   v
34.39.202.205  (IP estática, southamerica-east1)
   |
   v
PgBouncer :6432     pool_mode = transaction
   |
   | 127.0.0.1:5432
   v
PostgreSQL 16
   |
   v
retail_dwh
   public.*   tablas del esquema estrella
   curso.*    vistas de solo lectura en español
```

## Por qué esta forma

Hace falta un PostgreSQL educativo accesible por TCP, con los créditos de la cuenta y sin una plataforma de más. No apareció una razón técnica para preferir Cloud SQL: PgBouncer y PostgreSQL conviven en la misma VM y el dataset cabe en memoria. No hay Kubernetes, balanceador ni Spark en ejecución.

La VM es `e2-medium` (2 vCPU, 4 GB) con disco `pd-balanced` de 20 GB. Durante la prueba de 45 clientes el sistema usó unos 675 MB de RAM y quedaron unos 3,2 GB disponibles. El dataset ocupa 18 MB.

La región es `southamerica-east1` (São Paulo), la más cercana para una clase en UTC−5. La VPC `estudia-lab-vpc` es propia del laboratorio, así que no hereda la regla de SSH abierta de la red `default`.

## Pool

PgBouncer agrupa por usuario. Una consulta simultánea de los 45 alumnos puede usar hasta un backend por alumno, pero solo mientras la consulta está activa.

Medido con los 45 clientes todavía conectados:

| Momento | Clientes | Backends activos | Backends ociosos |
|---|---:|---:|---:|
| Justo después de la consulta | 45 | 0 | 45 |
| 12 s después, clientes aún abiertos | 45 | 0 | 0 |
| Después de cerrar los clientes | 0 | 0 | 0 |

`server_idle_timeout` es 10 s. Un alumno conectado y sin una consulta en curso no mantiene un proceso de PostgreSQL.

Límites: `max_client_conn = 120`, `default_pool_size = 2`, `max_user_connections = 2`, `max_db_connections = 60`. Cada rol de estudiante tiene `CONNECTION LIMIT 2`.

El modo transaction no conserva `SET`, tablas temporales ni prepared statements entre sentencias. Las consultas de la clase son una sentencia y funcionan.

## Seguridad de red

| Destino | Origen | Puerto |
|---|---|---|
| `estudia-lab-allow-pgbouncer` | `0.0.0.0/0` | TCP 6432 |
| `estudia-lab-allow-iap-ssh` | `35.235.240.0/20` (IAP) | TCP 22 |

PostgreSQL escucha solo en `127.0.0.1:5432`. Desde esta máquina, el puerto 5432 de la IP pública no acepta conexión. ufw repite la misma política dentro de la VM.

## TLS

PgBouncer exige TLS (`client_tls_sslmode = require`). El certificado está firmado por una CA del laboratorio y el SAN incluye la IP `34.39.202.205`. Con `sslmode=require` el tráfico va cifrado y el cliente no valida la CA. Quien quiera `verify-full` usa `docs/estudia-lab-ca.crt`. La clave privada no sale de la VM.

## Datos y permisos

`public` guarda `dim_date`, `dim_product`, `dim_customer`, `dim_store` y `fact_sales`. `curso` expone vistas no actualizables: `productos`, `clientes`, `tiendas`, `fechas` y `ventas`.

`rol_estudiante` no tiene login. `estudiante01` … `estudiante45` heredan solo `CONNECT` sobre `retail_dwh` y `SELECT` sobre `curso`. No tienen `CREATEDB`, `CREATEROLE`, superuser ni `TEMPORARY`. Un event trigger rechaza DDL hecho por esas cuentas. Además cada sesión de estudiante arranca con `default_transaction_read_only = on`, `statement_timeout = 60s` e `idle_in_transaction_session_timeout = 30s`.
