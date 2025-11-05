# Documentación de Transformaciones - Fase 7.3
# Codificación Categórica y Agregaciones Avanzadas

## Resumen

Este documento detalla las transformaciones de datos implementadas en la Fase 7.3 del proyecto flash-view-sheet, que incluyen operaciones de codificación categórica y agregaciones avanzadas. Estas transformaciones se integran con el sistema de transformaciones existente, siguiendo los mismos patrones de diseño y arquitectura.

## Contenido

### 1. Codificación Categórica

#### 1.1 Label Encoding Transformation

La transformación `LabelEncodingTransformation` convierte valores categóricos en etiquetas numéricas. Es útil cuando se tienen variables categóricas ordinales (con un orden natural) o para preparar datos para algoritmos de machine learning que requieren entrada numérica.

**Uso básico:**

```python
from core.transformations.encoding import create_label_encoding

# Crear transformación para la columna 'categoria'
transformation = create_label_encoding(['categoria'])

# Aplicar al DataFrame
df_encoded = transformation.execute(df)
```

**Parámetros:**

- `columns`: Lista de columnas a codificar
- `handle_unknown`: Cómo manejar valores desconocidos ('error', 'use_encoded_value', 'ignore')
- `handle_missing`: Cómo manejar valores faltantes ('error', 'use_encoded_value', 'ignore')

**Decodificación:**

```python
# Decodificar valores a sus valores originales
df_decoded = transformation.decode_values(df_encoded, 'categoria')
```

#### 1.2 One-Hot Encoding Transformation

La transformación `OneHotEncodingTransformation` convierte variables categóricas en variables dummy (binarias), creando una columna para cada categoría única. Es útil para variables categóricas nominales (sin orden natural) y para algoritmos de machine learning que tratan las características de forma independiente.

**Uso básico:**

```python
from core.transformations.encoding import create_one_hot_encoding

# Crear transformación para las columnas 'color' y 'tamaño'
transformation = create_one_hot_encoding(['color', 'tamaño'])

# Aplicar al DataFrame
df_encoded = transformation.execute(df)
```

**Parámetros:**

- `columns`: Lista de columnas a codificar
- `drop_first`: Si descartar la primera categoría (evita multicolinealidad)
- `prefix`: Prefijo para nombres de nuevas columnas (por defecto usa nombre de columna)
- `prefix_sep`: Separador entre prefijo y nombre de categoría
- `handle_unknown`: Cómo manejar valores desconocidos ('error', 'ignore')
- `handle_missing`: Cómo manejar valores faltantes ('error', 'ignore')

#### 1.3 Ordinal Encoding Transformation

La transformación `OrdinalEncodingTransformation` convierte valores categóricos en números ordinales según un orden predefinido. Es útil para variables categóricas con un orden natural o cuando se quiere mantener una relación ordinal entre las categorías.

**Uso básico:**

```python
from core.transformations.encoding import create_ordinal_encoding

# Crear mapeo para el orden
encoding_map = {
    'talla': [('S', 1), ('M', 2), ('L', 3), ('XL', 4)]
}

# Crear transformación
transformation = create_ordinal_encoding(['talla'], encoding_map)

# Aplicar al DataFrame
df_encoded = transformation.execute(df)
```

**Parámetros:**

- `columns`: Lista de columnas a codificar
- `encoding_map`: Diccionario con mapeos de valores a códigos
- `handle_unknown`: Cómo manejar valores desconocidos ('error', 'use_encoded_value', 'ignore')
- `handle_missing`: Cómo manejar valores faltantes ('error', 'use_encoded_value', 'ignore')

**Decodificación:**

```python
# Decodificar valores a sus valores originales
df_decoded = transformation.decode_values(df_encoded, 'talla')
```

#### 1.4 Target Encoding Transformation

La transformación `TargetEncodingTransformation` codifica valores categóricos usando la media de la variable objetivo para cada categoría. Es útil para reducir la dimensionalidad de variables categóricas con muchas categorías, pero debe usarse con precaución para evitar overfitting.

**Uso básico:**

```python
from core.transformations.encoding import create_target_encoding

# Crear transformación para 'ciudad' usando 'precio' como target
transformation = create_target_encoding(['ciudad'], 'precio', smoothing=10.0, noise=0.01)

# Aplicar al DataFrame
df_encoded = transformation.execute(df)
```

**Parámetros:**

- `columns`: Lista de columnas a codificar
- `target_column`: Nombre de la columna objetivo (variable a predecir)
- `smoothing`: Parámetro de suavizado para reducir overfitting
- `noise`: Ruido a añadir a la codificación para reducir overfitting
- `cv`: Número de pliegues para validación cruzada en el target encoding

### 2. Agregaciones Avanzadas

#### 2.1 Multi-Function Aggregation Transformation

La transformación `MultiFunctionAggregationTransformation` aplica múltiples funciones de agregación a diferentes columnas. Es útil para obtener un resumen estadístico completo de los datos agrupados.

**Uso básico:**

```python
from core.transformations.advanced_aggregations import create_multi_function_aggregation

# Crear funciones de agregación para columnas
aggregation_functions = {
    'ventas': ['sum', 'mean', 'std'],
    'unidades_vendidas': ['sum', 'max'],
    'descuento': ['mean', 'min']
}

# Crear transformación
transformation = create_multi_function_aggregation(['region', 'producto'], aggregation_functions)

# Aplicar al DataFrame
df_agg = transformation.execute(df)
```

**Parámetros:**

- `groupby_columns`: Lista de columnas para agrupar
- `aggregation_functions`: Diccionario con columnas y funciones a aplicar

#### 2.2 Advanced Pivoting Transformation

La transformación `AdvancedPivotingTransformation` crea tablas pivote con múltiples índices/columnas. Es útil para analizar datos multidimensionales y crear tablas de resumen interactivas.

**Uso básico:**

```python
from core.transformations.advanced_aggregations import create_advanced_pivoting

# Crear transformación de pivote
transformation = create_advanced_pivoting(
    index='region',
    columns=['producto', 'trimestre'],
    values='ventas',
    aggfunc='sum'
)

# Aplicar al DataFrame
df_pivot = transformation.execute(df)
```

**Parámetros:**

- `index`: Columna o lista de columnas para el índice
- `columns`: Columna o lista de columnas para las columnas del pivote
- `values`: Columna o lista de columnas para los valores
- `aggfunc`: Función o lista de funciones de agregación
- `fill_value`: Valor para rellenar celdas vacías
- `dropna`: Si eliminar filas con todos los valores NaN
- `margins`: Si calcular totales
- `margins_name`: Nombre para la fila/columna de totales

#### 2.3 Rolling Window Transformation

La transformación `RollingWindowTransformation` aplica funciones de agregación en ventanas deslizantes. Es útil para analizar tendencias temporales y patrones a corto plazo.

**Uso básico:**

```python
from core.transformations.advanced_aggregations import create_rolling_window

# Crear transformación de ventana deslizante
transformation = create_rolling_window(
    columns=['ventas'],
    window_size=7,  # Ventana de 7 períodos
    aggregation_function='mean'
)

# Aplicar al DataFrame
df_rolling = transformation.execute(df)
```

**Parámetros:**

- `columns`: Lista de columnas a aplicar la ventana
- `window_size`: Tamaño de la ventana
- `aggregation_function`: Función de agregación ('mean', 'sum', 'std', etc.)
- `min_periods`: Número mínimo de valores en la ventana
- `center`: Si centrar la ventana
- `closed`: Cómo definir los límites de la ventana

#### 2.4 Expanding Window Transformation

La transformación `ExpandingWindowTransformation` aplica funciones de agregación en ventanas expansivas (que crecen con el tiempo). Es útil para analizar tendencias a largo plazo y métricas acumulativas.

**Uso básico:**

```python
from core.transformations.advanced_aggregations import create_expanding_window

# Crear transformación de ventana expansiva
transformation = create_expanding_window(
    columns=['ventas'],
    min_periods=1,
    aggregation_function='mean'
)

# Aplicar al DataFrame
df_expanding = transformation.execute(df)
```

**Parámetros:**

- `columns`: Lista de columnas a aplicar la ventana
- `min_periods`: Número mínimo de valores en la ventana
- `center`: Si centrar la ventana
- `aggregation_function`: Función de agregación ('mean', 'sum', 'std', etc.)

#### 2.5 GroupBy Transformation

La transformación `GroupByTransformationTransformation` realiza transformaciones por grupos de datos. Es útil para calcular métricas que requieren considerar la estructura de los datos agrupados.

**Uso básico:**

```python
from core.transformations.advanced_aggregations import create_groupby_transformation

# Crear transformación de groupby
transformation = create_groupby_transformation(
    groupby_columns=['region'],
    transformation_function='rank',
    transformation_columns=['ventas']
)

# Aplicar al DataFrame
df_grouped = transformation.execute(df)
```

**Parámetros:**

- `groupby_columns`: Lista de columnas para agrupar
- `transformation_function`: Función de transformación ('rank', 'diff', 'shift', 'cumsum', 'cumprod', 'cummax', 'cummin')
- `transformation_columns`: Lista de columnas a transformar
- `new_column_suffix`: Sufijo para nombres de nuevas columnas

## Uso con el TransformationManager

Todas estas transformaciones están registradas en el `TransformationManager` y pueden utilizarse a través de su API:

```python
from core.transformations import get_transformation_manager

# Obtener el gestor de transformaciones
manager = get_transformation_manager()

# Listar transformaciones disponibles
print(manager.get_available_transformations())

# Aplicar una transformación
df_result = manager.execute_transformation(
    df_original, 
    'label_encoding', 
    {'columns': ['categoria']}
)

# Aplicar un pipeline de transformaciones
pipeline_steps = [
    {'transformation': 'label_encoding', 'parameters': {'columns': ['categoria']}},
    {'transformation': 'multi_function_aggregation', 'parameters': {
        'groupby_columns': ['categoria'], 
        'aggregation_functions': {'valor': ['sum', 'mean']}
    }}
]

df_pipeline_result = manager.execute_pipeline(df_original, pipeline_steps)
```

## Integración con el Sistema Existente

Estas transformaciones se integran completamente con el sistema de transformaciones existente, lo que permite su uso junto con las transformaciones de las fases anteriores:

- Se pueden combinar en pipelines con otras transformaciones
- Soportan deshacer/rehacer a través del `TransformationManager`
- Siguen los mismos patrones de validación y manejo de errores
- Mantienen la compatibilidad con el `data_handler.py` existente

## Casos de Uso Recomendados

### Label Encoding
- Variables categóricas ordinales (pequeño, mediano, grande)
- Preparación de datos para algoritmos que requieren entrada numérica

### One-Hot Encoding
- Variables categóricas nominales con pocas categorías
- Preparación de datos para algoritmos de machine learning

### Ordinal Encoding
- Variables categóricas con orden natural
- Cuando se quiere mantener el orden pero convertir a numérico

### Target Encoding
- Variables categóricas con muchas categorías
- Preparación de datos para modelos predictivos

### Multi-Function Aggregation
- Resumen estadístico completo de datos agrupados
- Creación de características agregadas para análisis

### Advanced Pivoting
- Análisis multidimensional de datos
- Creación de tablas de resumen interactivas

### Rolling Window
- Análisis de tendencias temporales
- Detección de patrones a corto plazo

### Expanding Window
- Análisis de tendencias a largo plazo
- Métricas acumulativas

### GroupBy Transformation
- Cálculo de métricas por grupo
- Normalización por grupo