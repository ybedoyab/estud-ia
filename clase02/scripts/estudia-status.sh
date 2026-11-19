#!/bin/bash
# Comprobaciones básicas del laboratorio. No imprime secretos.
set -euo pipefail

echo "=== servicios ==="
systemctl is-active postgresql
systemctl is-active pgbouncer

echo "=== escucha ==="
ss -lnt | awk 'NR==1 || /:5432|:6432/'

echo "=== cpu/ram ==="
uptime
free -h

echo "=== disco ==="
df -h / /var/lib/postgresql

echo "=== conexiones postgres ==="
sudo -u postgres psql -d retail_dwh -c \
  "SELECT usename, state, count(*) FROM pg_stat_activity WHERE datname = 'retail_dwh' GROUP BY 1, 2 ORDER BY 1, 2;"

echo "=== pgbouncer pools ==="
ADMIN_ENV="/root/estudia-lab/admin.env"
if [[ -r "$ADMIN_ENV" ]]; then
  ADMIN_PW="$(awk -F= '/^PGBOUNCER_ADMIN_PASSWORD=/{print substr($0, index($0,$2))}' "$ADMIN_ENV")"
  PGPASSWORD="$ADMIN_PW" psql \
    "host=127.0.0.1 port=6432 dbname=pgbouncer user=pgbouncer_admin sslmode=require" \
    -c "SHOW POOLS;" \
    -c "SHOW DATABASES;"
  unset ADMIN_PW
else
  echo "admin.env no legible; se omite SHOW POOLS"
fi
