#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")/.."
pendientes=0
while IFS= read -r relativo; do
  numero=0
  while IFS= read -r linea || [[ -n "$linea" ]]; do
    numero=$((numero + 1))
    if [[ "$linea" =~ ^[[:space:]]*# ]]; then continue; fi
    if [[ "$linea" == *COMPLETA* ]]; then
      echo "PENDIENTE ${relativo}:${numero}: ${linea}"
      pendientes=$((pendientes + 1))
    fi
  done < "$relativo"
done <<'LISTA'
plantillas/infraestructura/Dockerfile
plantillas/infraestructura/docker-compose.yml
plantillas/infraestructura/.env.example
LISTA
if [[ "$pendientes" -gt 0 ]]; then
  echo "Faltan ${pendientes} campos. No se construye nada."
  exit 1
fi
dockerfile="$(cat plantillas/infraestructura/Dockerfile)"
compose="$(cat plantillas/infraestructura/docker-compose.yml)"
entorno="$(cat plantillas/infraestructura/.env.example)"
errores=0
marcar() { echo "REVISAR $1"; errores=$((errores + 1)); }
[[ "$dockerfile" == *"FROM apache/airflow:3.4.0"* ]] || marcar "Dockerfile: FROM apache/airflow:3.4.0"
[[ "$dockerfile" == *"USER airflow"* ]] || marcar "Dockerfile: USER airflow"
[[ "$dockerfile" == *"pandas==3.1.0"* ]] || marcar "Dockerfile: pandas 3.1.0"
[[ "$dockerfile" == *"requests==2.34.2"* ]] || marcar "Dockerfile: requests 2.34.2"
[[ "$compose" == *"AIRFLOW__CORE__EXECUTOR: LocalExecutor"* ]] || marcar "Compose: LocalExecutor"
[[ "$compose" == *'AIRFLOW__CORE__PARALLELISM: "4"'* ]] || marcar "Compose: PARALLELISM 4"
[[ "$compose" == *'AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG: "1"'* ]] || marcar "Compose: una corrida activa"
[[ "$compose" == *"./dags:/opt/airflow/dags"* ]] || marcar "Compose: montaje dags"
[[ "$compose" == *"./logs:/opt/airflow/logs"* ]] || marcar "Compose: montaje logs"
[[ "$compose" == *"./data:/opt/airflow/data"* ]] || marcar "Compose: montaje data"
[[ "$compose" == *'127.0.0.1:${AIRFLOW_WEB_PORT:-8080}:8080'* ]] || marcar "Compose: interfaz en 127.0.0.1"
[[ "$compose" == *":5432"* ]] && marcar "Compose: no publiques PostgreSQL"
[[ "$entorno" == *"AIRFLOW_WEB_PORT=8080"* ]] || marcar ".env: puerto 8080"
[[ "$entorno" == *"AIRFLOW_ADMIN_USER=admin"* ]] || marcar ".env: usuario admin"
[[ "$entorno" == *"AIRFLOW_ADMIN_PASSWORD=estudia-local"* ]] || marcar ".env: contrasena estudia-local"
if [[ "$errores" -gt 0 ]]; then
  exit 1
fi
echo "Infraestructura completa. Siguiente: ./scripts/activar_infraestructura.sh"
