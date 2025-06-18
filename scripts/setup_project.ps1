# ====================================================================
# SecureVault - Script de Configuración Inicial (SIMPLIFICADO)
# ====================================================================

Write-Host "🔐 SecureVault - Configuración Inicial" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Verificar que estamos en la raíz del proyecto
if (-not (Test-Path "backend") -or -not (Test-Path "secure-app-frontend")) {
    Write-Host "❌ Error: Ejecutar desde la raíz del proyecto SecureVault" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Configurando Backend (Django)..." -ForegroundColor Yellow
Set-Location "backend"

# Detectar Python de forma simple
Write-Host "🔍 Detectando Python..." -ForegroundColor Yellow

$bestPython = $null

# Buscar en ubicación estándar primero
$standardPath = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
if (Test-Path $standardPath) {
    try {
        $version = & $standardPath --version 2>$null
        if ($version -match "Python 3\.\d+") {
            $bestPython = $standardPath
            Write-Host "✅ Python encontrado: $version" -ForegroundColor Green
            Write-Host "📍 Ubicación: $standardPath" -ForegroundColor Gray
        }
    }
    catch { }
}

# Si no se encontró, buscar cualquier Python3.x en Programs
if (-not $bestPython) {
    $pythonDir = "$env:LOCALAPPDATA\Programs\Python"
    if (Test-Path $pythonDir) {
        $pythonFolders = Get-ChildItem $pythonDir -Directory | Where-Object { $_.Name -match "Python3\d+" } | Sort-Object Name -Descending
        foreach ($folder in $pythonFolders) {
            $pythonExe = Join-Path $folder.FullName "python.exe"
            if (Test-Path $pythonExe) {
                try {
                    $version = & $pythonExe --version 2>$null
                    if ($version -match "Python 3\.\d+") {
                        $bestPython = $pythonExe
                        Write-Host "✅ Python encontrado: $version" -ForegroundColor Green
                        Write-Host "📍 Ubicación: $pythonExe" -ForegroundColor Gray
                        break
                    }
                }
                catch { }
            }
        }
    }
}

if (-not $bestPython) {
    Write-Host "❌ No se encontró Python 3.x instalado" -ForegroundColor Red
    Write-Host "💡 Instalar Python desde: https://python.org/downloads/" -ForegroundColor Yellow
    Set-Location ".."
    exit 1
}

Write-Host "🐍 Usando Python: $bestPython" -ForegroundColor Green

# Crear entorno virtual
if (-not (Test-Path "venv")) {
    Write-Host "🔧 Creando entorno virtual..." -ForegroundColor Yellow
    & $bestPython -m venv venv
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error: No se pudo crear el entorno virtual" -ForegroundColor Red
        Set-Location ".."
        exit 1
    }
    Write-Host "✅ Entorno virtual creado" -ForegroundColor Green
}
else {
    Write-Host "✅ Entorno virtual ya existe" -ForegroundColor Green
}

# Instalar dependencias
Write-Host "📦 Instalando dependencias de Python..." -ForegroundColor Yellow
$venvPython = "venv\Scripts\python.exe"

# Actualizar pip
& $venvPython -m pip install --upgrade pip setuptools

# Instalar requirements
& $venvPython -m pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencias de Python instaladas" -ForegroundColor Green
}
else {
    Write-Host "❌ Error instalando dependencias de Python" -ForegroundColor Red
}

# Configurar .env
if (-not (Test-Path ".env")) {
    Write-Host "📄 Configurando archivo .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Archivo .env creado desde .env.example" -ForegroundColor Green
    Write-Host "⚠️  Revisar y ajustar configuración en .env" -ForegroundColor Yellow
}
else {
    Write-Host "✅ Archivo .env ya existe" -ForegroundColor Green
}

Set-Location ".."

# Configurar Frontend
Write-Host "🅰️ Configurando Frontend (Angular)..." -ForegroundColor Yellow
Set-Location "secure-app-frontend"

# Verificar Node.js
try {
    $nodeVersion = & node --version 2>$null
    Write-Host "✅ Node.js encontrado: $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Node.js no encontrado. Instalar desde: https://nodejs.org/" -ForegroundColor Red
    Set-Location ".."
    exit 1
}

# Instalar dependencias npm
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Instalando dependencias de Node.js..." -ForegroundColor Yellow
    npm install
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencias de Node.js instaladas" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Error instalando dependencias de Node.js" -ForegroundColor Red
    }
}
else {
    Write-Host "✅ Dependencias de Node.js ya instaladas" -ForegroundColor Green
}

Set-Location ".."

Write-Host ""
Write-Host "🎉 Configuración inicial completada!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximos pasos:" -ForegroundColor Cyan
Write-Host "   1. Configurar base de datos: .\scripts\setup_database.ps1" -ForegroundColor White
Write-Host "   2. Ejecutar servidores: .\scripts\run_servers.ps1" -ForegroundColor White
Write-Host ""
