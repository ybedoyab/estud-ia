#!/bin/bash
# Prepara secretos y levanta el contenedor. No imprime contraseñas.
set -euo pipefail
BASE=/opt/estudia-clase04
CSV=/home/yulcr/estudia-clase04-cuentas.csv
mkdir -p "$BASE/infra"
python3 - "$CSV" "$BASE/infra/secrets.env" <<'PY'
import secrets
import sys
from pathlib import Path

csv_path, destino = sys.argv[1:]
password = ""
for linea in Path(csv_path).read_text(encoding="utf-8").splitlines()[1:]:
    usuario, clave = linea.split(",", 1)
    if usuario == "clase04_lectura":
        password = clave
if not password:
    raise SystemExit("falta la cuenta tecnica")
Path(destino).write_text(
    "\n".join([
        "ESTUDIA_PGHOST=10.20.0.2",
        "ESTUDIA_PGPORT=6432",
        "ESTUDIA_PGDATABASE=retail_dwh",
        "ESTUDIA_PGUSER=clase04_lectura",
        f"ESTUDIA_PGPASSWORD={password}",
        f"ESTUDIA_JWT_SECRET={secrets.token_urlsafe(48)}",
        "ESTUDIA_JWT_HORAS=4",
        "PUBLIC_BASE_URL=https://34.95.210.33.sslip.io",
        "ESTUDIA_SKIP_DB=0",
        "",
    ]),
    encoding="utf-8",
)
Path(destino).chmod(0o600)
print("secrets_listos")
PY
cd "$BASE/infra"
sudo docker compose up -d --build
sudo docker compose ps
