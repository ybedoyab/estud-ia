#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v docker >/dev/null; then
  echo "No esta docker. Instala Docker Desktop o Docker Engine y vuelve a intentar."
  exit 1
fi
docker info >/dev/null
echo "docker: $(docker --version)"
echo "compose: $(docker compose version)"

if [[ ! -f .env ]]; then
  cp .env.example .env
fi

if grep -q "FERNET_KEY=cambia-esta-clave-fernet" .env; then
  fernet="$(openssl rand -base64 32 | tr '+/' '-_')"
  tmp="$(mktemp)"
  sed "s|FERNET_KEY=cambia-esta-clave-fernet|FERNET_KEY=${fernet}|" .env > "$tmp"
  mv "$tmp" .env
  echo "FERNET_KEY generada en .env"
fi

clave="$(grep '^AIRFLOW_ADMIN_PASSWORD=' .env | head -n 1 | cut -d= -f2-)"
mkdir -p config
printf '{"admin":"%s"}\n' "$clave" > config/simple_auth_passwords.json
echo "Usuario local de Airflow: admin"
echo "La contrasena local quedo en .env. No es la de PostgreSQL ni la de la API."
docker compose build
echo "Imagenes listas. Siguiente: ./scripts/iniciar.sh"
