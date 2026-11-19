# Operación

La VM se administra por IAP. SSH no está abierto a internet.

```bash
gcloud config set account fastex.999@gmail.com
gcloud config set project drafty-autopilot-fx
gcloud compute ssh estudia-postgres-lab \
  --zone=southamerica-east1-a \
  --tunnel-through-iap
```

En esta máquina Windows, `gcloud compute ssh` intenta usar PuTTY (`plink`) y falla con `unknown option -o`. El túnel IAP sí funciona. Abrirlo y entrar con OpenSSH:

```bash
gcloud compute start-iap-tunnel estudia-postgres-lab 22 \
  --local-host-port=localhost:2222 \
  --zone=southamerica-east1-a \
  --iap-tunnel-disable-connection-check

ssh -i %USERPROFILE%\.ssh\google_compute_engine -p 2222 yulcr@127.0.0.1
```

## Estado

Dentro de la VM:

```bash
sudo estudia-status
sudo systemctl status postgresql --no-pager
sudo systemctl status pgbouncer --no-pager
sudo ss -lnt | grep -E '5432|6432'
uptime
free -h
df -h /
```

`estudia-status` muestra servicios, puertos, CPU, RAM, disco, sesiones de PostgreSQL y `SHOW POOLS` de PgBouncer. 5432 debe aparecer solo en `127.0.0.1`. 6432 debe aparecer en `0.0.0.0`.

Reinicio:

```bash
sudo systemctl restart postgresql
sudo systemctl restart pgbouncer
```

## Secretos

| Qué | Dónde | En Git |
|---|---|---|
| Contraseñas de estudiantes | `/root/estudia-lab/student_credentials.csv` y `clase02/student_credentials.csv` | no |
| Claves de PgBouncer | `/root/estudia-lab/admin.env` y `clase02/.secrets/admin.env` | no |
| Clave privada TLS | `/etc/pgbouncer/tls/` | no |
| CA pública | `clase02/docs/estudia-lab-ca.crt` | sí |

El superusuario `postgres` entra por socket local, sin contraseña:

```bash
sudo -u postgres psql -d retail_dwh
```

## Parar y encender

La VM tiene protección contra borrado. Pararla ahorra el cómputo; la IP estática, mientras no esté asociada a una VM encendida, sí se factura.

```bash
gcloud compute instances stop estudia-postgres-lab --zone=southamerica-east1-a --project=drafty-autopilot-fx
gcloud compute instances start estudia-postgres-lab --zone=southamerica-east1-a --project=drafty-autopilot-fx
```

No hace falta volver a cargar el dataset: PostgreSQL y PgBouncer arrancan con el sistema.

## Volver a aprovisionar

`scripts/bootstrap_vm.sh` se puede ejecutar otra vez como root. Regenera las contraseñas de los estudiantes y reescribe el CSV. La contraseña interna de PgBouncer se conserva si `/root/estudia-lab/admin.env` ya existe.

```bash
sudo bash /opt/estudia-lab/scripts/bootstrap_vm.sh 34.39.202.205
```
