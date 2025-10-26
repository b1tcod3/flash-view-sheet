# Flash View Sheet

Una aplicación de escritorio ligera para visualizar y analizar datos de archivos Excel y CSV, construida con Python 3 y PySide6.

## Características

-  📊 **Visualización de datos**: Tabla interactiva con soporte para archivos .xlsx, .xls, y .csv
-  📈 **Análisis estadístico**: Estadísticas descriptivas básicas
-  🔍 **Filtrado y búsqueda**: Operaciones simples de filtrado por columnas
-  📤 **Exportación múltiple**: PDF, Imagen (PNG/JPG), y SQL
-   **Interfaz intuitiva**: Diseño moderno y fácil de usar

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

1. **Ejecutar la aplicación**:
   ```bash
   python main.py
   ```

2. **Cargar archivos**:
   - Usa el menú "Archivo" → "Abrir..."
   - Selecciona archivos .xlsx, .xls, o .csv
   - La aplicación mostrará automáticamente un resumen de los datos

3. **Operaciones disponibles**:
   - **Filtrado**: Selecciona columna y escribe término de búsqueda
   - **Exportación**: Guarda datos en PDF, imagen, o base de datos SQL

## Estructura del Proyecto

```
flash-view-sheet/
├── main.py                 # Punto de entrada
├── app/
│   ├── __init__.py
│   ├── main_window.py     # Ventana principal
│   ├── widgets/
│   │   ├── __init__.py
│   │    └── info_panel.py   # Panel de información
│    └── models/
│       ├── __init__.py
│        └── pandas_model.py # Modelo para tabla
├── core/
│   ├── __init__.py
│    └── data_handler.py     # Manejo de datos
├── docs/
│   ├── plan.md             # Plan de desarrollo
│    └── avances.md          # Registro de avances
├── requirements.txt         # Dependencias
└── README.md               # Este archivo
```

## Dependencias

- **PySide6**: Framework GUI
- **Pandas**: Análisis y manipulación de datos
- **openpyxl**: Lectura de archivos Excel
- **SQLAlchemy**: Exportación a SQL
- **reportlab**: Exportación a PDF

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

## Roadmap

Ver [`docs/plan.md`](docs/plan.md) para el plan de desarrollo detallado.

## Registro de Avances

El progreso del desarrollo se documenta en [`docs/avances.md`](docs/avances.md)