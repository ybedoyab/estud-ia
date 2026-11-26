#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -f .env || ! -f config/simple_auth_passwords.json ]]; then
  echo "Falta la preparacion. Ejecuta primero ./scripts/preparar.sh"
  exit 1
fi
docker compose up airflow-init
docker compose up -d
puerto="8080"
valor="$(grep '^AIRFLOW_WEB_PORT=' .env | head -n 1 | cut -d= -f2- | tr -d '[:space:]' || true)"
if [[ -n "${valor}" ]]; then
  puerto="$valor"
fi
echo "Abre http://127.0.0.1:${puerto} cuando el api-server este healthy."
echo "Usuario: admin. Contrasena: la de AIRFLOW_ADMIN_PASSWORD en .env"
