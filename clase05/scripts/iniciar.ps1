$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path ".env") -or -not (Test-Path "config\simple_auth_passwords.json")) {
    Write-Host "Falta la preparacion. Ejecuta primero .\scripts\preparar.ps1"
    exit 1
}

docker compose up airflow-init
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
docker compose up -d
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Abre http://127.0.0.1:8080 cuando el api-server este healthy."
Write-Host "Usuario: admin. Contrasena: la de AIRFLOW_ADMIN_PASSWORD en .env"
