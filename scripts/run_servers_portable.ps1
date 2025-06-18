# ====================================================================
# SecureVault - Ejecutar Servidores (VERSION PORTABLE)
# ====================================================================
# Este script inicia ambos servidores detectando automaticamente las rutas
# Funciona desde cualquier directorio y para cualquier usuario

Write-Host "Iniciando SecureVault - Servidores (Portable)" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# Funcion para encontrar la raiz del proyecto
function Find-ProjectRoot {
    param($startPath)
    
    $currentPath = $startPath
    while ($currentPath -and $currentPath -ne (Split-Path -Parent $currentPath)) {
        $backendCheck = Join-Path $currentPath "backend\manage.py"
        $frontendCheck = Join-Path $currentPath "secure-app-frontend\package.json"
        
        if ((Test-Path $backendCheck) -and (Test-Path $frontendCheck)) {
            return $currentPath
        }
        $currentPath = Split-Path -Parent $currentPath
    }
    return $null
}

# Detectar la raiz del proyecto
$projectRoot = if ($PSScriptRoot) { 
    # Si se ejecuta como script, buscar desde el directorio padre de scripts
    Find-ProjectRoot (Split-Path -Parent $PSScriptRoot)
} else { 
    # Si se ejecuta interactivamente, buscar desde el directorio actual
    Find-ProjectRoot $PWD.Path
}

if (-not $projectRoot) {
    Write-Host "ERROR: No se pudo encontrar el proyecto SecureVault" -ForegroundColor Red
    Write-Host "   Asegurate de que los directorios 'backend' y 'secure-app-frontend' existan" -ForegroundColor Yellow
    Write-Host "   con 'manage.py' y 'package.json' respectivamente" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "Proyecto encontrado en: $projectRoot" -ForegroundColor Green

# Verificar estructura del proyecto
$backendPath = Join-Path $projectRoot "backend"
$frontendPath = Join-Path $projectRoot "secure-app-frontend"
$pythonExe = Join-Path $backendPath "venv\Scripts\python.exe"

Write-Host ""
Write-Host "Verificando componentes..." -ForegroundColor Yellow

if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR: Entorno virtual de Python no encontrado" -ForegroundColor Red
    Write-Host "   Esperado en: $pythonExe" -ForegroundColor Gray
    Write-Host "   Ejecutar primero: .\scripts\setup_project.ps1" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

if (-not (Test-Path (Join-Path $frontendPath "node_modules"))) {
    Write-Host "AVISO: Node modules no encontrados, verificando npm..." -ForegroundColor Yellow
}

Write-Host "Estructura del proyecto verificada correctamente" -ForegroundColor Green

# Crear script para backend
$backendScript = @"
Write-Host 'Iniciando Backend Django...' -ForegroundColor Yellow
Set-Location '$backendPath'

if (-not (Test-Path '$pythonExe')) {
    Write-Host 'ERROR: Python no encontrado en entorno virtual' -ForegroundColor Red
    Read-Host 'Presiona Enter para cerrar...'
    exit 1
}

try {
    Write-Host 'Verificando entorno Python...' -ForegroundColor Gray
    & '$pythonExe' --version
    
    Write-Host ''
    Write-Host 'Backend iniciado en http://localhost:8000' -ForegroundColor Green
    Write-Host 'API Docs: http://localhost:8000/api/docs/' -ForegroundColor Cyan
    Write-Host 'Admin: http://localhost:8000/admin/' -ForegroundColor Cyan
    Write-Host ''
    Write-Host 'Presiona Ctrl+C para detener el servidor' -ForegroundColor Yellow
    Write-Host ''
    
    & '$pythonExe' manage.py runserver
} catch {
    Write-Host 'ERROR al iniciar Django:' -ForegroundColor Red
    Write-Host `$_.Exception.Message -ForegroundColor Red
    Read-Host 'Presiona Enter para cerrar...'
    exit 1
}
"@

# Crear script para frontend
$frontendScript = @"
Write-Host 'Iniciando Frontend Angular...' -ForegroundColor Yellow
Set-Location '$frontendPath'

if (-not (Test-Path 'package.json')) {
    Write-Host 'ERROR: package.json no encontrado' -ForegroundColor Red
    Read-Host 'Presiona Enter para cerrar...'
    exit 1
}

if (-not (Test-Path 'node_modules')) {
    Write-Host 'Instalando dependencias npm...' -ForegroundColor Yellow
    npm install
    if (`$LASTEXITCODE -ne 0) {
        Write-Host 'ERROR al instalar dependencias' -ForegroundColor Red
        Read-Host 'Presiona Enter para cerrar...'
        exit 1
    }
}

try {
    Write-Host ''
    Write-Host 'Frontend iniciado en http://localhost:4200' -ForegroundColor Green
    Write-Host ''
    Write-Host 'Presiona Ctrl+C para detener el servidor' -ForegroundColor Yellow
    Write-Host ''
    
    npm start
} catch {
    Write-Host 'ERROR al iniciar Angular:' -ForegroundColor Red
    Write-Host `$_.Exception.Message -ForegroundColor Red
    Read-Host 'Presiona Enter para cerrar...'
    exit 1
}
"@

Write-Host ""
Write-Host "Iniciando servidores..." -ForegroundColor Yellow

# Iniciar backend en ventana separada
Start-Process powershell -ArgumentList @(
    "-NoExit"
    "-ExecutionPolicy", "Bypass"
    "-Command", $backendScript
)

# Esperar un poco antes de iniciar frontend
Start-Sleep -Seconds 3

# Iniciar frontend en ventana separada
Start-Process powershell -ArgumentList @(
    "-NoExit"
    "-ExecutionPolicy", "Bypass" 
    "-Command", $frontendScript
)

Write-Host ""
Write-Host "Servidores iniciados correctamente!" -ForegroundColor Green
Write-Host ""
Write-Host "URLs disponibles:" -ForegroundColor Cyan
Write-Host "   Frontend:      http://localhost:4200" -ForegroundColor White
Write-Host "   Backend API:   http://localhost:8000/api" -ForegroundColor White
Write-Host "   Documentacion: http://localhost:8000/api/docs/" -ForegroundColor White
Write-Host "   Admin Django:  http://localhost:8000/admin/" -ForegroundColor White
Write-Host ""
Write-Host "Para detener: Cerrar las ventanas de PowerShell o presionar Ctrl+C" -ForegroundColor Gray
Write-Host ""
Write-Host "Proyecto ejecutandose desde: $projectRoot" -ForegroundColor Gray
Write-Host ""
