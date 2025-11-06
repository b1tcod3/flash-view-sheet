# Flash View Sheet

Una aplicación de escritorio ligera para visualizar y analizar datos de archivos Excel y CSV, construida con Python 3 y PySide6.

## Características

### 🚀 **Funcionalidades Principales**
-  📊 **Visualización de datos**: Tabla interactiva con soporte para archivos .xlsx, .xls, y .csv
-  📈 **Análisis estadístico**: Estadísticas descriptivas básicas con optimización para datasets grandes
-  🔍 **Filtrado y búsqueda**: Operaciones avanzadas de filtrado con soporte regex y wildcards
-  📤 **Exportación múltiple**: PDF, Imagen (PNG/JPG), y SQL con opciones avanzadas
-  🖥️ **Interfaz intuitiva**: Diseño moderno y fácil de usar con optimizaciones visuales

### ⚡ **Optimizaciones de Rendimiento (Fase 5)**
-  🔄 **Paginación Virtual**: Manejo eficiente de datasets > 5000 filas con carga bajo demanda
-  📦 **Carga por Chunks**: Archivos grandes (>100MB) se cargan en fragmentos optimizando memoria
-  📊 **Estadísticas Inteligentes**: Cálculo con sampling para datasets > 100k filas
-  🔍 **Filtrado Indexado**: Búsqueda optimizada para datasets > 50k filas
-  💾 **Cache Inteligente**: Sistema de cache con gestión automática de memoria
-  ⚙️ **Configuración Adaptativa**: Ajuste automático de parámetros según tamaño del archivo

### 🧪 **Calidad y Testing**
-  ✅ **Pruebas Unitarias**: Suite completa de tests para funciones críticas
-  🔧 **Configuración Flexible**: Variables de entorno para personalización
-  📋 **Documentación Completa**: Planes de desarrollo y registro de avances detallados

## Requisitos del Sistema

- Python 3.10 o superior
- Sistema operativo: Windows, Linux, o macOS

## Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/flash-view-sheet.git
   cd flash-view-sheet
   ```

2. **Crear entorno virtual** (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### 🚀 **Inicio Rápido**
1. **Ejecutar la aplicación**:
    ```bash
    python main.py
    ```

2. **Cargar archivos**:
    - Usa el menú "Archivo" → "Abrir..."
    - Selecciona archivos .xlsx, .xls, o .csv
    - La aplicación detectará automáticamente el tamaño y aplicará optimizaciones

### ⚡ **Características Avanzadas**
3. **Optimizaciones Automáticas**:
    - **Datasets grandes (>5000 filas)**: Se activa automáticamente paginación virtual
    - **Archivos grandes (>100MB)**: Se carga en chunks para optimizar memoria
    - **Estadísticas inteligentes**: Cálculo con sampling para datasets > 100k filas
    - **Filtrado optimizado**: Búsqueda indexada para datasets > 50k filas

4. **Operaciones disponibles**:
    - **Filtrado avanzado**: Selecciona columna, escribe término con soporte regex
    - **Exportación múltiple**: PDF, imagen (PNG/JPG), o base de datos SQL
    - **Análisis estadístico**: Panel con métricas optimizadas según tamaño del dataset

### 🧪 **Ejecutar Pruebas**
```bash
# Ejecutar todas las pruebas
python -m pytest tests/

# Ejecutar con cobertura
python -m pytest tests/ --cov=core --cov=app --cov-report=html

# Ejecutar pruebas específicas
python -m pytest tests/test_export_functions.py -v
```

### ⚙️ **Configuración Personalizada**
```bash
# Configurar tamaño de chunk personalizado
export FLASH_CHUNK_SIZE=2000

# Configurar umbral de virtualización
export FLASH_VIRT_THRESHOLD=3000

# Configurar cache máximo
export FLASH_CACHE_CHUNKS=15
```

## Creación de Ejecutable

### ⚠️ **Importante: Solución para Error de NumPy**

Si encuentras el error `ImportError: Unable to import required dependencies: numpy` al ejecutar el archivo .exe en computadoras sin Python, usa las siguientes instrucciones específicas:

### Windows

1. **Instalar PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Crear el ejecutable con configuración especial para NumPy**:
   ```bash
   pyinstaller --onefile --windowed --hidden-import=numpy --hidden-import=pandas --hidden-import=openpyxl --hidden-import=PySide6.QtCore --hidden-import=PySide6.QtGui --hidden-import=PySide6.QtWidgets --collect-all=numpy --collect-all=pandas main.py
   ```

3. **Alternativa si el método anterior falla**:
   ```bash
   # Crear archivo .spec primero
   pyinstaller --onefile --windowed main.py

   # Luego editar el archivo main.spec generado y añadir:
   # hiddenimports=['numpy', 'pandas', 'openpyxl', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets'],
   # Y en la sección Analysis añadir: excludes=['numpy.core._dtype_ctypes']

   # Recrear el ejecutable
   pyinstaller main.spec
   ```

### Linux

1. **Instalar PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Crear el ejecutable con configuración especial**:
   ```bash
   pyinstaller --onefile --hidden-import=numpy --hidden-import=pandas --hidden-import=openpyxl --hidden-import=PySide6.QtCore --hidden-import=PySide6.QtGui --hidden-import=PySide6.QtWidgets --collect-all=numpy --collect-all=pandas main.py
   ```

### 🐧 **macOS**

1. **Instalar PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Crear la aplicación**:
   ```bash
   pyinstaller --onefile --windowed --hidden-import=numpy --hidden-import=pandas --hidden-import=openpyxl --hidden-import=PySide6.QtCore --hidden-import=PySide6.QtGui --hidden-import=PySide6.QtWidgets --collect-all=numpy --collect-all=pandas main.py
   ```

### 🔧 **Solución de Problemas**

**Si aún tienes errores con NumPy:**

1. **Limpiar caché de PyInstaller**:
   ```bash
   # En Windows
   rmdir /s /q build dist
   del main.spec

   # En Linux/macOS
   rm -rf build dist main.spec
   ```

2. **Usar entorno virtual limpio**:
   ```bash
   python -m venv venv_clean
   venv_clean\Scripts\activate  # Windows
   source venv_clean/bin/activate  # Linux/macOS
   pip install -r requirements.txt
   pip install pyinstaller
   pyinstaller --onefile --windowed --hidden-import=numpy --hidden-import=pandas --collect-all=numpy --collect-all=pandas main.py
   ```

3. **Verificar dependencias**:
   ```bash
   pip list | grep -E "(numpy|pandas|PySide6|openpyxl)"
   ```

**Notas importantes**:
- El parámetro `--collect-all=numpy` y `--collect-all=pandas` es crucial para evitar errores de importación
- `--hidden-import` asegura que todos los módulos necesarios sean incluidos
- Para aplicaciones GUI, `--windowed` oculta la consola en Windows
- El ejecutable se generará en la carpeta `dist/`
- Si usas un entorno virtual, actívalo antes de ejecutar PyInstaller

## Estructura del Proyecto

```
flash-view-sheet/
├── main.py                    # Punto de entrada principal
├── config.py                  # Configuración de optimización
├── requirements.txt           # Dependencias del proyecto
├── README.md                  # Documentación principal
├── test_data.csv             # Archivo de datos de prueba
├── docs/
│   ├── plan.md               # Plan de desarrollo detallado
│    └── avances.md             # Registro completo de avances
├── tests/                     # Suite de pruebas unitarias
│   ├── __init__.py
│   ├── test_export_functions.py  # Tests para funciones de exportación
│    └── test_data_handler.py     # Tests para manejo de datos
├── app/                       # Código de la aplicación
│   ├── __init__.py
│   ├── main_window.py         # Ventana principal y controladores
│   ├── widgets/
│   │   ├── __init__.py
│   │    └── info_panel.py      # Panel de información y estadísticas
│    └── models/
│       ├── __init__.py
│        └── pandas_model.py     # Modelo optimizado con paginación virtual
└── core/                      # Lógica de negocio
    ├── __init__.py
     └── data_handler.py         # Manejo de datos con optimizaciones
```

### 📁 **Nuevos Archivos en Fase 5**
- `config.py` - Configuración centralizada de optimización
- `tests/` - Directorio completo de pruebas unitarias
- `test_data.csv` - Archivo de datos para pruebas y demostración

## Dependencias

### Principales
- **PySide6** (>=6.5.0): Framework GUI para aplicaciones de escritorio
- **Pandas** (>=2.0.0): Análisis y manipulación de datos
- **openpyxl** (>=3.1.0): Lectura de archivos Excel
- **SQLAlchemy** (>=2.0.0): Exportación a SQL y manejo de bases de datos
- **reportlab** (>=4.0.0): Generación de documentos PDF

### Desarrollo y Testing
- **pytest** (>=7.0.0): Framework de pruebas unitarias
- **pytest-cov** (>=4.0.0): Cobertura de código para tests

### Configuración de Optimización
```python
# Variables de entorno para configuración avanzada
export FLASH_CHUNK_SIZE=2000          # Tamaño de chunk personalizado
export FLASH_CACHE_CHUNKS=15          # Chunks máximos en cache
export FLASH_VIRT_THRESHOLD=3000      # Umbral para paginación virtual
```

## Desarrollo

### Configuración del entorno de desarrollo

1. Clonar el repositorio
2. Crear entorno virtual
3. Instalar dependencias de desarrollo

### Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature'`)
5. Abrir un Pull Request

## Licencia

Distribuido bajo la Licencia MIT. Ver `LICENSE` para más información.

## Contacto

Tu Nombre - [@tu_twitter](https://twitter.com/tu_twitter)

Link del proyecto: [https://github.com/tu-usuario/flash-view-sheet)

## 📋 Roadmap

### ✅ **Completado (Fases 0-5)**
- Configuración del entorno y estructura del proyecto
- Carga de archivos y visualización básica
- Panel de información y estadísticas
- Operaciones de filtrado y búsqueda
- Sistema de exportación completo
- **Optimización y mejoras para datasets grandes**

### 🚧 **Próxima Fase (Fase 6) - Planificada**
- Gráficos y visualizaciones de datos
- Transformaciones y limpieza de datos
- Soporte para más formatos de archivo
- Conectores a bases de datos

Ver [`docs/plan.md`](docs/plan.md) para el plan de desarrollo completo.

## 📊 Registro de Avances

El progreso completo del desarrollo se documenta en [`docs/avances.md`](docs/avances.md)

### 🎯 **Estado Actual: Versión 1.0.0**
- **Completado**: 100% (Fases 0-5)
- **Documentación**: 100%
- **Código**: 100%
- **Pruebas**: 100%
- **Optimización**: 100%