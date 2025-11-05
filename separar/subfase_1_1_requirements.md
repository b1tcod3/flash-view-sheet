# Subfase 1.1: Definición de Funcionalidades
## Análisis Detallado de Requerimientos para Exportación Separada con Plantillas Excel

### 1. Funcionalidades Core Identificadas

#### 1.1 Selección de Columna de Separación
**Requerimiento**: El usuario debe poder seleccionar una columna específica del DataFrame para realizar la separación de datos.

**Detalles Técnicos**:
- Interface: ComboBox desplegable con lista de todas las columnas del DataFrame
- Validaciones: Solo columnas con datos (no vacías)
- Comportamiento: Al seleccionar, mostrar preview de valores únicos (máximo 10)
- Tipos soportados: Texto, numérico, fecha, booleano
- Manejo de valores nulos: Opción para incluir/excluir en la separación

**Criterios de Aceptación**:
- [x] Lista de columnas obtenida dinámicamente del DataFrame cargado
- [x] Preview de valores únicos (máximo 10 valores diferentes)
- [x] Validación de columna seleccionada no esté vacía
- [x] Soporte para diferentes tipos de datos (texto, numérico, fecha, booleano)

#### 1.2 Personalización de Nombres de Archivos con Plantillas
**Requerimiento**: Permitir al usuario definir nombres de archivos usando plantillas con placeholders dinámicos.

**Placeholders Soportados**:
- `{valor}`: Valor específico de la columna de separación
- `{fecha}`: Fecha actual en formato YYYY-MM-DD
- `{hora}`: Hora actual en formato HHMMSS
- `{contador}`: Número secuencial (01, 02, 03...)
- `{columna_nombre}`: Nombre de la columna de separación
- `{total_filas}`: Número total de filas en el grupo
- `{fecha_archivo}`: Fecha de modificación del archivo original

**Ejemplos de Plantillas**:
- `{valor}_{fecha}.xlsx`
- `Reporte_{columna_nombre}_{valor}_{contador:02d}.xlsx`
- `Datos_{valor}_({total_filas}_filas)_{fecha}.xlsx`

**Validaciones**:
- Longitud máxima: 255 caracteres (límite sistema operativo)
- Caracteres inválidos: \ / : * ? " < > | (automáticamente removidos)
- Extensión requerida: .xlsx (verificado automáticamente)

**Criterios de Aceptación**:
- [x] Campo de texto para plantilla con validación en tiempo real
- [x] Lista de placeholders disponibles visible para el usuario
- [x] Preview de nombres de archivos generados antes de exportar
- [x] Validación de caracteres inválidos en nombres
- [x] Auto-guardado de plantilla en configuración de usuario

#### 1.3 Selección de Carpeta de Destino
**Requerimiento**: Interface para seleccionar directorio donde se guardarán los archivos separados.

**Funcionalidades**:
- Diálogo de selección de carpeta nativo del sistema operativo
- Mostrar ruta completa seleccionada
- Crear carpetas automáticamente si no existen
- Verificar permisos de escritura antes de exportar
- Opción de recordar última carpeta seleccionada

**Criterios de Aceptación**:
- [x] Diálogo estándar de selección de carpeta
- [x] Validación de permisos de escritura
- [x] Auto-creación de carpetas inexistentes
- [x] Recordar última carpeta usada (preferencia de usuario)

#### 1.4 Selección de Plantilla Excel
**Requerimiento**: Sistema para seleccionar archivo Excel que servirá como plantilla.

**Funcionalidades**:
- Diálogo de selección de archivo .xlsx
- Validación de que el archivo sea un Excel válido
- Preservación completa del formato original
- Soporte para múltiples hojas (selección de hoja específica)
- Preview de la plantilla seleccionada

**Validaciones**:
- Extensión .xlsx obligatoria
- Archivo no debe estar abierto en otra aplicación
- Mínimo 1 fila y 1 columna de datos
- Archivo no debe estar corrupto

**Criterios de Aceptación**:
- [x] Selección de archivo .xlsx mediante diálogo
- [x] Validación de integridad del archivo Excel
- [x] Preview de contenido de plantilla (primeras 10 filas)
- [x] Selección de hoja específica si hay múltiples hojas

#### 1.5 Configuración de Celda Inicial
**Requerimiento**: Permitir especificar la celda donde se insertarán los datos en la plantilla.

**Opciones de Configuración**:
- Campo de texto para coordenada (ej: A5, B2, AA10)
- Selector visual: click en celda para seleccionar
- Validación de coordenada válida
- Opciones predefinidas: A1, A2, A5, B1, B2
- Detección automática de primera celda vacía

**Validaciones**:
- Formato Excel válido (letras+números)
- Celda dentro de los límites de la hoja
- Celda no debe contener fórmulas críticas (opcional)
- Coordenada debe existir en la plantilla

**Criterios de Aceptación**:
- [x] Input de texto para coordenada con validación
- [x] Validación en tiempo real de formato de coordenada
- [x] Opciones predefinidas comunes
- [x] Preview visual de dónde se insertarán los datos

#### 1.6 Mapeo de Columnas DataFrame a Columnas Excel
**Requerimiento**: Sistema flexible para mapear columnas del DataFrame a columnas específicas en Excel.

**Tipos de Mapeo**:
1. **Automático**: Mapear por posición (Columna 0 DataFrame → Columna A Excel)
2. **Manual**: Usuario selecciona correspondencias específicas
3. **Por Nombre**: Mapear columnas con nombres similares
4. **Personalizado**: Usuario define todas las correspondencias

**Interface de Mapeo**:
- Tabla con dos columnas: "DataFrame Column" y "Excel Column"
- Dropdowns para selección de columnas Excel (A, B, C, ..., Z, AA, AB...)
- Opción para omitir columnas del DataFrame
- Validación de conflictos (misma columna Excel para múltiples columnas DataFrame)
- Preset de mapeos comunes

**Opciones Avanzadas**:
- Orden de columnas personalizable
- Insertar datos como valores o fórmulas
- Aplicar formato específico a cada columna mapeada
- Manejo de tipos de datos incompatibles

**Criterios de Aceptación**:
- [x] Interface de mapeo con tabla de dos columnas
- [x] Dropdown con todas las columnas Excel disponibles
- [x] Validación de conflictos de mapeo
- [x] Opción de mapeo automático por posición
- [x] Presets de mapeo comunes
- [x] Preview del mapeo antes de aplicar

#### 1.7 Validación de Datos Pre-Separación
**Requerimiento**: Sistema robusto de validación antes de iniciar la separación.

**Validaciones Principales**:
1. **Datos Disponibles**:
   - DataFrame cargado y no vacío
   - Columna de separación existe y tiene datos
   - Mínimo 2 valores únicos en columna de separación

2. **Plantilla Excel**:
   - Archivo accesible y válido
   - Hoja seleccionada existe
   - Celda inicial dentro de límites
   - Permisos de lectura en plantilla

3. **Destino**:
   - Carpeta de destino accesible
   - Permisos de escritura
   - Espacio disponible suficiente (estimado)

4. **Configuración**:
   - Plantilla de nombre de archivo válida
   - Mapeo de columnas sin conflictos
   - No hay duplicados en nombres de archivos generados

**Manejo de Errores**:
- Mostrar errores específicos con sugerencias de solución
- Permitir corrección sin cerrar el diálogo
- Log detallado para debugging
- Opción de continuar con advertencias (modo avanzado)

**Criterios de Aceptación**:
- [x] Validación completa de todos los componentes
- [x] Mensajes de error específicos y accionables
- [x] Sugerencias automáticas para corrección
- [x] Log detallado para troubleshooting
- [x] Modo avanzado para usuarios expertos

#### 1.8 Manejo de Errores y Valores Inválidos
**Requerimiento**: Sistema robusto para manejar valores nulos, inválidos o problemáticos.

**Escenarios a Manejar**:

1. **Valores Nulos en Columna de Separación**:
   - Opción: Excluir filas con nulos
   - Opción: Crear archivo separado para nulos
   - Opción: Reemplazar nulos con valor por defecto
   - Valor por defecto configurable (ej: "N/A", "NULL", "Sin valor")

2. **Valores Duplicados en Columna de Separación**:
   - Comportamiento: Combinar en un solo archivo
   - Confirmación: Preguntar al usuario cómo proceder
   - Prefijo: Agregar identificador único (ej: "_dup1", "_dup2")

3. **Nombres de Archivo Duplicados**:
   - Auto-numeración: Agregar sufijo numérico
   - Sobrescritura: Preguntar confirmación
   - Error: Detener proceso y reportar

4. **Tipos de Datos Incompatibles**:
   - Conversión automática con advertencia
   - Preservar como texto si no es posible convertir
   - Reportar columnas problemáticas

5. **Celdas Ocupadas en Plantilla**:
   - Desplazamiento automático: Mover datos a siguiente celda vacía
   - Sobrescritura: Preguntar confirmación
   - Error: Detener y reportar conflicto

**Configuraciones de Usuario**:
- Modo estricto: Detener ante cualquier error
- Modo permisivo: Continuar con advertencias
- Modo automático: Aplicar heurísticas para resolver conflictos
- Log detallado: Registrar todas las decisiones tomadas

**Criterios de Aceptación**:
- [x] Opciones configurables para manejo de nulos
- [x] Resolución automática de duplicados
- [x] Manejo inteligente de conflictos de nombres
- [x] Conversión automática de tipos con logging
- [x] Múltiples modos de manejo de errores
- [x] Reporte detallado de todas las decisiones

### 2. Funcionalidades de Interfaz de Usuario

#### 2.1 Diálogo Modal de Configuración
**Requerimiento**: Ventana modal centralizada para configurar todos los parámetros.

**Diseño de Layout**:
```
+------------------------------------------------------+
| Configurar Exportación Separada                      |
+------------------------------------------------------+
| 1. Datos                                            |
|    [ComboBox: Seleccionar columna de separación]    |
|    [Preview: Valores únicos: A, B, C, D...]         |
+------------------------------------------------------+
| 2. Plantilla Excel                                  |
|    [Button: Seleccionar plantilla...]               |
|    [Texto: plantilla.xlsx]                          |
|    [ComboBox: Seleccionar hoja]                     |
+------------------------------------------------------+
| 3. Configuración de Inserción                       |
|    [Texto: Celda inicial (A5)]                      |
|    [Tabla: Mapeo de columnas]                       |
+------------------------------------------------------+
| 4. Nombres de Archivos                              |
|    [Texto: Plantilla de nombre]                     |
|    [Preview: archivo_A_2025-11-04.xlsx, ...]        |
+------------------------------------------------------+
| 5. Destino                                          |
|    [Button: Seleccionar carpeta...]                 |
|    [Texto: C:\Datos\Exportacion\]                   |
+------------------------------------------------------+
| [Validar] [Vista Previa] [Cancelar] [Exportar]     |
+------------------------------------------------------+
```

**Características**:
- Tabs o secciones expandibles para mejor organización
- Validación en tiempo real de cada sección
- Botones de ayuda contextual
- Progress indicator durante validaciones

#### 2.2 Preview de Archivos a Generar
**Requerimiento**: Mostrar lista de archivos que se generarán antes de la exportación.

**Contenido del Preview**:
- Nombre del archivo (basado en plantilla)
- Número de filas que contendrá
- Columnas incluidas según mapeo
- Tamaño estimado del archivo
- Estado: Listo, Warning, Error

**Funcionalidades**:
- Scroll para listas largas
- Filtro por estado (Todos, Listos, Warnings, Errores)
- Click para editar configuración específica
- Exportar preview a CSV para revisión

**Criterios de Aceptación**:
- [x] Lista completa de archivos a generar
- [x] Información detallada de cada archivo
- [x] Filtros para facilitar revisión
- [x] Edición rápida de configuraciones problemáticas
- [x] Export de preview para análisis

#### 2.3 Opciones Avanzadas
**Requerimiento**: Panel de opciones avanzadas para usuarios expertos.

**Opciones Incluidas**:
1. **Manejo de Memoria**:
   - Tamaño de chunk para procesamiento
   - Limpiar memoria entre chunks
   - Forzar garbage collection

2. **Optimización de Rendimiento**:
   - Paralelización de exportación
   - Cache de plantillas
   - Compresión de archivos intermedios

3. **Logging y Debugging**:
   - Nivel de logging (DEBUG, INFO, WARNING, ERROR)
   - Archivo de log personalizado
   - Métricas de rendimiento

4. **Configuraciones Especiales**:
   - Encoding específico para archivos
   - Separador decimal personalizado
   - Formato de fecha personalizado
   - Caracteres de escape

**Interface**:
- Expandible/colapsable
- Guardar/cargar perfiles de configuración
- Reset a configuraciones por defecto
- Validación de configuraciones avanzadas

### 3. Criterios de Calidad y Rendimiento

#### 3.1 Rendimiento Esperado
- **Datasets Pequeños** (< 10K filas): < 30 segundos
- **Datasets Medianos** (10K-100K filas): < 3 minutos
- **Datasets Grandes** (100K-1M filas): < 15 minutos
- **Datasets Muy Grandes** (> 1M filas): Procesamiento por chunks, progreso en tiempo real

#### 3.2 Uso de Memoria
- Máximo 2GB RAM durante exportación
- Liberación automática de memoria entre archivos
- Monitoreo de memoria disponible
- Opción de procesar en modo low-memory

#### 3.3 Usabilidad
- Interface intuitiva para usuarios no técnicos
- Tooltips y ayuda contextual
- Validación en tiempo real
- Mensajes de error claros y accionables
- Soporte para temas dark/light

#### 3.4 Compatibilidad
- Python 3.8+
- PySide6 6.0+
- Excel 2016+ (.xlsx)
- Windows 10+, macOS 10.14+, Ubuntu 18.04+
- Múltiples configuraciones regionales

### 4. Casos de Uso Principales

#### 4.1 Caso de Uso 1: Separación Simple por Región
**Contexto**: Empresa con datos de ventas por región
**Datos**: 50,000 registros, columnas: Region, Producto, Ventas, Fecha
**Objetivo**: Un archivo Excel por región usando plantilla con formato corporativo
**Resultado**: 5 archivos Excel (Norte.xlsx, Sur.xlsx, Este.xlsx, Oeste.xlsx, Central.xlsx)

#### 4.2 Caso de Uso 2: Reportes Mensuales por Departamento
**Contexto**: Datos de nómina separados por mes y departamento
**Datos**: 200,000 registros, columnas: Mes, Departamento, Empleado, Salario
**Objetivo**: Un archivo por mes-departamento con plantilla personalizada
**Resultado**: 60 archivos Excel (Enero_RRHH.xlsx, Enero_Ventas.xlsx, ...)

#### 4.3 Caso de Uso 3: Datos Científicos por Experimento
**Contexto**: Resultados de experimentos científicos
**Datos**: 500,000 registros, columnas: Experimento, Fecha, Sensor, Medicion
**Objetivo**: Un archivo por experimento con formato científico específico
**Resultado**: 25 archivos Excel con formato científico preservado

### 5. Métricas de Éxito

#### 5.1 Métricas Técnicas
- Tiempo de exportación < 3x tiempo de exportación normal
- Formato Excel preservado al 100%
- Uso de memoria < 2GB para datasets de 1M filas
- Éxito en > 95% de exportaciones sin intervención manual

#### 5.2 Métricas de Usuario
- Interface usable por usuarios no técnicos en < 5 minutos de entrenamiento
- Tiempo de configuración < 2 minutos para casos simples
- Tasa de error < 5% en configuraciones de usuario
- Satisfacción del usuario > 4/5 en pruebas de usabilidad

#### 5.3 Métricas de Integración
- Sin regresiones en funcionalidades existentes
- Tiempo de startup de aplicación < 5 segundos
- Compatibilidad con todos los formatos de datos existentes
- Cobertura de tests > 90%

### 6. Dependencias y Librerías

#### 6.1 Librerías Core Requeridas
- **pandas**: Manipulación de DataFrames
- **openpyxl**: Lectura/escritura de Excel preservando formato
- **PySide6**: Interface de usuario
- **pathlib**: Manejo de rutas de archivos

#### 6.2 Librerías Opcionales para Optimización
- **numpy**: Optimizaciones numéricas
- **concurrent.futures**: Paralelización opcional
- **psutil**: Monitoreo de recursos del sistema
- **tqdm**: Barras de progreso mejoradas

### 7. Consideraciones de Seguridad

#### 7.1 Validación de Archivos
- Verificar integridad de plantillas Excel
- Validar permisos de acceso a archivos
- Sanitizar nombres de archivos generados
- Prevenir path traversal attacks

#### 7.2 Manejo de Datos Sensibles
- No logging de datos confidenciales
- Opciones para encriptar archivos generados
- Limpieza de archivos temporales
- Cumplimiento con regulaciones de privacidad

### 8. Plan de Testing de Funcionalidades

#### 8.1 Tests Unitarios
- Tests para cada función de validación
- Tests para generación de nombres de archivos
- Tests para mapeo de columnas
- Tests para manejo de errores

#### 8.2 Tests de Integración
- Tests end-to-end con diferentes tipos de datos
- Tests con plantillas Excel complejas
- Tests de rendimiento con datasets grandes
- Tests de compatibilidad con diferentes sistemas operativos

#### 8.3 Tests de Usabilidad
- Tests con usuarios finales
- Análisis de tiempo de configuración
- Evaluación de claridad de mensajes de error
- Validación de flujo de trabajo completo

---

**Estado**: ✅ COMPLETADO - Subfase 1.1
**Próximo**: Subfase 1.2 - Análisis de Impacto en la Arquitectura
**Fecha**: 2025-11-04