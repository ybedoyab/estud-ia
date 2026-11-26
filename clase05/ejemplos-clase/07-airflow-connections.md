# Connection `estudia_api`

En Admin, Connections, con Airflow 3.4 y tipo HTTP:

| Campo | Valor |
|---|---|
| Connection Id | `estudia_api` |
| Connection Type | HTTP |
| Host | `34.95.210.33.sslip.io` |
| Schema | `https` |
| Login | usuario PostgreSQL |
| Password | contraseña de ese usuario |
| Port | vacío |

El código acepta también un host que ya traiga `https://`.

No pongas el token en la Connection. La tarea hace POST `/api/v4/auth/login`, usa el Bearer y olvida el token.

La contraseña queda cifrada con la Fernet de `.env`. No la copies al DAG ni a un log.
