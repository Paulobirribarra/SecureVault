# ====================================================================
# SecureVault - Script de Configuración Inicial
# ====================================================================
# Este script automatiza la configuración inicial del proyecto SecureVault
# Ejecutar desde la raíz del proyecto: .\scripts\setup_project.ps1

Write-Host "🔐 SecureVault - Configuración Inicial" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Verificar que estamos en la raíz del proyecto
if (-not (Test-Path "backend") -or -not (Test-Path "secure-app-frontend")) {
    Write-Host "❌ Error: Ejecutar desde la raíz del proyecto SecureVault" -ForegroundColor Red
    exit 1
}

# Función para detectar la mejor instalación de Python
function Get-BestPython {
    Write-Host "🔍 Detectando Python universal..." -ForegroundColor Yellow
    
    # Rutas comunes de Python (universales)
    $pythonLocations = @(
        "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe",
        "C:\Python*\python.exe",
        "C:\Program Files\Python*\python.exe",
        "C:\Program Files (x86)\Python*\python.exe"
    )
    
    $validPythons = @()
    
    foreach ($pattern in $pythonLocations) {
        $found = Get-ChildItem $pattern -ErrorAction SilentlyContinue
        foreach ($pythonExe in $found) {
            try {
                $version = & $pythonExe --version 2>$null
                if ($version -and $version -match "Python 3\.\d+") {
                    $validPythons += @{
                        Path = $pythonExe.FullName
                        Version = $version
                        Score = if ($pythonExe.FullName -like "*Programs\Python*") { 100 } else { 50 }
                    }
                }
            }
            catch { }
        }
    }
    
    # También verificar 'python' en PATH (excluyendo Microsoft Store)
    try {
        $whereOutput = & where.exe python 2>$null
        if ($whereOutput) {
            foreach ($path in ($whereOutput -split "`n")) {
                if ($path -and $path -notlike "*WindowsApps*" -and $path -notlike "*Microsoft.WindowsApps*") {
                    try {
                        $version = & $path --version 2>$null
                        if ($version -and $version -match "Python 3\.\d+") {
                            $validPythons += @{
                                Path = $path
                                Version = $version
                                Score = 75
                            }
                        }
                    }
                    catch { }
                }
            }
        }
    }
    catch { }
    
    if ($validPythons.Count -eq 0) {
        Write-Host "❌ No se encontró Python 3.x instalado" -ForegroundColor Red
        Write-Host "💡 Instalar Python desde: https://python.org/downloads/" -ForegroundColor Yellow
        return $null
    }
    
    # Remover duplicados y ordenar por score
    $uniquePythons = $validPythons | Sort-Object Path -Unique | Sort-Object Score -Descending
    
    Write-Host "📍 Versiones de Python encontradas:" -ForegroundColor Gray
    foreach ($python in $uniquePythons) {
        $score = if ($python.Score -eq 100) { "✅ RECOMENDADO" } 
                elseif ($python.Score -eq 75) { "👍 BUENO" } 
                else { "⚠️  BÁSICO" }
        Write-Host "   $($python.Version) - $($python.Path) [$score]" -ForegroundColor Gray
    }
    
    return $uniquePythons[0].Path
}

Write-Host "📁 Configurando Backend (Django)..." -ForegroundColor Yellow

# Cambiar al directorio backend
Set-Location "backend"

# Detectar la mejor versión de Python
$bestPython = Get-BestPython

if (-not $bestPython) {
    Write-Host "❌ No se puede continuar sin Python" -ForegroundColor Red
    Set-Location ".."
    exit 1
}

Write-Host "🐍 Usando Python: $bestPython" -ForegroundColor Green

# Verificar versión de Python
try {
    $pythonVersion = & $bestPython --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error: Python no funciona correctamente" -ForegroundColor Red
    exit 1
}

# Crear entorno virtual si no existe
if (-not (Test-Path "venv")) {
    Write-Host "🔧 Creando entorno virtual con $bestPython..." -ForegroundColor Yellow
    & $bestPython -m venv venv
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error: No se pudo crear el entorno virtual" -ForegroundColor Red
        exit 1
    }
}

# Verificar que el entorno virtual se creó correctamente
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "❌ Error: Entorno virtual no se creó correctamente" -ForegroundColor Red
    exit 1
}

# Activar entorno virtual
Write-Host "🔧 Activando entorno virtual..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Usar Python del entorno virtual
$venvPython = "venv\Scripts\python.exe"

# Actualizar pip y setuptools usando Python del venv
Write-Host "🔧 Actualizando herramientas en entorno virtual..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install --upgrade setuptools

# Instalar dependencias usando Python del venv
Write-Host "📦 Instalando dependencias de Python..." -ForegroundColor Yellow
& $venvPython -m pip install -r requirements.txt

# Configurar archivo .env
if (-not (Test-Path ".env")) {
    Write-Host "🔧 Configurando archivo .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  IMPORTANTE: Editar backend\.env con tu contraseña de PostgreSQL" -ForegroundColor Magenta
}

# Volver a la raíz
Set-Location ".."

Write-Host "🅰️ Configurando Frontend (Angular)..." -ForegroundColor Yellow

# Cambiar al directorio frontend
Set-Location "secure-app-frontend"

# Verificar Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js encontrado: $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error: Node.js no encontrado. Instalar Node.js 18+" -ForegroundColor Red
    Set-Location ".."
    exit 1
}

# Verificar si Angular CLI está instalado
try {
    $ngVersion = ng version --skip-git 2>&1
    Write-Host "✅ Angular CLI encontrado" -ForegroundColor Green
}
catch {
    Write-Host "🔧 Instalando Angular CLI..." -ForegroundColor Yellow
    npm install -g @angular/cli
}

# Instalar dependencias de Node.js
Write-Host "📦 Instalando dependencias de Node.js..." -ForegroundColor Yellow
npm install

# Volver a la raíz
Set-Location ".."

Write-Host ""
Write-Host "🎉 Configuración inicial completada!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximos pasos:" -ForegroundColor Cyan
Write-Host "1. Configurar PostgreSQL y crear base de datos 'secure_app_db'" -ForegroundColor White
Write-Host "2. Editar backend\.env con tu contraseña de PostgreSQL" -ForegroundColor White
Write-Host "3. Ejecutar: .\scripts\setup_database.ps1" -ForegroundColor White
Write-Host "4. Ejecutar: .\scripts\run_servers.ps1" -ForegroundColor White
Write-Host ""
