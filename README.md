# Flash View Sheet

Visor de datos tabulares con soporte para archivos Excel y CSV, construido con Python 3 y PySide6.

## Características

- Visualización de datos en tabla interactiva
- Filtrado avanzado con soporte regex
- Exportación a PDF, Excel, CSV, SQL e imágenes
- Tablas pivote (simple y combinada)
- Cruce de datos (join entre datasets)
- Carga de carpetas con múltiples archivos
- Optimizado para datasets grandes (paginación virtual)

## Requisitos

- Python 3.10+
- PySide6, Pandas, openpyxl, SQLAlchemy, reportlab

## Instalación

```bash
git clone https://github.com/b1tcod3/flash-view-sheet.git
cd flash-view-sheet
pip install -r requirements.txt
```

## Ejecución

```bash
python3 main.py
```

## Estructura

```
flash-sheet/
├── main.py                    # Punto de entrada
├── config.py                  # Configuración
├── requirements.txt           # Dependencias
├── app/                       # Aplicación principal
│   ├── app_coordinator.py    # Orquestador
│   ├── menus/                 # Menús
│   ├── services/             # Servicios (datos, exportación, filtros, pivote)
│   ├── toolbar/              # Barra de herramientas
│   ├── view_manager/         # Gestor de vistas
│   └── widgets/              # Widgets UI
├── core/                     # Lógica de negocio
├── paginacion/               # Paginación virtual
└── tests/                    # Pruebas
```

## Licencia

MIT
