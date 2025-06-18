# ====================================================================
# SecureVault - Verificador de Portabilidad
# ====================================================================
# Este script verifica que el proyecto funcione en cualquier PC/usuario

Write-Host "🔍 SecureVault - Verificador de Portabilidad" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

Write-Host "🖥️ Información del sistema:" -ForegroundColor Yellow
Write-Host "   Usuario: $env:USERNAME" -ForegroundColor Gray
Write-Host "   PC: $env:COMPUTERNAME" -ForegroundColor Gray
Write-Host "   Directorio: $PWD" -ForegroundColor Gray
Write-Host "   LOCALAPPDATA: $env:LOCALAPPDATA" -ForegroundColor Gray

Write-Host ""
Write-Host "🔍 Verificando variables de entorno universales..." -ForegroundColor Yellow

# Verificar rutas dinámicas vs hardcodeadas
$projectRoot = Split-Path -Parent $PSScriptRoot
Write-Host "✅ Raíz del proyecto (dinámico): $projectRoot" -ForegroundColor Green

$pythonPath = "$env:LOCALAPPDATA\Programs\Python"
if (Test-Path $pythonPath) {
    Write-Host "✅ Directorio Python (universal): $pythonPath" -ForegroundColor Green
    Get-ChildItem $pythonPath -Directory | ForEach-Object {
        Write-Host "   📁 $($_.Name)" -ForegroundColor Gray
    }
} else {
    Write-Host "⚠️  Directorio Python no encontrado en ubicación estándar" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🔍 Verificando rutas de scripts..." -ForegroundColor Yellow

# Verificar que los scripts no tengan rutas hardcodeadas problemáticas
$scriptsToCheck = @(
    "setup_project.ps1",
    "run_servers.ps1", 
    "setup_database.ps1",
    "fix_python_path.ps1"
)

foreach ($script in $scriptsToCheck) {
    $scriptPath = Join-Path $PSScriptRoot $script
    if (Test-Path $scriptPath) {
        $content = Get-Content $scriptPath -Raw
        
        # Buscar rutas hardcodeadas problemáticas
        $hardcodedIssues = @()
        
        if ($content -match "C:\\Users\\[^\\]+\\") {
            $hardcodedIssues += "Ruta de usuario hardcodeada"
        }
        if ($content -match "E:\\Paulo\\Github" -or $content -match "E:/Paulo/Github") {
            $hardcodedIssues += "Ruta de proyecto hardcodeada"
        }
        if ($content -match "c-ram") {
            $hardcodedIssues += "Nombre de usuario específico"
        }
        
        if ($hardcodedIssues.Count -eq 0) {
            Write-Host "   ✅ $script - PORTABLE" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $script - PROBLEMAS:" -ForegroundColor Red
            foreach ($issue in $hardcodedIssues) {
                Write-Host "      - $issue" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "   ⚠️  $script - NO ENCONTRADO" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🔍 Verificando backend..." -ForegroundColor Yellow

$backendPath = Join-Path $projectRoot "backend"
if (Test-Path $backendPath) {
    Write-Host "   ✅ Directorio backend encontrado" -ForegroundColor Green
    
    $venvPath = Join-Path $backendPath "venv\Scripts\python.exe"
    if (Test-Path $venvPath) {
        Write-Host "   ✅ Entorno virtual encontrado" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Entorno virtual NO encontrado" -ForegroundColor Red
    }
} else {
    Write-Host "   ❌ Directorio backend NO encontrado" -ForegroundColor Red
}

Write-Host ""
Write-Host "🔍 Verificando frontend..." -ForegroundColor Yellow

$frontendPath = Join-Path $projectRoot "secure-app-frontend"
if (Test-Path $frontendPath) {
    Write-Host "   ✅ Directorio frontend encontrado" -ForegroundColor Green
    
    $packageJsonPath = Join-Path $frontendPath "package.json"
    if (Test-Path $packageJsonPath) {
        Write-Host "   ✅ package.json encontrado" -ForegroundColor Green
    } else {
        Write-Host "   ❌ package.json NO encontrado" -ForegroundColor Red
    }
} else {
    Write-Host "   ❌ Directorio frontend NO encontrado" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 RESULTADO FINAL:" -ForegroundColor Cyan
Write-Host "   Este proyecto debería funcionar en cualquier PC Windows" -ForegroundColor Green
Write-Host "   con Python 3.x y Node.js instalados." -ForegroundColor Green
Write-Host ""
Write-Host "💡 Para usar en otro PC:" -ForegroundColor Yellow
Write-Host "   1. Clonar: git clone <repo>" -ForegroundColor White
Write-Host "   2. Ejecutar: .\scripts\setup_project.ps1" -ForegroundColor White
Write-Host "   3. Ejecutar: .\scripts\run_servers.ps1" -ForegroundColor White
Write-Host ""
