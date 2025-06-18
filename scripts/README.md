# 📜 Scripts de SecureVault

Esta carpeta contiene scripts de PowerShell para automatizar las tareas comunes del proyecto SecureVault.

## ⚠️ IMPORTANTE: Problema de Múltiples Versiones de Python

### 🔍 **Si tienes problemas con Python:**

**Síntomas comunes:**
- ❌ `ModuleNotFoundError: No module named 'django'`
- ❌ `python` no reconocido o usa versión incorrecta
- ❌ Dependencias instaladas pero no encontradas

**Causa:** Múltiples instalaciones de Python
- 🟡 Python desde Microsoft Store
- 🟡 Python desde python.org
- ✅ Python del entorno virtual (correcto)

**Verificar cuántos Python tienes:**
```powershell
where.exe python
```

**Solución recomendada:**
1. **DESINSTALAR** Python de Microsoft Store (Settings > Apps)
2. **MANTENER** solo Python desde python.org
3. **USAR** nuestros scripts que especifican el Python correcto

### 🛠️ **Desinstalar Python de Microsoft Store:**
1. `Windows + I` → Apps
2. Buscar "Python"
3. Desinstalar cualquier versión de "Microsoft Corporation"
4. **Mantener** solo la versión de "Python Software Foundation"

## 🚀 Scripts Disponibles

### 1. `setup_project.ps1` - Configuración Inicial
Configura el entorno de desarrollo por primera vez.

```powershell
.\scripts\setup_project.ps1
```

**¿Qué hace?**
- ✅ Verifica Python y Node.js
- 🔧 Crea entorno virtual de Python
- 📦 Instala dependencias de backend y frontend
- 🔧 Instala Angular CLI si no está disponible
- 📄 Copia archivo .env.example a .env

### 2. `setup_database.ps1` - Configuración de Base de Datos
Configura PostgreSQL y ejecuta migraciones.

```powershell
.\scripts\setup_database.ps1
```

**¿Qué hace?**
- 🗄️ Crea base de datos PostgreSQL (opcional)
- 🔧 Crea migraciones de Django
- 📊 Aplica migraciones a la base de datos
- 👤 Crea superusuario (opcional)

### 3. `run_servers.ps1` - Ejecutar Servidores
Inicia backend y frontend simultáneamente.

```powershell
.\scripts\run_servers.ps1
```

**¿Qué hace?**
- 🐍 Inicia servidor Django (puerto 8000)
- 🅰️ Inicia servidor Angular (puerto 4200)
- 🌐 Muestra URLs disponibles

### 4. `clean_project.ps1` - Limpieza de Proyecto
Limpia archivos temporales y resetea el proyecto.

```powershell
# Solo limpiar caché
.\scripts\clean_project.ps1 -Cache

# Resetear base de datos
.\scripts\clean_project.ps1 -Database

# Limpieza completa (incluye node_modules y venv)
.\scripts\clean_project.ps1 -Full
```

## 🔄 Flujo de Trabajo Recomendado

### Primera vez (PC nuevo):
1. `.\scripts\setup_project.ps1`
2. Editar `backend\.env` con tu contraseña de PostgreSQL
3. `.\scripts\setup_database.ps1`
4. `.\scripts\run_servers.ps1`

### Desarrollo diario:
```powershell
.\scripts\run_servers.ps1
```

### Cuando hay problemas:
```powershell
.\scripts\clean_project.ps1 -Cache
.\scripts\setup_database.ps1
```

### Reset completo:
```powershell
.\scripts\clean_project.ps1 -Full
.\scripts\setup_project.ps1
.\scripts\setup_database.ps1
```

## 🛠️ Requisitos

- **PowerShell 5.0+** (incluido en Windows 10+)
- **Permisos de ejecución** (ejecutar una vez como administrador):
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

## 📋 Solución de Problemas

### ⚠️ **PROBLEMA CRÍTICO: Múltiples versiones de Python**

Si tienes Python de la **web oficial** + **Microsoft Store**, los scripts pueden fallar:

```powershell
# Verificar problema
where.exe python

# Si ves múltiples rutas (problemático):
# C:\Users\[usuario]\AppData\Local\Microsoft\WindowsApps\python.exe  ← PROBLEMÁTICO
# C:\Users\[usuario]\AppData\Local\Programs\Python\Python313\python.exe  ← OK
```

**💡 Solución:**
Los scripts están configurados para usar rutas absolutas, pero si fallan:

```powershell
# 1. Desinstalar Python de Microsoft Store (recomendado)
# Configuración → Apps → buscar "Python" → Desinstalar versión de Store

# 2. O ejecutar scripts con Python específico
# Editar temporalmente los scripts para usar ruta absoluta:
# Cambiar: python manage.py runserver
# Por: & "C:\Users\[usuario]\AppData\Local\Programs\Python\Python313\python.exe" manage.py runserver
```

### Error "no se puede cargar el archivo porque la ejecución de scripts está deshabilitada"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error "psql no se reconoce como comando"
Agregar PostgreSQL al PATH del sistema o usar la ruta completa:
```powershell
# Ejemplo de ruta completa
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
```

### Puertos en uso
Los scripts verifican y muestran mensajes si los puertos están ocupados.

## 🚨 Solución de Problemas Comunes

### 🐍 **Error: Django no encontrado**
```bash
ModuleNotFoundError: No module named 'django'
```

**Diagnóstico:**
```powershell
# 1. Verificar múltiples Python
where.exe python

# 2. Verificar entorno virtual activo
python -c "import sys; print(sys.executable)"

# 3. Verificar Django instalado
python -c "import django; print(django.get_version())"
```

**Solución:**
1. **DESINSTALAR Python de Microsoft Store** (principal causa)
2. Re-ejecutar: `.\scripts\setup_project.ps1`
3. Si persiste, usar comando directo:
```powershell
# Desde backend/
.\venv\Scripts\python.exe manage.py runserver
```

### 🅰️ **Error: npm no encuentra package.json**
```bash
npm error enoent Could not read package.json
```

**Causa:** PowerShell no está en el directorio correcto

**Solución:**
```powershell
# Verificar directorio
cd E:\Paulo\Github\SecureVault\secure-app-frontend
npm start
```

### ⚡ **Error: Execution Policy**
```bash
la ejecución de scripts está deshabilitada en este sistema
```

**Solución:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

### 🔌 **Error: Puertos ocupados**
**Backend (8000) o Frontend (4200) ya en uso**

**Verificar:**
```powershell
netstat -an | findstr "8000"
netstat -an | findstr "4200"
```

**Solución:**
```powershell
# Matar procesos en puerto 8000
netstat -ano | findstr "8000"
taskkill /PID [PID_NUMBER] /F

# O usar puertos alternativos
python manage.py runserver 8001
ng serve --port 4201
```

## ✅ **Portabilidad Garantizada**

### 🌍 **Scripts Universales**
Todos los scripts utilizan **variables de entorno de Windows** y rutas relativas, garantizando que funcionen en cualquier PC:

- ✅ **`$env:LOCALAPPDATA`** - Detecta automáticamente el directorio del usuario
- ✅ **`$PSScriptRoot`** - Usa la ubicación del script como referencia
- ✅ **`Split-Path -Parent`** - Calcula rutas relativas dinámicamente
- ✅ **Detección automática de Python** - Busca en ubicaciones estándar

### 📱 **Comprobado en:**
- ✅ Diferentes usuarios de Windows
- ✅ Diferentes ubicaciones de proyecto
- ✅ Múltiples versiones de Python 3.x
- ✅ Instalaciones estándar desde python.org

### 🧪 **Verificar portabilidad:**
```powershell
.\scripts\test_portability.ps1
```

---

## 🔒 Seguridad

- ❌ **NUNCA** subas la carpeta `scripts/` con credenciales hardcodeadas
- ✅ Los scripts usan variables de entorno y input del usuario
- ✅ Las contraseñas se solicitan de forma segura (AsSecureString)
