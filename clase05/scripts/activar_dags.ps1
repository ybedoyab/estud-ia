# Comprueba el DAG pedido dentro de Airflow y, si esta bien, lo copia a dags/.
# Sin argumento activa los dos, como antes.
param(
    [Parameter(Position = 0)]
    [string]$Cual = "todos"
)
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Cual = $Cual.ToLower()
if ($Cual -notin @("primero", "pipeline", "todos")) {
    Write-Host "Usa: primero, pipeline o todos."
    exit 1
}

& (Join-Path $PSScriptRoot "validar_dags.ps1") $Cual
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$vivos = @(docker compose ps --status running --services)
if ($vivos -notcontains "airflow-scheduler") {
    Write-Host "Airflow no esta en marcha. Ejecuta iniciar y vuelve a activar el DAG."
    exit 1
}

$copias = @()
if ($Cual -eq "primero" -or $Cual -eq "todos") {
    $copias += "plantillas\dags\estudia_clase05_mi_primer_dag.py"
}
if ($Cual -eq "pipeline" -or $Cual -eq "todos") {
    $copias += "plantillas\dags\estudia_clase05_practica.py"
}

foreach ($relativo in $copias) {
    $nombre = Split-Path $relativo -Leaf
    Get-Content (Join-Path $Root $relativo) -Raw | docker compose exec -T airflow-scheduler python -c "import sys; compile(sys.stdin.read(), '$nombre', 'exec')"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error de sintaxis en $nombre. No se copia."
        exit $LASTEXITCODE
    }
}

New-Item -ItemType Directory -Force -Path "dags" | Out-Null
foreach ($relativo in $copias) {
    Copy-Item (Join-Path $Root $relativo) (Join-Path $Root "dags\$(Split-Path $relativo -Leaf)") -Force
}
Start-Sleep -Seconds 20
docker compose exec -T airflow-scheduler airflow dags list-import-errors
docker compose exec -T airflow-scheduler airflow dags list --output plain
Write-Host "Si el DAG activado aparece y no hay errores de importacion, ya puedes abrir Graph."
exit 0
