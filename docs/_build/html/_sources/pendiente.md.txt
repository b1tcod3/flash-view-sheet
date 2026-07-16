# Plan de Tareas Pendientes - Flash View Sheet

## Análisis de Estado Actual

Después de revisar el archivo `docs/avances.md` y el código actual del proyecto, se ha identificado que **todas las tareas inmediatas próximas listadas en la sección "Próximas Tareas Inmediatas" ya han sido implementadas**. Específicamente:

### Tareas Listadas como Pendientes (que ya están completadas):
- [x] Crear widget de vista principal con botón de carga, card e icono
- [x] Crear modal de información para detalles del archivo
- [x] Crear widget de vista de gráficos para charts y stats
- [x] Actualizar barra de herramientas con botones para cambiar vistas
- [x] Integrar vistas en MainWindow y manejar cambios
- [x] Actualizar manejo de datos para aplicar filtros a vista de gráficos

### Verificación de Implementación:

1. **Vista Principal (MainView)**: ✅ Implementada en `app/widgets/main_view.py`
   - Contiene botón de carga de archivo
   - Muestra card con información del archivo
   - Incluye icono de spreadsheet (📊)
   - Botón de opciones de carga (visible después de cargar datos)

2. **Modal de Información (InfoModal)**: ✅ Implementada en `app/widgets/info_modal.py`
   - Muestra detalles del archivo (nombre, filas, columnas)
   - Lista tipos de datos de columnas
   - Incluye estadísticas descriptivas
   - Funciona como modal (QDialog)

3. **Vista de Gráficos (GraphicsView)**: ✅ Implementada en `app/widgets/graphics_view.py`
   - Soporta múltiples tipos de gráficos (histograma, scatter plot, box plot, correlación, línea)
   - Incluye controles para selección de columnas
   - Muestra tabla de datos filtrados
   - Generación asíncrona de gráficos con barra de progreso

4. **Barra de Herramientas**: ✅ Implementada en `main.py`
   - Botones para cambiar entre vistas (Vista Principal, Información, Gráficos)
   - Funcionalidad de filtrado integrada
   - Conexiones de señales implementadas

5. **Integración en MainWindow**: ✅ Implementada en `main.py`
   - QStackedWidget para manejo de vistas
   - Métodos `switch_view()` y `show_info_modal()`
   - Actualización de datos entre vistas

6. **Manejo de Datos con Filtros**: ✅ Implementado
   - Filtros aplicados a vista de gráficos (`graphics_view.update_data()`)
   - Sincronización entre tabla y gráficos
   - Modelo virtualizado para datasets grandes

## Estado del Proyecto

**Conclusión**: El proyecto se encuentra **completamente actualizado** con respecto a las tareas inmediatas listadas. La Fase 6 "Separación de Vistas" está marcada como COMPLETADA en el archivo de avances, y la implementación actual refleja esto.

### Próximas Fases Futuras (Fase 7+):
Según el documento de avances, las siguientes mejoras están planificadas pero no son inmediatas:
- Implementar gráficos y visualizaciones de datos avanzadas
- **Añadir soporte para más formatos de archivo (JSON, XML, etc.) - PLAN DETALLADO ABAJO**
- Implementar operaciones de transformación de datos
- Añadir funcionalidad de exportación a Excel
- Crear interfaz de configuración de optimizaciones
- Implementar temas y personalización de UI

---

## Plan Detallado: Soporte para Más Formatos de Archivo (Fase 7.2)

### Formatos Ya Soportados
- ✅ **Excel**: `.xlsx`, `.xls` (usando `openpyxl` y `pandas`)
- ✅ **CSV**: `.csv` (con carga por chunks para archivos grandes)
- ✅ **JSON**: `.json` (usando `pandas.read_json`)
- ✅ **XML**: `.xml` (usando `pandas.read_xml` o `lxml` como fallback)

### Formatos Adicionales a Implementar

#### 1. **TSV (Tab-Separated Values)**
- **Prioridad**: Alta
- **Complejidad**: Baja
- **Implementación**: Extensión de funcionalidad CSV existente
- **Dependencias**: Ninguna adicional

#### 2. **Parquet**
- **Prioridad**: Alta
- **Complejidad**: Media
- **Implementación**: Usar `pandas.read_parquet` con `pyarrow` o `fastparquet`
- **Dependencias**: `pyarrow>=10.0.0` o `fastparquet>=2023.0.0`
- **Ventajas**: Excelente compresión, rápido para datasets grandes

#### 3. **HDF5**
- **Prioridad**: Media
- **Complejidad**: Media-Alta
- **Implementación**: Usar `pandas.read_hdf` con `tables` (PyTables)
- **Dependencias**: `tables>=3.8.0`
- **Uso**: Datasets científicos grandes

#### 4. **Feather**
- **Prioridad**: Media
- **Complejidad**: Baja
- **Implementación**: Usar `pandas.read_feather` con `pyarrow`
- **Dependencias**: `pyarrow>=10.0.0`
- **Ventajas**: Muy rápido, formato columnar

#### 5. **Pickle (PKL)**
- **Prioridad**: Baja
- **Complejidad**: Baja
- **Implementación**: Usar `pandas.read_pickle`
- **Dependencias**: Ninguna adicional
- **Nota**: Solo para confianza total en la fuente

#### 6. **SQLite**
- **Prioridad**: Media
- **Complejidad**: Media
- **Implementación**: Usar `pandas.read_sql` con `sqlalchemy`
- **Dependencias**: Ya incluida (`sqlalchemy>=2.0.0`)
- **Uso**: Importar desde bases de datos

#### 7. **YAML**
- **Prioridad**: Baja
- **Complejidad**: Media
- **Implementación**: Usar `pandas.read_json` con preprocesamiento YAML
- **Dependencias**: `pyyaml>=6.0`

### Arquitectura de Implementación

#### Patrón de Diseño
- **Loader Pattern**: Crear una clase base `FileLoader` con método `load()` abstracto
- **Factory Pattern**: `FileLoaderFactory` que retorna el loader apropiado según extensión
- **Strategy Pattern**: Cada formato implementa su propia estrategia de carga

#### Estructura de Código
```
core/loaders/
├── base_loader.py          # Clase base FileLoader
├── csv_loader.py           # Loader para CSV/TSV
├── excel_loader.py         # Loader para Excel
├── json_loader.py          # Loader para JSON
├── xml_loader.py           # Loader para XML
├── parquet_loader.py       # Loader para Parquet
├── hdf5_loader.py          # Loader para HDF5
├── feather_loader.py       # Loader para Feather
├── pickle_loader.py        # Loader para Pickle
├── sqlite_loader.py        # Loader para SQLite
└── yaml_loader.py          # Loader para YAML
```

#### Integración con UI
- Actualizar `QFileDialog` en `main.py` para incluir nuevos formatos
- Modificar `cargar_datos_con_opciones()` para delegar a factory
- Mantener compatibilidad con opciones existentes (skip_rows, column_names)

### Plan de Implementación por Fases

#### Fase 7.2.1: Formatos de Alta Prioridad (Semana 1-2)
1. **TSV Support**
   - Extender `csv_loader.py` para detectar TSV por extensión
   - Usar `sep='\t'` en `pandas.read_csv`
   - Tests unitarios

2. **Parquet Support**
   - Instalar `pyarrow`
   - Crear `parquet_loader.py`
   - Soporte para opciones de carga
   - Tests unitarios

#### Fase 7.2.2: Formatos de Media Prioridad (Semana 3-4)
3. **Feather Support**
   - Usar `pyarrow` (ya incluido para Parquet)
   - Crear `feather_loader.py`
   - Tests unitarios

4. **SQLite Import Support**
   - Extender funcionalidad existente
   - Crear `sqlite_loader.py`
   - Diálogo para selección de tabla
   - Tests unitarios

#### Fase 7.2.3: Formatos Avanzados (Semana 5-6)
5. **HDF5 Support**
   - Instalar `tables`
   - Crear `hdf5_loader.py`
   - Manejo de keys/grupos HDF5
   - Tests unitarios

6. **YAML Support**
   - Instalar `pyyaml`
   - Crear `yaml_loader.py`
   - Conversión YAML a JSON para pandas
   - Tests unitarios

#### Fase 7.2.4: Formatos de Baja Prioridad (Semana 7-8)
7. **Pickle Support**
   - Crear `pickle_loader.py`
   - Advertencias de seguridad
   - Tests unitarios

### Consideraciones Técnicas

#### Optimización de Rendimiento
- Mantener carga por chunks para formatos que lo soporten
- Implementar sampling para preview de archivos grandes
- Cache inteligente para formatos comprimidos

#### Manejo de Errores
- Validación de dependencias al inicio
- Mensajes de error específicos por formato
- Fallback a formatos similares cuando sea posible

#### Compatibilidad
- Mantener API existente de `cargar_datos_con_opciones()`
- Soporte para `skip_rows` y `column_names` en todos los formatos
- Actualizar documentación y tooltips

#### Testing
- Tests unitarios para cada loader
- Tests de integración con UI
- Tests de rendimiento con archivos grandes
- Tests de edge cases (archivos corruptos, formatos inválidos)

### Dependencias Adicionales Requeridas
```python
# requirements.txt additions
pyarrow>=10.0.0          # Para Parquet y Feather
tables>=3.8.0           # Para HDF5
pyyaml>=6.0             # Para YAML
fastparquet>=2023.0.0   # Alternativa opcional para Parquet
```

### Métricas de Éxito
- ✅ Soporte para al menos 5 formatos adicionales
- ✅ Tiempo de carga < 30s para archivos de 100MB
- ✅ Cobertura de tests > 90%
- ✅ Compatibilidad backward completa
- ✅ Documentación actualizada

### Riesgos y Mitigaciones
- **Dependencias grandes**: Usar instalación opcional para formatos avanzados
- **Compatibilidad**: Tests exhaustivos en múltiples plataformas
- **Rendimiento**: Profiling y optimización durante desarrollo
- **Seguridad**: Validaciones estrictas para formatos binarios

## Recomendaciones

1. **Actualizar Documentación**: El archivo `avances.md` refleja correctamente el estado actual del proyecto.

2. **Pruebas de Usuario**: Como sugiere la "Próxima Revisión", sería beneficioso realizar pruebas exhaustivas con usuarios para validar la usabilidad de las nuevas vistas.

3. **Optimizaciones de UX**: Mejorar estilos, animaciones y responsividad de la interfaz.

4. **Funcionalidades Avanzadas**: Considerar implementar algunas de las mejoras futuras mencionadas.

## Plan de Acción Inmediato

Dado que no hay tareas pendientes inmediatas, se recomienda:

1. Realizar pruebas exhaustivas de la aplicación completa
2. Documentar cualquier bug o mejora de UX identificada
3. Preparar el proyecto para la siguiente fase de desarrollo
4. Actualizar la fecha de "Próxima Revisión" en `avances.md`

**Estado Final**: ✅ **No hay tareas pendientes inmediatas** - El proyecto está al día con las especificaciones documentadas.