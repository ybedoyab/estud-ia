# Revisa los DAG de practica. No los copia a dags/.
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$archivos = @(
    "plantillas\dags\estudia_clase05_mi_primer_dag.py",
    "plantillas\dags\estudia_clase05_practica.py"
)
$pendientes = 0
foreach ($relativo in $archivos) {
    $numero = 0
    foreach ($linea in Get-Content (Join-Path $Root $relativo)) {
        $numero++
        if ($linea.TrimStart().StartsWith("#")) { continue }
        if ($linea -cmatch "COMPLETA") {
            Write-Host ("PENDIENTE {0}:{1}: {2}" -f $relativo, $numero, $linea.Trim())
            $pendientes++
        }
    }
}
if ($pendientes -gt 0) {
    Write-Host "Faltan $pendientes campos en los DAG. No se copian a dags/."
    exit 1
}

$primero = Get-Content "plantillas\dags\estudia_clase05_mi_primer_dag.py" -Raw
$pipeline = Get-Content "plantillas\dags\estudia_clase05_practica.py" -Raw
$errores = @()
if ($primero -notmatch 'dag_id="estudia_clase05_mi_primer_dag"') { $errores += "Primer DAG: dag_id estudia_clase05_mi_primer_dag" }
if ($primero -notmatch "schedule=None") { $errores += "Primer DAG: schedule=None" }
if ($primero -notmatch "catchup=False") { $errores += "Primer DAG: catchup=False" }
if ($primero -notmatch 'task_id="saludar"') { $errores += "Primer DAG: task_id saludar" }
if ($primero -notmatch 'task_id="finalizar"') { $errores += "Primer DAG: task_id finalizar" }
if ($primero -notmatch "python_callable=saludar") { $errores += "Primer DAG: python_callable=saludar" }
if ($primero -notmatch "python_callable=finalizar") { $errores += "Primer DAG: python_callable=finalizar" }
$lineaInicio = $false
foreach ($linea in Get-Content "plantillas\dags\estudia_clase05_mi_primer_dag.py") {
    if ($linea.Trim() -eq "inicio >> fin") { $lineaInicio = $true }
}
if (-not $lineaInicio) { $errores += "Primer DAG: escribe la linea inicio >> fin" }

foreach ($nombre in @("extraer_api", "guardar_bronze", "transformar_silver", "validar_datos", "generar_gold", "exportar_reporte")) {
    if ($pipeline -notmatch ('task_id="' + $nombre + '"')) { $errores += "Pipeline: falta task_id $nombre" }
    if ($pipeline -notmatch ("python_callable=" + $nombre)) { $errores += "Pipeline: falta python_callable $nombre" }
}
if ($pipeline -notmatch 'dag_id="estudia_clase05_api_medallion"') { $errores += "Pipeline: dag_id estudia_clase05_api_medallion" }
if ($pipeline -notmatch "schedule=None") { $errores += "Pipeline: schedule=None" }
if ($pipeline -notmatch "catchup=False") { $errores += "Pipeline: catchup=False" }
if ($pipeline -notmatch "max_active_runs=1") { $errores += "Pipeline: max_active_runs=1" }
if ($pipeline -notmatch '"retries": 1') { $errores += "Pipeline: retries 1" }
$lineaCadena = $false
foreach ($linea in Get-Content "plantillas\dags\estudia_clase05_practica.py") {
    if ($linea.Trim() -eq "t1 >> t2 >> t3 >> t4 >> t5 >> t6") { $lineaCadena = $true }
}
if (-not $lineaCadena) { $errores += "Pipeline: escribe la linea t1 >> t2 >> t3 >> t4 >> t5 >> t6" }
if ($pipeline -notmatch 'get_connection\("estudia_api"\)') { $errores += "Pipeline: Connection estudia_api" }
if ($pipeline -notmatch '\["access_token"\]') { $errores += "Pipeline: la clave del token es access_token" }
if ($pipeline -notmatch '"Authorization"') { $errores += "Pipeline: el encabezado es Authorization" }
if ($pipeline -notmatch "Aragón") { $errores += "Pipeline: la region de la practica es Aragón" }
if ($pipeline -notmatch "range\(1, 3\)") { $errores += "Pipeline: range(1, 3) pide las paginas 1 y 2" }
if ($pipeline -notmatch '"page": numero') { $errores += "Pipeline: page usa la variable numero" }
if ($pipeline -notmatch '"page_size": 100') { $errores += "Pipeline: page_size 100" }
if ($pipeline -notmatch 'tirar\(contexto, "extraer_api"\)') { $errores += "Pipeline: XCom desde extraer_api" }
if ($pipeline -notmatch 'tirar\(contexto, "transformar_silver"\)') { $errores += "Pipeline: XCom desde transformar_silver" }
if ($pipeline -notmatch 'datos\["data"\]') { $errores += "Pipeline: el JSON plano trae data" }
if ($pipeline -notmatch "ignore_index=True") { $errores += "Pipeline: ignore_index=True" }
if ($pipeline -notmatch 'groupby\("categoria"') { $errores += "Pipeline: agrupa por categoria" }
if ($pipeline -notmatch 'groupby\("region"') { $errores += "Pipeline: agrupa por region" }
if ($pipeline -notmatch "\.sum\(\)") { $errores += "Pipeline: la agregacion es sum" }
if ($pipeline -notmatch 'df\["id_transaccion"\]\.isna\(\)') { $errores += "Pipeline: rechaza id nulo" }
if ($pipeline -notmatch 'df\["id_transaccion"\]\.duplicated\(\)') { $errores += "Pipeline: rechaza id duplicado" }

if ($errores.Count -gt 0) {
    $errores | ForEach-Object { Write-Host "REVISAR $_" }
    exit 1
}
Write-Host "DAGs completos. Siguiente: .\scripts\activar_dags.ps1"
exit 0
