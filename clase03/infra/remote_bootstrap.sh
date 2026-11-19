#!/bin/bash
# Se ejecuta en la VM de Airflow, con el codigo ya copiado en /opt/estudia-clase03.
set -euo pipefail
cd /opt/estudia-clase03/airflow
install -d -m 755 /opt/estudia-clase03/airflow/{dags,logs,plugins,specs,reportes,config}
if [[ ! -f /root/estudia-clase03/secrets.env ]]; then
  install -d -m 700 /root/estudia-clase03
  python3 - << 'PY'
import base64, json, secrets
from pathlib import Path
values = {
    "FERNET_KEY": base64.urlsafe_b64encode(secrets.token_bytes(32)).decode(),
    "JWT_SECRET": secrets.token_urlsafe(32),
    "METADATA_PASSWORD": secrets.token_urlsafe(24),
    "ESTUDIA_PGPASSWORD": secrets.token_urlsafe(24),
    "ESTUDIA_JWT_SECRET": secrets.token_urlsafe(32),
    "ESTUDIA_ADMIN_TOKEN": secrets.token_urlsafe(32),
    "AIRFLOW_ADMIN_PASSWORD": secrets.token_urlsafe(18),
}
Path("/root/estudia-clase03/secrets.env").write_text(
    "\n".join(f"{key}={value}" for key, value in values.items()) + "\n",
    encoding="utf-8",
)
Path("/root/estudia-clase03/airflow_lectura.password").write_text(
    values["ESTUDIA_PGPASSWORD"] + "\n", encoding="utf-8"
)
print("secrets-created")
PY
  chmod 600 /root/estudia-clase03/secrets.env /root/estudia-clase03/airflow_lectura.password
fi
set -a
# shellcheck disable=SC1091
source /root/estudia-clase03/secrets.env
set +a
cat > .env << EOF
FERNET_KEY=${FERNET_KEY}
JWT_SECRET=${JWT_SECRET}
METADATA_PASSWORD=${METADATA_PASSWORD}
ESTUDIA_PGPASSWORD=${ESTUDIA_PGPASSWORD}
ESTUDIA_JWT_SECRET=${ESTUDIA_JWT_SECRET}
ESTUDIA_ADMIN_TOKEN=${ESTUDIA_ADMIN_TOKEN}
AIRFLOW_ADMIN_USER=docente
AIRFLOW_ADMIN_PASSWORD=${AIRFLOW_ADMIN_PASSWORD}
PUBLIC_API_URL=https://34.95.210.33.sslip.io
PUBLIC_AIRFLOW_URL=https://airflow.34.95.210.33.sslip.io
API_HOST=34.95.210.33.sslip.io
AIRFLOW_HOST=airflow.34.95.210.33.sslip.io
ESTUDIA_PGHOST=10.20.0.2
ESTUDIA_PGPORT=6432
ESTUDIA_PGDATABASE=retail_dwh
ESTUDIA_PGUSER=airflow_lectura
EOF
chmod 600 .env
python3 - << PY
import json
from pathlib import Path
Path("config/simple_auth_manager_passwords.json").write_text(
    json.dumps({"docente": "${AIRFLOW_ADMIN_PASSWORD}"}),
    encoding="utf-8",
)
PY
chmod 600 config/simple_auth_manager_passwords.json
chown -R 50000:0 dags logs plugins specs reportes config
if ! command -v docker >/dev/null; then
  apt-get update
  apt-get install -y docker.io docker-compose-v2
  systemctl enable --now docker
fi
docker compose build
docker compose up airflow-init
docker compose up -d
echo "bootstrap-ok"
