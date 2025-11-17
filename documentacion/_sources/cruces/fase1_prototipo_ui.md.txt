# Prototipo de UI: Funcionalidad de Cruce de Datos

## Resumen Ejecutivo

Este documento presenta el diseño de interfaz de usuario para la funcionalidad de cruce de datos, incluyendo mockups detallados, diagramas de flujo y plan de integración con el sistema existente.

## Diálogo de Configuración de Join (JoinDialog)

### Mockup Principal

```
┌─────────────────────────────────────────────────────────────┐
│                Configurar Cruce de Datos                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Dataset Izquierdo: [ventas_2023.xlsx] 📄 [Cambiar...]      │
│  (1,250 filas × 8 columnas)                                 │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Cargar Dataset Derecho                                │    │
│  │                                                     │    │
│  │ [📁 Seleccionar archivo...]                         │    │
│  │                                                     │    │
│  │ Formatos soportados: CSV, Excel, JSON, etc.        │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  Dataset Derecho: [clientes.xlsx] 📄 [Cambiar...]           │
│  (850 filas × 5 columnas)                                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Configuración del Join                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Tipo de Join: [Inner Join ▼]                               │
│     ○ Inner Join - Solo coincidencias                       │
│     ○ Left Join  - Todo izquierdo + coincidencias           │
│     ○ Right Join - Todo derecho + coincidencias             │
│     ○ Cross Join - Producto cartesiano                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Columnas para Join                                   │    │
│  │                                                     │    │
│  │ Izquierdo: [cliente_id ▼]                           │    │
│  │ Derecho:  [id ▼]                                     │    │
│  │                                                     │    │
│  │ [+ Añadir columna]                                   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  Opciones Avanzadas ▼                                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Sufijos para columnas duplicadas:                    │    │
│  │ Izquierdo: [_left]  Derecho: [_right]               │    │
│  │                                                     │    │
│  │ □ Validar integridad referencial                    │    │
│  │ □ Añadir columna indicador (_merge)                 │    │
│  │ □ Ordenar resultados                                │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Preview de Resultados                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Estimación: 980 filas × 12 columnas                │    │
│  │ Tiempo estimado: ~2.3 segundos                       │    │
│  │ Memoria requerida: ~45 MB                            │    │
│  │                                                     │    │
│  │ [🔄 Actualizar Preview]                              │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Preview (primeras 10 filas):                       │    │
│  │ ┌─────────┬────────────┬─────────┬─────────┐       │    │
│  │ │cliente_id│nombre     │producto│cantidad│       │    │
│  │ ├─────────┼────────────┼─────────┼─────────┤       │    │
│  │ │CLI001   │Juan Pérez │Laptop  │2       │       │    │
│  │ │CLI002   │María García│Mouse   │1       │       │    │
│  │ │...      │...        │...     │...     │       │    │
│  │ └─────────┴────────────┴─────────┴─────────┘       │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│            [⚠️ Validar]    [🚀 Ejecutar Join]    [❌ Cancelar] │
└─────────────────────────────────────────────────────────────┘
```

### Estados del Diálogo

#### Estado Inicial
- Solo dataset izquierdo disponible (datos principales)
- Botón "Cargar Dataset Derecho" prominente
- Opciones de join deshabilitadas

#### Estado con Datasets Cargados
- Ambos datasets mostrados con información básica
- Configuración de join habilitada
- Preview disponible

#### Estado con Errores de Validación
- Iconos de advertencia en campos problemáticos
- Mensajes de error descriptivos
- Sugerencias de corrección

## Vista de Datos Cruzados (JoinedDataView)

### Mockup de Vista Principal

```
┌─────────────────────────────────────────────────────────────┐
│ Flash View Sheet - Datos Cruzados                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 📊 Metadatos del Cruce                                      │
│ ┌─────────────────────────────────────────────────────┐    │
│ │ Tipo: Inner Join                                       │    │
│ │ Datasets: ventas_2023.xlsx + clientes.xlsx           │    │
│ │ Columnas join: cliente_id = id                        │    │
│ │ Resultado: 980 filas × 12 columnas                   │    │
│ │ Tiempo procesamiento: 2.1 segundos                    │    │
│ │ Memoria usada: 42 MB                                  │    │
│ │                                                         │    │
│ │ Estadísticas:                                           │    │
│ │ • Coincidencias: 980/1,250 (78.4%)                    │    │
│ │ • Pérdidas izquierdo: 270/1,250 (21.6%)              │    │
│ │ • Pérdidas derecho: 0/850 (0%)                        │    │
│ └─────────────────────────────────────────────────────┘    │
│                                                             │
│ ┌─────────────────────────────────────────────────────┐    │
│ │ Filtros                                                │    │
│ │ Columna: [cliente_id ▼]  Buscar: [     ] [Aplicar]   │    │
│ │ [Limpiar Filtro]                                       │    │
│ └─────────────────────────────────────────────────────┘    │
│                                                             │
│ ┌─────────────────────────────────────────────────────┐    │
│ │ Datos Cruzados                                        │    │
│ │ ┌─────────┬────────────┬─────────┬─────────┬─────┐   │    │
│ │ │cliente_id│nombre     │producto│cantidad│origen│  │    │
│ │ ├─────────┼────────────┼─────────┼─────────┼─────┤   │    │
│ │ │CLI001   │Juan Pérez │Laptop  │2       │ambos │  │    │
│ │ │CLI002   │María García│Mouse   │1       │ambos │  │    │
│ │ │CLI003   │Carlos Ruiz│Teclado │3       │izq  │  │    │
│ │ │...      │...        │...     │...     │...  │  │    │
│ │ └─────────┴────────────┴─────────┴─────────┴─────┘   │    │
│ │ Página 1 de 98 (1-10 de 980 filas)                   │    │
│ │ [⏮️] [◀️] [▶️] [⏭️]  Filas por página: [10 ▼]         │    │
│ └─────────────────────────────────────────────────────┘    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ [💾 Exportar...] [🔄 Nuevo Cruce] [📋 Historial] [❓ Ayuda]  │
└─────────────────────────────────────────────────────────────┘
```

### Indicadores Visuales

#### Columna de Origen
- **ambos**: Fila con datos de ambos datasets
- **izq**: Fila solo del dataset izquierdo
- **der**: Fila solo del dataset derecho

#### Resaltado de Columnas
- Columnas de join en negrita
- Columnas con sufijos coloreadas
- Tooltips con información de origen

## Integración con UI Existente

### Modificaciones al Menú Principal

```
Archivo    Editar    Ver    Datos    Ayuda
                        │
                        ├── Cruzar Datos...
                        ├── Separar Datos...
                        └── Tabla Pivote
                            ├── Simple...
                            └── Combinada...
```

### Nuevo Menú "Datos"
- **Cruzar Datos...**: Abre JoinDialog
- **Separar Datos...**: Funcionalidad existente
- **Tabla Pivote**: Funcionalidad existente

### Toolbar Actualizada

```
Vista Principal | Vista de Datos | Vista Información | Vista Gráficos | Cruzar Datos
```

## Diagramas de Flujo

### Flujo de Configuración de Join

```mermaid
graph TD
    A[Usuario selecciona 'Cruzar Datos'] --> B[JoinDialog se abre]
    B --> C[Dataset izquierdo precargado]
    C --> D[Usuario carga dataset derecho]
    D --> E[Validación automática de compatibilidad]
    E --> F[Usuario configura tipo de join]
    F --> G[Usuario selecciona columnas de join]
    G --> H[Preview automático de resultados]
    H --> I[Usuario ajusta opciones avanzadas]
    I --> J[Validación final]
    J --> K[Usuario ejecuta join]
    K --> L[JoinedDataView muestra resultados]
```

### Flujo de Navegación

```mermaid
graph TD
    A[MainWindow] --> B{¿Datos cargados?}
    B -->|No| C[Mostrar MainView]
    B -->|Sí| D[Mostrar DataView]
    D --> E[Usuario selecciona 'Cruzar Datos']
    E --> F[JoinDialog modal]
    F --> G{¿Join exitoso?}
    G -->|Sí| H[JoinedDataView]
    G -->|No| I[Mostrar error]
    H --> J[Usuario puede exportar/filtrar]
    J --> K[Volver a DataView normal]
```

## Validaciones y Feedback

### Validaciones en Tiempo Real

#### Durante Carga de Dataset
- ✅ Archivo válido
- ✅ Formato soportado
- ⚠️ Archivo muy grande (advertencia)
- ❌ Archivo corrupto

#### Durante Configuración
- ✅ Columnas de join compatibles
- ✅ Tipos de datos matching
- ⚠️ Columnas duplicadas detectadas
- ❌ Columnas de join no existen

#### Durante Preview
- ✅ Estimación de resultados calculada
- ✅ Memoria suficiente disponible
- ⚠️ Tiempo de procesamiento largo
- ❌ Join causaría out of memory

### Mensajes de Error

#### Errores Críticos
```
❌ Error: Las columnas de join tienen tipos incompatibles
   cliente_id (str) ≠ id (int)

   Sugerencia: Convertir tipos o elegir columnas diferentes
```

#### Advertencias
```
⚠️ Advertencia: Se detectaron 5 columnas duplicadas
   Se aplicarán sufijos automáticamente: _left, _right

   Columnas afectadas: nombre, email, telefono
```

## Optimizaciones de UX

### Progressive Disclosure
- Opciones básicas visibles por defecto
- Opciones avanzadas colapsadas inicialmente
- Preview se actualiza automáticamente

### Context-Aware Defaults
- Sufijos inteligentes basados en nombres de archivos
- Tipo de join recomendado basado en análisis de datos
- Columnas de join sugeridas por matching de nombres

### Performance Indicators
- Barra de progreso durante carga y procesamiento
- Estimaciones de tiempo y memoria
- Cancelación disponible en operaciones largas

## Accesibilidad

### Navegación por Teclado
- Tab order lógico a través de todos los controles
- Shortcuts para acciones comunes (Ctrl+O para cargar)
- Enter para ejecutar join

### Soporte para Lectores de Pantalla
- Labels descriptivos en todos los controles
- Información de estado anunciada
- Tablas con headers apropiados

## Próximos Pasos

1. Implementar JoinDialog con validación básica
2. Crear JoinedDataView heredando de DataView
3. Integrar con MainWindow y menú principal
4. Añadir indicadores visuales y metadatos
5. Implementar sistema de preview
6. Testing de UX con usuarios reales
7. Optimizaciones de performance y accesibilidad