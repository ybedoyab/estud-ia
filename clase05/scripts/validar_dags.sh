#!/usr/bin/env bash
# Sin argumento equivale a todos, como antes.
set -uo pipefail
cd "$(dirname "$0")/.."
modo="${1:-todos}"
case "$modo" in
  primero|pipeline|todos) ;;
  *) echo "Usa: primero, pipeline o todos."; exit 1 ;;
esac

archivos=()
if [[ "$modo" == "primero" || "$modo" == "todos" ]]; then
  archivos+=("plantillas/dags/estudia_clase05_mi_primer_dag.py")
fi
if [[ "$modo" == "pipeline" || "$modo" == "todos" ]]; then
  archivos+=("plantillas/dags/estudia_clase05_practica.py")
fi

pendientes=0
for relativo in "${archivos[@]}"; do
  numero=0
  while IFS= read -r linea || [[ -n "$linea" ]]; do
    numero=$((numero + 1))
    if [[ "$linea" =~ ^[[:space:]]*# ]]; then continue; fi
    if [[ "$linea" == *COMPLETA* ]]; then
      echo "PENDIENTE ${relativo}:${numero}: ${linea}"
      pendientes=$((pendientes + 1))
    fi
  done < "$relativo"
done
if [[ "$pendientes" -gt 0 ]]; then
  echo "Faltan ${pendientes} campos. No se copia ese DAG a dags/."
  exit 1
fi

errores=0
marcar() { echo "REVISAR $1"; errores=$((errores + 1)); }

if [[ "$modo" == "primero" || "$modo" == "todos" ]]; then
  primero="$(cat plantillas/dags/estudia_clase05_mi_primer_dag.py)"
  [[ "$primero" == *'dag_id="estudia_clase05_mi_primer_dag"'* ]] || marcar "Primer DAG: dag_id"
  [[ "$primero" == *"schedule=None"* ]] || marcar "Primer DAG: schedule=None"
  [[ "$primero" == *"catchup=False"* ]] || marcar "Primer DAG: catchup=False"
  [[ "$primero" == *'task_id="saludar"'* ]] || marcar "Primer DAG: saludar"
  [[ "$primero" == *'task_id="finalizar"'* ]] || marcar "Primer DAG: finalizar"
  grep -qx '[[:space:]]*inicio >> fin[[:space:]]*' plantillas/dags/estudia_clase05_mi_primer_dag.py || marcar "Primer DAG: inicio >> fin"
fi

if [[ "$modo" == "pipeline" || "$modo" == "todos" ]]; then
  pipeline="$(cat plantillas/dags/estudia_clase05_practica.py)"
  [[ "$pipeline" == *'dag_id="estudia_clase05_api_medallion"'* ]] || marcar "Pipeline: dag_id"
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
fi

if [[ "$errores" -gt 0 ]]; then
  exit 1
fi
echo "Listo (${modo}). Siguiente: ./scripts/activar_dags.sh ${modo}"
exit 0
