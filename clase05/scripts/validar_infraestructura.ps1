# Revisa las plantillas. No construye imagenes ni levanta contenedores.
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$archivos = @(
    "plantillas\infraestructura\Dockerfile",
    "plantillas\infraestructura\docker-compose.yml",
    "plantillas\infraestructura\.env.example"
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
    Write-Host "Faltan $pendientes campos. No se construye nada."
    exit 1
}

$dockerfile = Get-Content "plantillas\infraestructura\Dockerfile" -Raw
$compose = Get-Content "plantillas\infraestructura\docker-compose.yml" -Raw
$entorno = Get-Content "plantillas\infraestructura\.env.example" -Raw
$errores = @()

if ($dockerfile -notmatch "FROM apache/airflow:3\.4\.0") { $errores += "Dockerfile: FROM debe ser apache/airflow:3.4.0" }
if ($dockerfile -notmatch "USER airflow") { $errores += "Dockerfile: USER debe ser airflow" }
if ($dockerfile -notmatch "pandas==3\.1\.0") { $errores += "Dockerfile: pandas debe ser 3.1.0" }
if ($dockerfile -notmatch "requests==2\.34\.2") { $errores += "Dockerfile: requests debe ser 2.34.2" }
if ($compose -notmatch "AIRFLOW__CORE__EXECUTOR: LocalExecutor") { $errores += "Compose: el ejecutor es LocalExecutor" }
if ($compose -notmatch 'AIRFLOW__CORE__PARALLELISM: "4"') { $errores += "Compose: PARALLELISM es 4" }
if ($compose -notmatch 'AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG: "1"') { $errores += "Compose: MAX_ACTIVE_RUNS_PER_DAG es 1" }
if ($compose -notmatch "\./dags:/opt/airflow/dags") { $errores += "Compose: el montaje de dags termina en /opt/airflow/dags" }
if ($compose -notmatch "\./logs:/opt/airflow/logs") { $errores += "Compose: el montaje de logs termina en /opt/airflow/logs" }
if ($compose -notmatch "\./data:/opt/airflow/data") { $errores += "Compose: el montaje de data termina en /opt/airflow/data" }
if ($compose -notmatch '127\.0\.0\.1:\$\{AIRFLOW_WEB_PORT:-8080\}:8080') { $errores += "Compose: la interfaz solo escucha en 127.0.0.1 y el puerto del contenedor es 8080" }
if ($compose -match "\d+:5432") { $errores += "Compose: no publiques el puerto de PostgreSQL" }
foreach ($linea in Get-Content "plantillas\infraestructura\docker-compose.yml") {
    if ($linea -match "condition:\s*(\S+)") {
        $condicion = $Matches[1]
        if ($condicion -notin @("service_healthy", "service_completed_successfully")) {
            $errores += "Compose: condicion no valida: $condicion"
        }
    }
}
$servicio = ""
foreach ($linea in Get-Content "plantillas\infraestructura\docker-compose.yml") {
    if ($linea -match "^  ([a-z0-9-]+):\s*$") { $servicio = $Matches[1] }
    if ($linea -match "^\s+image:\s*(\S+)\s*$" -and $servicio -eq "postgres") {
        if ($Matches[1] -ne "postgres:16.6") { $errores += "Compose: la imagen de postgres es postgres:16.6" }
    }
    if ($linea -match "^\s+command:\s*(\S+)\s*$") {
        $comando = $Matches[1]
        $esperado = @{
            "airflow-apiserver" = "api-server"
            "airflow-scheduler" = "scheduler"
            "airflow-dag-processor" = "dag-processor"
        }
        if ($esperado.ContainsKey($servicio) -and $comando -ne $esperado[$servicio]) {
            $errores += "Compose: $servicio usa el comando $($esperado[$servicio])"
        }
    }
}
if ($entorno -notmatch "(?m)^AIRFLOW_WEB_PORT=8080\s*$") { $errores += ".env: AIRFLOW_WEB_PORT=8080" }
if ($entorno -notmatch "(?m)^AIRFLOW_ADMIN_USER=admin\s*$") { $errores += ".env: AIRFLOW_ADMIN_USER=admin" }
if ($entorno -notmatch "(?m)^AIRFLOW_ADMIN_PASSWORD=estudia-local\s*$") { $errores += ".env: AIRFLOW_ADMIN_PASSWORD=estudia-local" }

if ($errores.Count -gt 0) {
    $errores | ForEach-Object { Write-Host "REVISAR $_" }
    exit 1
}
Write-Host "Infraestructura completa. Siguiente: .\scripts\activar_infraestructura.ps1"
exit 0
