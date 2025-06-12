@echo off
echo Configurando VS Code para usar el entorno virtual...

:: Activar el entorno virtual
call "%~dp0backend\venv\Scripts\activate.bat"

:: Verificar que Python está funcionando
echo Verificando Python...
python --version

:: Verificar que Django está instalado
echo Verificando Django...
python -c "import django; print('Django version:', django.get_version())"

:: Abrir VS Code con la configuración correcta
echo Abriendo VS Code...
code .

echo.
echo ===================================
echo VS Code configurado correctamente!
echo ===================================
echo.
echo Para seleccionar el intérprete manualmente:
echo 1. Presiona Ctrl+Shift+P
echo 2. Escribe "Python: Select Interpreter"
echo 3. Selecciona: .\backend\venv\Scripts\python.exe
echo.
pause
