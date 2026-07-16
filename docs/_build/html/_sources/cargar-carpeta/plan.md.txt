# Plan de Implementación: Carga de Carpeta con Múltiples Archivos Excel

## Resumen Ejecutivo

Se implementará una nueva funcionalidad que permita cargar una carpeta completa con múltiples archivos Excel y consolidarlos en un único dataset. La funcionalidad se integrará en las opciones de carga existentes y en el menú principal de la aplicación.

## Requerimientos Funcionales

### Funcionalidades Principales
- **Selección de carpeta**: Permitir al usuario seleccionar una carpeta que contenga archivos Excel
- **Escaneo automático**: Identificar automáticamente todos los archivos Excel (.xlsx, .xls) en la carpeta seleccionada
- **Selección de archivos**: Mostrar lista de archivos encontrados con opción para ignorar archivos específicos por nombre
- **Alineación de columnas**: Las columnas se alinearán por posición (orden) en lugar de por nombre
- **Alineación manual**: Permitir arrastrar y soltar columnas para alinearlas manualmente entre archivos
- **Vista previa**: Mostrar tabla de alineación de columnas antes de la consolidación
- **Renombrado de columnas**: Permitir cambiar los nombres de las columnas consolidadas
- **Selección de columnas**: Permitir al usuario seleccionar qué columnas incluir en el consolidado final
- **Consolidación**: Unir todos los datos en un único DataFrame de Pandas

### Manejo de Diferencias entre Archivos
- **Columnas desiguales**: Cuando archivos tienen diferente número de columnas, el usuario podrá elegir:
  - Ignorar columnas adicionales
  - Crear columnas vacías para archivos con menos columnas
  - Decidir caso por caso
- **Nombres de columnas**: Los nombres originales se preservarán pero podrán ser renombrados globalmente

## Arquitectura Propuesta

### Componentes del Sistema

#### 1. Core Components
- **`FolderLoader`**: Clase principal para manejar la carga de carpetas
  - Ubicación: `core/loaders/folder_loader.py`
  - Responsabilidades:
    - Escanear carpeta en busca de archivos Excel
    - Validar archivos soportados
    - Cargar metadata de cada archivo (columnas, filas, etc.)

- **`ExcelConsolidator`**: Clase para consolidar múltiples DataFrames
  - Ubicación: `core/consolidation/excel_consolidator.py`
  - Responsabilidades:
    - Alinear columnas por posición
    - Manejar diferencias en estructura
    - Aplicar selección de columnas
    - Aplicar renombrado de columnas
    - Consolidar datos en único DataFrame

#### 2. UI Components
- **`FolderLoadDialog`**: Diálogo principal para configuración de carga de carpeta
  - Ubicación: `app/widgets/folder_load_dialog.py`
  - Elementos:
    - Selector de carpeta
    - Lista de archivos con checkboxes para selección
    - Vista previa de alineación de columnas
    - Opciones de selección de columnas
    - Opciones de renombrado de columnas
    - Configuración de manejo de diferencias

- **`ColumnAlignmentPreview`**: Widget para mostrar vista previa de alineación
  - Ubicación: `app/widgets/column_alignment_preview.py`
  - Funcionalidad:
    - Tabla que muestra columnas de cada archivo alineadas por posición
    - Funcionalidad de arrastrar y soltar para realinear columnas manualmente
    - Checkboxes para incluir/excluir columnas del consolidado
    - Indicadores visuales para diferencias y alineaciones automáticas
    - Opciones de renombrado inline
    - Botones para auto-alinear por posición o nombre

#### 3. Modelos de Datos
- **`FolderLoadConfig`**: Configuración para carga de carpeta
  - Ubicación: `core/models/folder_load_config.py`
  - Propiedades:
    - Ruta de carpeta
    - Lista de archivos a incluir/excluir
    - Lista de columnas a incluir/excluir
    - Estrategia de alineación de columnas
    - Mapeo de renombrado de columnas

- **`FileMetadata`**: Metadata de cada archivo Excel
  - Ubicación: `core/models/file_metadata.py`
  - Propiedades:
    - Nombre de archivo
    - Número de filas/columnas
    - Nombres de columnas
    - Tamaño del archivo

## Flujo de Usuario

### Paso 1: Selección de Carpeta
1. Usuario hace clic en "Cargar Carpeta" en la vista principal
2. Se abre diálogo de selección de carpeta
3. Sistema escanea automáticamente archivos Excel en la carpeta

### Paso 2: Configuración de Archivos
1. Se muestra lista de archivos encontrados
2. Usuario puede desmarcar archivos que desea ignorar
3. Sistema carga metadata de cada archivo seleccionado

### Paso 3: Vista Previa de Alineación
1. Se muestra tabla con columnas alineadas automáticamente por posición
2. Cada columna muestra los nombres de las columnas correspondientes de cada archivo
3. Usuario puede arrastrar y soltar columnas para realinearlas manualmente
4. Botones disponibles para auto-alinear por posición o intentar por nombre
5. Usuario puede identificar y resolver conflictos o diferencias

### Paso 4: Configuración de Columnas
1. Usuario puede seleccionar qué columnas incluir/excluir del consolidado
2. Usuario puede renombrar las columnas consolidadas
3. Se configuran opciones para manejar diferencias entre archivos
4. Se valida la configuración

### Paso 5: Consolidación
1. Sistema procesa todos los archivos según configuración
2. Se muestra progreso de carga
3. Datos consolidados se cargan en la aplicación principal

## Consideraciones Técnicas

### Rendimiento
- **Carga diferida**: Los archivos se cargarán completamente solo cuando sea necesario
- **Procesamiento por lotes**: Para carpetas grandes, procesar archivos en lotes
- **Validación previa**: Verificar compatibilidad antes de procesar completamente

### Manejo de Errores
- **Archivos corruptos**: Saltar archivos que no se puedan leer
- **Estructuras incompatibles**: Alertar sobre diferencias críticas
- **Límites de memoria**: Implementar chunking para datasets grandes

### Compatibilidad
- **Formatos soportados**: .xlsx y .xls inicialmente
- **Extensiones futuras**: Posibilidad de extender a otros formatos
- **Versiones de Excel**: Compatibilidad con diferentes versiones

## Plan de Implementación

### Fase 1: Arquitectura Base (Semanas 1-2)
- [ ] Crear clases base `FolderLoader` y `ExcelConsolidator`
- [ ] Implementar modelos de datos `FolderLoadConfig` y `FileMetadata`
- [ ] Crear estructura básica del diálogo `FolderLoadDialog`

### Fase 2: Funcionalidad Core (Semanas 3-4)
- [ ] Implementar escaneo de carpeta y detección de archivos
- [ ] Desarrollar lógica de alineación de columnas por posición
- [ ] Crear sistema de consolidación de DataFrames

### Fase 3: Interfaz de Usuario (Semanas 5-6)
- [ ] Desarrollar `ColumnAlignmentPreview` widget con drag-and-drop
- [ ] Implementar lista de archivos con selección
- [ ] Crear opciones de selección de columnas
- [ ] Crear opciones de renombrado de columnas
- [ ] Implementar lógica de arrastrar y soltar para realineación manual

### Fase 4: Integración y Testing (Semanas 7-8)
- [ ] Integrar con sistema existente de carga
- [ ] Crear tests unitarios y de integración
- [ ] Probar casos edge y manejo de errores

### Fase 5: Documentación y Optimización (Semana 9)
- [ ] Actualizar documentación de usuario
- [ ] Optimizar rendimiento para casos de uso comunes
- [ ] Crear ejemplos de uso

## Riesgos y Mitigaciones

### Riesgos Técnicos
- **Diferencias en estructura de archivos**: Mitigación - Vista previa detallada y opciones flexibles
- **Rendimiento con carpetas grandes**: Mitigación - Procesamiento por lotes y carga diferida
- **Compatibilidad con versiones de Excel**: Mitigación - Usar librerías robustas como openpyxl

### Riesgos de Usuario
- **Complejidad de configuración**: Mitigación - Interfaz intuitiva con vista previa
- **Errores de alineación**: Mitigación - Validación automática y advertencias claras

## Métricas de Éxito

- **Funcionalidad**: Capacidad de consolidar correctamente archivos con diferentes estructuras
- **Usabilidad**: Tiempo promedio para configurar una carga de carpeta < 5 minutos
- **Rendimiento**: Procesar carpeta con 50 archivos en < 30 segundos
- **Confiabilidad**: Tasa de éxito > 95% en archivos Excel válidos

## Próximos Pasos

1. Revisar y aprobar este plan
2. Comenzar implementación de la Fase 1
3. Crear prototipos de UI para validar la experiencia de usuario
4. Definir casos de prueba específicos

---

**Fecha de creación**: Noviembre 2025
**Versión del plan**: 1.0
**Estado**: Pendiente de aprobación