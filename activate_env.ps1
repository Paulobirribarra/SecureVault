# Script para activar el entorno virtual automáticamente
Write-Host "Activando entorno virtual..." -ForegroundColor Green

$venvPath = Join-Path $PSScriptRoot "backend\venv\Scripts\Activate.ps1"

if (Test-Path $venvPath) {
    & $venvPath
    Write-Host "Entorno virtual activado!" -ForegroundColor Green
    Write-Host "Para instalar dependencias ejecuta: pip install -r backend/requirements.txt" -ForegroundColor Yellow
}
else {
    Write-Host "Entorno virtual no encontrado. Creando..." -ForegroundColor Yellow
    Set-Location "$PSScriptRoot\backend"
    python -m venv venv
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "Entorno virtual creado y activado!" -ForegroundColor Green
}
