# Funcionalidad de Cruce de Datos (Join)

## Resumen

La funcionalidad de cruce de datos permite combinar dos datasets mediante operaciones de join (inner, left, right, cross) directamente desde la interfaz de Flash View Sheet.

## Características

### Tipos de Join Soportados

- **Inner Join**: Solo filas con coincidencias en ambas tablas
- **Left Join**: Todas las filas del dataset izquierdo + coincidencias del derecho
- **Right Join**: Todas las filas del dataset derecho + coincidencias del izquierdo
- **Cross Join**: Producto cartesiano de ambas tablas

### Funcionalidades

- Configuración intuitiva mediante diálogo modal
- Preview de resultados antes de ejecutar
- Validación en tiempo real
- Gestión automática de memoria
- Historial de operaciones
- Exportación de resultados
- Metadatos detallados del cruce

## Uso

### Acceso a la Funcionalidad

1. Cargar un dataset principal en Flash View Sheet
2. Ir al menú **Datos > Cruzar Datos...**
3. Seleccionar el dataset derecho para el cruce
4. Configurar el tipo de join y columnas
5. Ejecutar el cruce

### Configuración del Join

- **Tipo de Join**: Seleccionar entre inner, left, right o cross
- **Columnas de Join**: Especificar las columnas que sirven como clave
- **Sufijos**: Personalizar sufijos para columnas duplicadas
- **Opciones Avanzadas**:
  - Validación de integridad referencial
  - Columna indicador (_merge)
  - Ordenamiento de resultados

## Arquitectura

### Componentes Principales

- `DataJoinManager`: Motor de procesamiento de joins
- `JoinDialog`: Interfaz de configuración
- `JoinedDataView`: Vista especializada para resultados
- `JoinHistory`: Sistema de historial

### Modelos de Datos

- `JoinConfig`: Configuración de la operación
- `JoinResult`: Resultado con metadatos
- `ValidationResult`: Resultado de validaciones

## API

### DataJoinManager

```python
manager = DataJoinManager(left_df, right_df)
result = manager.execute_join(config)
preview = manager.get_join_preview(config, max_rows=100)
validation = manager.validate_join(config)
```

### JoinHistory

```python
history = JoinHistory()
history.add_entry(left_name, right_name, config, result)
entries = history.get_entries(limit=20)
history.export_history(filepath)
```

## Limitaciones

- Solo soporta cruce entre 2 datasets
- Columnas de join deben tener tipos de datos compatibles
- Cross joins pueden generar datasets muy grandes
- Requiere pandas >= 2.0.0

## Testing

Los tests se ejecutan con:

```bash
python -m pytest tests/test_join.py -v
```

## Próximos Pasos

- Soporte para joins múltiples (> 2 datasets)
- Joins complejos con condiciones
- Optimizaciones para datasets muy grandes
- Interfaz de configuración avanzada