@echo off
echo Activando entorno virtual...
call "%~dp0backend\venv\Scripts\activate.bat"
echo Entorno virtual activado!
echo Para instalar dependencias ejecuta: pip install -r requirements.txt
cmd /k
