#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
./scripts/validar_infraestructura.sh
cp plantillas/infraestructura/Dockerfile Dockerfile
cp plantillas/infraestructura/docker-compose.yml docker-compose.yml
if [[ ! -f .env ]]; then
  cp plantillas/infraestructura/.env.example .env
  echo "Se creo .env desde la plantilla. preparar generara FERNET_KEY y JWT_SECRET."
fi
docker compose config --quiet
echo "Listo para construir. Siguiente: ./scripts/preparar.sh"
