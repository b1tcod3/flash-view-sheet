# core/data_handler.py — Documentación Completa

Núcleo de operaciones de datos de Flash View Sheet. Contiene las funciones de carga con el sistema de loaders, análisis/estadísticas, filtrado, exportación (PDF, SQL, imagen, XLSX, CSV) y el sistema de **exportación separada con plantillas Excel** (`ExcelTemplateSplitter`).

---

## Índice

1. [Visión General](#1-visión-general)
2. [Importaciones](#2-importaciones)
3. [Carga de Datos](#3-carga-de-datos)
4. [Formato y Soporte de Archivos](#4-formato-y-soporte-de-archivos)
5. [Análisis y Estadísticas](#5-análisis-y-estadísticas)
6. [Filtrado](#6-filtrado)
7. [Exportación](#7-exportación)
8. [Limpieza y Agregación](#8-limpieza-y-agregación)
9. [Pivote](#9-pivote)
10. [Sistema de Exportación Separada con Plantillas](#10-sistema-de-exportación-separada-con-plantillas)
    - [10.1 Dataclasses y Excepciones](#101-dataclasses-y-excepciones)
    - [10.2 Clase ExcelTemplateSplitter](#102-clase-exceltemplatesplitter)
    - [10.3 Función exportar_datos_separados](#103-función-exportardatosseparados)
11. [Diagrama de Dependencias](#11-diagrama-de-dependencias)
12. [Resumen](#12-resumen)

---

## 1. Visión General

`data_handler.py` (1389 líneas) es el **módulo central de lógica de datos**. Se organiza en dos bloques:

**Bloque A — Operaciones generales (líneas 1–621):**
- `cargar_datos()` y `cargar_datos_con_opciones()` — carga usando el **Factory Pattern** de `core/loaders/`
- `get_supported_file_formats()`, `is_file_format_supported()` — formato soportado
- `obtener_metadata()`, `obtener_estadisticas()`, `obtener_estadisticas_basicas()` — análisis
- `aplicar_filtro()` con optimización indexada para datasets grandes
- `exportar_a_pdf/sql/imagen/xlsx/csv()` — exportación
- `limpiar_datos()`, `agregar_datos()`, `pivotar_datos()` — transformación

**Bloque B — Exportación separada con plantillas (líneas 622–1389):**
- `ExportSeparatedConfig`, `ValidationResult`, `ExportResult` (dataclasses)
- `ExcelTemplateSplitter` — separa un DataFrame por columna y exporta cada grupo a un archivo Excel basado en plantilla, preservando formato
- `exportar_datos_separados()` — función de nivel superior que envuelve al splitter

**Diseño:**
- El Bloque A depende de `core/loaders` (Factory) para cargar y de `config.optimization_config` para umbrales de rendimiento
- El Bloque B usa `openpyxl` (opcional, flag `OPENPYXL_AVAILABLE`) y `core/performance_optimizer` (opcional, flag `PERFORMANCE_OPTIMIZER_AVAILABLE`)
- `ExcelTemplateSplitter` delega la preservación de formato a `core/simple_excel_preserver`

---

## 2. Importaciones

### Módulos estándar
| Módulo | Uso |
|--------|-----|
| `os` | `os.access` para permisos de escritura, `os.environ` (Bloque B) |
| `sys` | Insertar raíz del proyecto en `sys.path` para importar `config` |
| `Path` | `pathlib.Path` — rutas de archivos y plantillas |
| `Any`, `Callable` | Tipos genéricos |
| `re`, `json`, `shutil`, `hashlib`, `gc`, `tempfile` | Bloque B (sanitizar nombres, resúmenes, cleanup) |
| `time`, `datetime` | Bloque B (timestamps, tiempos de procesamiento) |
| `dataclass`, `field` | Bloque B (dataclasses) |
| `Enum` | Bloque B (fallback `ChunkingStrategy`) |
| `namedtuple`, `defaultdict` | Bloque B |

### Terceros
| Símbolo | Módulo | Uso |
|---------|--------|-----|
| `pd` | `pandas` | DataFrames, `groupby`, `pivot_table` |
| `np` | `numpy` | `np.mean`, `np.sum` en `pivotar_datos` |
| `optimization_config` | `config` | Umbrales de virtualización, stats, filtrado y chunking |
| `load_workbook`, `Workbook`, `get_column_letter`, `column_index_from_string`, `coordinate_to_tuple` | `openpyxl` (opcional) | Bloque B |
| `Font`, `PatternFill`, `Border`, `Alignment` | `openpyxl.styles` (opcional) | Bloque B |
| `PerformanceOptimizer`, `ExcelFormatOptimizer`, `ProgressMonitor`, `ChunkingStrategy`, `SystemResources`, `PerformanceConfig`, `PerformanceResult`, `ProgressInfo` | `core.performance_optimizer` (opcional) | Bloque B, optimización de chunking |

### Imports lazy (dentro de funciones)
| Símbolo | Módulo | Cuándo se importa |
|---------|--------|-------------------|
| `get_file_loader` | `core.loaders` | `cargar_datos()`, `cargar_datos_con_opciones()` |
| `CsvLoader`, `ExcelLoader` | `core.loaders.csv_loader`, `core.loaders.excel_loader` | `cargar_datos_con_opciones()` |
| `get_supported_formats`, `is_file_supported` | `core.loaders` | `get_supported_file_formats()`, `is_file_format_supported()` |
| `SimpleDocTemplate`, `Table`, `TableStyle`, `colors`, `letter` | `reportlab` | `exportar_a_pdf()` |
| `create_engine` | `sqlalchemy` | `exportar_a_sql()` |
| `QApplication`, `QPixmap` | `PySide6.QtWidgets`, `PySide6.QtGui` | `exportar_a_imagen()` |
| `openpyxl`, `dataframe_to_rows` | `openpyxl.utils.dataframe` | `exportar_a_xlsx()` |
| `create_excel_with_simple_format_preservation` | `core.simple_excel_preserver` | `_create_excel_file_with_template()` |

---

## 3. Carga de Datos

### `cargar_datos(filepath, chunk_size=None) -> pd.DataFrame`

Carga un archivo usando el Factory de loaders.

**Flujo:**
1. `get_file_loader(filepath)` → obtiene el loader según extensión
2. Si `chunk_size` se especifica **o** el loader soporta chunks y `file_size_mb > 100`:
   - Si `chunk_size is None`, calcula el tamaño: `1000` si `estimated_rows > VIRTUALIZATION_THRESHOLD` (5000), si no `10000`
   - `loader.load_in_chunks(chunk_size)`; si falla, hace fallback a `loader.load()`
3. Si no aplica chunking → `loader.load()`

**Excepciones:** `FileNotFoundError` (archivo inexistente), `ValueError` (formato no soportado).

### `cargar_datos_con_opciones(filepath, skip_rows=0, column_names=None, chunk_size=None, separator=None, sheet_name=None) -> pd.DataFrame`

Variante con opciones avanzadas:
- `skip_rows` → filas a saltar al inicio (la siguiente fila se usa como header)
- `column_names` → renombrado `{original: nuevo}`
- `separator` → separador personalizado para CSV/TSV
- `sheet_name` → hoja para Excel

**Regla clave:** si `skip_rows > 0` o hay `column_names`, usa **carga normal** (porque `load_in_chunks` no soporta opciones). En caso contrario aplica la misma lógica de chunking de `cargar_datos`.

---

## 4. Formato y Soporte de Archivos

| Función | Firma | Descripción |
|---------|-------|-------------|
| `get_supported_file_formats` | `() -> list` | Extensiones soportadas (delega en `core.loaders.get_supported_formats`) |
| `is_file_format_supported` | `(filepath: str) -> bool` | Verifica si la extensión es soportada (delega en `is_file_supported`) |

---

## 5. Análisis y Estadísticas

### `obtener_metadata(df) -> dict[str, Any]`
Devuelve: `filas`, `columnas`, `nombres_columnas`, `tipos_datos` (str), `columnas_numericas` (`number`), `columnas_texto` (`object`), `valores_nulos` (dict por columna).

### `obtener_estadisticas(df, columnas=None, percentiles=None) -> pd.DataFrame`
- Si `columnas is None`, usa solo numéricas (si no hay, todas)
- Percentiles por defecto `[0.25, 0.5, 0.75]` (convierte `p>1` a decimal)
- **Optimización:** si `should_sample_stats(len(df))` (dataset > 100k filas), usa muestra de `STATS_SAMPLE_SIZE` (50k) con `random_state=42`
- Retorna `df.describe(percentiles=..., include='all')`

### `obtener_estadisticas_basicas(df) -> dict`
Devuelve: `total_filas`, `total_columnas`, `columnas_numericas`, `columnas_texto`, `columnas_fecha`, `memoria_uso_mb`, `filas_duplicadas`, `valores_nulos_total`.

---

## 6. Filtrado

### `aplicar_filtro(df, columna, termino, use_index=True) -> pd.DataFrame`
- `ValueError` si `columna` no existe en `df.columns`
- Si `should_optimize_filtering(len(df))` (dataset > 50k filas) **y** `use_index` → `_aplicar_filtro_indexado()`, si no `_aplicar_filtro_simple()`

### `_aplicar_filtro_simple(df, columna, termino) -> pd.DataFrame`
`df[df[columna].astype(str).str.contains(termino, case=False, na=False)]`

### `_aplicar_filtro_indexado(df, columna, termino) -> pd.DataFrame`
Soporta tres modos según el término:
- `^...$` → búsqueda exacta (`str.match`, regex)
- `*...*` → wildcards (`*` convertido a `.*`, `str.contains` regex)
- resto → búsqueda normal case-insensitive

Si falla, cae en `_aplicar_filtro_simple`.

---

## 7. Exportación

Todas devuelven `bool` (éxito) y usan import lazy.

| Función | Firma | Detalles |
|---------|-------|----------|
| `exportar_a_pdf` | `(df, filepath) -> bool` | reportlab `SimpleDocTemplate` + `Table` con estilo (header gris, filas beige, grid) |
| `exportar_a_sql` | `(df, filepath, nombre_tabla) -> bool` | SQLAlchemy engine SQLite; `to_sql(..., if_exists='replace', index=False)`; si no hay columnas crea `_placeholder` |
| `exportar_a_imagen` | `(table_view, filepath) -> bool` | Captura `table_view.grab()` y guarda como `QPixmap` |
| `exportar_a_xlsx` | `(df, filepath) -> bool` | openpyxl `Workbook` + `dataframe_to_rows` |
| `exportar_a_csv` | `(df, filepath, delimiter=',', encoding='utf-8') -> bool` | `df.to_csv(..., index=False)` |

---

## 8. Limpieza y Agregación

### `limpiar_datos(df, opciones=None) -> pd.DataFrame`
Opciones: `eliminar_duplicados` (True), `eliminar_nulos` (False), `rellenar_nulos` (`{col: valor}`), `eliminar_columnas` (list), `convertir_tipos` (`{col: 'numeric'|'datetime'|'string'}`). Copia el df antes de mutar.

### `agregar_datos(df, operaciones) -> pd.DataFrame`
Cada operación: `{'grupo': [...], 'funciones': {...}, 'nombre': ...}`. Soporta groupby+agg y agregación global. Aplana columnas MultiIndex y añade columna `operacion`. Concatena resultados con `pd.concat`.

---

## 9. Pivote

### `pivotar_datos(df, index, columns, values, aggfunc='mean') -> pd.DataFrame`
`aggfunc` soporta `mean` (`np.mean`), `sum` (`np.sum`), `count`, o cualquier función pasada como string. Usa `df.pivot_table(...)` y `reset_index()`.

> **Nota:** el pivote automático moderno vive en `PivotService.generate_auto_pivots()` (ver `docs/app/services.md` y `docs/core/pivot.md`).

---

## 10. Sistema de Exportación Separada con Plantillas

### 10.1 Dataclasses y Excepciones

#### `ExportSeparatedConfig` (dataclass)

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `separator_column` | `str` | (requerido) | Columna para separar |
| `template_path` | `str` | (requerido) | Ruta a plantilla `.xlsx`/`.xlsm` |
| `output_folder` | `str` | (requerido) | Carpeta destino |
| `start_cell` | `str` | `"A1"` | Celda inicial para datos |
| `file_template` | `str` | `"{valor}.xlsx"` | Plantilla de nombre de archivo |
| `column_mapping` | `dict[str, str]` | `{}` | `{'col_df': 'A', ...}` |
| `handle_duplicates` | `str` | `"overwrite"` | `'overwrite'`/`'append'`/`'skip'` |
| `create_summary` | `bool` | `True` | Crear archivo resumen |
| `preserve_format` | `bool` | `True` | Preservar formato Excel |
| `enable_chunking` | `bool` | `True` | Chunking automático |
| `max_memory_mb` | `int` | `2048` | Límite de memoria |
| `progress_callback` | `Callable | None` | `None` | Callback de progreso |

**Métodos:**
- `validate() -> dict` — devuelve `{'valid', 'errors', 'warnings'}`. Valida columna de separación, existencia/extensión de plantilla, permisos de escritura en `output_folder` (crea el dir), celda inicial (`coordinate_to_tuple`), template de nombre `.xlsx`
- `get_default_mapping(df_columns) -> dict` — mapeo posicional `A–Z, AA, AB...` vía `get_column_letter`
- `to_dict() -> dict` — serializa todos los campos

#### `ValidationResult` (dataclass)
`is_valid=True`, `errors[]`, `warnings[]`, `info[]` + `add_error()`, `add_warning()`, `add_info()`.

#### `ExportResult` (dataclass)
`success=False`, `file_path=""`, `group_name=""`, `rows_processed=0`, `processing_time=0.0`, `error=""`, `timestamp=None`.

### 10.2 Clase ExcelTemplateSplitter

```python
class ExcelTemplateSplitter:
    def __init__(self, df: pd.DataFrame, config: ExportSeparatedConfig) -> None
```

**Atributos:** `df`, `config`, `progress_callback`, `logger`, `created_files[]`, `failed_groups{}`, `_cancelled`. Lanza `ImportError` si `openpyxl` no está disponible.

**Configuración de rendimiento (`_setup_performance_optimization`):**
- Si `PERFORMANCE_OPTIMIZER_AVAILABLE` y `config.enable_chunking`: crea `PerformanceOptimizer(memory_threshold_mb=config.max_memory_mb)`, determina estrategia con `determine_optimal_chunking_strategy(df, separator_column)`, crea `ExcelFormatOptimizer` y `ProgressMonitor`
- Fallback básico: chunking si `len(df) > VIRTUALIZATION_THRESHOLD` o memoria > `max_memory_mb`; `chunk_size = min(DEFAULT_CHUNK_SIZE, max(1000, len(df)//20))`

**Métodos principales:**

| Método | Descripción |
|--------|-------------|
| `validate_configuration() -> ValidationResult` | Valida config (via `config.validate()`), df no vacío, columna existe, valores únicos, plantilla legible |
| `analyze_data() -> dict` | `total_rows`, `total_columns`, `memory_usage_mb`, análisis de columna separadora (unique, nulos, top_values, estimated_groups), tiempo estimado y recomendaciones |
| `generate_file_preview() -> list[dict]` | Preview por grupo: `filename`, `group_name`, `rows`, `estimated_size_kb`, `file_path`, `status` |
| `separate_and_export() -> dict` | Flujo completo (validar → analizar → iterar grupos → resumen) |
| `_export_group(group_name, group_df) -> ExportResult` | Genera nombre, resuelve conflictos, crea Excel |
| `_create_excel_file_with_template(output_path, data) -> bool` | Usa `create_excel_with_simple_format_preservation`; fallback a `_create_excel_file_with_template_fallback` |
| `_create_excel_file_with_template_fallback(output_path, data) -> bool` | Carga plantilla y escribe solo valores (minimalista) |
| `cancel_operation()` | Marca `_cancelled = True` |
| `cleanup_temp_files()` | Elimina archivos creados |

**Métodos privados de utilidad:**
- `_generate_filename_for_group(group_name, row_count)` — reemplaza `{valor}`, `{columna}`, `{fecha}`, `{fecha_hora}`, `{filas}`, `{timestamp}`
- `_process_file_template(template, group_info)` — sustituye placeholders
- `_sanitize_filename(filename)` — elimina `[<>:"/\\|?*]`, puntos finales, normaliza espacios, limita a 255 chars, evita nombre vacío
- `_resolve_filename_conflicts(file_path)` — auto-numeración `_01`, `_02`... hasta 999, luego timestamp

**Retorno de `separate_and_export()`:**
```python
{
  'success': bool,
  'files_created': list[str],
  'groups_processed': int,
  'total_rows': int,
  'successful_exports': int,
  'failed_exports': int,
  'processing_time': float,
  'errors': list[str],
  'warnings': list[str],
  'failed_groups': dict[str, str],
  'analysis': dict,
}
```

### 10.3 Función `exportar_datos_separados`

```python
def exportar_datos_separados(df: pd.DataFrame, config_dict: dict) -> dict
```

Construye un `ExportSeparatedConfig` desde el dict (claves: `separator_column`, `template_path`, `start_cell`, `output_folder`, `file_template`, `column_mapping`, `handle_duplicates`, `create_summary`, `preserve_format`, `enable_chunking`, `max_memory_mb`) y delega en `ExcelTemplateSplitter.separate_and_export()`. Retorna el mismo dict normalizado; en caso de error devuelve un dict con `success=False` y `errors`.

---

## 11. Diagrama de Dependencias

```
core/data_handler.py
├── config.py (optimization_config)          → umbrales de rendimiento
├── core/loaders/ (Factory + loaders)        → carga de archivos
├── core/simple_excel_preserver.py           → preservación de formato (Bloque B)
├── core/performance_optimizer.py (opcional) → PerformanceOptimizer, ExcelFormatOptimizer, ProgressMonitor
└── (lazy) reportlab, sqlalchemy, PySide6, openpyxl
```

```
app/services/export_service.py  → usa exportar_a_pdf/xlsx/csv/sql/imagen/datos_separados
app/services/data_service.py    → usa cargar_datos_con_opciones, get_supported_file_formats
app/services/profiler_service.py→ usa obtener_estadisticas_basicas
```

---

## 12. Resumen

| Aspecto | Detalle |
|---------|---------|
| **Líneas** | 1389 |
| **Responsabilidad** | Operaciones centrales de datos + exportación separada con plantillas |
| **Carga** | Factory Pattern (`core/loaders`), chunking > 100MB |
| **Exportaciones** | PDF, SQL, imagen, XLSX, CSV, separado |
| **Dataclasses** | `ExportSeparatedConfig`, `ValidationResult`, `ExportResult` |
| **Dependencias opcionales** | openpyxl, performance_optimizer |
