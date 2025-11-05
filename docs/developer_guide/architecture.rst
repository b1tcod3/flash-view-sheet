Sistema de Arquitectura - Exportación Separada
==============================================

Esta documentación describe la arquitectura del sistema de Exportación de Datos Separados con Plantillas Excel.

Arquitectura General
-------------------

El sistema sigue una arquitectura modular con separación clara de responsabilidades:

.. code-block:: text

   📦 Flash Sheet Application
   ├── 🖥️ Interface Layer (UI)
   │   ├── ExportSeparatedDialog (Main Configuration)
   │   ├── ColumnMappingWidget (Column Management)
   │   ├── ExcelTemplateDialog (Template Selection)
   │   └── FilePreviewDialog (Preview & Validation)
   │
   ├── 🔧 Business Logic Layer
   │   ├── ExcelTemplateSplitter (Core Logic)
   │   ├── ExportSeparatedConfig (Configuration)
   │   └── Performance Optimization System
   │
   ├── 💾 Data Access Layer
   │   ├── Data Loading System
   │   ├── Transformation Pipeline
   │   └── Excel Template Management
   │
   └── 🗃️ Integration Layer
       ├── Main Application Menu
       ├── File System Operations
       └── Existing Flash Sheet Features

Diagrama de Flujo de Datos
--------------------------

.. code-block:: text

   📊 DataFrame Source 
           ↓
   ┌─────────────────────┐
   │  ExcelTemplateSplitter  │
   │  ┌─────────────────┐ │
   │  │ Validation       │ │
   │  │ ┌─────────────┐ │ │
   │  │ │ Data Analysis │ │ │
   │  │ │ & Preview    │ │ │
   │  │ └─────────────┘ │ │
   │  │                 │ │
   │  │ Column Mapping   │ │
   │  │ ┌─────────────┐ │ │
   │  │ │ Auto Detect  │ │ │
   │  │ │ Manual Config│ │ │
   │  │ └─────────────┘ │ │
   │  │                 │ │
   │  │ Export Process   │ │
   │  │ ┌─────────────┐ │ │
   │  │ │ Chunking     │ │ │
   │  │ │ Template Use │ │ │
   │  │ │ File Creation│ │ │
   │  │ └─────────────┘ │ │
   │  └─────────────────┘ │
   └─────────────────────┘
           ↓
   📁 Multiple Excel Files

Componentes Principales
-----------------------

1. ExcelTemplateSplitter (Core Logic)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Responsabilidad**: Lógica principal de separación y exportación

**Características**:
- Análisis y validación de DataFrame
- Gestión de configuración de separación
- Procesamiento con optimizaciones de memoria
- Manejo robusto de errores y recovery

**Código Base**: `core/data_handler.py`

2. ExportSeparatedConfig (Configuration Management)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Responsabilidad**: Gestión de configuraciones y validaciones

**Características**:
- Dataclass con validación integrada
- Mapeo de columnas flexible
- Configuración de plantillas Excel
- Opciones de rendimiento

**Campos Principales**:
- `separator_column`: Columna para separar datos
- `template_path`: Ruta a plantilla Excel
- `output_folder`: Carpeta destino
- `column_mapping`: Mapeo DataFrame ↔ Excel

3. UI Components (User Interface)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**ExportSeparatedDialog**: Diálogo principal de configuración

**ColumnMappingWidget**: Gestión flexible de mapeos

**ExcelTemplateDialog**: Selección y validación de plantillas

**FilePreviewDialog**: Vista previa de archivos a generar

Patrones de Diseño
-----------------

1. Factory Pattern
~~~~~~~~~~~~~~~~~~

Usado para creación de configuraciones y validación:

.. code-block:: python

   # Factory para configuración
   config = ExportSeparatedConfig(
       separator_column="category",
       template_path="template.xlsx",
       # ... más parámetros
   )

2. Strategy Pattern
~~~~~~~~~~~~~~~~~~

Para diferentes estrategias de optimización:

.. code-block:: python

   class ChunkingStrategy(Enum):
       NONE = "none"
       MODERATE = "moderate"
       SIZE_BASED = "size"
       GROUP_BASED = "group"
       AGGRESSIVE = "aggressive"

3. Observer Pattern
~~~~~~~~~~~~~~~~~~

Para notificaciones de progreso:

.. code-block:: python

   def progress_callback(processed_groups, total_groups):
       # Actualizar UI con progreso
       update_progress_bar(processed_groups, total_groups)

4. Template Method Pattern
~~~~~~~~~~~~~~~~~~~~~~~~~~

Para procesamiento de plantillas Excel:

.. code-block:: python

   def _create_excel_file_with_template(self, output_path, data):
       # Template method con pasos definidos
       workbook = self._load_template()
       self._apply_column_mapping(data)
       self._insert_data(data)
       self._save_file(output_path)

Manejo de Memoria y Rendimiento
-------------------------------

1. Sistema de Chunking Inteligente
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Estrategias Disponibles**:

- **NONE**: Sin chunking (datasets pequeños)
- **MODERATE**: Chunking conservador (datasets medianos)
- **SIZE_BASED**: Basado en tamaño de memoria
- **GROUP_BASED**: Basado en número de grupos
- **AGGRESSIVE**: Chunking agresivo (datasets muy grandes)

**Decisión Automática**:

.. code-block:: python

   def determine_optimal_chunking_strategy(self, df, separator_column):
       # Análisis de dataset para estrategia óptima
       total_rows = len(df)
       memory_usage = df.memory_usage(deep=True).sum()
       unique_groups = df[separator_column].nunique()
       
       if total_rows > 100000 and memory_usage > 500 * 1024 * 1024:
           return ChunkingStrategy.AGGRESSIVE
       elif total_rows > 10000:
           return ChunkingStrategy.MODERATE
       else:
           return ChunkingStrategy.NONE

2. Gestión de Memoria
~~~~~~~~~~~~~~~~~~~~

**Monitoreo Continuo**:

- Tracking de uso de memoria en tiempo real
- Garbage collection automático
- Límites configurables (default: 2GB)

**Recovery Automático**:

- Cleanup de archivos temporales
- Continuidad de operaciones interrumpidas
- Progreso persistente en archivos .json

3. Optimización de Plantillas Excel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Preservación de Formato**:

- openpyxl para máxima compatibilidad
- Preservación completa de estilos
- Mantenimiento de fórmulas y formatos

**Cache de Formatos**:

- Cache de formatos Excel para performance
- Reutilización de estilos entre archivos
- Optimización de operaciones de escritura

Integración con Sistema Existente
---------------------------------

1. Menú Principal
~~~~~~~~~~~~~~~~

**Ubicación**: Nivel "Separar" al mismo nivel que "Archivo"

**Opciones Disponibles**:
- Exportar Datos Separados
- Configurar Plantillas

2. Sistema de Validación
~~~~~~~~~~~~~~~~~~~~~~~

**Integración con Sistema de Loaders**:
- Compatible con todos los formatos soportados
- Validación de datos integrada
- Manejo de errores consistente

3. Sistema de Transformaciones
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Compatibilidad con Pipeline de Transformaciones**:
- Funciona con datos transformados
- Preserva historial de transformaciones
- No interfiere con funcionalidades existentes

Manejo de Errores
-----------------

1. Jerarquía de Excepciones
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   SeparationError (Base)
   ├── TemplateError (Problemas con plantillas Excel)
   ├── ConfigurationError (Configuración inválida)
   └── MemoryError (Problemas de memoria)

2. Recovery Automático
~~~~~~~~~~~~~~~~~~~~

**Estrategias de Recovery**:
- Templates por defecto para archivos corruptos
- Auto-renombrado para conflictos de nombres
- Continuidad post-falla con progreso persistente

3. Logging y Auditoría
~~~~~~~~~~~~~~~~~~~~

**Sistema de Logging**:
- Logging detallado para debugging
- Métricas de rendimiento
- Auditoría de operaciones

Flujo de Procesamiento Detallado
-------------------------------

1. **Inicialización**
   - Cargar DataFrame
   - Validar datos
   - Configurar optimizaciones

2. **Configuración**
   - Seleccionar columna de separación
   - Configurar plantilla Excel
   - Definir mapeo de columnas

3. **Validación**
   - Verificar integridad de datos
   - Validar configuración
   - Generar preview

4. **Procesamiento**
   - Separar por grupos
   - Aplicar plantilla
   - Crear archivos Excel

5. **Finalización**
   - Generar resumen
   - Cleanup de archivos temporales
   - Reporte de resultados

Consideraciones de Escalabilidad
-------------------------------

1. **Datasets Pequeños** (< 10K filas)
   - Sin chunking
   - Procesamiento directo
   - Tiempo objetivo: < 30 segundos

2. **Datasets Medianos** (10K-100K filas)
   - Chunking moderado
   - Optimización de memoria
   - Tiempo objetivo: < 3 minutos

3. **Datasets Grandes** (100K-1M+ filas)
   - Chunking agresivo
   - Monitoreo continuo
   - Tiempo objetivo: < 15 minutos

Extensibilidad del Sistema
-------------------------

1. **Nuevas Estrategias de Chunking**
   - Implementar nuevas estrategias en `ChunkingStrategy`
   - Agregar lógica de decisión en `determine_optimal_chunking_strategy`

2. **Nuevos Tipos de Plantillas**
   - Extender `ExcelTemplateManager`
   - Agregar nuevos formatos de importación

3. **Nuevas Validaciones**
   - Extender `ValidationResult`
   - Agregar nuevos tipos de validación

4. **Nuevos Formatos de Salida**
   - Implementar nuevos exportadores
   - Agregar soporte para diferentes formatos

Futuras Mejoras
--------------

1. **Paralelización**
   - Procesamiento paralelo de grupos
   - Multi-threading para I/O

2. **Cloud Integration**
   - Soporte para storage en la nube
   - Sincronización automática

3. **Advanced Templates**
   - Plantillas dinámicas
   - Configuración visual de plantillas

4. **Real-time Processing**
   - Streaming para datasets masivos
   - Procesamiento en tiempo real