#!/usr/bin/env bash
# Sin argumento activa los dos, como antes.
set -euo pipefail
cd "$(dirname "$0")/.."
modo="${1:-todos}"
case "$modo" in
  primero|pipeline|todos) ;;
  *) echo "Usa: primero, pipeline o todos."; exit 1 ;;
esac

./scripts/validar_dags.sh "$modo"
if ! docker compose ps --status running --services | grep -qx airflow-scheduler; then
  echo "Airflow no esta en marcha. Ejecuta iniciar y vuelve a activar el DAG."
  exit 1
fi

copiar() {
  local relativo="$1"
  local nombre
  nombre="$(basename "$relativo")"
  docker compose exec -T airflow-scheduler python -c 'import sys; compile(sys.stdin.read(), sys.argv[1], "exec")' "$nombre" < "$relativo"
  mkdir -p dags
  cp "$relativo" "dags/$nombre"
}

if [[ "$modo" == "primero" || "$modo" == "todos" ]]; then
  copiar plantillas/dags/estudia_clase05_mi_primer_dag.py
fi
if [[ "$modo" == "pipeline" || "$modo" == "todos" ]]; then
  copiar plantillas/dags/estudia_clase05_practica.py
fi

sleep 20
docker compose exec -T airflow-scheduler airflow dags list-import-errors
docker compose exec -T airflow-scheduler airflow dags list --output plain
echo "Si el DAG activado aparece y no hay errores de importacion, ya puedes abrir Graph."
