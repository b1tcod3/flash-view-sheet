# Ejemplos de Carga de Carpeta

Esta carpeta contiene ejemplos prácticos de cómo usar la funcionalidad de carga de carpeta de Flash Sheet para consolidar múltiples archivos Excel.

## 📁 Estructura de Ejemplos

```
examples/folder_loading/
├── README.md                    # Este archivo
├── sample_data/                 # Datos de ejemplo
│   ├── ventas_q1.xlsx          # Ventas primer trimestre
│   ├── ventas_q2.xlsx          # Ventas segundo trimestre
│   ├── ventas_q3.xlsx          # Ventas tercer trimestre
│   └── ventas_q4.xlsx          # Ventas cuarto trimestre
├── basic_example.py             # Ejemplo básico de uso programático
├── advanced_example.py          # Ejemplo avanzado con configuración
└── performance_example.py       # Ejemplo de uso con grandes volúmenes
```

## 🚀 Ejemplos Disponibles

### 1. Ejemplo Básico (`basic_example.py`)

Muestra cómo cargar una carpeta completa de archivos Excel de forma programática:

```python
from core.loaders.folder_loader import FolderLoader
from core.consolidation.excel_consolidator import ExcelConsolidator

# Cargar carpeta
loader = FolderLoader("ruta/a/carpeta")
consolidator = ExcelConsolidator()

# Procesar archivos
for file_path in loader.get_excel_files():
    df = pd.read_excel(file_path)
    consolidator.add_dataframe(df, file_path)

# Consolidar
result = consolidator.consolidate()
print(f"Datos consolidados: {len(result)} filas")
```

### 2. Ejemplo Avanzado (`advanced_example.py`)

Demuestra configuración avanzada con filtros, renombrado de columnas y manejo de errores:

- Filtros de archivos por nombre
- Renombrado automático de columnas
- Manejo de archivos con estructuras diferentes
- Configuración de alineación de columnas

### 3. Ejemplo de Rendimiento (`performance_example.py`)

Optimizaciones para procesar grandes volúmenes de datos:

- Procesamiento por lotes (chunked processing)
- Carga diferida de metadatos
- Monitoreo de progreso
- Gestión de memoria

## 📊 Datos de Ejemplo

Los archivos `ventas_q*.xlsx` contienen datos de ventas trimestrales con la siguiente estructura:

| Columna    | Descripción              |
|------------|--------------------------|
| Fecha      | Fecha de la venta        |
| Producto   | Nombre del producto      |
| Cantidad   | Cantidad vendida         |
| Precio     | Precio unitario          |
| Total      | Total de la venta        |
| Vendedor   | Nombre del vendedor      |
| Región     | Región de venta          |

## 🛠️ Cómo Ejecutar los Ejemplos

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecutar ejemplo básico:**
   ```bash
   python examples/folder_loading/basic_example.py
   ```

3. **Ejecutar ejemplo avanzado:**
   ```bash
   python examples/folder_loading/advanced_example.py
   ```

4. **Ejecutar ejemplo de rendimiento:**
   ```bash
   python examples/folder_loading/performance_example.py
   ```

## 🎯 Casos de Uso Comunes

### Consolidación de Reportes Mensuales

Cuando tienes reportes separados por mes y quieres analizar tendencias anuales.

### Unión de Datos por Región

Archivos de diferentes sucursales o regiones que necesitan consolidarse.

### Procesamiento de Exportaciones

Múltiples archivos exportados de diferentes sistemas que requieren unificación.

### Análisis de Series Temporales

Datos históricos distribuidos en archivos separados por período.

## 📈 Beneficios de la Consolidación

- **Análisis Unificado**: Ver todos los datos en un solo lugar
- **Tendencias Claras**: Identificar patrones a través de períodos
- **Comparaciones**: Contrastar rendimiento entre diferentes segmentos
- **Reportes Consolidados**: Generar informes unificados automáticamente

## 🔧 Personalización

Los ejemplos pueden adaptarse para:

- Diferentes estructuras de archivos
- Varios formatos de fecha
- Múltiples monedas
- Categorizaciones personalizadas

## 📝 Notas Importantes

- Los archivos Excel deben tener la misma estructura básica
- Se recomienda backup de los archivos originales
- Para grandes volúmenes, considera el ejemplo de rendimiento
- La consolidación preserva los nombres de archivo en columna `__source__`