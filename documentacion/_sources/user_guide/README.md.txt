# Guía de Usuario - Flash View Sheet

## 📋 Índice

1. [Introducción](#introducción)
2. [Funcionalidades Principales](#funcionalidades-principales)
   - [Carga de Carpeta](#carga-de-carpeta)
   - [Cruce de Datos (Joins)](#cruce-de-datos-joins)
   - [Exportación Separada](#exportación-separada)
3. [Carga de Carpeta - Tutorial](#carga-de-carpeta---tutorial)
4. [Cruce de Datos - Tutorial](#cruce-de-datos---tutorial)
5. [Exportación Separada - Tutorial](#exportación-separada---tutorial)
6. [Guía Detallada](#guía-detallada)
7. [Configuración Avanzada](#configuración-avanzada)
8. [Ejemplos Prácticos](#ejemplos-prácticos)
9. [Solución de Problemas](#solución-de-problemas)
10. [Preguntas Frecuentes](#preguntas-frecuentes)

## Introducción

**Flash View Sheet** es una herramienta poderosa para análisis y manipulación de datos que incluye múltiples funcionalidades avanzadas:

- **Carga de Carpeta**: Consolidar múltiples archivos Excel de una carpeta en un único dataset
- **Cruce de Datos (Joins)**: Combinar datasets mediante operaciones de join
- **Exportación Separada**: Dividir datos en múltiples archivos Excel personalizados
- **Visualización Interactiva**: Tablas dinámicas, gráficos y análisis
- **Soporte Multi-Formato**: CSV, Excel, JSON, SQL y más

## Funcionalidades Principales

### Carga de Carpeta

La funcionalidad de **Carga de Carpeta** permite cargar múltiples archivos Excel desde una carpeta y consolidarlos en un único dataset. Esta herramienta es especialmente útil para:

- **Consolidación de Datos**: Unir datos de múltiples archivos Excel en uno solo
- **Análisis Agregado**: Combinar reportes mensuales, regionales o departamentales
- **Procesamiento por Lotes**: Manejar grandes volúmenes de datos distribuidos en archivos
- **Alineación Inteligente**: Alinear columnas automáticamente por posición o manualmente

#### Características

✅ **Escaneo Automático**: Detecta automáticamente archivos Excel (.xlsx, .xls) en la carpeta
✅ **Selección Flexible**: Elige qué archivos incluir/excluir de la consolidación
✅ **Alineación de Columnas**: Alinea columnas por posición o manualmente con drag-and-drop
✅ **Vista Previa**: Visualiza cómo se alinearán las columnas antes de consolidar
✅ **Renombrado de Columnas**: Personaliza los nombres de las columnas consolidadas
✅ **Manejo de Diferencias**: Gestiona archivos con diferente número de columnas
✅ **Optimización de Rendimiento**: Procesamiento eficiente para carpetas grandes

### Cruce de Datos (Joins)

La funcionalidad de **Cruce de Datos** permite combinar dos datasets mediante operaciones de join directamente desde la interfaz, similar a las consultas SQL. Es ideal para:

- **Enriquecimiento de Datos**: Añadir información de clientes a ventas
- **Análisis Combinado**: Unir datos de múltiples fuentes
- **Consolidación**: Merge de datasets relacionados
- **Limpieza de Datos**: Identificar coincidencias y diferencias

#### Tipos de Join Soportados

- **Inner Join**: Solo filas con coincidencias en ambas tablas
- **Left Join**: Todas las filas del primer dataset + coincidencias del segundo
- **Right Join**: Todas las filas del segundo dataset + coincidencias del primero
- **Cross Join**: Producto cartesiano de ambas tablas

#### Características

✅ **Interfaz Intuitiva**: Configuración visual paso a paso
✅ **Preview en Tiempo Real**: Ver resultados antes de ejecutar
✅ **Validación Automática**: Detección de errores y sugerencias
✅ **Optimización de Rendimiento**: Manejo eficiente de datasets grandes
✅ **Historial Completo**: Re-ejecución de operaciones previas
✅ **Exportación**: Resultados en múltiples formatos

### Exportación Separada

La **Exportación de Datos Separados** permite dividir un conjunto de datos en múltiples archivos Excel personalizados usando plantillas predefinidas. Esta herramienta es especialmente útil para:

- **Reportes Empresariales**: Separar datos por región, departamento, período
- **Análisis por Categorías**: Dividir datos por tipos de productos, clientes, etc.
- **Distribuciones Automatizadas**: Generar reportes individuales para diferentes entidades
- **Plantillas Personalizadas**: Mantener formato corporativo consistente

## Carga de Carpeta - Tutorial

### Concepto Básico

Imagina que tienes una carpeta con múltiples archivos Excel de ventas mensuales:

```
📁 Ventas_2025/
├── Enero.xlsx    (Producto, Ventas, Región)
├── Febrero.xlsx  (Producto, Ventas, Región)
├── Marzo.xlsx    (Producto, Ventas, Región)
└── Abril.xlsx    (Producto, Ventas, Región)
```

La **Carga de Carpeta** te permite:

1. **Seleccionar la carpeta** con todos los archivos
2. **Elegir qué archivos incluir** en la consolidación
3. **Alinear las columnas** automáticamente por posición
4. **Generar un único dataset** con todos los datos consolidados

### Características Principales

✅ **Detección Automática**: Encuentra todos los archivos Excel en la carpeta
✅ **Selección Interactiva**: Elige qué archivos procesar con checkboxes
✅ **Vista Previa de Alineación**: Ve cómo se alinearán las columnas antes de consolidar
✅ **Drag & Drop Manual**: Realinea columnas arrastrando y soltando
✅ **Renombrado de Columnas**: Personaliza los nombres de las columnas finales
✅ **Manejo Inteligente**: Gestiona diferencias en estructura entre archivos

## Tutorial Rápido

### Paso 1: Preparar tus Archivos
1. Organiza tus archivos Excel en una carpeta dedicada
2. Asegúrate de que todos los archivos tengan estructura similar
3. Verifica que las columnas estén en orden consistente

### Paso 2: Acceder a la Función
1. En el menú **Archivo**, selecciona **"Cargar Carpeta..."**
2. Se abre el diálogo de configuración de carga de carpeta

### Paso 3: Seleccionar Carpeta
1. **Haz clic en "Seleccionar Carpeta..."**
2. **Navega** hasta la carpeta con tus archivos Excel
3. El sistema **escanea automáticamente** y muestra los archivos encontrados

### Paso 4: Configurar Archivos
1. **Revisa la lista** de archivos Excel encontrados
2. **Desmarca archivos** que no quieras incluir (opcional)
3. El sistema carga **metadata** de cada archivo seleccionado

### Paso 5: Vista Previa de Alineación
1. **Observa la tabla** que muestra cómo se alinearán las columnas
2. Cada columna muestra los nombres de las columnas correspondientes de cada archivo
3. **Arrastra y suelta** columnas para realinearlas manualmente si es necesario
4. **Haz doble clic** en nombres de columna para renombrarlas

### Paso 6: Configuración Final
1. **Revisa los nombres** de las columnas consolidadas
2. **Añade renombrados** si deseas cambiar los nombres finales
3. **Configura opciones** adicionales si es necesario

### Paso 7: Consolidación
1. **Haz clic en "Aceptar"** para iniciar la consolidación
2. El sistema **procesa todos los archivos** según tu configuración
3. Los datos consolidados se **cargan en la aplicación principal**

¡Listo! Ahora tienes un único dataset con todos tus datos consolidados.

## Guía Detallada - Carga de Carpeta

### Selección de Carpeta

**¿Cómo elegir la carpeta correcta?**

1. **Organización lógica**: Agrupa archivos relacionados en la misma carpeta
2. **Estructura consistente**: Asegúrate de que los archivos tengan columnas similares
3. **Acceso permitido**: Verifica que tengas permisos de lectura en la carpeta

### Selección de Archivos

**Opciones disponibles:**
- ✅ **Incluir todos**: Por defecto, todos los archivos Excel se incluyen
- ✅ **Selección manual**: Desmarca archivos específicos que no quieras procesar
- ✅ **Filtros automáticos**: El sistema excluye archivos que no se puedan leer

### Alineación de Columnas

**Métodos de alineación:**

1. **Por Posición (Predeterminado)**
   - Las columnas se alinean por su orden en cada archivo
   - Columna 1 del Archivo A ↔ Columna 1 del Archivo B
   - Ideal cuando los archivos tienen estructura idéntica

2. **Por Nombre (Futuro)**
   - Las columnas se alinean por nombres coincidentes
   - Requiere nombres de columna consistentes

3. **Manual con Drag & Drop**
   - Arrastra columnas para realinearlas
   - Control total sobre la alineación final

### Manejo de Diferencias

**Cuando los archivos tienen diferente número de columnas:**

1. **Columnas faltantes**: Se rellenan con valores nulos (NaN)
2. **Columnas adicionales**: Se incluyen como columnas extra
3. **Vista previa clara**: La tabla muestra exactamente qué sucederá

### Renombrado de Columnas

**Opciones de personalización:**
- **Renombrado individual**: Doble clic en la tabla de vista previa
- **Renombrado masivo**: Usar la tabla de renombrado en la parte inferior
- **Nombres finales**: Los nombres que aparecerán en el dataset consolidado

### Ejemplo Práctico

**Archivos de entrada:**

*ventas_enero.xlsx:*
```
Producto | Ventas | Región
Laptop   | 1000   | Norte
Mouse    | 200    | Norte
```

*ventas_febrero.xlsx:*
```
Producto | Ventas | Región
Teclado  | 300    | Sur
Monitor  | 500    | Sur
```

**Resultado consolidado:**
```
Producto | Ventas | Región | __source__
Laptop   | 1000   | Norte  | ventas_enero.xlsx
Mouse    | 200    | Norte  | ventas_enero.xlsx
Teclado  | 300    | Sur    | ventas_febrero.xlsx
Monitor  | 500    | Sur    | ventas_febrero.xlsx
```

## Cruce de Datos - Tutorial

### Paso 1: Preparar tus Datos

1. **Carga el dataset principal** en Flash Sheet (ventas, transacciones, etc.)
2. **Identifica qué información adicional** necesitas añadir
3. **Prepara el dataset secundario** con los datos complementarios

### Paso 2: Acceder a la Función

1. En el menú **Datos**, selecciona **"Cruzar Datos..."**
2. Se abre el diálogo de configuración de cruce

### Paso 3: Configuración Básica

1. **Carga el dataset derecho** usando "Cargar Dataset Derecho"
2. **Selecciona el tipo de join** apropiado para tu caso:
   - Inner Join: Solo datos que existen en ambas tablas
   - Left Join: Todos los datos principales + matches del secundario
   - Right Join: Todos los datos secundarios + matches del principal
   - Cross Join: Combinación completa (usar con cuidado)

3. **Selecciona las columnas de join**:
   - Columna del dataset izquierdo
   - Columna del dataset derecho
   - Deben tener tipos de datos compatibles

### Paso 4: Opciones Avanzadas (Opcional)

- **Sufijos para columnas duplicadas**: Personaliza `_left` y `_right`
- **Validación de integridad**: Verifica consistencia de datos
- **Columna indicador**: Añade `_merge` para ver origen de datos
- **Ordenar resultados**: Ordena por columna de join

### Paso 5: Preview y Ejecución

1. **Haz clic en "Actualizar Preview"** para ver resultados
2. **Revisa las estadísticas**: filas resultantes, tiempo estimado
3. **Ejecuta el join** con "🚀 Ejecutar Join"

### Paso 6: Visualizar Resultados

- Los resultados se muestran en una vista especializada
- **Metadatos del cruce**: estadísticas detalladas
- **Opciones de filtrado**: búsqueda y filtrado específico
- **Exportación**: guarda resultados en Excel, CSV, PDF

### Ejemplo Práctico

**Dataset Ventas:**
```
cliente_id | producto | cantidad
1          | Laptop   | 2
2          | Mouse    | 1
```

**Dataset Clientes:**
```
id | nombre      | ciudad
1  | Juan Pérez  | Madrid
2  | Ana García  | Barcelona
```

**Resultado Left Join (cliente_id = id):**
```
cliente_id | producto | cantidad | id | nombre      | ciudad
1          | Laptop   | 2        | 1  | Juan Pérez  | Madrid
2          | Mouse    | 1        | 2  | Ana García  | Barcelona
```

## Exportación Separada - Tutorial

### Concepto Básico

Imagina que tienes un DataFrame con datos de ventas de múltiples regiones:

| Región | Vendedor | Producto | Ventas |
|--------|----------|----------|--------|
| Norte  | Juan     | Laptop   | 1500   |
| Sur    | María    | Mouse    | 200    |
| Norte  | Carlos   | Teclado  | 300    |
| Sur    | Ana      | Monitor  | 800    |

La **Exportación Separada** te permite:

1. **Seleccionar la columna de separación** (ej: "Región")
2. **Definir una plantilla Excel** con tu formato corporativo
3. **Generar automáticamente**:
   - `Norte_2025-11-05.xlsx` (datos de región Norte)
   - `Sur_2025-11-05.xlsx` (datos de región Sur)

### Características Principales

✅ **Plantillas Excel Personalizadas**: Preserva formato, colores, fórmulas
✅ **Mapeo Inteligente**: Conversión automática de columnas
✅ **Optimización Automática**: Maneja datasets grandes sin problemas
✅ **Interfaz Visual**: Configuración intuitiva paso a paso
✅ **Preview en Tiempo Real**: Ve qué archivos se crearán antes de exportar
✅ **Validación Completa**: Verifica configuración antes de procesar

## Requisitos Previos

### Datos Requeridos
- **DataFrame cargado** en Flash Sheet
- **Columna de separación** con valores categóricos (texto, números)
- **Datos consistentes** en formato tabular

### Archivos de Plantilla
- **Archivo Excel** (.xlsx) con formato deseado
- **Encabezados** en primera fila (recomendado)
- **Formato corporativo** (colores, fuentes, logos)

### Espacio en Disco
- **Mínimo**: 2x el tamaño de datos originales
- **Recomendado**: 3x para datasets grandes con plantillas complejas

## Tutorial Rápido

### Paso 1: Preparar Datos
1. Carga tu archivo en Flash Sheet (CSV, Excel, etc.)
2. Verifica que los datos se muestran correctamente
3. Identifica la columna que usarás para separar

### Paso 2: Acceder a la Función
1. En el menú principal, busca **"Separar"**
2. Selecciona **"Exportar Datos Separados..."**
3. Se abre el diálogo de configuración

### Paso 3: Configuración Básica
1. **Selecciona columna** de separación del dropdown
2. **Selecciona plantilla Excel** usando el botón "Seleccionar"
3. **Define carpeta destino** para los archivos
4. **Configura nombres** de archivos con templates

### Paso 4: Verificar y Exportar
1. Haz clic en **"Vista Previa"** para ver archivos a generar
2. **Revisa la validación** (debe aparecer ✅ verde)
3. Haz clic en **"Exportar"** para procesar

¡Listo! Tus archivos Excel separados se han generado automáticamente.

## Guía Detallada

### Sección 1: Selección de Columna de Separación

**¿Cómo elegir la columna correcta?**

1. **Identifica la categorización deseada**:
   - Por región geográfica
   - Por departamento
   - Por período de tiempo
   - Por categoría de producto
   - Por cliente/empresa

2. **Verifica la calidad de la columna**:
   - Valores consistentes (evita variaciones de texto)
   - Número razonable de categorías (2-100 ideal)
   - Sin demasiados valores nulos

**Ejemplo de Preview:**
```
✅ Buena columna: "Región" con valores: Norte, Sur, Este, Oeste
❌ Problema: "Comentarios" con 500+ valores únicos
```

### Sección 2: Configuración de Plantilla Excel

**Pasos para seleccionar plantilla:**

1. **Haz clic en "Seleccionar Plantilla Excel"**
2. **Navega** hasta tu archivo de plantilla
3. **Selecciona la hoja** si el archivo tiene múltiples hojas
4. **Configura celda inicial** donde insertar datos

**Características de una buena plantilla:**
- ✅ Encabezados en primera fila
- ✅ Formato corporativo aplicado
- ✅ Celdas vacías suficientes para datos
- ✅ Fórmulas preservadas donde sea necesario

### Sección 3: Mapeo de Columnas

**El sistema mapea automáticamente**:
- Columna DataFrame → Columna Excel (A, B, C...)
- Mantiene orden por defecto
- Permite ajuste manual si es necesario

**Ajuste manual de mapeo:**
1. Ve a la pestaña **"Mapeo de Columnas"**
2. **Modifica asignaciones** usando dropdowns
3. **Vista previa** muestra cómo se verá en Excel

### Sección 4: Plantillas de Nombres de Archivo

**Placeholders disponibles:**

- `{valor}` - Valor de la columna de separación
- `{fecha}` - Fecha actual (YYYY-MM-DD)
- `{hora}` - Hora actual (HHMMSS)
- `{contador}` - Número secuencial (01, 02, 03...)
- `{columna_nombre}` - Nombre de columna de separación
- `{total_filas}` - Número de filas en el grupo

**Ejemplos útiles:**
```
Reporte_{valor}_{fecha}.xlsx
→ Norte_2025-11-05.xlsx

{valor}_Ventas_Q4.xlsx
→ ProductoA_Ventas_Q4.xlsx

Reporte_{valor}_{contador}.xlsx
→ Norte_01.xlsx, Sur_02.xlsx
```

## Configuración Avanzada

### Opciones de Rendimiento

**Chunking Automático:**
- **Habilitado por defecto** para datasets > 10K filas
- **Optimiza memoria** sin afectar calidad
- **Recomendado** para datasets grandes

**Tamaño de Chunk:**
- **Conservador**: 1,000 filas (seguro)
- **Moderado**: 10,000 filas (equilibrado)
- **Agresivo**: 100,000+ filas (solo expertos)

### Manejo de Duplicados

**Opciones disponibles:**

1. **Sobrescribir archivos existentes**
   - Más rápido, pero puede perder datos
   - Recomendado para procesamiento inicial

2. **Numerar automáticamente**
   - Crea archivos: archivo_01.xlsx, archivo_02.xlsx
   - Preserva todos los datos

3. **Evitar sobrescritura**
   - Solo crea si no existe el archivo
   - Más seguro, puede fallar si hay duplicados

### Configuración de Celda Inicial

**Opciones predefinidas:**
- A1 (inicio normal)
- A2 (deja espacio para títulos)
- A5 (deja espacio para logos/headers)

**Coordenadas personalizadas:**
- Formato: C10, B15, etc.
- Útil para plantillas complejas

## Ejemplos Prácticos

### Ejemplo 1: Reporte de Ventas por Región

**Datos de entrada:**
```
| Región | Vendedor | Producto | Ventas | Fecha    |
|--------|----------|----------|--------|----------|
| Norte  | Juan     | Laptop   | 1500   | 2025-11-01|
| Sur    | María    | Mouse    | 200    | 2025-11-01|
| Norte  | Carlos   | Teclado  | 300    | 2025-11-01|
| Sur    | Ana      | Monitor  | 800    | 2025-11-01|
```

**Configuración:**
- **Columna**: Región
- **Plantilla**: `template_ventas.xlsx`
- **Nombre**: `Reporte_{valor}_Nov2025.xlsx`

**Resultado:**
- `Reporte_Norte_Nov2025.xlsx` (2 filas)
- `Reporte_Sur_Nov2025.xlsx` (2 filas)

### Ejemplo 2: Análisis por Período

**Datos de entrada:**
```
| Mes    | Categoría | Ventas |
|--------|-----------|--------|
| Enero  | A         | 1000   |
| Febrero| A         | 1200   |
| Enero  | B         | 800    |
| Febrero| B         | 900    |
```

**Configuración:**
- **Columna**: Mes
- **Plantilla**: `template_mensual.xlsx`
- **Nombre**: `{valor}_Analisis.xlsx`

**Resultado:**
- `Enero_Analisis.xlsx` (2 filas - categorías A y B)
- `Febrero_Analisis.xlsx` (2 filas - categorías A y B)

### Ejemplo 3: Exportación con Múltiples Plantillas

**Para diferentes tipos de reportes:**
1. **Plantilla de Ventas** → Reportes comerciales
2. **Plantilla de Inventario** → Reportes de stock
3. **Plantilla Financiera** → Reportes contables

## Solución de Problemas

### Problemas con Carga de Carpeta

#### Problema: "No se encontraron archivos Excel en la carpeta"

**Posibles causas y soluciones:**

1. **Archivos en subcarpetas**
   - ✅ El sistema busca recursivamente en subcarpetas
   - ✅ Verifica que los archivos estén en subcarpetas accesibles

2. **Extensiones no reconocidas**
   - ✅ Solo se detectan .xlsx y .xls
   - ✅ Renombra archivos con extensiones correctas
   - ✅ Verifica que no sean archivos ocultos

3. **Permisos de carpeta**
   - ✅ Asegúrate de tener permisos de lectura
   - ✅ Prueba con una carpeta diferente

#### Problema: "Error al cargar archivo específico"

**Soluciones por tipo de error:**

1. **Archivo corrupto**
   - ✅ Salta automáticamente al siguiente archivo
   - ✅ Revisa el archivo en Excel antes de cargarlo
   - ✅ Usa "Reparar" en Excel si está disponible

2. **Contraseña protegido**
   - ❌ Actualmente no soporta archivos con contraseña
   - ✅ Remueve la protección antes de cargar

3. **Archivo muy grande**
   - ✅ Optimización automática para archivos grandes
   - ✅ Divide archivos muy grandes si es posible

#### Problema: "Columnas no se alinean correctamente"

**Ajustes de alineación:**

1. **Vista previa no coincide**
   - ✅ Revisa la tabla de vista previa antes de consolidar
   - ✅ Usa drag & drop para realinear manualmente

2. **Nombres de columna diferentes**
   - ✅ Renombra columnas en la vista previa
   - ✅ Usa la tabla de renombrado para cambios masivos

3. **Estructuras muy diferentes**
   - ✅ Considera procesar archivos por separado
   - ✅ Revisa si los archivos son realmente compatibles

#### Problema: "Procesamiento muy lento"

**Optimizaciones:**

1. **Demasiados archivos**
   - ✅ Reduce el número de archivos por carga
   - ✅ Procesa en lotes más pequeños

2. **Archivos muy grandes**
   - ✅ Verifica el tamaño total de los archivos
   - ✅ Cierra otras aplicaciones para liberar memoria

3. **Disco duro lento**
   - ✅ Usa SSD si es posible
   - ✅ Libera espacio en disco

### Problema: "Configuración inválida"

**Posibles causas y soluciones:**

1. **Columna de separación vacía**
   - ✅ Selecciona una columna válida
   - ✅ Verifica que tenga datos

2. **Plantilla Excel no encontrada**
   - ✅ Verifica que el archivo existe
   - ✅ Confirma que tiene extensión .xlsx
   - ✅ Asegúrate de tener permisos de lectura

3. **Carpeta destino sin permisos**
   - ✅ Selecciona una carpeta donde tengas permisos de escritura
   - ✅ Evita rutas del sistema (C:\Windows, etc.)

### Problema: "Archivos duplicados"

**Soluciones:**

1. **Cambiar estrategia de duplicados**
   - Selecciona "Numerar automáticamente"
   - O cambia la plantilla de nombres

2. **Limpiar carpeta destino**
   - Elimina archivos conflictivos
   - Usa carpeta vacía para nueva exportación

### Problema: "Procesamiento muy lento"

**Optimizaciones:**

1. **Habilitar chunking**
   - Activa "Optimización automática"
   - Reduce tamaño de chunk si es necesario

2. **Simplificar plantilla**
   - Usa plantilla más simple
   - Evita fórmulas complejas

3. **Cerrar otros programas**
   - Libera memoria para el procesamiento

### Problema: "Formato no preservado"

**Verificaciones:**

1. **Plantilla compatible**
   - Usa archivos .xlsx (no .xls)
   - Verifica que el formato se vea bien en Excel

2. **Celdas no ocupadas**
   - Configura celda inicial correcta
   - Verifica que no hay datos que interfieran

## Preguntas Frecuentes

### Preguntas sobre Carga de Carpeta

#### ¿Qué tipos de archivos Excel soporta?

- ✅ **Formatos soportados**: .xlsx y .xls
- ✅ **Versiones**: Compatible con Excel 2007 y superiores
- ✅ **Compresión**: Maneja archivos comprimidos
- ❌ **No soportados**: .xlsb, .xlsm con macros complejas

#### ¿Cuántos archivos puedo cargar de una carpeta?

- **Sin límite técnico** (depende de memoria disponible)
- **Recomendado**: Hasta 100 archivos para buen rendimiento
- **Límite práctico**: ~500 archivos dependiendo del sistema y tamaño

#### ¿Qué pasa si los archivos tienen estructuras diferentes?

**Manejo inteligente de diferencias:**
- **Columnas desiguales**: Se alinean por posición, rellenando con nulos
- **Nombres diferentes**: Se preservan los nombres originales
- **Tipos de datos**: Se convierten automáticamente cuando es posible
- **Vista previa**: Siempre puedes ver exactamente qué sucederá

#### ¿Se puede cancelar una carga en progreso?

✅ **Sí**. La carga incluye:
- Barra de progreso con botón "Cancelar"
- Procesamiento por lotes para recuperación
- Estado guardado para continuar después

#### ¿Cómo funciona la alineación de columnas?

**Tres métodos disponibles:**
1. **Automática por posición**: Las columnas se alinean por orden (1↔1, 2↔2, etc.)
2. **Manual con drag & drop**: Arrastra columnas para realinear
3. **Renombrado**: Cambia nombres de columnas consolidadas

#### ¿Se preservan los datos originales?

✅ **Sí, completamente**. Los archivos originales no se modifican. Los datos consolidados se cargan como un nuevo dataset en la aplicación.

#### ¿Hay límite en el tamaño de los archivos?

- **Sin límite técnico** por archivo (depende de memoria)
- **Optimización automática**: Archivos grandes se procesan eficientemente
- **Recomendado**: Hasta 50MB por archivo para buen rendimiento

#### ¿Puedo excluir archivos específicos?

✅ **Sí, completamente**:
- **Selección visual**: Desmarca archivos en la lista
- **Filtros por nombre**: Excluye archivos que contengan ciertas palabras
- **Selección múltiple**: Mantén Ctrl para seleccionar varios

#### ¿Qué pasa con archivos corruptos o ilegibles?

**Manejo robusto de errores:**
- **Archivos corruptos**: Se saltan automáticamente con advertencia
- **Permisos insuficientes**: Se reporta el error específico
- **Formato incompatible**: Se intenta recuperar datos cuando es posible

#### ¿Se puede automatizar la carga de carpetas?

- **Configuración guardada**: Las configuraciones se pueden reutilizar
- **Línea de comandos**: Soporte futuro para automatización
- **APIs programáticas**: Disponible para desarrolladores

### Preguntas sobre Cruce de Datos (Joins)

#### ¿Qué tipos de join están disponibles?

- **Inner Join**: Solo filas con coincidencias en ambas tablas
- **Left Join**: Todas las filas de la tabla izquierda + coincidencias de la derecha
- **Right Join**: Todas las filas de la tabla derecha + coincidencias de la izquierda
- **Cross Join**: Producto cartesiano (todas las combinaciones posibles)

#### ¿Cuántos datasets puedo cruzar a la vez?

Actualmente, se soporta el cruce entre **2 datasets**:
- Un dataset principal (izquierdo)
- Un dataset adicional (derecho)

Para cruces más complejos, puedes encadenar operaciones de join.

#### ¿Qué pasa si las columnas de join tienen tipos diferentes?

El sistema **advierte automáticamente** sobre incompatibilidades de tipos:
- `cliente_id (str) ≠ id (int)` → Sugiere conversión
- Puedes elegir columnas diferentes o convertir tipos manualmente

#### ¿Se preservan los datos originales?

✅ **Sí, completamente**. Los datasets originales no se modifican. Los resultados del cruce se almacenan en una vista separada.

#### ¿Cómo funciona el preview?

- **Muestreo inteligente**: Para cross joins grandes, usa subconjuntos
- **Estimación rápida**: Calcula filas y columnas resultantes
- **Validación en tiempo real**: Detecta errores antes de ejecutar

#### ¿Hay límite en el tamaño de los datasets?

- **Sin límite técnico** (depende de memoria disponible)
- **Optimización automática**: Chunking para datasets grandes
- **Recomendado**: Hasta 1M filas por dataset para buen rendimiento

#### ¿Se puede deshacer un join?

- Los datos originales **siempre se preservan**
- Puedes **volver a la vista anterior** sin perder información
- El **historial** permite re-ejecutar joins previos

### Preguntas sobre Exportación Separada

#### ¿Qué formatos de archivo soporta?

- ✅ **Entrada**: CSV, Excel (.xlsx), JSON, Parquet, HDF5
- ✅ **Plantillas**: Solo Excel (.xlsx, .xlsm)
- ✅ **Salida**: Excel (.xlsx) únicamente

### ¿Cuántos archivos puedo generar?

- **Sin límite técnico** (solo espacio en disco)
- **Recomendado**: Máximo 1,000 archivos para mejor rendimiento
- **Límite práctico**: ~10,000 archivos dependiendo del sistema

### ¿Se preservan las fórmulas Excel?

✅ **Sí, completamente**. La funcionalidad usa openpyxl que preserva:
- Fórmulas existentes
- Formato de celdas
- Colores y estilos
- Validaciones de datos
- Gráficos (si están en área no afectada)

### ¿Qué pasa con valores nulos en la columna de separación?

**Opciones disponibles:**
1. **Agrupar juntos** → Un archivo "Valores_Nulos.xlsx"
2. **Archivo separado** → "Con_Valores.xlsx" y "Sin_Valores.xlsx"
3. **Excluir** → Solo exportar filas con valores válidos
4. **Valor personalizado** → Reemplazar nulos con "N/A"

### ¿Puedo cancelar un procesamiento en curso?

✅ **Sí**. El procesamiento incluye:
- Barra de progreso con botón "Cancelar"
- Recovery automático si se interrumpe
- Continúa desde el punto de interrupción

### ¿Funciona con datasets muy grandes?

✅ **Optimizado para datasets grandes**:
- **< 10K filas**: Procesamiento directo
- **10K-100K filas**: Chunking moderado
- **100K+ filas**: Chunking agresivo con monitoreo

### ¿Se mantiene la compatibilidad con otras funciones?

✅ **100% compatible**:
- No afecta otras funcionalidades
- Preserva transformaciones existentes
- Compatible con sistema de loaders

### ¿Hay límite en el tamaño de plantilla?

- **Recomendado**: < 50MB por plantilla
- **Límite práctico**: Dependiente de memoria disponible
- **Optimización**: Plantillas grandes se procesan de forma optimizada

### ¿Puedo usar múltiples hojas en plantillas?

✅ **Sí, completamente soportado**:
- Selección de hoja específica
- Cada archivo usa la misma hoja seleccionada
- Preservación completa del formato de la hoja

### ¿Qué pasa si se interrumpe la alimentación eléctrica?

✅ **Recovery automático**:
- Progreso se guarda automáticamente
- Al reiniciar, continúa desde donde se detuvo
- Archivos corruptos se recuperan automáticamente

## Soporte y Recursos

### Documentación Adicional
- **Guía Técnica**: Para desarrolladores
- **API Reference**: Para programación
- **Testing Documentation**: Para validaciones

### Ejemplos y Plantillas
- Plantillas de ejemplo incluidas en `/examples/`
- Casos de uso empresariales documentados
- Scripts de ejemplo para automatización

### Resolución de Problemas
- Logs detallados en archivo de aplicación
- Herramientas de diagnóstico incluidas
- Modo debug para problemas complejos

---

**¡Gracias por usar Flash Sheet - Exportación Separada!**

Esta funcionalidad está diseñada para simplificar tus tareas de análisis y distribución de datos. Si tienes preguntas adicionales o encuentras problemas, consulta la documentación técnica o revisa los ejemplos incluidos.