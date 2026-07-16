# Guía de Instalación y Actualización
## Flash Sheet v1.0.0 - Exportación Separada

### 📋 Contenido
1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación Nueva](#instalación-nueva)
3. [Actualización desde Versiones Anteriores](#actualización-desde-versiones-anteriores)
4. [Instalación desde Código Fuente](#instalación-desde-código-fuente)
5. [Verificación de Instalación](#verificación-de-instalación)
6. [Solución de Problemas](#solución-de-problemas)
7. [Configuración Post-Instalación](#configuración-post-instalación)

---

## 🖥️ Requisitos del Sistema

### Requisitos Mínimos

**Sistema Operativo:**
- Windows 10 o superior (64-bit)
- macOS 10.14 (Mojave) o superior
- Ubuntu 18.04 LTS o superior

**Hardware:**
- **Procesador**: Intel i5 / AMD Ryzen 5 o equivalente
- **Memoria RAM**: 4 GB mínimo, 8 GB recomendado
- **Espacio en Disco**: 2 GB para instalación base, 10 GB recomendado
- **Resolución**: 1024x768 mínimo, 1920x1080 recomendado

**Software:**
- **Python**: 3.8, 3.9, 3.10, o 3.11
- **Excel**: 2016 o superior (para funcionalidad completa)
- **Administrador de paquetes**: pip (incluido con Python)

### Requisitos para Funcionalidad Completa

**Para ExcelTemplateSplitter (Exportación Separada):**
- **Memoria RAM**: 8 GB (para datasets > 50K filas)
- **Espacio en Disco**: 3x tamaño de datos originales
- **Python Packages**: pandas, openpyxl, PySide6

**Para Datasets Grandes (> 1M filas):**
- **Memoria RAM**: 16 GB o superior
- **Procesador**: Intel i7 / AMD Ryzen 7 o superior
- **Almacenamiento**: SSD recomendado

---

## 🚀 Instalación Nueva

### Método 1: Instalación Rápida (Recomendado)

**Windows:**
```cmd
# Verificar Python
python --version

# Instalar usando pip
pip install flash-sheet==1.0.0

# O instalar con dependencias opcionales
pip install flash-sheet[full]==1.0.0
```

**macOS/Linux:**
```bash
# Verificar Python 3
python3 --version

# Instalar usando pip
pip3 install flash-sheet==1.0.0

# O instalar con dependencias opcionales
pip3 install flash-sheet[full]==1.0.0
```

### Método 2: Instalación con Entorno Virtual

**Crear entorno virtual:**
```bash
# Crear entorno
python -m venv flash-sheet-env

# Activar entorno
# Windows:
flash-sheet-env\Scripts\activate

# macOS/Linux:
source flash-sheet-env/bin/activate

# Instalar Flash Sheet
pip install flash-sheet==1.0.0
```

### Método 3: Instalación desde Ejecutable

**Windows:**
1. Descargar `FlashSheet-1.0.0-Windows-x86_64.exe`
2. Ejecutar como administrador
3. Seguir el asistente de instalación
4. Verificar que se agregó al PATH del sistema

**macOS:**
1. Descargar `FlashSheet-1.0.0-macOS.dmg`
2. Abrir archivo .dmg
3. Arrastrar Flash Sheet a Applications
4. Verificar en Launchpad

---

## 🔄 Actualización desde Versiones Anteriores

### Backup Recomendado

**Antes de actualizar, crear backup:**
```bash
# Windows
robocopy "%USERPROFILE%\.flash-sheet" "%USERPROFILE%\.flash-sheet-backup-%date%" /E /R:3 /W:1

# macOS/Linux
cp -r ~/.flash-sheet ~/flash-sheet-backup-$(date +%Y%m%d)/
```

### Actualización Simple

**Verificar versión actual:**
```bash
flash-sheet --version
# O si no está en PATH:
python -m flash_sheet --version
```

**Actualizar usando pip:**
```bash
# Actualizar a v1.0.0
pip install --upgrade flash-sheet==1.0.0

# Verificar que se actualizó
pip show flash-sheet
```

### Actualización con Conservación de Configuración

**Pasos recomendados:**

1. **Hacer backup de configuración:**
```bash
# Windows
copy "%USERPROFILE%\.flash-sheet\config.json" "%USERPROFILE%\flash-sheet-config-backup.json"

# macOS/Linux
cp ~/.flash-sheet/config.json ~/flash-sheet-config-backup.json
```

2. **Actualizar aplicación:**
```bash
pip install --upgrade flash-sheet==1.0.0
```

3. **Verificar que la configuración se preservó:**
```bash
# Verificar que la nueva funcionalidad está disponible
flash-sheet --check-features
```

4. **Si hay problemas, restaurar configuración:**
```bash
# Windows
copy "%USERPROFILE%\flash-sheet-config-backup.json" "%USERPROFILE%\.flash-sheet\config.json"

# macOS/Linux
cp ~/flash-sheet-config-backup.json ~/.flash-sheet/config.json
```

### Migración desde v0.x a v1.0.0

**Cambios en la configuración:**
- No requiere migración manual
- La configuración v0.x se convierte automáticamente
- Nuevas opciones se inicializan con valores por defecto

**Verificar migración:**
```python
# Script de verificación
import json
from pathlib import Path

config_path = Path.home() / ".flash-sheet" / "config.json"
if config_path.exists():
    with open(config_path) as f:
        config = json.load(f)
    print("✅ Configuración migrada exitosamente")
    print(f"Versión configurada: {config.get('version', 'unknown')}")
else:
    print("❌ Configuración no encontrada")
```

---

## 🛠️ Instalación desde Código Fuente

### Requisitos para Desarrollo

```bash
# Instalar herramientas de desarrollo
pip install setuptools wheel twine
```

### Clonar y Compilar

```bash
# Clonar repositorio
git clone https://github.com/flash-sheet/flash-sheet.git
cd flash-sheet

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Instalar en modo desarrollo
pip install -e .

# Instalar dependencias adicionales para desarrollo
pip install -r requirements-dev.txt
```

### Compilar Distribución

```bash
# Crear distribución
python setup.py sdist bdist_wheel

# Instalar desde distribución local
pip install dist/flash_sheet-1.0.0-py3-none-any.whl
```

---

## ✅ Verificación de Instalación

### Verificación Básica

**Test 1: Ejecutar aplicación**
```bash
flash-sheet --help
```

**Test 2: Verificar importación de módulos**
```python
# Crear archivo test_installation.py
import sys
try:
    from core.data_handler import ExcelTemplateSplitter
    print("✅ ExcelTemplateSplitter disponible")
    
    from app.widgets.export_separated_dialog import ExportSeparatedDialog
    print("✅ ExportSeparatedDialog disponible")
    
    import openpyxl
    print("✅ OpenPyXL disponible")
    
    import pandas as pd
    print("✅ Pandas disponible")
    
    print("\n🎉 Instalación verificada exitosamente!")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    sys.exit(1)
```

**Ejecutar test:**
```bash
python test_installation.py
```

### Verificación de Funcionalidad

**Test 3: Crear DataFrame de prueba**
```python
# test_functionality.py
import pandas as pd
from core.data_handler import ExcelTemplateSplitter

# Crear datos de prueba
data = {
    'Región': ['Norte', 'Sur', 'Norte', 'Este', 'Sur'] * 100,
    'Producto': ['A', 'B', 'A', 'C', 'B'] * 100,
    'Ventas': list(range(500))
}

df = pd.DataFrame(data)

# Verificar que el separador funciona
try:
    splitter = ExcelTemplateSplitter(df, {})
    print("✅ ExcelTemplateSplitter inicializado correctamente")
    
    # Verificar análisis de datos
    analysis = splitter.analyze_data()
    print(f"✅ Análisis completado: {analysis.estimated_groups} grupos detectados")
    
except Exception as e:
    print(f"❌ Error en funcionalidad: {e}")
```

**Ejecutar test:**
```bash
python test_functionality.py
```

### Verificación de UI

**Test 4: Verificar interfaz gráfica**
```python
# test_ui.py
import sys
from PySide6.QtWidgets import QApplication
from app.widgets.export_separated_dialog import ExportSeparatedDialog
import pandas as pd

try:
    app = QApplication(sys.argv)
    data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
    df = pd.DataFrame(data)
    
    dialog = ExportSeparatedDialog(df)
    print("✅ ExportSeparatedDialog creado correctamente")
    print("✅ Interfaz gráfica disponible")
    
except Exception as e:
    print(f"❌ Error en interfaz: {e}")
```

---

## 🔧 Solución de Problemas

### Problema 1: Error "python no se reconoce"

**Windows:**
```cmd
# Verificar instalación de Python
where python
# Si no se encuentra, reinstalar Python marcando "Add to PATH"
```

**macOS:**
```bash
# Instalar Python desde python.org
# O usar Homebrew:
brew install python
```

**Linux:**
```bash
# Ubuntu/Debian:
sudo apt update
sudo apt install python3 python3-pip

# CentOS/RHEL:
sudo yum install python3 python3-pip
```

### Problema 2: Error "pip no se reconoce"

**Solución:**
```cmd
# Windows - usar python -m pip
python -m pip install flash-sheet==1.0.0

# macOS/Linux - usar pip3
pip3 install flash-sheet==1.0.0
```

### Problema 3: Error de permisos

**Linux/macOS:**
```bash
# Usar --user para instalación local
pip install --user flash-sheet==1.0.0

# O usar sudo (no recomendado)
sudo pip install flash-sheet==1.0.0
```

**Windows:**
```cmd
# Ejecutar como administrador
# O usar --user
python -m pip install --user flash-sheet==1.0.0
```

### Problema 4: Error "Microsoft Visual C++ 14.0 is required"

**Windows:**
1. Descargar e instalar "Microsoft C++ Build Tools"
2. O instalar "Visual Studio Community" (gratuito)
3. Reiniciar sistema y intentar instalación nuevamente

**Alternativa:**
```cmd
# Usar versión pre-compilada
pip install --only-binary=all flash-sheet==1.0.0
```

### Problema 5: OpenPyXL falla en macOS Big Sur+

**Solución:**
```bash
# Reinstalar openpyxl con dependencias actualizadas
pip uninstall openpyxl
pip install --upgrade openpyxl
```

### Problema 6: Memoria insuficiente con datasets grandes

**Solución - Configuración de memoria:**
```python
# Configurar límites de memoria en ~/.flash-sheet/config.json
{
    "export_separated": {
        "max_memory_mb": 4096,
        "chunk_size": 5000,
        "aggressive_chunking": true
    }
}
```

### Problema 7: ExportSeparatedDialog no aparece

**Verificar dependencias Qt:**
```bash
pip install --upgrade PySide6
```

**Verificar permisos de archivos:**
```bash
# Crear directorio si no existe
mkdir -p ~/.flash-sheet
chmod 755 ~/.flash-sheet
```

---

## ⚙️ Configuración Post-Instalación

### Configuración Inicial

**1. Crear archivo de configuración:**
```bash
# Windows
mkdir "%USERPROFILE%\.flash-sheet"
echo {} > "%USERPROFILE%\.flash-sheet\config.json"

# macOS/Linux
mkdir -p ~/.flash-sheet
touch ~/.flash-sheet/config.json
```

**2. Configuración básica recomendada:**
```json
{
    "version": "1.0.0",
    "theme": "light",
    "language": "es",
    "auto_save": true,
    "recent_files_limit": 10,
    "export_separated": {
        "default_memory_limit_mb": 2048,
        "auto_chunking": true,
        "validation_level": "strict",
        "backup_before_export": true
    }
}
```

### Configuración para Entorno Empresarial

**Optimización para datasets grandes:**
```json
{
    "export_separated": {
        "max_memory_mb": 8192,
        "chunk_size": 10000,
        "parallel_processing": true,
        "aggressive_chunking": true,
        "validation_level": "permissive",
        "log_level": "INFO"
    }
}
```

**Configuración para IT:**
```json
{
    "enterprise": {
        "disable_telemetry": true,
        "restrict_network": true,
        "allowed_file_extensions": [".xlsx", ".csv", ".json"],
        "max_file_size_mb": 500,
        "audit_log": true
    }
}
```

### Verificar Configuración

**Script de configuración:**
```python
# verify_config.py
import json
from pathlib import Path
import tempfile

def check_configuration():
    config_path = Path.home() / ".flash-sheet" / "config.json"
    
    if not config_path.exists():
        print("⚠️  Archivo de configuración no encontrado")
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        version = config.get('version', 'unknown')
        print(f"✅ Configuración cargada (versión: {version})")
        
        # Verificar configuraciones críticas
        if 'export_separated' in config:
            print("✅ Configuración de exportación separada encontrada")
        else:
            print("⚠️  Configuración de exportación separada no encontrada")
            
        return True
        
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return False

if __name__ == "__main__":
    check_configuration()
```

---

## 🆘 Soporte de Instalación

### Logs de Instalación

**Ubicaciones de logs:**
- Windows: `%TEMP%\flash-sheet-install.log`
- macOS: `/tmp/flash-sheet-install.log`
- Linux: `/tmp/flash-sheet-install.log`

### Información del Sistema

**Crear reporte de información del sistema:**
```python
# system_info.py
import sys
import platform
import subprocess
import pkg_resources

def generate_system_report():
    print("=== Flash Sheet - Información del Sistema ===")
    print(f"Python: {sys.version}")
    print(f"Plataforma: {platform.platform()}")
    print(f"Arquitectura: {platform.architecture()}")
    
    # Versiones de paquetes instalados
    packages = ['pandas', 'openpyxl', 'PySide6', 'numpy']
    for pkg in packages:
        try:
            version = pkg_resources.get_distribution(pkg).version
            print(f"{pkg}: {version}")
        except:
            print(f"{pkg}: NO INSTALADO")
    
    # Verificar Flash Sheet
    try:
        import flash_sheet
        print(f"Flash Sheet: {flash_sheet.__version__}")
    except:
        print("Flash Sheet: NO INSTALADO")

if __name__ == "__main__":
    generate_system_report()
```

### Contactar Soporte

**Información a incluir en reportes:**
1. Output del script `system_info.py`
2. Comando exacto usado para instalación
3. Error completo (traceback)
4. Logs de instalación relevantes

**Canales de soporte:**
- **GitHub Issues**: Para bugs y problemas técnicos
- **Documentación**: `docs/user_guide/README.md`
- **Email**: support@flash-sheet.com (para clientes empresariales)

---

## 🎉 ¡Instalación Completada!

Si has llegado hasta aquí, Flash Sheet v1.0.0 debería estar funcionando correctamente con la nueva funcionalidad de **Exportación de Datos Separados con Plantillas Excel**.

**Próximos pasos:**
1. [Guía de Usuario](README.md) - Aprende a usar las nuevas funcionalidades
2. [Configuración Avanzada](advanced_configuration.md) - Optimiza para tu entorno
3. [Ejemplos Prácticos](examples_and_use_cases.md) - Casos de uso reales

**¡Disfruta la nueva funcionalidad!**

---

*Guía de Instalación v1.0.0 - Actualizada el 5 de Noviembre, 2025*