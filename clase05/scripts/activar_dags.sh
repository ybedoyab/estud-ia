#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
./scripts/validar_dags.sh
if ! docker compose ps --status running --services | grep -qx airflow-scheduler; then
  echo "Airflow no esta en marcha. Ejecuta iniciar y vuelve a activar los DAG."
  exit 1
fi
for relativo in plantillas/dags/estudia_clase05_mi_primer_dag.py plantillas/dags/estudia_clase05_practica.py; do
  nombre="$(basename "$relativo")"
  docker compose exec -T airflow-scheduler python -c 'import sys; compile(sys.stdin.read(), sys.argv[1], "exec")' "$nombre" < "$relativo"
done
mkdir -p dags
cp plantillas/dags/estudia_clase05_mi_primer_dag.py dags/
cp plantillas/dags/estudia_clase05_practica.py dags/
sleep 20
docker compose exec -T airflow-scheduler airflow dags list-import-errors
docker compose exec -T airflow-scheduler airflow dags list --output plain
echo "Si los dos DAG aparecen y no hay errores de importacion, ya puedes abrir Graph."
