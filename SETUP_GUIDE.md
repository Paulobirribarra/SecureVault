# 🔧 Guía de Configuración - SecureVault

## ⚠️ PROBLEMA CRÍTICO: Múltiples versiones de Python

### 🔍 Diagnóstico
Si tienes problemas con Django/Python, verifica las instalaciones:

```powershell
where.exe python
```

**❌ Problemático (múltiples versiones):**
```
E:\Paulo\Github\SecureVault\backend\venv\Scripts\python.exe    ← Entorno virtual (CORRECTO)
C:\Users\[usuario]\AppData\Local\Microsoft\WindowsApps\python.exe    ← Microsoft Store (PROBLEMÁTICO)
C:\Users\[usuario]\AppData\Local\Programs\Python\Python313\python.exe    ← python.org (OK)
```

### 💡 Soluciones

#### **Opción A: Desinstalar Python de Microsoft Store (Recomendado)**
1. `Windows + I` → Apps
2. Buscar "Python" 
3. Desinstalar versión de Microsoft Store
4. Mantener solo la versión de python.org

#### **Opción B: Usar Scripts Mejorados**
Los scripts en `/scripts/` ya están configurados para:
- ✅ Detectar automáticamente la mejor versión de Python
- ✅ Evitar la versión de Microsoft Store
- ✅ Usar rutas absolutas para entornos virtuales
- ✅ Diagnosticar problemas de PATH

## 🚀 Configuración Automática (Recomendada)

### 1. Primera vez:
```powershell
# Desde la raíz del proyecto
.\scripts\setup_project.ps1     # Configura entorno
# Editar backend\.env con tu contraseña de PostgreSQL
.\scripts\setup_database.ps1    # Configura base de datos
.\scripts\run_servers.ps1       # Inicia servidores
```

### 2. Uso diario:
```powershell
.\scripts\run_servers.ps1
```

### 3. Si hay problemas:
```powershell
.\scripts\clean_project.ps1 -Cache
.\scripts\setup_database.ps1
```

## 🛠️ Configuración Manual (Si scripts fallan)

### Backend:
```powershell
cd backend

# Usar Python específico (NO Microsoft Store)
C:\Users\[usuario]\AppData\Local\Programs\Python\Python313\python.exe -m venv venv

# Activar entorno virtual
& "venv\Scripts\Activate.ps1"

# Instalar dependencias
venv\Scripts\python.exe -m pip install -r requirements.txt

# Ejecutar servidor
venv\Scripts\python.exe manage.py runserver
```

### Frontend:
```powershell
cd secure-app-frontend

# Verificar directorio correcto
Get-Location  # Debe ser ...\secure-app-frontend
Test-Path package.json  # Debe ser True

# Instalar dependencias
npm install

# Ejecutar servidor
npm start
```

## 🔍 Verificación de Funcionamiento

### ✅ Backend funcionando:
- **URL**: http://localhost:8000
- **Admin**: http://localhost:8000/admin/
- **API**: http://localhost:8000/api/

### ✅ Frontend funcionando:
- **URL**: http://localhost:4200

### 🐛 Depuración común:
```powershell
# Verificar Python en entorno virtual
backend\venv\Scripts\python.exe -c "import django; print('Django:', django.get_version())"

# Verificar npm en directorio correcto
cd secure-app-frontend
npm --version
```

## 📝 Notas Importantes

1. **PowerShell**: Usar PowerShell 5+ (incluido en Windows 10+)
2. **Permisos**: Ejecutar una vez: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. **PostgreSQL**: Debe estar instalado y ejecutándose
4. **Puertos**: 8000 (backend) y 4200 (frontend) deben estar libres

## 🆘 Soporte

Si sigues teniendo problemas:
1. Verificar versiones de Python con `where.exe python`
2. Desinstalar Python de Microsoft Store
3. Usar solo Python de python.org
4. Ejecutar scripts desde la raíz del proyecto
5. Verificar que PostgreSQL esté ejecutándose

## 🎯 Resultado Esperado

Después de seguir esta guía:
- ✅ Backend en http://localhost:8000
- ✅ Frontend en http://localhost:4200
- ✅ Sin errores de importación de Django
- ✅ Entorno virtual funcionando correctamente
