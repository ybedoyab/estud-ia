$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
docker compose ps
curl.exe -fsS http://127.0.0.1:8080/api/v2/monitor/health
Write-Host ""
Write-Host "Si el health responde, entra a http://127.0.0.1:8080"
