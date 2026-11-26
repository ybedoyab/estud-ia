# Copia las plantillas ya llenas a la raiz y comprueba el YAML con Docker.
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

& (Join-Path $PSScriptRoot "validar_infraestructura.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Copy-Item "plantillas\infraestructura\Dockerfile" "Dockerfile" -Force
Copy-Item "plantillas\infraestructura\docker-compose.yml" "docker-compose.yml" -Force
if (-not (Test-Path ".env")) {
    Copy-Item "plantillas\infraestructura\.env.example" ".env" -Force
    Write-Host "Se creo .env desde la plantilla. preparar generara FERNET_KEY y JWT_SECRET."
}
docker compose config --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "El YAML no paso docker compose config. Revisa la indentacion."
    exit $LASTEXITCODE
}
Write-Host "Listo para construir. Siguiente: .\scripts\preparar.ps1"
exit 0
