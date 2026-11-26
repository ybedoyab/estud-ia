#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose ps
curl -fsS http://127.0.0.1:8080/api/v2/monitor/health
echo
echo "Si el health responde, entra a http://127.0.0.1:8080"
