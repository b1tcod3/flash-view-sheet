# SUBFASE 2.2: DISEÑO DE ALGORITMOS
## Especificación Detallada de Algoritmos para Separación de Datos con Plantillas Excel

### 📋 Objetivo
Definir algoritmos específicos y optimizados para el procesamiento eficiente de separación de datos, mapeo de columnas, generación de nombres de archivos, y validación con manejo de casos especiales.

### 🧮 Algoritmos Principales

#### **1. Algoritmo de Separación Eficiente**

**Nombre**: `DataFrameSeparationAlgorithm`

**Propósito**: Separar DataFrame en grupos por columna específica con optimización de memoria y rendimiento.

**Pseudocódigo**:
```python
def separate_dataframe_efficiently(df: pd.DataFrame, separator_column: str, 
                                 enable_chunking: bool = True) -> Iterator[GroupData]:
    """
    Algoritmo principal de separación con optimización de memoria
    
    Args:
        df: DataFrame a separar
        separator_column: Columna para agrupar
        enable_chunking: Habilitar chunking automático
    
    Yields:
        GroupData: Datos del grupo con metadata
    """
    
    # FASE 1: Validación y Preparación
    if separator_column not in df.columns:
        raise ValueError(f"Columna '{separator_column}' no existe en DataFrame")
    
    # Detectar valores nulos para manejo especial
    null_mask = df[separator_column].isnull()
    if null_mask.any():
        null_group_name = handle_null_values(separator_column)
        yield GroupData(name=null_group_name, 
                       data=df[null_mask], 
                       is_null_group=True)
    
    # FASE 2: Optimización para chunking
    if enable_chunking and should_use_chunking(df):
        for chunk in iterate_dataframe_in_chunks(df, chunk_size=get_optimal_chunk_size()):
            for group_data in process_chunk_separation(chunk, separator_column):
                yield group_data
    else:
        # FASE 3: Separación directa para datasets pequeños
        grouped_data = df[~null_mask].groupby(separator_column)
        total_groups = len(grouped_data)
        
        for group_name, group_df in grouped_data:
            yield GroupData(
                name=str(group_name), 
                data=group_df,
                group_size=len(group_df),
                group_index=get_group_index(group_name, grouped_data),
                total_groups=total_groups
            )
```

**Optimizaciones Específicas**:
1. **Detección Temprana de Nulos**: Procesar nulos por separado para evitar overhead
2. **Chunking Inteligente**: Usar chunks solo cuando sea necesario
3. **Index Caching**: Cache de índices para grupos frecuentes
4. **Memory Profiling**: Monitoreo continuo de uso de memoria

**Complejidad**:
- **Tiempo**: O(n log n) para grouping + O(n) para procesamiento
- **Espacio**: O(k * chunk_size) donde k es número de grupos

#### **2. Algoritmo de Mapeo DataFrame → Excel**

**Nombre**: `ColumnMappingAlgorithm`

**Propósito**: Mapear columnas DataFrame a coordenadas Excel (A, B, C...) con validación y presets automáticos.

**Pseudocódigo**:
```python
def map_dataframe_to_excel_columns(df_columns: List[str], 
                                 excel_columns: List[str],
                                 mapping_strategy: str = "positional") -> ColumnMapping:
    """
    Algoritmo de mapeo flexible entre DataFrame y Excel
    
    Args:
        df_columns: Columnas del DataFrame
        excel_columns: Columnas disponibles en plantilla Excel
        mapping_strategy: "positional", "by_name", "preset", "manual"
    
    Returns:
        ColumnMapping: Mapeo completo con validación
    """
    
    mapping = ColumnMapping()
    
    if mapping_strategy == "positional":
        # Mapeo 1:1 por posición
        mapping.positional = create_positional_mapping(df_columns, excel_columns)
        
    elif mapping_strategy == "by_name":
        # Mapeo por coincidencia de nombres (case-insensitive)
        mapping.name_based = create_name_based_mapping(df_columns, excel_columns)
        
    elif mapping_strategy == "preset":
        # Mapeo usando preset predefinido
        mapping.preset = apply_preset_mapping(df_columns)
        
    elif mapping_strategy == "manual":
        # Mapeo manual (requiere configuración UI)
        mapping.manual = validate_manual_mapping(df_columns, excel_columns)
    
    # FASE 2: Validación y Completado Automático
    validation_result = validate_mapping_completeness(mapping, df_columns)
    
    if not validation_result.is_complete:
        # Completar automáticamente columnas faltantes
        missing_mappings = validation_result.missing_columns
        auto_filled = auto_complete_mapping(missing_mappings, excel_columns)
        mapping.update(auto_filled)
    
    # FASE 3: Optimización de Columnas
    optimized_mapping = optimize_column_layout(mapping)
    
    return optimized_mapping

def create_positional_mapping(df_columns: List[str], 
                            excel_columns: List[str]) -> Dict[str, str]:
    """Mapeo posicional 1:1"""
    mapping = {}
    min_columns = min(len(df_columns), len(excel_columns))
    
    for i in range(min_columns):
        df_col = df_columns[i]
        excel_col = excel_columns[i]
        mapping[df_col] = excel_col
    
    return mapping

def create_name_based_mapping(df_columns: List[str], 
                            excel_columns: List[str]) -> Dict[str, str]:
    """Mapeo por coincidencia de nombres (fuzzy matching)"""
    mapping = {}
    
    for df_col in df_columns:
        best_match = find_best_column_match(df_col, excel_columns)
        if best_match:
            mapping[df_col] = best_match
    
    return mapping

def auto_complete_mapping(missing_columns: List[str], 
                        available_excel_columns: List[str]) -> Dict[str, str]:
    """Completar automáticamente columnas faltantes"""
    mapping = {}
    used_excel_cols = set()
    
    # Priorizar columnas por tipo de datos
    for col in missing_columns:
        best_excel_col = find_most_suitable_excel_column(
            col, available_excel_columns, used_excel_cols
        )
        if best_excel_col:
            mapping[col] = best_excel_col
            used_excel_cols.add(best_excel_col)
    
    return mapping
```

**Presets de Mapeo Predefinidos**:
```python
COLUMN_MAPPING_PRESETS = {
    "ventas_empresariales": {
        "fecha": "A", "region": "B", "vendedor": "C", "producto": "D",
        "cantidad": "E", "precio_unitario": "F", "total": "G", "comision": "H"
    },
    "reportes_financieros": {
        "periodo": "A", "categoria": "B", "subcategoria": "C", "ingresos": "D",
        "gastos": "E", "utilidad": "F", "margen": "G", "crecimiento": "H"
    },
    "datos_cientificos": {
        "experimento": "A", "muestra": "B", "parametro": "C", "valor": "D",
        "unidad": "E", "precision": "F", "fecha_medicion": "G", "observaciones": "H"
    }
}

def apply_preset_mapping(df_columns: List[str]) -> Dict[str, str]:
    """Aplicar preset más compatible con columnas disponibles"""
    best_preset = None
    best_score = 0
    
    for preset_name, preset_mapping in COLUMN_MAPPING_PRESETS.items():
        score = calculate_preset_compatibility(df_columns, preset_mapping)
        if score > best_score:
            best_score = score
            best_preset = preset_mapping
    
    return best_preset if best_score > 0.7 else {}
```

#### **3. Algoritmo de Generación de Nombres con Templates**

**Nombre**: `FileNamingTemplateProcessor`

**Propósito**: Procesar plantillas de nombres de archivo con placeholders dinámicos y validación de compatibilidad del SO.

**Pseudocódigo**:
```python
class FileNamingTemplateProcessor:
    PLACEHOLDER_PROCESSORS = {
        '{valor}': lambda group: sanitize_string(str(group['valor'])),
        '{columna}': lambda group: sanitize_string(str(group['columna'])),
        '{fecha}': lambda group: datetime.now().strftime('%Y-%m-%d'),
        '{fecha_hora}': lambda group: datetime.now().strftime('%Y-%m-%d_%H%M'),
        '{filas}': lambda group: str(group['filas']),
        '{indice}': lambda group: f"{group['indice']:02d}",  # 01, 02, 03...
        '{timestamp}': lambda group: str(int(time.time())),
        '{tamaño_archivo}': lambda group: format_file_size(group['tamaño_mb']),
        '{hash_md5}': lambda group: generate_short_hash(group['datos'])
    }
    
    def process_template(self, template: str, group_info: Dict) -> str:
        """
        Procesar plantilla de nombre de archivo
        
        Args:
            template: Plantilla con placeholders (ej: "Reporte_{valor}_{fecha}.xlsx")
            group_info: Información del grupo para substituir placeholders
        
        Returns:
            str: Nombre de archivo procesado y sanitizado
        """
        
        # FASE 1: Validación de plantilla
        template_validation = self.validate_template_syntax(template)
        if not template_validation.is_valid:
            raise ValueError(f"Plantilla inválida: {template_validation.errors}")
        
        # FASE 2: Extracción de placeholders
        placeholders = self.extract_placeholders(template)
        
        # FASE 3: Procesamiento de cada placeholder
        processed_template = template
        for placeholder in placeholders:
            if placeholder in self.PLACEHOLDER_PROCESSORS:
                try:
                    replacement = self.PLACEHOLDER_PROCESSORS[placeholder](group_info)
                    processed_template = processed_template.replace(placeholder, replacement)
                except Exception as e:
                    # Fallback para placeholder problemático
                    fallback_value = self.get_fallback_value(placeholder)
                    processed_template = processed_template.replace(placeholder, fallback_value)
            else:
                # Placeholder desconocido - mantener original pero sanitizar
                sanitized_placeholder = sanitize_filename(placeholder)
                processed_template = processed_template.replace(placeholder, sanitized_placeholder)
        
        # FASE 4: Sanitización final para compatibilidad del SO
        sanitized_filename = self.sanitize_filename_for_os(processed_template)
        
        # FASE 5: Validación de longitud y caracteres
        final_filename = self.validate_filename_constraints(sanitized_filename)
        
        return final_filename
    
    def extract_placeholders(self, template: str) -> List[str]:
        """Extraer todos los placeholders válidos de la plantilla"""
        import re
        pattern = r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}'
        matches = re.findall(pattern, template)
        return [f'{{{match}}}' for match in matches]
    
    def sanitize_filename_for_os(self, filename: str) -> str:
        """Sanitizar nombre para compatibilidad cross-platform"""
        # Caracteres prohibidos en diferentes SO
        forbidden_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(forbidden_chars, '_', filename)
        
        # Remover puntos múltiples al final
        sanitized = re.sub(r'\.+$', '', sanitized)
        
        # Asegurar que no esté vacío
        if not sanitized.strip():
            sanitized = 'archivo_sin_nombre'
        
        # Normalizar espacios
        sanitized = ' '.join(sanitized.split())
        
        return sanitized
    
    def validate_filename_constraints(self, filename: str) -> str:
        """Validar restricciones de longitud y formato"""
        MAX_LENGTH = 255  # Universal
        
        if len(filename) > MAX_LENGTH:
            # Truncar inteligentemente preservando extensión
            name_part, ext = os.path.splitext(filename)
            available_length = MAX_LENGTH - len(ext)
            truncated_name = name_part[:available_length-3] + '...'
            filename = truncated_name + ext
        
        return filename

def generate_unique_filename(base_filename: str, existing_files: Set[str]) -> str:
    """Generar nombre único para evitar conflictos"""
    if base_filename not in existing_files:
        return base_filename
    
    # Intentar con números secuenciales
    name_part, ext = os.path.splitext(base_filename)
    counter = 1
    
    while True:
        new_filename = f"{name_part}_{counter:02d}{ext}"
        if new_filename not in existing_files:
            return new_filename
        counter += 1
        
        # Límite de seguridad
        if counter > 999:
            # Usar timestamp como último recurso
            timestamp = str(int(time.time()))
            new_filename = f"{name_part}_{timestamp}{ext}"
            return new_filename
```

#### **4. Algoritmo de Validación y Pre-análisis**

**Nombre**: `DataValidationAlgorithm`

**Propósito**: Validar configuración completa y analizar datos antes de proceder con separación.

**Pseudocódigo**:
```python
class DataValidationAlgorithm:
    def validate_complete_configuration(self, df: pd.DataFrame, 
                                      config: ExportSeparatedConfig) -> ValidationResult:
        """
        Validación exhaustiva de configuración y datos
        
        Returns:
            ValidationResult: Resultado completo con warnings y errores
        """
        result = ValidationResult()
        result.start_validation()
        
        # FASE 1: Validación de datos de entrada
        data_validation = self.validate_input_data(df)
        result.merge(data_validation)
        
        # FASE 2: Validación de configuración
        config_validation = self.validate_configuration(config, df)
        result.merge(config_validation)
        
        # FASE 3: Validación de plantilla Excel
        if config.template_path:
            template_validation = self.validate_excel_template(config.template_path)
            result.merge(template_validation)
        
        # FASE 4: Análisis predictivo
        analysis = self.predict_processing_requirements(df, config)
        result.analysis = analysis
        
        # FASE 5: Validación de recursos del sistema
        system_validation = self.validate_system_resources(analysis)
        result.merge(system_validation)
        
        result.finish_validation()
        return result
    
    def validate_input_data(self, df: pd.DataFrame) -> ValidationResult:
        """Validar DataFrame de entrada"""
        result = ValidationResult()
        
        # Verificar DataFrame vacío
        if df.empty:
            result.add_error("DataFrame está vacío")
            return result
        
        # Verificar columnas
        if len(df.columns) == 0:
            result.add_error("DataFrame no tiene columnas")
            return result
        
        # Verificar nombres de columnas duplicados
        duplicated_cols = df.columns[df.columns.duplicated()].tolist()
        if duplicated_cols:
            result.add_warning(f"Columnas duplicadas detectadas: {duplicated_cols}")
        
        # Verificar tipos de datos problemáticos
        problematic_types = self.detect_problematic_data_types(df)
        if problematic_types:
            result.add_info(f"Tipos de datos problemáticos: {problematic_types}")
        
        # Análisis de memoria
        memory_usage_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        if memory_usage_mb > 2048:  # 2GB
            result.add_warning(f"Uso de memoria alto: {memory_usage_mb:.1f}MB")
        
        return result
    
    def predict_processing_requirements(self, df: pd.DataFrame, 
                                      config: ExportSeparatedConfig) -> ProcessingAnalysis:
        """Análisis predictivo de requisitos de procesamiento"""
        analysis = ProcessingAnalysis()
        
        # Estimación de grupos
        if config.separator_column in df.columns:
            unique_values = df[config.separator_column].nunique()
            null_count = df[config.separator_column].isnull().sum()
            analysis.estimated_groups = unique_values + (1 if null_count > 0 else 0)
        else:
            analysis.estimated_groups = 0
        
        # Estimación de tamaño de archivos
        avg_rows_per_group = len(df) / max(analysis.estimated_groups, 1)
        analysis.estimated_rows_per_group = avg_rows_per_group
        
        # Predicción de tiempo de procesamiento
        processing_time_per_mb = 0.5  # Segundos por MB (estimado)
        total_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        analysis.estimated_processing_time = total_mb * processing_time_per_mb
        
        # Predicción de uso de memoria pico
        peak_memory_mb = total_mb * 1.5  # 50% overhead por procesamiento
        analysis.estimated_peak_memory_mb = peak_memory_mb
        
        # Recomendaciones de optimización
        recommendations = []
        if analysis.estimated_groups > 100:
            recommendations.append("Considerar usar chunking para mejor rendimiento")
        if analysis.estimated_processing_time > 300:
            recommendations.append("Procesamiento largo detectado - habilitar progreso detallado")
        if peak_memory_mb > 2048:
            recommendations.append("Alto uso de memoria - considerar procesamiento por chunks")
        
        analysis.recommendations = recommendations
        
        return analysis
```

### ⚡ Algoritmos de Optimización

#### **5. Algoritmo de Chunking Inteligente**

**Nombre**: `IntelligentChunkingAlgorithm`

**Propósito**: Determinar estrategia óptima de chunking basada en características del dataset.

```python
def determine_optimal_chunking_strategy(df: pd.DataFrame, 
                                      config: ExportSeparatedConfig) -> ChunkingStrategy:
    """
    Algoritmo para determinar estrategia óptima de chunking
    
    Estrategia basada en:
    1. Tamaño total del DataFrame
    2. Número de grupos únicos
    3. Distribución de tamaños de grupo
    4. Recursos del sistema disponibles
    """
    
    total_rows = len(df)
    memory_usage_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
    unique_groups = df[config.separator_column].nunique() if config.separator_column in df.columns else 0
    
    # Análisis de distribución de grupos
    if unique_groups > 0:
        group_sizes = df.groupby(config.separator_column).size()
        largest_group_size = group_sizes.max()
        smallest_group_size = group_sizes.min()
        group_size_variance = group_sizes.var()
    else:
        largest_group_size = total_rows
        smallest_group_size = total_rows
        group_size_variance = 0
    
    # Decisión de estrategia
    if memory_usage_mb > 2048 or total_rows > 1000000:
        # Estrategia agresiva para datasets muy grandes
        return ChunkingStrategy.AGGRESSIVE
        
    elif unique_groups > 100 and group_size_variance > 10000:
        # Muchos grupos con tamaños variables
        return ChunkingStrategy.GROUP_BASED
        
    elif largest_group_size > 50000:
        # Algunos grupos muy grandes
        return ChunkingStrategy.SIZE_BASED
        
    elif memory_usage_mb > 500:
        # Dataset moderadamente grande
        return ChunkingStrategy.MODERATE
        
    else:
        # Dataset pequeño - procesamiento directo
        return ChunkingStrategy.NONE

class ChunkingStrategy:
    NONE = "none"           # Procesamiento directo
    MODERATE = "moderate"   # Chunking conservador
    SIZE_BASED = "size"     # Basado en tamaño de grupos
    GROUP_BASED = "group"   # Basado en número de grupos
    AGGRESSIVE = "aggressive"  # Chunking agresivo
```

#### **6. Algoritmo de Preservación de Formato Excel**

**Nombre**: `ExcelFormatPreservationAlgorithm`

**Propósito**: Insertar datos en plantilla Excel preservando 100% del formato original.

```python
def preserve_excel_format_during_insert(workbook: Workbook, 
                                       start_cell: str, 
                                       data_df: pd.DataFrame,
                                       column_mapping: Dict[str, str]) -> bool:
    """
    Algoritmo para preservar formato Excel durante inserción de datos
    
    Estrategia:
    1. Detectar y cachear formato existente
    2. Insertar datos sin alterar estilos
    3. Restaurar formato si es necesario
    4. Optimizar performance de openpyxl
    """
    
    # FASE 1: Análisis de formato existente
    sheet = workbook.active
    start_row, start_col = cell_coordinates_to_indices(start_cell)
    
    # Detectar área de datos existente
    existing_data_range = detect_existing_data_range(sheet, start_cell)
    existing_formats = cache_existing_formats(sheet, existing_data_range)
    
    # FASE 2: Preparación para inserción optimizada
    # Deshabilitar cálculo automático de fórmulas
    sheet.sheet_properties.tabColor = sheet.sheet_properties.tabColor
    
    # FASE 3: Inserción de datos con formato preservado
    success = True
    for row_idx, (_, row_data) in enumerate(data_df.iterrows()):
        excel_row = start_row + row_idx
        
        for df_col, excel_col_letter in column_mapping.items():
            if df_col in data_df.columns:
                excel_col_idx = column_letter_to_index(excel_col_letter)
                cell = sheet.cell(row=excel_row, column=excel_col_idx)
                
                # Insertar valor preservando formato
                value = row_data[df_col]
                if pd.isna(value):
                    cell.value = None
                else:
                    cell.value = value
                
                # Preservar formato original si existe
                if (excel_row, excel_col_idx) in existing_formats:
                    cell.font = existing_formats[(excel_row, excel_col_idx)]['font']
                    cell.fill = existing_formats[(excel_row, excel_col_idx)]['fill']
                    cell.border = existing_formats[(excel_row, excel_col_idx)]['border']
                    cell.number_format = existing_formats[(excel_row, excel_col_idx)]['number_format']
    
    # FASE 4: Optimización final
    workbook._archive.close()  # Forzar escritura
    
    return success

def cache_existing_formats(sheet: Worksheet, data_range: str) -> Dict:
    """Cachear formatos existentes para preservación"""
    formats = {}
    
    if not data_range:
        return formats
    
    try:
        for row in sheet[data_range]:
            for cell in row:
                if cell.value is not None:  # Solo cachear celdas con contenido
                    formats[(cell.row, cell.column)] = {
                        'font': copy_font(cell.font),
                        'fill': copy_fill(cell.fill),
                        'border': copy_border(cell.border),
                        'number_format': cell.number_format,
                        'alignment': copy_alignment(cell.alignment)
                    }
    except Exception as e:
        print(f"Warning: No se pudo cachear formato completo: {e}")
        # Fallback: cachear solo número de formato
        for row in sheet[data_range]:
            for cell in row:
                if cell.value is not None:
                    formats[(cell.row, cell.column)] = {
                        'number_format': cell.number_format
                    }
    
    return formats
```

### 🔄 Algoritmos de Manejo de Errores

#### **7. Algoritmo de Recovery y Rollback**

**Nombre**: `ErrorRecoveryAlgorithm`

**Propósito**: Recovery automático en caso de fallos parciales con rollback de archivos inconsistentes.

```python
class ErrorRecoveryAlgorithm:
    def __init__(self, output_directory: str):
        self.output_directory = output_directory
        self.created_files = []
        self.backup_directory = None
    
    def execute_with_recovery(self, export_function: Callable) -> ExportResult:
        """Ejecutar exportación con recovery automático"""
        
        # FASE 1: Preparación del entorno
        self.setup_recovery_environment()
        
        try:
            # FASE 2: Ejecución con monitoreo
            result = export_function()
            
            # FASE 3: Verificación post-proceso
            if self.verify_export_completeness(result):
                self.cleanup_recovery_environment()
                return result
            else:
                # FASE 4: Recovery en caso de inconsistencia
                return self.perform_recovery(result)
                
        except Exception as e:
            # FASE 5: Recovery por excepción
            return self.handle_critical_error(e)
    
    def setup_recovery_environment(self):
        """Preparar entorno para recovery"""
        # Crear directorio de backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_directory = os.path.join(
            self.output_directory, f".backup_{timestamp}"
        )
        os.makedirs(self.backup_directory, exist_ok=True)
    
    def perform_recovery(self, partial_result: ExportResult) -> ExportResult:
        """Realizar recovery de exportación parcial"""
        
        recovery_result = ExportResult()
        recovery_result.success = False
        recovery_result.recovery_attempted = True
        
        # Verificar integridad de archivos creados
        valid_files = []
        corrupted_files = []
        
        for file_path in partial_result.files_created:
            if self.verify_file_integrity(file_path):
                valid_files.append(file_path)
            else:
                corrupted_files.append(file_path)
                # Mover a backup para análisis
                backup_path = os.path.join(self.backup_directory, os.path.basename(file_path))
                shutil.move(file_path, backup_path)
        
        recovery_result.files_created = valid_files
        recovery_result.files_corrupted = corrupted_files
        recovery_result.recovery_successful = len(valid_files) > 0
        
        # Limpiar archivos corruptos
        self.cleanup_corrupted_files(corrupted_files)
        
        return recovery_result
    
    def verify_file_integrity(self, file_path: str) -> bool:
        """Verificar integridad de archivo Excel"""
        try:
            # Intentar abrir con openpyxl
            workbook = openpyxl.load_workbook(file_path)
            workbook.close()
            return True
        except Exception:
            return False
```

### 📊 Métricas de Rendimiento de Algoritmos

#### **Análisis de Complejidad**

| Algoritmo | Complejidad Temporal | Complejidad Espacial | Optimizaciones |
|-----------|---------------------|---------------------|----------------|
| `DataFrameSeparationAlgorithm` | O(n log n) | O(k × chunk_size) | Chunking inteligente |
| `ColumnMappingAlgorithm` | O(n × m) | O(n + m) | Presets automáticos |
| `FileNamingTemplateProcessor` | O(t × p) | O(t) | Cache de resultados |
| `DataValidationAlgorithm` | O(n) | O(1) | Análisis incremental |
| `ExcelFormatPreservationAlgorithm` | O(n × c) | O(f) | Cache de formatos |
| `ErrorRecoveryAlgorithm` | O(f log f) | O(f) | Verificación paralela |

#### **Benchmarks Estimados**

| Dataset Size | Rows | Groups | Processing Time | Memory Peak |
|-------------|------|--------|----------------|-------------|
| Small | < 10K | < 10 | < 30s | < 100MB |
| Medium | 10K-100K | 10-100 | < 3min | < 500MB |
| Large | 100K-1M | 100-1000 | < 15min | < 2GB |
| Very Large | 1M+ | 1000+ | < 1hr | < 4GB |

### ✅ Criterios de Validación de Algoritmos

#### **Testing de Algoritmos**
1. **Unit Tests**: Cada algoritmo debe tener > 95% cobertura
2. **Performance Tests**: Benchmarks contra datasets estándar
3. **Edge Case Tests**: Valores nulos, caracteres especiales, límites del SO
4. **Integration Tests**: Algoritmos trabajando juntos
5. **Stress Tests**: Datasets extremos para identificar límites

#### **Métricas de Calidad**
- **Accuracy**: 100% preservación de datos
- **Performance**: < 3x tiempo de exportación normal
- **Reliability**: > 99% éxito sin intervención manual
- **Memory Efficiency**: < 2GB pico para datasets de 1M filas
- **Format Preservation**: 100% preservación de formato Excel

---

**CONCLUSIÓN**: Los algoritmos especificados proporcionan una base sólida y optimizada para la separación eficiente de datos con plantillas Excel, con énfasis en rendimiento, confiabilidad y preservación de formato. Cada algoritmo incluye optimizaciones específicas y manejo robusto de casos especiales.