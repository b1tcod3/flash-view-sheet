# Módulo de Paginación para Vista de Datos

Este directorio contiene los componentes necesarios para implementar paginación en la vista de datos de Flash View Sheet.

## Arquitectura

### Componentes principales:

1. **DataView** (`data_view.py`): Widget principal que contiene la tabla paginada, controles de paginación y filtros integrados
2. **PaginationManager** (`pagination_manager.py`): Clase que maneja la lógica de paginación
3. **__init__.py**: Inicialización del módulo

### Características:

- Tabla paginada con controles de navegación
- Filtros integrados (columna, término de búsqueda, aplicar/limpiar)
- Paginación personalizable (filas por página)
- Integración con el modelo virtualizado de pandas
- Señales para comunicación con la ventana principal

## Uso

El widget DataView se integra en la aplicación principal reemplazando la vista de tabla simple y hereda sus funcionalidades de filtrado.