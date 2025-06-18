# ====================================================================
# SecureVault - Test de Portabilidad
# ====================================================================
# Este script verifica que el proyecto sea portable

Write-Host "Test de Portabilidad - SecureVault" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

# Informacion del sistema
Write-Host "Sistema:" -ForegroundColor Yellow
Write-Host "  Usuario: $env:USERNAME" -ForegroundColor Gray
Write-Host "  PC: $env:COMPUTERNAME" -ForegroundColor Gray
Write-Host "  Directorio actual: $PWD" -ForegroundColor Gray

# Detectar proyecto
$projectRoot = Split-Path -Parent $PSScriptRoot
Write-Host "  Proyecto en: $projectRoot" -ForegroundColor Gray

Write-Host ""
Write-Host "Verificando estructura..." -ForegroundColor Yellow

$checks = @(
    @{ Path = "backend\manage.py"; Name = "Django manage.py" },
    @{ Path = "secure-app-frontend\package.json"; Name = "Angular package.json" },
    @{ Path = "backend\venv"; Name = "Entorno virtual Python" },
    @{ Path = "scripts\setup_project.ps1"; Name = "Script de setup" },
    @{ Path = "scripts\run_servers_portable.ps1"; Name = "Script portable" }
)

$allOk = $true
foreach ($check in $checks) {
    $fullPath = Join-Path $projectRoot $check.Path
    if (Test-Path $fullPath) {
        Write-Host "  OK: $($check.Name)" -ForegroundColor Green
    }
    else {
        Write-Host "  ERROR: $($check.Name) - No encontrado" -ForegroundColor Red
        $allOk = $false
    }
}

Write-Host ""
if ($allOk) {
    Write-Host "RESULTADO: Proyecto portable y listo para usar" -ForegroundColor Green
    Write-Host ""
    Write-Host "Para usar en otro PC:" -ForegroundColor Cyan
    Write-Host "  1. Copiar toda la carpeta SecureVault" -ForegroundColor White
    Write-Host "  2. Ejecutar: .\scripts\setup_project.ps1" -ForegroundColor White
    Write-Host "  3. Ejecutar: .\scripts\run_servers_portable.ps1" -ForegroundColor White
}
else {
    Write-Host "RESULTADO: Hay problemas de estructura" -ForegroundColor Red
}
Write-Host ""
