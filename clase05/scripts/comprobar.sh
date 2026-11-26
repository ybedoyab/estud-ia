#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

puerto="8080"
if [[ -f .env ]]; then
  valor="$(grep '^AIRFLOW_WEB_PORT=' .env | head -n 1 | cut -d= -f2- | tr -d '[:space:]' || true)"
  if [[ -n "${valor}" ]]; then
    puerto="$valor"
  fi
fi
url="http://127.0.0.1:${puerto}"

docker compose ps
echo "Comprobando ${url}"
curl -fsS "${url}/api/v2/monitor/health"
echo
echo "Si el health responde, entra a ${url}"
