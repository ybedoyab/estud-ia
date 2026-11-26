# Comprueba los DAG dentro de Airflow y, si estan bien, los copia a dags/.
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

& (Join-Path $PSScriptRoot "validar_dags.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$vivos = @(docker compose ps --status running --services)
if ($vivos -notcontains "airflow-scheduler") {
    Write-Host "Airflow no esta en marcha. Ejecuta iniciar y vuelve a activar los DAG."
    exit 1
}

$copias = @(
    "plantillas\dags\estudia_clase05_mi_primer_dag.py",
    "plantillas\dags\estudia_clase05_practica.py"
)
foreach ($relativo in $copias) {
    $nombre = Split-Path $relativo -Leaf
    Get-Content (Join-Path $Root $relativo) -Raw | docker compose exec -T airflow-scheduler python -c "import sys; compile(sys.stdin.read(), '$nombre', 'exec')"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error de sintaxis en $nombre. No se copia."
        exit $LASTEXITCODE
    }
}

New-Item -ItemType Directory -Force -Path "dags" | Out-Null
Copy-Item "plantillas\dags\estudia_clase05_mi_primer_dag.py" "dags\estudia_clase05_mi_primer_dag.py" -Force
Copy-Item "plantillas\dags\estudia_clase05_practica.py" "dags\estudia_clase05_practica.py" -Force
Start-Sleep -Seconds 20
docker compose exec -T airflow-scheduler airflow dags list-import-errors
docker compose exec -T airflow-scheduler airflow dags list --output plain
Write-Host "Si los dos DAG aparecen y no hay errores de importacion, ya puedes abrir Graph."
exit 0
