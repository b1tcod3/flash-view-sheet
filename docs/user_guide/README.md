# Guía de Usuario - Exportación de Datos Separados

## 📋 Índice

1. [Introducción](#introducción)
2. [¿Qué es la Exportación Separada?](#qué-es-la-exportación-separada)
3. [Requisitos Previos](#requisitos-previos)
4. [Tutorial Rápido](#tutorial-rápido)
5. [Guía Detallada](#guía-detallada)
6. [Configuración Avanzada](#configuración-avanzada)
7. [Ejemplos Prácticos](#ejemplos-prácticos)
8. [Solución de Problemas](#solución-de-problemas)
9. [Preguntas Frecuentes](#preguntas-frecuentes)

## Introducción

La **Exportación de Datos Separados** es una funcionalidad avanzada de Flash Sheet que permite dividir un conjunto de datos en múltiples archivos Excel personalizados usando plantillas predefinidas. Esta herramienta es especialmente útil para:

- **Reportes Empresariales**: Separar datos por región, departamento, período
- **Análisis por Categorías**: Dividir datos por tipos de productos, clientes, etc.
- **Distribuciones Automatizadas**: Generar reportes individuales para diferentes entidades
- **Plantillas Personalizadas**: Mantener formato corporativo consistente

## ¿Qué es la Exportación Separada?

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

### ¿Qué formatos de archivo soporta?

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