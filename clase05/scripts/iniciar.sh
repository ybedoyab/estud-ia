#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -f .env || ! -f config/simple_auth_passwords.json ]]; then
  echo "Falta la preparacion. Ejecuta primero ./scripts/preparar.sh"
  exit 1
fi
docker compose up airflow-init
docker compose up -d
echo "Abre http://127.0.0.1:8080 cuando el api-server este healthy."
echo "Usuario: admin. Contrasena: la de AIRFLOW_ADMIN_PASSWORD en .env"
