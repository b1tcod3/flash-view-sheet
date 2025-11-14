Sistema de Arquitectura - Flash Sheet
=====================================

Esta documentación describe la arquitectura de los sistemas principales de Flash Sheet, incluyendo Exportación de Datos Separados y Cruce de Datos (Joins).

Arquitectura General
-------------------

Flash Sheet implementa una arquitectura modular con separación clara de responsabilidades para sus dos funcionalidades principales:

**Exportación Separada**: Sistema para dividir datasets en múltiples archivos Excel usando plantillas
**Cruce de Datos (Joins)**: Sistema para combinar datasets mediante operaciones de join

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

**Cruce de Datos (Join System)**:

.. code-block:: text

   📊 Left DataFrame     📊 Right DataFrame
           ↓                     ↓
   ┌─────────────────────┐       │
   │  DataJoinManager    │◄──────┘
   │  ┌─────────────────┐ │
   │  │ Join Processing │ │
   │  │ ┌─────────────┐ │ │
   │  │ │ Validation   │ │ │
   │  │ │ ┌─────────┐ │ │ │ │
   │  │ │ │ Type     │ │ │ │ │
   │  │ │ │ Check    │ │ │ │ │
   │  │ │ └─────────┘ │ │ │ │
   │  │ │             │ │ │ │
   │  │ │ Memory Est. │ │ │ │
   │  │ │ ┌─────────┐ │ │ │ │
   │  │ │ │ Chunking │ │ │ │ │
   │  │ │ │ Decision │ │ │ │ │
   │  │ │ └─────────┘ │ │ │ │
   │  │ └─────────────┘ │ │
   │  │                 │ │
   │  │ Join Execution  │ │
   │  │ ┌─────────────┐ │ │
   │  │ │ Inner/Left/ │ │ │
   │  │ │ Right/Cross │ │ │
   │  │ │ Operations  │ │ │
   │  │ └─────────────┘ │ │
   │  └─────────────────┘ │
   └─────────────────────┘
           ↓
   📊 Joined DataFrame + Metadata
           ↓
   💾 JoinHistory Storage

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

4. DataJoinManager (Core Join Logic)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Responsabilidad**: Lógica principal de operaciones de cruce de datos

**Características**:
- Ejecución de operaciones de join (inner, left, right, cross)
- Gestión automática de memoria con chunking
- Validación de compatibilidad de datos
- Optimizaciones de rendimiento para datasets grandes
- Generación de metadatos detallados

**Código Base**: `core/join/data_join_manager.py`

5. JoinConfig (Join Configuration)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Responsabilidad**: Gestión de configuraciones para operaciones de join

**Características**:
- Configuración completa de parámetros de join
- Validación integrada de configuración
- Soporte para múltiples tipos de join
- Gestión de sufijos para columnas duplicadas

**Campos Principales**:
- `join_type`: Tipo de join (INNER, LEFT, RIGHT, CROSS)
- `left_keys`/`right_keys`: Columnas de join
- `suffixes`: Sufijos para columnas duplicadas
- `validate_integrity`: Validación de integridad referencial

6. JoinHistory (History Management)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Responsabilidad**: Sistema de historial para operaciones de join

**Características**:
- Almacenamiento persistente de operaciones
- Re-ejecución de joins previos
- Exportación/importación de configuraciones
- Gestión automática de límite de entradas

**Código Base**: `core/join/join_history.py`

7. UI Components - Join System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**JoinDialog**: Diálogo principal de configuración de joins

**JoinedDataView**: Vista especializada para resultados de joins con metadatos

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

5. Strategy Pattern (Join System)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Para diferentes estrategias de chunking en joins:

.. code-block:: python

   class JoinChunkingStrategy(Enum):
       NONE = "none"           # Sin chunking
       CROSS_OPTIMIZED = "cross"  # Optimizado para cross joins
       MEMORY_BASED = "memory"    # Basado en límites de memoria
       SIZE_BASED = "size"        # Basado en tamaño de datasets

6. Factory Pattern (Join System)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Para creación de configuraciones de join:

.. code-block:: python

   # Factory para configuración de join
   config = JoinConfig(
       join_type=JoinType.LEFT,
       left_keys=['customer_id'],
       right_keys=['id'],
       suffixes=('_sales', '_customer'),
       validate_integrity=True
   )

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

4. Optimizaciones de Memoria - Join System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Chunking Inteligente para Joins**:

- **Cross Joins**: Procesamiento por chunks del dataset más pequeño
- **Regular Joins**: Chunking del dataset más grande cuando es necesario
- **Memory-Based**: Activación automática cuando se supera umbral de memoria
- **Size-Based**: Basado en tamaño estimado del resultado

**Estimación de Memoria**:

.. code-block:: python

    def _estimate_memory_usage(self, config: JoinConfig) -> float:
        # Estimación basada en tipos de join
        if config.join_type == JoinType.CROSS:
            # Cross join: producto cartesiano
            estimated_rows = len(left_df) * len(right_df)
        else:
            # Otros joins: estimación conservadora
            estimated_rows = max(len(left_df), len(right_df))

        # Memoria por celda × filas × columnas
        return estimated_rows * total_cols * 8  # 8 bytes por valor

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

4. Integración del Sistema de Joins
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Menú Principal - Join System**:

**Ubicación**: Nuevo menú "Datos" con opción "Cruzar Datos..."

**Opciones Disponibles**:
- Cruzar Datos...: Abre diálogo de configuración de joins
- Historial de Joins: Gestión del historial de operaciones

**Sistema de Validación - Join Integration**:

**Integración con Sistema de Loaders**:
- Compatible con todos los formatos soportados
- Validación automática de tipos de datos para joins
- Detección de columnas compatibles

**Sistema de Transformaciones - Join Compatibility**:
- Joins funcionan con datos previamente transformados
- Resultados de joins pueden ser transformados posteriormente
- Historial completo preservado a través de operaciones

Manejo de Errores
-----------------

1. Jerarquía de Excepciones
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   SeparationError (Base)
   ├── TemplateError (Problemas con plantillas Excel)
   ├── ConfigurationError (Configuración inválida)
   └── MemoryError (Problemas de memoria)

**Jerarquía de Excepciones - Join System**:

.. code-block:: text

   JoinError (Base)
   ├── JoinValidationError (Errores de validación de configuración)
   ├── JoinExecutionError (Errores durante ejecución)
   ├── MemoryLimitExceededError (Límite de memoria excedido)
   └── UnsupportedJoinError (Tipo de join no soportado)

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

**Consideraciones de Escalabilidad - Join System**:

4. **Cross Joins Grandes** (Producto Cartesiano)
    - Chunking automático del dataset más pequeño
    - Monitoreo de memoria continuo
    - Tiempo objetivo: Dependiente del tamaño del resultado

5. **Joins con Datasets Desbalanceados**
    - Optimización automática basada en tamaños relativos
    - Selección inteligente del dataset de referencia
    - Memoria eficiente para joins left/right

6. **Joins Múltiples Columnas**
    - Optimización de índices para múltiples keys
    - Validación eficiente de integridad referencial
    - Memoria optimizada para joins complejos

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

**Extensibilidad del Sistema - Join System**:

5. **Nuevos Tipos de Join**
    - Extender `JoinType` enum
    - Implementar lógica específica en `DataJoinManager`
    - Agregar validaciones correspondientes

6. **Nuevas Estrategias de Chunking**
    - Implementar `JoinChunkingStrategy` adicionales
    - Agregar lógica de decisión en `_should_use_chunking`
    - Optimizar para casos de uso específicos

7. **Nuevos Validadores de Datos**
    - Extender `ValidationResult` con nuevas reglas
    - Implementar validaciones específicas de dominio
    - Agregar soporte para tipos de datos personalizados

8. **Nuevos Formatos de Historial**
    - Extender `JoinHistory` para nuevos formatos
    - Agregar import/export para diferentes serializaciones
    - Implementar sincronización con bases de datos

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

**Futuras Mejoras - Join System**:

5. **Joins en Paralelo**
    - Procesamiento paralelo de chunks
    - Multi-threading para cross joins grandes
    - Optimización para sistemas multi-core

6. **Joins Distribuidos**
    - Soporte para datasets que no caben en memoria
    - Integración con bases de datos externas
    - Procesamiento distribuido en clúster

7. **Joins Inteligentes**
    - Detección automática de tipos de join apropiados
    - Sugerencias basadas en análisis de datos
    - Optimización automática de configuración

8. **Joins con Condiciones Complejas**
    - Soporte para joins con condiciones no-equality
    - Joins con funciones personalizadas
    - Joins basados en similitud de texto