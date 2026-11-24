#!/bin/bash
# Carga de 45 usuarios. No imprime contraseñas.
set -euo pipefail
SALIDA=/tmp/estudia-locust
mkdir -p "$SALIDA"
chmod 777 "$SALIDA"
monitor() {
  local etiqueta="$1"
  local segundos="$2"
  local fin=$((SECONDS + segundos))
  while (( SECONDS < fin )); do
    {
      echo "muestra $etiqueta $(date -u +%H:%M:%S)"
      docker stats --no-stream --format '{{.Name}} {{.CPUPerc}} {{.MemUsage}}' infra-clase04-1 airflow-fastapi-1 airflow-airflow-scheduler-1 || true
      docker exec infra-clase04-1 python -c 'from app.db import consultar; print(consultar("SELECT count(*) AS activas FROM pg_stat_activity WHERE usename = %s", ("clase04_lectura",)))'
    } >> "$SALIDA/muestras.txt" 2>/dev/null || true
    sleep 30
  done
}

correr() {
  local escenario="$1"
  echo "inicio $escenario"
  monitor "$escenario" 600 &
  local pid=$!
  if ! docker run --rm --name "estudia-locust-$escenario" \
    -v /opt/estudia-clase04/tests/load:/mnt:ro \
    -v /home/yulcr/estudia-clase04-cuentas.csv:/cuentas.csv:ro \
    -v "$SALIDA":/out \
    -e ESTUDIA_CUENTAS=/cuentas.csv \
    -e ESTUDIA_ESCENARIO="$escenario" \
    locustio/locust:2.32.4 \
    -f /mnt/locustfile.py --headless -u 45 -r 9 --run-time 10m \
    --host https://34.95.210.33.sslip.io \
    --csv "/out/$escenario" --html "/out/$escenario.html" --only-summary
  then
    kill "$pid" 2>/dev/null || true
    echo "locust_fallo $escenario"
    return 1
  fi
  kill "$pid" 2>/dev/null || true
  wait "$pid" 2>/dev/null || true
  echo "fin $escenario"
}

correr individual
correr compartida
echo "carga_terminada"
