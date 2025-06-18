# ====================================================================
# SecureVault - Arreglar PATH de Python
# ====================================================================
# Este script limpia conflictos de múltiples instalaciones de Python

Write-Host "🔧 SecureVault - Limpiando PATH de Python" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

# Configurar Python correcto usando variables de entorno
$pythonRoot = "$env:LOCALAPPDATA\Programs\Python\Python313"

# Verificar que la instalación existe
if (-not (Test-Path $pythonRoot)) {
    Write-Host "⚠️  Python 3.13 no encontrado en la ubicación estándar" -ForegroundColor Yellow
    Write-Host "   Buscando otras versiones..." -ForegroundColor Gray
    
    # Buscar cualquier versión de Python 3.x
    $pythonDirs = Get-ChildItem "$env:LOCALAPPDATA\Programs\Python\" -Directory -ErrorAction SilentlyContinue | 
                  Where-Object { $_.Name -match "Python3\d+" } | 
                  Sort-Object Name -Descending
    
    if ($pythonDirs.Count -gt 0) {
        $pythonRoot = $pythonDirs[0].FullName
        Write-Host "   Encontrado: $pythonRoot" -ForegroundColor Green
    } else {
        Write-Host "❌ No se encontró Python instalado" -ForegroundColor Red
        Write-Host "   Instalar Python desde: https://python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
}

# Limpiar PATH de referencias problemáticas
Write-Host "🧹 Limpiando PATH..." -ForegroundColor Yellow
$cleanPath = $env:PATH -split ';' | Where-Object { 
    $_ -notlike '*Microsoft\WindowsApps*' -and 
    $_ -notlike '*console-ninja*' -and 
    $_ -notlike '*scoop*' 
} | Sort-Object -Unique

# Establecer Python correcto al inicio
$env:PATH = "$pythonRoot\Scripts;$pythonRoot;" + ($cleanPath -join ';')

# Remover variables problemáticas
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue

# Configurar variables de entorno Python
$env:PYTHONHOME = $pythonRoot
$env:PYTHON = "$pythonRoot\python.exe"

Write-Host "✅ PATH limpiado" -ForegroundColor Green
Write-Host "🐍 Python configurado: $pythonRoot" -ForegroundColor Green

# Verificar
Write-Host "🔍 Verificando configuración..." -ForegroundColor Yellow
python --version
where.exe python | Select-Object -First 2

Write-Host ""
Write-Host "💡 Para aplicar permanentemente:" -ForegroundColor Cyan
Write-Host "   1. Configuración → Sistema → Configuración avanzada del sistema" -ForegroundColor White
Write-Host "   2. Variables de entorno → PATH del usuario" -ForegroundColor White
Write-Host "   3. Remover: $env:LOCALAPPDATA\Microsoft\WindowsApps" -ForegroundColor White
Write-Host "   4. Agregar al inicio: $pythonRoot\Scripts;$pythonRoot" -ForegroundColor White
Write-Host ""
