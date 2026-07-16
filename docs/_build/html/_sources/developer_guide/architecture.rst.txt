Sistema de Arquitectura de Flash Sheet
=======================================

Esta documentación describe la arquitectura completa de Flash Sheet, una aplicación de escritorio para visualización y análisis de datos tabulares.

Resumen de Arquitectura
-----------------------

Flash Sheet es una aplicación de escritorio desarrollada en Python usando PySide6 (Qt6) que implementa una arquitectura MVC (Modelo-Vista-Controlador) con clara separación de responsabilidades. La aplicación está diseñada para manejar datasets grandes con optimizaciones de rendimiento y memoria.

**Arquitectura General**:

.. code-block:: text

    ┌─────────────────────────────────────────────────────────────┐
    │                    Aplicación Flash Sheet                   │
    │  ┌─────────────────────────────────────────────────────────┐ │
    │  │                    MainWindow (Controlador)              │ │
    │  │  ┌─────────────────────────────────────────────────────┐ │ │
    │  │  │  Barra de Menú  │  Barra de Herramientas  │  Barra de Estado               │ │ │
    │  │  └─────────────────────────────────────────────────────┘ │ │
    │  │  ┌─────────────────────────────────────────────────────┐ │ │
    │  │  │              QStackedWidget (Vistas)                 │ │ │
    │  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │ │ │
    │  │  │  │MainView │ │DataView │ │Graphics │ │Joined   │     │ │ │
    │  │  │  │         │ │         │ │ View    │ │DataView │     │ │ │
    │  │  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘     │ │ │
    │  │  └─────────────────────────────────────────────────────┘ │ │
    │  └─────────────────────────────────────────────────────────┘ │
    │  ┌─────────────────────────────────────────────────────────┐ │
    │  │                 Lógica de Negocio Core                      │ │
    │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐         │ │
    │  │  │Data     │ │Join     │ │Pivot    │ │Export   │         │ │
    │  │  │Handler  │ │Manager  │ │Tables  │ │Functions│         │ │
    │  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘         │ │
    │  └─────────────────────────────────────────────────────────┘ │
    │  ┌─────────────────────────────────────────────────────────┐ │
    │  │                    Componentes UI                         │ │
    │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐         │ │
    │  │  │Widgets  │ │Dialogs  │ │Views    │ │Modals   │         │ │
    │  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘         │ │
    │  └─────────────────────────────────────────────────────────┘ │
    │  ┌─────────────────────────────────────────────────────────┐ │
    │  │                 Capa de Acceso a Datos                    │ │
    │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐         │ │
    │  │  │File     │ │Database │ │Memory   │ │Cache    │         │ │
    │  │  │Loaders  │ │Connect. │ │Manager  │ │System   │         │ │
    │  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘         │ │
    │  └─────────────────────────────────────────────────────────┘ │
    └─────────────────────────────────────────────────────────────┘

Componentes Principales de Arquitectura
----------------------------------------

1. **MainWindow (Controlador Principal)**
   - Coordina todas las operaciones de aplicación
   - Gestiona el ciclo de vida de vistas
   - Maneja comunicación entre componentes
   - Implementa patrón Singleton para acceso global

2. **Sistema de Vistas (Capa de Vista)**
   - **MainView**: Vista inicial con opciones de carga de datos
   - **DataView**: Vista de tabla con paginación y filtrado
   - **GraphicsView**: Herramientas de gráficos y visualización
   - **JoinedDataView**: Resultados de operaciones de unión de datos

3. **Lógica de Negocio Core**
   - **DataHandler**: Gestión de carga, procesamiento y exportación de datos
   - **JoinManager**: Operaciones de unión de datos tipo SQL
   - **PivotTables**: Funcionalidades de tablas pivote
   - **ExportFunctions**: Múltiples formatos de exportación

4. **Componentes UI**
   - Widgets reutilizables para interfaces
   - Diálogos modales para configuraciones
   - Barras de herramientas y menús

5. **Capa de Acceso a Datos**
   - Cargadores especializados por formato de archivo
   - Conexiones de base de datos
   - Gestión de memoria y caché

Flujo de Datos Principal
------------------------

.. code-block:: text

    Usuario → MainWindow → Vista Activa → Lógica Core → Acceso a Datos → Almacenamiento
       ↓       ↓       ↓       ↓       ↓       ↓
    Interfaz ← Coordinación ← Actualización ← Procesamiento ← Consulta ← Persistencia

**Flujo Detallado**:

1. **Entrada de Usuario**: Acciones de menú, botones, diálogos
2. **Coordinación**: MainWindow dirige acción a vista apropiada
3. **Procesamiento**: Vista delega lógica de negocio a módulo Core correspondiente
4. **Acceso a Datos**: Core usa Capa de Acceso a Datos para operaciones I/O
5. **Actualización UI**: Resultados fluyen de vuelta actualizando vistas
6. **Persistencia**: Datos se guardan según formato requerido

Patrones de Diseño Implementados
-------------------------------

1. **MVC (Modelo-Vista-Controlador)**
   - **Modelo**: DataFrames de Pandas, configuraciones, estado de aplicación
   - **Vista**: Clases PySide6 (QWidgets, QDialogs, vistas personalizadas)
   - **Controlador**: MainWindow coordina entre modelos y vistas

2. **Patrón Observer**
   - Señales y slots de Qt para comunicación de componentes
   - Callbacks para notificación de progreso en operaciones largas

3. **Patrón Factory**
   - Creación de cargador de archivos según extensión
   - Generación de configuración y validador

4. **Patrón Strategy**
   - Diferentes estrategias de chunking para datasets grandes
   - Múltiples algoritmos de exportación

5. **Patrón Singleton**
   - Instancia única de MainWindow
   - Managers compartidos (JoinHistory, etc.)

6. **Patrón Command**
   - Operaciones de transformación de datos encapsuladas
   - Historial de operaciones para deshacer/rehacer

Características Avanzadas
-------------------------

Flash Sheet implementa características avanzadas con arquitecturas especializadas:

Arquitectura General
--------------------

Flash Sheet implementa una arquitectura modular con clara separación de responsabilidades para sus dos funcionalidades principales:

**Exportación Separada**: Sistema para dividir datasets en múltiples archivos Excel usando plantillas
**Uniones de Datos (Joins)**: Sistema para combinar datasets a través de operaciones de unión

El sistema sigue una arquitectura modular con clara separación de responsabilidades:

.. code-block:: text

   📦 Aplicación Flash Sheet
   ├── 🖥️ Capa de Interfaz (UI)
   │   ├── ExportSeparatedDialog (Configuración Principal)
   │   ├── ColumnMappingWidget (Gestión de Columnas)
   │   ├── ExcelTemplateDialog (Selección de Plantilla)
   │   └── FilePreviewDialog (Preview y Validación)
   │
   ├── 🔧 Capa de Lógica de Negocio
   │   ├── ExcelTemplateSplitter (Lógica Core)
   │   ├── ExportSeparatedConfig (Configuración)
   │   └── Sistema de Optimización de Performance
   │
   ├── 💾 Capa de Acceso a Datos
   │   ├── Sistema de Carga de Datos
   │   ├── Pipeline de Transformación
   │   └── Gestión de Plantillas Excel
   │
   └── 🗃️ Capa de Integración
       ├── Menú Principal de Aplicación
       ├── Operaciones de Sistema de Archivos
       └── Características Existentes de Flash Sheet

Diagrama de Flujo de Datos
--------------------------

.. code-block:: text

   📊 DataFrame Fuente
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
   📁 Múltiples Archivos Excel

**Uniones de Datos (Sistema Join)**:

.. code-block:: text

   📊 DataFrame Izquierdo     📊 DataFrame Derecho
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
   │  └─────────────┘ │ │
   │                  │ │
   │ Join Execution  │ │
   │ ┌─────────────┐ │ │
   │ │ Inner/Left/ │ │ │
   │ │ Right/Cross │ │ │
   │ │ Operations  │ │ │
   │ └─────────────┘ │ │
   └─────────────────┘ │
           ↓
   📊 DataFrame Unificado + Metadata
           ↓
   💾 Almacenamiento JoinHistory

Componentes Principales
-----------------------

1. ExcelTemplateSplitter (Lógica Core)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Responsabilidad**: Lógica principal de separación y exportación

**Características**:
- Análisis y validación de DataFrame
- Gestión de configuración de separación
- Procesamiento con optimizaciones de memoria
- Manejo robusto de errores y recuperación

**Código Base**: `core/data_handler.py`

2. ExportSeparatedConfig (Gestión de Configuración)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Responsabilidad**: Gestión de configuración y validación

**Características**:
- Dataclass con validación integrada
- Mapeo flexible de columnas
- Configuración de plantillas Excel
- Opciones de performance

**Campos**:
- `separator_column`: Columna para separación de datos
- `template_path`: Ruta a plantilla Excel
- `output_folder`: Carpeta destino
- `column_mapping`: Mapeo DataFrame ↔ Excel de columnas

3. Componentes UI (Interfaz de Usuario)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**ExportSeparatedDialog**: Diálogo principal de configuración

**ColumnMappingWidget**: Gestión flexible de mapeo

**ExcelTemplateDialog**: Selección y validación de plantilla

**FilePreviewDialog**: Preview de archivos a generar

4. DataJoinManager (Lógica Core de Join)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Responsabilidad**: Lógica principal de operaciones de unión de datos

**Características**:
- Ejecución de operaciones de unión (inner, left, right, cross)
- Gestión automática de memoria con chunking
- Validación de compatibilidad de datos
- Optimizaciones de performance para datasets grandes
- Generación detallada de metadata

**Código Base**: `core/join/data_join_manager.py`

5. JoinConfig (Configuración de Join)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Responsabilidad**: Gestión de configuración para operaciones de join

**Características**:
- Configuración completa de parámetros para joins
- Validación integrada de configuración
- Soporte para múltiples tipos de join
- Gestión de sufijos para columnas duplicadas

**Campos**:
- `join_type`: Tipo de join (INNER, LEFT, RIGHT, CROSS)
- `left_keys`/`right_keys`: Columnas de join
- `suffixes`: Sufijos para columnas duplicadas
- `validate_integrity`: Validación de integridad referencial

6. JoinHistory (Gestión de Historial)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Responsabilidad**: Sistema de historial para operaciones de join

**Características**:
- Almacenamiento persistente de operaciones
- Re-ejecución de joins previos
- Importación/exportación de configuración
- Gestión automática de límite de entradas

**Código Base**: `core/join/join_history.py`

7. Componentes UI - Sistema Join
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**JoinDialog**: Diálogo principal de configuración de join

**JoinedDataView**: Vista especializada para resultados de join con metadata

Patrones de Diseño
------------------

1. Patrón Factory
~~~~~~~~~~~~~~~~~

Usado para creación de configuración y validación:

.. code-block:: python

   # Factory de configuración
   config = ExportSeparatedConfig(
       separator_column="categoria",
       template_path="plantilla.xlsx",
       # ... más parámetros
   )

2. Patrón Strategy
~~~~~~~~~~~~~~~~~~

Para diferentes estrategias de optimización:

.. code-block:: python

   class ChunkingStrategy(Enum):
       NONE = "none"
       MODERATE = "moderate"
       SIZE_BASED = "size"
       GROUP_BASED = "group"
       AGGRESSIVE = "aggressive"

3. Patrón Observer
~~~~~~~~~~~~~~~~~~

Para notificaciones de progreso:

.. code-block:: python

   def progress_callback(groups_procesados, total_groups):
       # Actualizar UI con progreso
       update_progress_bar(groups_procesados, total_groups)

4. Patrón Template Method
~~~~~~~~~~~~~~~~~~~~~~~~~

Para procesamiento de plantillas Excel:

.. code-block:: python

   def _create_excel_file_with_template(self, output_path, data):
       # Método template con pasos definidos
       workbook = self._load_template()
       self._apply_column_mapping(data)
       self._insert_data(data)
       self._save_file(output_path)

5. Patrón Strategy (Sistema Join)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Para diferentes estrategias de chunking en joins:

.. code-block:: python

   class JoinChunkingStrategy(Enum):
       NONE = "none"           # Sin chunking
       CROSS_OPTIMIZED = "cross"  # Optimizado para cross joins
       MEMORY_BASED = "memory"    # Basado en límites de memoria
       SIZE_BASED = "size"        # Basado en tamaño de dataset

6. Patrón Factory (Sistema Join)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Para creación de configuración de join:

.. code-block:: python

   # Factory de configuración de join
   config = JoinConfig(
       join_type=JoinType.LEFT,
       left_keys=['customer_id'],
       right_keys=['id'],
       suffixes=('_sales', '_customer'),
       validate_integrity=True
   )

Gestión de Memoria y Performance
--------------------------------

1. Sistema de Chunking Inteligente Automático
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~

**Monitoreo Continuo**:

- Seguimiento continuo de uso de memoria
- Recolección automática de basura
- Límites configurables (por defecto: 2GB)
- Alertas automáticas de uso excesivo

**Recuperación Automática**:

- Limpieza de archivos temporales
- Continuidad de operaciones interrumpidas
- Persistencia de progreso en archivos .json

3. Preservación de Formato de Plantilla Excel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Preservación Completa de Formato**:

- Uso exclusivo de openpyxl para máxima compatibilidad
- Preservación completa de estilos
- Mantenimiento de fórmulas y validaciones
- Compatibilidad con Excel 2016+

**Caché de Formato**:

- Caché de formato Excel para performance
- Reutilización de estilos entre archivos
- Optimización de operaciones de escritura

4. Optimizaciones de Memoria - Sistema Join
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Chunking Inteligente para Joins**:

- **Cross Joins**: Procesamiento por chunks del dataset más pequeño
- **Regular Joins**: Chunking del dataset más grande cuando necesario
- **Memory-Based**: Activación automática cuando se excede umbral de memoria
- **Size-Based**: Basado en tamaño de resultado estimado

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

Integración del Sistema
-----------------------

1. Menú Principal
~~~~~~~~~~~~~~~~~

**Ubicación**: Nivel "Separar" al mismo nivel que "Archivo"

**Opciones Disponibles**:
- Exportar Datos Separados
- Configurar Plantillas

2. Sistema de Validación
~~~~~~~~~~~~~~~~~~~~~~~~

**Integración con Cargadores Existentes**:
- Compatible con todos los formatos soportados
- Validación integrada de datos
- Manejo consistente de errores

3. Sistema de Transformación
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Compatibilidad con Pipeline de Transformación**:
- Funciona con datos transformados
- Preserva historial de transformación
- No interfiere con funcionalidades existentes

4. Integración de Sistema Join
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Menú Principal - Sistema Join**:

**Ubicación**: Nuevo menú "Datos" con opción "Unir Datos..."

**Opciones Disponibles**:
- Unir Datos...: Abre diálogo de configuración de join
- Historial de Join: Gestión de operaciones de join

**Sistema de Validación - Integración Join**:

**Integración con Sistema de Cargadores**:
- Compatible con todos los formatos soportados
- Validación automática de tipos de datos para joins
- Detección de columnas compatibles

**Sistema de Transformación - Compatibilidad Join**:
- Los joins funcionan con datos previamente transformados
- Los resultados de join pueden transformarse posteriormente
- Historial completo preservado entre operaciones

Manejo de Errores
-----------------

1. Jerarquía de Excepciones
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   SeparationError (Base)
   ├── TemplateError (Problemas de plantilla Excel)
   ├── ConfigurationError (Configuración inválida)
   └── MemoryError (Problemas de memoria)

**Jerarquía de Excepciones - Sistema Join**:

.. code-block:: text

   JoinError (Base)
   ├── JoinValidationError (Errores de validación de configuración)
   ├── JoinExecutionError (Errores de ejecución)
   ├── MemoryLimitExceededError (Límite de memoria excedido)
   └── UnsupportedJoinError (Tipo de join no soportado)

2. Recuperación Automática
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Estrategias de Recuperación**:
- Plantillas predeterminadas para archivos corruptos
- Renombrado automático para conflictos de nombres
- Continuidad post-falla con persistencia de progreso

3. Logging y Auditoría
~~~~~~~~~~~~~~~~~~~~~~~

**Sistema de Logging**:
- Logging detallado para debugging
- Métricas automáticas de performance
- Auditoría de operaciones

Flujo de Procesamiento Detallado
--------------------------------

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
   - Limpiar archivos temporales
   - Reporte de resultados

Consideraciones de Escalabilidad
--------------------------------

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

**Consideraciones de Escalabilidad - Sistema Join**:

4. **Cross Joins Grandes** (Producto Cartesiano)
   - Chunking automático del dataset más pequeño
   - Monitoreo continuo de memoria
   - Tiempo objetivo: Dependiente del tamaño del resultado

5. **Joins de Datasets Desbalanceados**
   - Optimización automática basada en tamaños relativos
   - Selección inteligente de dataset de referencia
   - Eficiente en memoria para joins left/right

6. **Joins de Múltiples Columnas**
   - Optimización de índice para múltiples claves
   - Validación eficiente de integridad
   - Optimizado en memoria para joins complejos

Extensibilidad del Sistema
--------------------------

1. **Nuevas Estrategias de Chunking**
   - Implementar nuevas estrategias en `ChunkingStrategy`
   - Agregar lógica de decisión en `determine_optimal_chunking_strategy`

2. **Nuevos Tipos de Plantilla**
   - Extender `ExcelTemplateManager`
   - Agregar nuevos formatos de importación

3. **Nuevas Validaciones**
   - Extender `ValidationResult`
   - Agregar nuevos tipos de validación

4. **Nuevos Formatos de Salida**
   - Implementar nuevos exportadores
   - Agregar soporte para diferentes formatos

**Extensibilidad del Sistema - Sistema Join**:

5. **Nuevos Tipos de Join**
   - Extender enum `JoinType`
   - Implementar lógica específica en `DataJoinManager`
   - Agregar validaciones correspondientes

6. **Nuevas Estrategias de Chunking**
   - Implementar `JoinChunkingStrategy` adicional
   - Agregar lógica de decisión en `_should_use_chunking`
   - Optimizar para casos de uso específicos

7. **Nuevos Validadores de Datos**
   - Extender `ValidationResult` con nuevas reglas
   - Implementar validaciones específicas de dominio
   - Agregar soporte para tipos de datos personalizados

8. **Nuevos Formatos de Historial**
   - Extender `JoinHistory` para nuevos formatos
   - Agregar importación/exportación para diferentes serializaciones
   - Implementar sincronización de base de datos

Mejoras Futuras
---------------

1. **Paralelización**
   - Procesamiento paralelo de grupos
   - Multi-threading para I/O

2. **Integración Cloud**
   - Exportación directa a servicios cloud
   - Sincronización automática

3. **Plantillas Avanzadas**
   - Plantillas dinámicas
   - Configuración visual de plantillas

4. **Procesamiento en Tiempo Real**
   - Streaming para datasets masivos
   - Procesamiento en tiempo real

**Mejoras Futuras - Sistema Join**:

5. **Joins Paralelos**
   - Procesamiento paralelo de chunks
   - Multi-threading para cross joins grandes
   - Optimización para sistemas multi-core

6. **Joins Distribuidos**
   - Soporte para datasets que no caben en memoria
   - Integración con bases de datos externas
   - Procesamiento distribuido en clusters

7. **Joins Inteligentes**
   - Detección automática de tipos de join apropiados
   - Sugerencias basadas en análisis de datos
   - Optimización automática de configuración

8. **Joins de Condiciones Complejas**
   - Soporte para joins con condiciones no de igualdad
   - Joins personalizados basados en funciones
   - Joins basados en similitud de texto