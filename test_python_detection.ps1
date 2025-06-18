# Test simple para detectar Python
Write-Host "🔍 Detectando Python..." -ForegroundColor Yellow

# Método simple y directo
$pythonPath = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"

if (Test-Path $pythonPath) {
    $version = & $pythonPath --version 2>$null
    Write-Host "✅ Python encontrado: $version en $pythonPath" -ForegroundColor Green
    Write-Host "🎯 Resultado: $pythonPath" -ForegroundColor Cyan
} else {
    Write-Host "❌ Python no encontrado en: $pythonPath" -ForegroundColor Red
}

# También probar con where.exe
Write-Host ""
Write-Host "🔍 Verificando con where.exe..." -ForegroundColor Yellow
try {
    $whereResult = & where.exe python 2>$null
    if ($whereResult) {
        Write-Host "✅ where.exe encontró: $whereResult" -ForegroundColor Green
    } else {
        Write-Host "❌ where.exe no encontró python" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error ejecutando where.exe" -ForegroundColor Red
}
