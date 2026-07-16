# Diseño Arquitectónico: Funcionalidad de Cruce de Datos

## Resumen Ejecutivo

Este documento detalla el diseño arquitectónico para la implementación de la funcionalidad de cruce de datos en Flash View Sheet. Se define la estructura de componentes, interfaces, formatos de datos y sistemas de validación que permitirán integrar operaciones de join con el sistema existente.

## Arquitectura General

### Componentes Principales

#### 1. DataJoinManager
**Ubicación:** `core/join/data_join_manager.py`

Clase principal responsable de ejecutar operaciones de cruce entre datasets.

**Responsabilidades:**
- Ejecutar operaciones de join (inner, left, right, cross)
- Gestionar memoria para datasets grandes
- Optimizar rendimiento con chunking
- Validar compatibilidad de datos
- Generar metadatos del cruce

**Interfaz Principal:**
```python
class DataJoinManager:
    def __init__(self, left_df: pd.DataFrame, right_df: pd.DataFrame):
        pass

    def execute_join(self, config: JoinConfig) -> JoinResult:
        pass

    def validate_join(self, config: JoinConfig) -> ValidationResult:
        pass

    def get_join_preview(self, config: JoinConfig, max_rows: int = 100) -> pd.DataFrame:
        pass
```

#### 2. JoinDialog
**Ubicación:** `app/widgets/join/join_dialog.py`

Diálogo modal para configurar operaciones de cruce.

**Características:**
- Selección de dataset adicional
- Configuración de columnas para join
- Selección de tipo de join
- Configuración de sufijos para columnas duplicadas
- Preview de resultados antes de ejecutar
- Validación en tiempo real

#### 3. JoinedDataView
**Ubicación:** `app/widgets/join/joined_data_view.py`

Vista especializada para mostrar resultados de cruces.

**Funcionalidades:**
- Herencia de DataView existente
- Metadatos del cruce (filas resultantes, tiempo de procesamiento)
- Información de origen de datos (dataset izquierdo/derecho)
- Estadísticas del cruce
- Opciones de filtrado específicas para datos cruzados

#### 4. JoinHistory
**Ubicación:** `core/join/join_history.py`

Sistema para mantener historial de operaciones de cruce.

**Características:**
- Almacenamiento de configuraciones de join
- Re-ejecución de joins previos
- Exportación/importación de configuraciones
- Gestión de memoria para historial

### Integración con Sistema Existente

#### Modificaciones a MainWindow
- Nuevo menú "Datos" > "Cruzar Datos..."
- Gestión de múltiples datasets (principal + adicional)
- Integración con sistema de vistas existente

#### Uso de Componentes Existentes
- `core/data_handler.py`: Carga de dataset adicional
- `DataView`: Visualización de resultados
- Sistema de exportación: Exportación de datos cruzados
- `PivotTableWidget`: Consistencia en UI de configuración

## Formatos de Datos

### JoinConfig
Configuración completa para una operación de join.

```python
@dataclass
class JoinConfig:
    """Configuración para operación de join"""
    left_keys: List[str]  # Columnas del dataset izquierdo
    right_keys: List[str]  # Columnas del dataset derecho
    join_type: JoinType   # INNER, LEFT, RIGHT, CROSS
    suffixes: Tuple[str, str] = ('_left', '_right')  # Sufijos para columnas duplicadas
    validate_integrity: bool = True  # Validar integridad referencial
    sort_results: bool = True  # Ordenar resultados
    indicator: bool = False  # Añadir columna _merge
    how: str = 'left'  # Método de join (pandas)
```

### JoinResult
Resultado de una operación de join.

```python
@dataclass
class JoinResult:
    """Resultado de operación de join"""
    data: pd.DataFrame  # Datos resultantes
    metadata: JoinMetadata  # Metadatos del cruce
    success: bool = True
    error_message: str = ""
    processing_time: float = 0.0
```

### JoinMetadata
Metadatos descriptivos del cruce.

```python
@dataclass
class JoinMetadata:
    """Metadatos del cruce realizado"""
    left_rows: int  # Filas en dataset izquierdo
    right_rows: int  # Filas en dataset derecho
    result_rows: int  # Filas en resultado
    join_type: JoinType
    join_keys: List[str]
    matched_rows: int  # Filas con coincidencias
    left_only_rows: int  # Filas solo en izquierdo
    right_only_rows: int  # Filas solo en derecho
    memory_usage_mb: float
    processing_time_seconds: float
    timestamp: datetime
```

## Sistema de Validación

### ValidationResult
Resultado de validación de configuración.

```python
@dataclass
class ValidationResult:
    """Resultado de validación"""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
```

### Reglas de Validación

#### Validación de Columnas
- Columnas de join existen en ambos datasets
- Tipos de datos compatibles para join
- No hay columnas duplicadas sin sufijos apropiados

#### Validación de Memoria
- Estimación de memoria requerida para el join
- Verificación de límites de memoria del sistema
- Recomendaciones de chunking para datasets grandes

#### Validación de Rendimiento
- Estimación de tiempo de procesamiento
- Recomendaciones de optimización
- Alertas para joins potencialmente costosos

## Interfaces y Comunicación

### Señales y Slots

#### JoinDialog → MainWindow
- `join_configured(config: JoinConfig)`: Configuración completada
- `join_cancelled()`: Operación cancelada

#### MainWindow → JoinedDataView
- `set_join_result(result: JoinResult)`: Establecer datos cruzados

#### DataJoinManager → JoinDialog
- `validation_result(result: ValidationResult)`: Resultado de validación
- `preview_available(data: pd.DataFrame)`: Preview disponible

### Flujo de Datos

1. **Configuración**: JoinDialog → JoinConfig
2. **Validación**: JoinConfig → DataJoinManager → ValidationResult
3. **Ejecución**: JoinConfig → DataJoinManager → JoinResult
4. **Visualización**: JoinResult → JoinedDataView
5. **Historial**: JoinConfig + JoinResult → JoinHistory

## Optimizaciones de Rendimiento

### Chunking para Datasets Grandes
- Procesamiento por bloques para joins grandes
- Gestión automática de memoria
- Progreso en tiempo real

### Optimizaciones de Pandas
- Uso de `merge` con parámetros optimizados
- Indexación automática en columnas de join
- Liberación de memoria intermedia

### Paralelización
- Procesamiento paralelo para múltiples grupos
- Optimización para joins cross (producto cartesiano)

## Manejo de Errores

### Excepciones Personalizadas
- `JoinValidationError`: Error en validación de configuración
- `JoinExecutionError`: Error durante ejecución del join
- `MemoryLimitExceededError`: Límite de memoria excedido
- `UnsupportedJoinError`: Tipo de join no soportado

### Estrategias de Recuperación
- Fallback a joins más simples
- Chunking automático
- Cancelación graceful con cleanup

## Seguridad y Robustez

### Validación de Entrada
- Sanitización de nombres de columnas
- Validación de tipos de datos
- Límites en tamaños de datasets

### Manejo de Memoria
- Monitoreo continuo de uso de memoria
- Liberación automática de recursos
- Límites configurables

### Logging y Debugging
- Logs detallados de operaciones
- Información de rendimiento
- Tracing de errores

## Próximos Pasos

1. Implementar DataJoinManager con operaciones básicas
2. Crear JoinDialog con UI de configuración
3. Integrar JoinedDataView con DataView existente
4. Implementar sistema de validación
5. Añadir optimizaciones de rendimiento
6. Testing exhaustivo con diferentes tipos de datos