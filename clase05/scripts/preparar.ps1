# Continue: en Windows PowerShell 5.1 un aviso de Docker en stderr
# detiene el script si la preferencia es Stop.
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "No esta el comando docker. Instala Docker Desktop, reinicia si hace falta y abre la aplicacion."
    exit 1
}

docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker Desktop no responde. Abrelo y espera a que el motor este en marcha."
    exit 1
}

Write-Host "docker:" (docker --version)
Write-Host "compose:" (docker compose version)

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

$texto = Get-Content ".env" -Raw
if ($texto -match "FERNET_KEY=cambia-esta-clave-fernet") {
    $bytes = New-Object byte[] 32
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $fernet = [Convert]::ToBase64String($bytes).Replace("+", "-").Replace("/", "_")
    $texto = $texto.Replace("FERNET_KEY=cambia-esta-clave-fernet", "FERNET_KEY=$fernet")
    Set-Content -Path ".env" -Value $texto -Encoding ascii
    Write-Host "FERNET_KEY generada en .env"
}

$texto = Get-Content ".env" -Raw
if ($texto -notmatch "(?m)^JWT_SECRET=.+" -or $texto -match "JWT_SECRET=cambia-esta-clave-jwt") {
    $bytes = New-Object byte[] 32
    [System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
    $jwt = [Convert]::ToBase64String($bytes).Replace("+", "-").Replace("/", "_")
    if ($texto -match "JWT_SECRET=cambia-esta-clave-jwt") {
        $texto = $texto.Replace("JWT_SECRET=cambia-esta-clave-jwt", "JWT_SECRET=$jwt")
    } else {
        $texto = $texto.TrimEnd() + "`r`nJWT_SECRET=$jwt`r`n"
    }
    Set-Content -Path ".env" -Value $texto -Encoding ascii
    Write-Host "JWT_SECRET generada en .env"
}

$clave = "estudia-local"
foreach ($linea in Get-Content ".env") {
    if ($linea -like "AIRFLOW_ADMIN_PASSWORD=*") {
        $clave = $linea.Substring(24)
    }
}
New-Item -ItemType Directory -Force -Path "config" | Out-Null
$json = '{"admin":"' + ($clave.Replace("\", "\\").Replace('"', '\"')) + '"}'
Set-Content -Path "config\simple_auth_passwords.json" -Value $json -Encoding ascii
Write-Host "Usuario local de Airflow: admin"
Write-Host "La contrasena local quedo en .env. No es la de PostgreSQL ni la de la API."

docker compose build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Imagenes listas. Siguiente: .\scripts\iniciar.ps1"
