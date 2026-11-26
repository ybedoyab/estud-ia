#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose stop
echo "Servicios detenidos. Los volumenes de metadatos se conservan."
echo "Para volver: ./scripts/iniciar.sh"
echo "Para borrar tambien la base de metadatos: docker compose down -v"
