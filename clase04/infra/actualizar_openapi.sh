#!/bin/bash
# Actualiza solo el código de la API. No regenera secretos ni contraseñas.
set -euo pipefail
sudo cp /tmp/clase04-main.py /opt/estudia-clase04/backend/app/main.py
cd /opt/estudia-clase04/infra
sudo docker compose up -d --build
sudo docker compose ps
