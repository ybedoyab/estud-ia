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
plantillas/dags/estudia_clase05_mi_primer_dag.py
plantillas/dags/estudia_clase05_practica.py
LISTA
if [[ "$pendientes" -gt 0 ]]; then
  echo "Faltan ${pendientes} campos en los DAG. No se copian a dags/."
  exit 1
fi
primero="$(cat plantillas/dags/estudia_clase05_mi_primer_dag.py)"
pipeline="$(cat plantillas/dags/estudia_clase05_practica.py)"
errores=0
marcar() { echo "REVISAR $1"; errores=$((errores + 1)); }
[[ "$primero" == *'dag_id="estudia_clase05_mi_primer_dag"'* ]] || marcar "Primer DAG: dag_id"
[[ "$primero" == *"schedule=None"* ]] || marcar "Primer DAG: schedule=None"
[[ "$primero" == *"catchup=False"* ]] || marcar "Primer DAG: catchup=False"
[[ "$primero" == *'task_id="saludar"'* ]] || marcar "Primer DAG: saludar"
[[ "$primero" == *'task_id="finalizar"'* ]] || marcar "Primer DAG: finalizar"
grep -qx '[[:space:]]*inicio >> fin[[:space:]]*' plantillas/dags/estudia_clase05_mi_primer_dag.py || marcar "Primer DAG: inicio >> fin"
[[ "$pipeline" == *'dag_id="estudia_clase05_api_medallion"'* ]] || marcar "Pipeline: dag_id"
[[ "$pipeline" == *"t1 >> t2 >> t3 >> t4 >> t5 >> t6"* ]] || true
grep -qx '[[:space:]]*t1 >> t2 >> t3 >> t4 >> t5 >> t6[[:space:]]*' plantillas/dags/estudia_clase05_practica.py || marcar "Pipeline: la linea de dependencias"
[[ "$pipeline" == *'get_connection("estudia_api")'* ]] || marcar "Pipeline: estudia_api"
[[ "$pipeline" == *'["access_token"]'* ]] || marcar "Pipeline: access_token"
[[ "$pipeline" == *'"Authorization"'* ]] || marcar "Pipeline: Authorization"
[[ "$pipeline" == *'tirar(contexto, "extraer_api")'* ]] || marcar "Pipeline: XCom extraer_api"
[[ "$pipeline" == *'tirar(contexto, "transformar_silver")'* ]] || marcar "Pipeline: XCom transformar_silver"
for nombre in extraer_api guardar_bronze transformar_silver validar_datos generar_gold exportar_reporte; do
  [[ "$pipeline" == *"task_id=\"${nombre}\""* ]] || marcar "Pipeline: task_id ${nombre}"
  [[ "$pipeline" == *"python_callable=${nombre}"* ]] || marcar "Pipeline: callable ${nombre}"
done
if [[ "$errores" -gt 0 ]]; then
  exit 1
fi
echo "DAGs completos. Siguiente: ./scripts/activar_dags.sh"
