$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$puerto = "8080"
if (Test-Path ".env") {
    foreach ($linea in Get-Content ".env") {
        if ($linea -like "AIRFLOW_WEB_PORT=*") {
            $valor = $linea.Substring(17).Trim()
            if ($valor) { $puerto = $valor }
        }
    }
}
$url = "http://127.0.0.1:$puerto"

docker compose ps
Write-Host "Comprobando $url"
curl.exe -fsS "$url/api/v2/monitor/health"
Write-Host ""
Write-Host "Si el health responde, entra a $url"
