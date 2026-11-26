$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$destino = Join-Path $Root "dist"
New-Item -ItemType Directory -Force -Path $destino | Out-Null
$stage = Join-Path $destino "EstudIA_Clase05_laboratorio"
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Force -Path $stage | Out-Null

$incluir = @(
    "README.md", "docker-compose.yml", "Dockerfile", "requirements.txt",
    ".env.example", ".dockerignore", "dags", "plantillas", "fixtures", "scripts"
)
foreach ($item in $incluir) {
    Copy-Item $item -Destination (Join-Path $stage $item) -Recurse -Force
}

# Montajes vacios. No se copian corridas, logs ni la clave local.
foreach ($capa in @("bronze", "silver", "gold", "reports", "staging")) {
    $carpeta = Join-Path $stage "data\$capa"
    New-Item -ItemType Directory -Force -Path $carpeta | Out-Null
    New-Item -ItemType File -Force -Path (Join-Path $carpeta ".gitkeep") | Out-Null
}
New-Item -ItemType Directory -Force -Path (Join-Path $stage "logs") | Out-Null
New-Item -ItemType File -Force -Path (Join-Path $stage "logs\.gitkeep") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $stage "pipeline") | Out-Null
Copy-Item "pipeline\__init__.py" (Join-Path $stage "pipeline\__init__.py")

Get-ChildItem $stage -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
Get-ChildItem $stage -Recurse -Filter *.pyc | Remove-Item -Force
Get-ChildItem $stage -Recurse -File -Include *.env,simple_auth_passwords.json | Remove-Item -Force
Get-ChildItem (Join-Path $stage "dags") -File | Where-Object { $_.Name -like "*profesor*" } | Remove-Item -Force

New-Item -ItemType Directory -Force -Path (Join-Path $stage "docs") | Out-Null
Copy-Item "docs\GUIA_ESTUDIANTE.md" (Join-Path $stage "docs\GUIA_ESTUDIANTE.md")
New-Item -ItemType Directory -Force -Path (Join-Path $stage "notebooks") | Out-Null
Copy-Item "notebooks\EstudIA_Clase05_PRACTICA.ipynb" (Join-Path $stage "notebooks\EstudIA_Clase05_PRACTICA.ipynb")

$zip = Join-Path $destino "EstudIA_Clase05_laboratorio.zip"
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path (Join-Path $stage "*") -DestinationPath $zip
Write-Host "ZIP" $zip
