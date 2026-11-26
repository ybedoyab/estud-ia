$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
docker compose stop
Write-Host "Servicios detenidos. Los volumenes de metadatos se conservan."
Write-Host "Para volver: .\scripts\iniciar.ps1"
Write-Host "Para borrar tambien la base de metadatos: docker compose down -v"
