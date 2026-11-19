#!/bin/bash
# Instala PostgreSQL + PgBouncer TLS y carga el laboratorio. Ejecutar como root.
set -euo pipefail
trap 'echo "bootstrap failed at line $LINENO"' ERR

PUBLIC_IP="${1:?usage: bootstrap_vm.sh PUBLIC_IP}"
LAB="/opt/estudia-lab"
PG_VER=""

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y \
  postgresql \
  postgresql-contrib \
  pgbouncer \
  python3 \
  python3-venv \
  python3-pip \
  python3-psycopg2 \
  openssl \
  git \
  ca-certificates \
  ufw \
  iproute2

PG_VER="$(ls /etc/postgresql | sort -V | tail -n 1)"
install -d -m 755 "/etc/postgresql/${PG_VER}/main/conf.d"

cat > "/etc/postgresql/${PG_VER}/main/conf.d/estudia.conf" <<'EOF'
listen_addresses = 'localhost'
port = 5432
max_connections = 100
superuser_reserved_connections = 5
shared_buffers = 512MB
effective_cache_size = 2GB
work_mem = 8MB
maintenance_work_mem = 256MB
wal_buffers = 16MB
random_page_cost = 1.1
effective_io_concurrency = 200
max_worker_processes = 2
max_parallel_workers_per_gather = 1
max_parallel_workers = 2
password_encryption = 'scram-sha-256'
ssl = off
timezone = 'America/Bogota'
log_timezone = 'America/Bogota'
lc_messages = 'C'
log_connections = on
log_disconnections = on
log_line_prefix = '%m [%p] %q%u@%d '
log_min_duration_statement = 2000
log_statement = 'none'
EOF

cat > "/etc/postgresql/${PG_VER}/main/pg_hba.conf" <<'EOF'
local   all   postgres   peer
local   all   all        peer
host    all   all        127.0.0.1/32   scram-sha-256
host    all   all        ::1/128        scram-sha-256
EOF
chown postgres:postgres "/etc/postgresql/${PG_VER}/main/pg_hba.conf"
chmod 640 "/etc/postgresql/${PG_VER}/main/pg_hba.conf"

systemctl enable postgresql
systemctl restart postgresql

if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='retail_dwh'" | grep -q 1; then
  sudo -u postgres psql -v ON_ERROR_STOP=1 -c \
    "CREATE DATABASE retail_dwh TEMPLATE template0 ENCODING 'UTF8' LC_COLLATE 'C.UTF-8' LC_CTYPE 'C.UTF-8'"
fi
sudo -u postgres psql -d retail_dwh -v ON_ERROR_STOP=1 -c \
  "ALTER DATABASE retail_dwh SET timezone TO 'America/Bogota'"

sudo -u postgres psql -d retail_dwh -v ON_ERROR_STOP=1 -f "$LAB/sql/01_roles.sql"
bash "$LAB/scripts/load_dataset.sh"
sudo -u postgres psql -d retail_dwh -v ON_ERROR_STOP=1 -f "$LAB/sql/03_spanish_views.sql"
sudo -u postgres psql -d retail_dwh -v ON_ERROR_STOP=1 -f "$LAB/sql/04_permissions.sql"

install -d -m 700 /root/estudia-lab
python3 - <<'PY'
import os
import secrets
from pathlib import Path
path = Path("/root/estudia-lab/admin.env")
if not path.exists():
    path.write_text(
        "PGBOUNCER_AUTH_PASSWORD={auth}\nPGBOUNCER_ADMIN_PASSWORD={admin}\n".format(
            auth=secrets.token_urlsafe(24),
            admin=secrets.token_urlsafe(24),
        ),
        encoding="utf-8",
    )
    os.chmod(path, 0o600)
PY
cp /root/estudia-lab/admin.env /var/lib/postgresql/estudia-admin.env
chown postgres:postgres /var/lib/postgresql/estudia-admin.env
chmod 600 /var/lib/postgresql/estudia-admin.env

sudo -u postgres python3 "$LAB/scripts/create_service_roles.py"
sudo -u postgres python3 "$LAB/scripts/create_students.py" \
  --host "$PUBLIC_IP" \
  --port 6432 \
  --database retail_dwh \
  --sslmode require \
  --count 45 \
  --out /tmp/student_credentials.csv
mv /tmp/student_credentials.csv /root/estudia-lab/student_credentials.csv
chown root:root /root/estudia-lab/student_credentials.csv
chmod 600 /root/estudia-lab/student_credentials.csv

AUTH_PW="$(python3 -c 'from pathlib import Path; lines=Path("/root/estudia-lab/admin.env").read_text().splitlines();
print([l.split("=",1)[1] for l in lines if l.startswith("PGBOUNCER_AUTH_PASSWORD=")][0])')"
install -d -o postgres -g postgres -m 755 /etc/pgbouncer
printf '"pgbouncer_auth" "%s"\n' "$AUTH_PW" > /etc/pgbouncer/userlist.txt
unset AUTH_PW
chown postgres:postgres /etc/pgbouncer/userlist.txt
chmod 640 /etc/pgbouncer/userlist.txt

install -d -o postgres -g postgres -m 750 /etc/pgbouncer/tls
if [[ ! -f /etc/pgbouncer/tls/server.key ]]; then
  openssl req -x509 -newkey rsa:2048 -sha256 -days 825 -nodes \
    -keyout /etc/pgbouncer/tls/ca.key \
    -out /etc/pgbouncer/tls/ca.crt \
    -subj "/CN=EstudIA Lab CA"
  openssl req -newkey rsa:2048 -nodes \
    -keyout /etc/pgbouncer/tls/server.key \
    -out /etc/pgbouncer/tls/server.csr \
    -subj "/CN=${PUBLIC_IP}"
  cat > /etc/pgbouncer/tls/server.ext <<EOF
subjectAltName=IP:${PUBLIC_IP},DNS:estudia-postgres-lab
extendedKeyUsage=serverAuth
keyUsage=digitalSignature,keyEncipherment
EOF
  openssl x509 -req \
    -in /etc/pgbouncer/tls/server.csr \
    -CA /etc/pgbouncer/tls/ca.crt \
    -CAkey /etc/pgbouncer/tls/ca.key \
    -CAcreateserial \
    -out /etc/pgbouncer/tls/server.crt \
    -days 825 -sha256 \
    -extfile /etc/pgbouncer/tls/server.ext
fi
chown -R postgres:postgres /etc/pgbouncer/tls
chmod 640 /etc/pgbouncer/tls/server.key /etc/pgbouncer/tls/ca.key
chmod 644 /etc/pgbouncer/tls/server.crt /etc/pgbouncer/tls/ca.crt
cp /etc/pgbouncer/tls/ca.crt /root/estudia-lab/estudia-lab-ca.crt
chmod 644 /root/estudia-lab/estudia-lab-ca.crt

if [[ -f /etc/pgbouncer/pgbouncer.ini && ! -f /etc/pgbouncer/pgbouncer.ini.dist ]]; then
  cp -a /etc/pgbouncer/pgbouncer.ini /etc/pgbouncer/pgbouncer.ini.dist
fi

cat > /etc/pgbouncer/pgbouncer.ini <<EOF
[databases]
retail_dwh = host=127.0.0.1 port=5432 dbname=retail_dwh

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
unix_socket_dir = /var/run/postgresql
unix_socket_mode = 0770
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt
auth_user = pgbouncer_auth
auth_query = SELECT usename, passwd FROM pgbouncer.user_search(\$1)
auth_dbname = retail_dwh
pool_mode = transaction
max_client_conn = 120
default_pool_size = 25
min_pool_size = 0
reserve_pool_size = 5
reserve_pool_timeout = 2
max_db_connections = 60
max_user_connections = 40
max_prepared_statements = 0
server_reset_query = RESET ALL
server_idle_timeout = 10
server_lifetime = 3600
server_connect_timeout = 5
query_timeout = 60
query_wait_timeout = 30
client_idle_timeout = 900
client_tls_sslmode = require
client_tls_key_file = /etc/pgbouncer/tls/server.key
client_tls_cert_file = /etc/pgbouncer/tls/server.crt
server_tls_sslmode = disable
ignore_startup_parameters = extra_float_digits,options,statement_timeout,idle_in_transaction_session_timeout,default_transaction_read_only,search_path,timezone,lc_messages,datestyle,intervalstyle,client_encoding,application_name
admin_users = pgbouncer_admin
stats_users = pgbouncer_admin
log_connections = 1
log_disconnections = 1
log_pooler_errors = 1
verbose = 0
pidfile = /var/run/postgresql/pgbouncer.pid
logfile = /var/log/postgresql/pgbouncer.log
EOF
chown postgres:postgres /etc/pgbouncer/pgbouncer.ini
chmod 640 /etc/pgbouncer/pgbouncer.ini

install -d -m 755 /etc/systemd/system/pgbouncer.service.d
cat > /etc/systemd/system/pgbouncer.service.d/limits.conf <<'EOF'
[Service]
LimitNOFILE=4096
EOF
systemctl daemon-reload
systemctl enable pgbouncer
systemctl restart pgbouncer
systemctl is-active postgresql
systemctl is-active pgbouncer || { journalctl -u pgbouncer -n 80 --no-pager; exit 1; }

if ss -lnt | grep -E '0\.0\.0\.0:5432|\[::\]:5432'; then
  echo "PostgreSQL quedó expuesto fuera de localhost"
  exit 1
fi
ss -lnt | grep -q ':6432'

ufw default deny incoming
ufw default allow outgoing
ufw allow from 35.235.240.0/20 to any port 22 proto tcp
ufw allow 6432/tcp
ufw --force enable

install -m 755 "$LAB/scripts/estudia-status.sh" /usr/local/bin/estudia-status
echo "bootstrap ok ip=$PUBLIC_IP db=retail_dwh port=6432"
