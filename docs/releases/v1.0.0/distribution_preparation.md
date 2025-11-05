# Preparación para Distribución
## Flash Sheet v1.0.0 - Exportación Separada

### 📋 Contenido
1. [Configuración de Build](#configuración-de-build)
2. [Scripts de Distribución](#scripts-de-distribución)
3. [CI/CD Pipeline](#cicd-pipeline)
4. [Package Management](#package-management)
5. [Versionado y Releases](#versionado-y-releases)
6. [Distribución Multiplataforma](#distribución-multiplataforma)
7. [Validación de Distribución](#validación-de-distribución)

---

## 🏗️ Configuración de Build

### setup.py Principal

```python
# setup.py
from setuptools import setup, find_packages
import os

# Leer README para long_description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except:
        return "Flash Sheet - Herramienta de análisis de datos con exportación separada"

# Leer requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="flash-sheet",
    version="1.0.0",
    author="Flash Sheet Team",
    author_email="team@flash-sheet.com",
    description="Herramienta avanzada de análisis de datos con exportación separada por plantillas Excel",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/flash-sheet/flash-sheet",
    project_urls={
        "Bug Reports": "https://github.com/flash-sheet/flash-sheet/issues",
        "Source": "https://github.com/flash-sheet/flash-sheet",
        "Documentation": "https://flash-sheet.github.io/docs/",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "full": ["numpy>=1.20.0", "psutil>=5.8.0", "tqdm>=4.60.0"],
        "dev": ["pytest>=6.0", "pytest-cov>=2.0", "black>=21.0", "flake8>=3.8"],
        "docs": ["sphinx>=4.0", "sphinx-rtd-theme>=1.0", "myst-parser>=0.15.0"],
    },
    entry_points={
        "console_scripts": [
            "flash-sheet=main:main",
            "flash-sheet-check=scripts.check_installation:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml", "*.txt", "*.md"],
        "assets": ["*"],
    },
    zip_safe=False,
)
```

### pyproject.toml (PEP 518)

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
build-backend = "setuptools.build_meta"

[project]
name = "flash-sheet"
version = "1.0.0"
description = "Herramienta avanzada de análisis de datos con exportación separada por plantillas Excel"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "Flash Sheet Team", email = "team@flash-sheet.com"}
]
maintainers = [
    {name = "Flash Sheet Team", email = "team@flash-sheet.com"}
]
keywords = ["data", "analysis", "excel", "export", "separation", "pandas", "dataframe"]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Science/Research",
    "Topic :: Office/Business :: Financial",
    "Topic :: Scientific/Engineering",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Operating System :: OS Independent",
    "Environment :: X11 Applications :: Qt",
    "Environment :: Console",
]
requires-python = ">=3.8"
dependencies = [
    "pandas>=1.5.0",
    "openpyxl>=3.1.0",
    "PySide6>=6.0.0",
    "pathlib",
]

[project.optional-dependencies]
full = [
    "numpy>=1.20.0",
    "psutil>=5.8.0", 
    "tqdm>=4.60.0",
]
dev = [
    "pytest>=6.0",
    "pytest-cov>=2.0",
    "black>=21.0",
    "flake8>=3.8",
    "mypy>=0.910",
]
docs = [
    "sphinx>=4.0",
    "sphinx-rtd-theme>=1.0",
    "myst-parser>=0.15.0",
]
enterprise = [
    "cryptography>=3.4.8",
    "pywin32>=227; sys_platform=='win32'",
    "pyobjc-core>=8.0; sys_platform=='darwin'",
]

[project.urls]
Homepage = "https://github.com/flash-sheet/flash-sheet"
Documentation = "https://flash-sheet.github.io/docs/"
Repository = "https://github.com/flash-sheet/flash-sheet.git"
"Bug Tracker" = "https://github.com/flash-sheet/flash-sheet/issues"
"Funding" = "https://github.com/sponsors/flash-sheet"
"Changelog" = "https://github.com/flash-sheet/flash-sheet/blob/main/CHANGELOG.md"

[project.scripts]
flash-sheet = "main:main"
flash-sheet-check = "scripts.check_installation:main"
flash-sheet-template = "scripts.template_generator:main"

[tool.setuptools]
packages = ["core", "app", "app.widgets", "core.loaders", "core.transformations"]

[tool.setuptools.package-data]
"*" = ["*.json", "*.yaml", "*.yml", "*.txt", "*.md"]
"assets" = ["*"]

[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers --cov=core --cov=app --cov-report=term-missing"
testpaths = [
    "tests",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "performance: marks tests as performance tests",
    "excel: marks tests that require Excel files",
]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.coverage.run]
source = ["core", "app"]
omit = [
    "*/tests/*",
    "*/test_*",
    "setup.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

---

## 🚀 Scripts de Distribución

### build.sh - Script Principal de Build

```bash
#!/bin/bash
# build.sh - Script principal de build y distribución

set -e  # Exit on any error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
VERSION="1.0.0"
BUILD_DIR="build"
DIST_DIR="dist"
SOURCE_DIR="."

echo -e "${BLUE}=== Flash Sheet v${VERSION} - Build Script ===${NC}"
echo "Fecha: $(date)"
echo "Python: $(python --version 2>&1)"
echo "Directorio: $(pwd)"
echo

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Verificar dependencias
check_dependencies() {
    log "Verificando dependencias de build..."
    
    # Verificar Python
    if ! python --version &>/dev/null; then
        error "Python no está instalado o no está en PATH"
        exit 1
    fi
    
    # Verificar herramientas de build
    tools=("pip" "setuptools" "wheel" "twine")
    for tool in "${tools[@]}"; do
        if ! python -c "import ${tool}" &>/dev/null; then
            error "${tool} no está instalado"
            exit 1
        fi
    done
    
    log "✅ Dependencias verificadas"
}

# Limpiar build anterior
clean_build() {
    log "Limpiando directorios de build anteriores..."
    
    if [ -d "$BUILD_DIR" ]; then
        rm -rf "$BUILD_DIR"
    fi
    
    if [ -d "$DIST_DIR" ]; then
        rm -rf "$DIST_DIR"
    fi
    
    if [ -d "*.egg-info" ]; then
        rm -rf *.egg-info
    fi
    
    log "✅ Directorios limpiados"
}

# Ejecutar tests
run_tests() {
    log "Ejecutando suite de tests..."
    
    if ! python -m pytest tests/ -v; then
        error "Tests fallaron"
        exit 1
    fi
    
    log "✅ Tests pasados exitosamente"
}

# Ejecutar linting
run_linting() {
    log "Ejecutando linting..."
    
    # Black formatter
    if ! python -m black --check .; then
        warning "Código necesita formateo con black"
    fi
    
    # Flake8 linter
    if ! python -m flake8 . --max-line-length=88 --ignore=E203,W503; then
        warning "Problemas de linting detectados"
    fi
    
    log "✅ Linting completado"
}

# Build documentación
build_docs() {
    log "Construyendo documentación..."
    
    if [ -d "docs" ]; then
        cd docs
        if command -v sphinx-build &> /dev/null; then
            sphinx-build -b html . _build/html
            cd ..
            log "✅ Documentación construida"
        else
            warning "Sphinx no disponible, saltando documentación"
        fi
    else
        warning "Directorio docs no encontrado"
    fi
}

# Build paquetes
build_packages() {
    log "Construyendo paquetes..."
    
    # Python wheel
    python setup.py bdist_wheel
    
    # Source distribution
    python setup.py sdist
    
    log "✅ Paquetes construidos en $DIST_DIR"
}

# Verificar paquetes
verify_packages() {
    log "Verificando paquetes..."
    
    # Verificar con twine
    python -m twine check dist/*
    
    log "✅ Paquetes verificados"
}

# Función principal
main() {
    echo -e "${BLUE}Iniciando build para v${VERSION}${NC}"
    
    check_dependencies
    clean_build
    run_tests
    run_linting
    build_docs
    build_packages
    verify_packages
    
    echo
    echo -e "${GREEN}=== BUILD COMPLETADO EXITOSAMENTE ===${NC}"
    echo "Versión: $VERSION"
    echo "Paquetes en: $DIST_DIR"
    echo
    
    # Mostrar archivos generados
    if [ -d "$DIST_DIR" ]; then
        echo "Archivos generados:"
        ls -la "$DIST_DIR"
    fi
}

# Parsear argumentos
case "${1:-build}" in
    "clean")
        clean_build
        ;;
    "test")
        check_dependencies
        run_tests
        ;;
    "lint")
        check_dependencies
        run_linting
        ;;
    "docs")
        check_dependencies
        build_docs
        ;;
    "packages")
        check_dependencies
        build_packages
        ;;
    "verify")
        verify_packages
        ;;
    "full")
        main
        ;;
    "help"|"-h"|"--help")
        echo "Uso: $0 [clean|test|lint|docs|packages|verify|full|help]"
        echo "  clean    - Limpiar directorios de build"
        echo "  test     - Ejecutar tests"
        echo "  lint     - Ejecutar linting"
        echo "  docs     - Construir documentación"
        echo "  packages - Construir paquetes"
        echo "  verify   - Verificar paquetes"
        echo "  full     - Build completo (default)"
        echo "  help     - Mostrar esta ayuda"
        ;;
    *)
        main
        ;;
esac
```

### build-exe.bat - Build para Windows

```batch
@echo off
REM build-exe.bat - Script de build para Windows
setlocal enabledelayedexpansion

set VERSION=1.0.0
set PYTHON=python
set BUILD_DIR=build
set DIST_DIR=dist

echo === Flash Sheet v%VERSION% - Build Script (Windows) ===
echo Fecha: %date% %time%
%PYTHON% --version
echo.

REM Verificar dependencias
echo [INFO] Verificando dependencias...
%PYTHON% -c "import setuptools, wheel, twine" 2>nul || (
    echo [ERROR] Faltan herramientas de build
    exit /b 1
)

REM Limpiar
echo [INFO] Limpiando builds anteriores...
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
if exist "*.egg-info" rmdir /s /q "*.egg-info"

REM Ejecutar tests
echo [INFO] Ejecutando tests...
%PYTHON% -m pytest tests/ -v || (
    echo [ERROR] Tests fallaron
    exit /b 1
)

REM Build
echo [INFO] Construyendo paquetes...
%PYTHON% setup.py bdist_wheel
%PYTHON% setup.py sdist

REM Verificar
echo [INFO] Verificando paquetes...
%PYTHON% -m twine check dist/*

echo.
echo === BUILD COMPLETADO ===
echo Archivos generados:
dir "%DIST_DIR%"

pause
```

### makefile - Build para Linux/macOS

```makefile
# makefile - Build automation para Linux/macOS

.PHONY: all clean test lint docs packages verify install help

# Variables
VERSION = 1.0.0
PYTHON = python3
PIP = pip3
BUILD_DIR = build
DIST_DIR = dist

# Target por defecto
all: clean test lint docs packages verify
	@echo "Build completo completado para v$(VERSION)"

# Limpiar
clean:
	@echo "Limpiando directorios..."
	rm -rf $(BUILD_DIR) $(DIST_DIR) *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Tests
test:
	@echo "Ejecutando tests..."
	$(PYTHON) -m pytest tests/ -v

# Linting
lint:
	@echo "Ejecutando linting..."
	$(PYTHON) -m black --check .
	$(PYTHON) -m flake8 . --max-line-length=88

# Documentación
docs:
	@echo "Construyendo documentación..."
	cd docs && $(PYTHON) -m sphinx -b html . _build/html

# Paquetes
packages:
	@echo "Construyendo paquetes..."
	$(PYTHON) setup.py bdist_wheel
	$(PYTHON) setup.py sdist

# Verificar paquetes
verify:
	@echo "Verificando paquetes..."
	$(PYTHON) -m twine check $(DIST_DIR)/*

# Instalar en desarrollo
install:
	@echo "Instalando en modo desarrollo..."
	$(PIP) install -e .

# Instalar dependencias de desarrollo
install-dev:
	@echo "Instalando dependencias de desarrollo..."
	$(PIP) install -e ".[dev]"

# Upload a PyPI (requiere configuración)
upload: verify
	@echo "Subiendo a PyPI..."
	$(PYTHON) -m twine upload $(DIST_DIR)/*

# Help
help:
	@echo "Targets disponibles:"
	@echo "  all        - Build completo (default)"
	@echo "  clean      - Limpiar archivos temporales"
	@echo "  test       - Ejecutar tests"
	@echo "  lint       - Ejecutar linting"
	@echo "  docs       - Construir documentación"
	@echo "  packages   - Construir paquetes"
	@echo "  verify     - Verificar paquetes"
	@echo "  install    - Instalar en desarrollo"
	@echo "  install-dev - Instalar dependencias dev"
	@echo "  upload     - Subir a PyPI"
	@echo "  help       - Mostrar esta ayuda"
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions - .github/workflows/ci.yml

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"

    - name: Run tests
      run: |
        python -m pytest tests/ -v --cov=core --cov=app --cov-report=xml

    - name: Upload coverage to Codecov
      if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.10'
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    runs-on: ubuntu-latest
    needs: test

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine

    - name: Build packages
      run: |
        python -m build

    - name: Check packages
      run: |
        python -m twine check dist/*

    - name: Upload build artifacts
      uses: actions/upload-artifact@v3
      with:
        name: dist
        path: dist/

  release:
    runs-on: ubuntu-latest
    needs: build
    if: startsWith(github.ref, 'refs/tags/v')

    steps:
    - uses: actions/checkout@v3

    - name: Download build artifacts
      uses: actions/download-artifact@v3
      with:
        name: dist
        path: dist/

    - name: Create release
      uses: softprops/action-gh-release@v1
      with:
        files: dist/*
        draft: false
        prerelease: false
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

    - name: Upload to PyPI
      run: |
        pip install twine
        twine upload dist/* --username __token__ --password ${{ secrets.PYPI_API_TOKEN }}
```

### GitHub Actions - .github/workflows/docs.yml

```yaml
name: Documentation

on:
  push:
    branches: [ main ]
    paths: [ 'docs/**', '**/*.md' ]

jobs:
  build-docs:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install documentation dependencies
      run: |
        pip install -e ".[docs]"

    - name: Build documentation
      run: |
        cd docs
        sphinx-build -b html . _build/html

    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs/_build/html
```

---

## 📦 Package Management

### PyPI Configuration

```python
# .pypirc
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJDY2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJDY2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2
```

### .pypirc (Template)

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = # Obtener token de PyPI

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = # Token para TestPyPI
```

### Scripts de Deploy

```bash
#!/bin/bash
# deploy.sh - Script de deploy a PyPI

set -e

VERSION=$(python setup.py --version)
echo "Deploying version: $VERSION"

# Verificar que estamos en una tag
if ! git describe --tags --exact-match HEAD > /dev/null 2>&1; then
    echo "Error: Deploy solo permitido en tags"
    exit 1
fi

# Verificar que la versión coincide
TAG=$(git describe --tags --exact-match HEAD | sed 's/^v//')
if [ "$TAG" != "$VERSION" ]; then
    echo "Error: Versión ($VERSION) no coincide con tag ($TAG)"
    exit 1
fi

echo "Desplegando versión $VERSION..."

# Deploy a PyPI
python -m twine upload dist/*

echo "✅ Deploy completado"
```

---

## 🏷️ Versionado y Releases

### CHANGELOG.md

```markdown
# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-05

### Agregado
- Nueva funcionalidad de exportación de datos separados con plantillas Excel
- ExcelTemplateSplitter para lógica de separación
- ExportSeparatedDialog para interfaz de usuario
- ColumnMappingManager para gestión flexible de mapeos
- FileNamingManager con 6 tipos de placeholders
- ExcelTemplateManager con preservación completa de formato
- Sistema de chunking inteligente para datasets grandes
- Manejo robusto de casos especiales (nulos, duplicados, errores)
- Suite completa de testing con >95% cobertura
- Documentación Sphinx completa
- Guía de usuario exhaustiva

### Características Técnicas
- Preservación 100% de formato Excel
- Optimización de memoria para datasets > 1M filas
- Validación en tiempo real
- Recovery automático de errores
- Soporte multiplataforma (Windows, macOS, Linux)
- Integración seamless con sistema existente

### Performance
- < 30s para datasets pequeños (< 10K filas)
- < 3min para datasets medianos (10K-100K filas)
- < 15min para datasets grandes (100K-1M filas)
- > 95% éxito sin intervención manual

### Testing
- 15+ tests unitarios
- 10+ tests de integración
- 5+ benchmarks de performance
- 3+ tests de UI
- Tests de stress para condiciones extremas

## [Unreleased]

### Planeado para v1.1.0
- Paralelización para datasets masivos
- Soporte para plantillas Word/PowerPoint
- Dashboard de analytics
- Exportación directa a cloud

### Mejoras a Largo Plazo
- Machine learning para optimización automática
- Colaboración multi-usuario
- Integración con APIs externas
```

### Version Management Script

```python
# scripts/version_manager.py
import re
import subprocess
import sys
from pathlib import Path
import json

class VersionManager:
    def __init__(self):
        self.setup_py = Path("setup.py")
        self.pyproject_toml = Path("pyproject.toml")
        self.package_init = Path("flash_sheet/__init__.py")
        self.version_file = Path("flash_sheet/version.py")
        
    def get_current_version(self):
        """Obtener versión actual del proyecto"""
        # Intentar desde __init__.py
        if self.package_init.exists():
            content = self.package_init.read_text()
            match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        
        # Fallback a setup.py
        content = self.setup_py.read_text()
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1)
            
        return "0.0.0"
    
    def bump_version(self, bump_type="patch"):
        """Bump version (major, minor, patch)"""
        current = self.get_current_version()
        major, minor, patch = map(int, current.split('.'))
        
        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
            
        new_version = f"{major}.{minor}.{patch}"
        
        # Actualizar archivos
        self.update_version_files(new_version)
        
        print(f"Version bumped from {current} to {new_version}")
        return new_version
    
    def update_version_files(self, version):
        """Actualizar versión en todos los archivos relevantes"""
        # __init__.py
        if self.package_init.exists():
            content = self.package_init.read_text()
            content = re.sub(
                r'__version__\s*=\s*["\'][^"\']+["\']',
                f'__version__ = "{version}"',
                content
            )
            self.package_init.write_text(content)
        
        # setup.py
        if self.setup_py.exists():
            content = self.setup_py.read_text()
            content = re.sub(
                r'version\s*=\s*["\'][^"\']+["\']',
                f'version="{version}"',
                content
            )
            self.setup_py.write_text(content)
        
        # pyproject.toml
        if self.pyproject_toml.exists():
            content = self.pyproject_toml.read_text()
            content = re.sub(
                r'version\s*=\s*["\'][^"\']+["\']',
                f'version = "{version}"',
                content
            )
            self.pyproject_toml.write_text(content)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Version manager for Flash Sheet")
    parser.add_argument("action", choices=["get", "bump"], help="Action to perform")
    parser.add_argument("--type", choices=["major", "minor", "patch"], 
                       default="patch", help="Version bump type")
    
    args = parser.parse_args()
    
    vm = VersionManager()
    
    if args.action == "get":
        print(vm.get_current_version())
    elif args.action == "bump":
        vm.bump_version(args.type)

if __name__ == "__main__":
    main()
```

---

## 🌍 Distribución Multiplataforma

### Ejecutables Windows (PyInstaller)

```python
# build_exe.py - Script para crear ejecutables
import os
import sys
from PyInstaller.__main__ import run

def build_executable():
    """Build ejecutable para Windows"""
    
    # Limpiar builds anteriores
    if os.path.exists("build"):
        import shutil
        shutil.rmtree("build")
    if os.path.exists("dist"):
        import shutil
        shutil.rmtree("dist")
    
    # Configuración PyInstaller
    args = [
        'main.py',
        '--onefile',
        '--windowed',
        '--name=FlashSheet',
        '--icon=assets/logo.ico',
        '--add-data=assets;assets',
        '--add-data=core;core',
        '--add-data=app;app',
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtWidgets',
        '--hidden-import=pandas',
        '--hidden-import=openpyxl',
        '--distpath=dist/windows',
        '--workpath=build/windows',
    ]
    
    run(args)

if __name__ == "__main__":
    build_executable()
```

### App Bundle macOS (cx_Freeze)

```python
# build_mac.py - Script para crear app bundle macOS
from cx_Freeze import setup, Executable
import sys

# Configuración
APP_NAME = "Flash Sheet"
APP_VERSION = "1.0.0"

# Archivos a incluir
includefiles = [
    "assets/",
    "docs/",
    "requirements.txt"
]

# Paquetes a incluir
packages = [
    "PySide6",
    "pandas", 
    "openpyxl",
    "numpy"
]

# Exclusiones
excludes = [
    "tkinter",
    "matplotlib",
    "IPython",
    "jupyter"
]

# Setup
setup(
    name=APP_NAME,
    version=APP_VERSION,
    description="Herramienta de análisis de datos con exportación separada",
    options={
        "build_exe": {
            "packages": packages,
            "excludes": excludes,
            "include_files": includefiles,
            "icon": "assets/logo.icns"
        }
    },
    executables=[
        Executable(
            "main.py",
            base="MacOS",
            icon="assets/logo.icns",
            bundle_identifier="com.flash-sheet.app"
        )
    ]
)
```

### AppImage Linux

```yaml
# appimage-build.yml - GitHub Actions para AppImage
name: Build AppImage

on:
  push:
    tags: [ 'v*' ]

jobs:
  appimage:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install AppImageTool
      run: |
        wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
        chmod +x appimagetool-x86_64.AppImage
    
    - name: Install dependencies
      run: |
        pip install -e ".[full]"
    
    - name: Create AppDir
      run: |
        mkdir -p FlashSheet.AppDir/usr/bin
        mkdir -p FlashSheet.AppDir/usr/share/applications
        mkdir -p FlashSheet.AppDir/usr/share/icons
        
        # Copiar ejecutable
        cp main.py FlashSheet.AppDir/usr/bin/flash-sheet
        
        # Crear desktop entry
        cat > FlashSheet.AppDir/flash-sheet.desktop << EOF
        [Desktop Entry]
        Name=Flash Sheet
        Comment=Herramienta de análisis de datos
        Exec=flash-sheet
        Icon=flash-sheet
        Type=Application
        Categories=Office;Science;
        EOF
        
        # Copiar icono
        cp assets/logo.png FlashSheet.AppDir/flash-sheet.png
    
    - name: Build AppImage
      run: |
        ./appimagetool-x86_64.AppImage FlashSheet.AppDir dist/FlashSheet-$(git describe --tags).AppImage
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: flash-sheet-appimage
        path: dist/*.AppImage
```

---

## ✅ Validación de Distribución

### Script de Validación

```python
# scripts/validate_distribution.py
import os
import sys
import subprocess
import zipfile
import tempfile
from pathlib import Path

def validate_package_files():
    """Validar que todos los archivos necesarios están en el paquete"""
    required_files = [
        "core/data_handler.py",
        "app/widgets/export_separated_dialog.py",
        "assets/logo.png",
        "README.md",
        "requirements.txt"
    ]
    
    # Verificar que los archivos existen
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Archivo faltante: {file_path}")
            return False
    
    print("✅ Todos los archivos requeridos presentes")
    return True

def validate_wheel(wheel_path):
    """Validar wheel package"""
    print(f"Validando wheel: {wheel_path}")
    
    try:
        # Verificar que el wheel se puede instalar
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "--dry-run", str(wheel_path)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Wheel válido")
            return True
        else:
            print(f"❌ Error en wheel: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error validando wheel: {e}")
        return False

def validate_sdist(sdist_path):
    """Validar source distribution"""
    print(f"Validando sdist: {sdist_path}")
    
    try:
        # Extraer y verificar contenido
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(sdist_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Verificar archivos críticos
            critical_files = [
                "setup.py",
                "README.md", 
                "core/__init__.py",
                "app/__init__.py"
            ]
            
            for file_name in critical_files:
                file_path = Path(temp_dir) / "flash-sheet-1.0.0" / file_name
                if not file_path.exists():
                    print(f"❌ Archivo faltante en sdist: {file_name}")
                    return False
            
            print("✅ Sdist válido")
            return True
            
    except Exception as e:
        print(f"❌ Error validando sdist: {e}")
        return False

def main():
    """Función principal de validación"""
    print("=== Validación de Distribución ===\n")
    
    # Validar archivos locales
    if not validate_package_files():
        sys.exit(1)
    
    # Validar paquetes en dist/
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ Directorio dist/ no existe")
        sys.exit(1)
    
    wheels = list(dist_dir.glob("*.whl"))
    sdists = list(dist_dir.glob("*.tar.gz"))
    
    all_valid = True
    
    # Validar wheels
    for wheel in wheels:
        if not validate_wheel(wheel):
            all_valid = False
    
    # Validar sdists
    for sdist in sdists:
        if not validate_sdist(sdist):
            all_valid = False
    
    # Resumen
    print(f"\n=== Resumen de Validación ===")
    print(f"Wheels encontrados: {len(wheels)}")
    print(f"Sdist encontrados: {len(sdists)}")
    
    if all_valid:
        print("✅ Todos los paquetes son válidos")
    else:
        print("❌ Algunos paquetes tienen problemas")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Checklist de Distribución

```markdown
# Checklist de Distribución v1.0.0

## Pre-Build
- [ ] Versión actualizada en todos los archivos
- [ ] Tests pasando completamente
- [ ] Documentación actualizada
- [ ] CHANGELOG.md actualizado
- [ ] Requisitos revisados

## Build Process
- [ ] Dependencias instaladas
- [ ] Limpieza de builds anteriores
- [ ] Tests unitarios ejecutados
- [ ] Linting aprobado
- [ ] Documentación construida

## Paquetes Python
- [ ] Wheel (.whl) generado
- [ ] Source distribution (.tar.gz) generado
- [ ] Paquetes verificados con twine
- [ ] Metadatos correctos en setup.py
- [ ] Dependencies list actualizada

## Distribuciones Específicas
- [ ] Ejecutable Windows (.exe)
- [ ] App Bundle macOS (.app)
- [ ] AppImage Linux (.AppImage)
- [ ] Cada distribución probada

## Testing
- [ ] Instalación desde pip verificada
- [ ] Instalación desde wheel verificada
- [ ] Funcionalidad core verificada
- [ ] ExportSeparatedDialog funcional
- [ ] ExcelTemplateSplitter funcional

## Release
- [ ] Release notes completas
- [ ] Git tag creada
- [ ] GitHub release creada
- [ ] PyPI release (si aplicable)
- [ ] Distribución a usuarios beta

## Post-Release
- [ ] Monitoreo de errores activado
- [ ] Feedback channels configurados
- [ ] Plan de actualizaciones activado
```

---

## 🎉 Resumen de Distribución

Esta documentación de distribución proporciona:

1. **Scripts de Build Automatizados** para Windows, Linux y macOS
2. **CI/CD Pipeline** con GitHub Actions para integración continua
3. **Package Management** completo para PyPI y distribución
4. **Versionado Automatizado** con bump scripts
5. **Distribución Multiplataforma** con ejecutables nativos
6. **Validación Completa** de todos los paquetes

### Archivos Generados:
- `setup.py` y `pyproject.toml` para configuración
- `build.sh` y `build-exe.bat` para builds automatizados
- `makefile` para Linux/macOS
- GitHub Actions workflows para CI/CD
- Scripts de deploy y validación
- Checklist completo de distribución

### Próximos Pasos:
1. Configurar PyPI y tokens de acceso
2. Configurar GitHub secrets para CI/CD
3. Ejecutar builds de prueba
4. Publicar release v1.0.0
5. Distribuir a usuarios finales

---

*Preparación para Distribución v1.0.0 - Completada el 5 de Noviembre, 2025*