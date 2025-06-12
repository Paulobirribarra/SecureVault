#!/usr/bin/env python
"""
Script de inicialización para configurar las variables de entorno de Django.
"""
import os
import sys
import django
from pathlib import Path

# Agregar el directorio backend al PYTHONPATH
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'secure_project.settings')

try:
    django.setup()
    print("✅ Django configurado correctamente")
    print(f"📂 Backend directory: {backend_dir}")
    print(f"🐍 Python path: {sys.executable}")
    print(f"🔧 Django version: {django.get_version()}")
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    sys.exit(1)
