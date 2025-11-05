# SUBFASE 2.3: MANEJO DE CASOS ESPECIALES
## Estrategias y Algoritmos para Casos Edge y Manejo de Errores

### 📋 Objetivo
Definir estrategias específicas y algoritmos robustos para manejar casos especiales, situaciones edge, y escenarios de error que pueden ocurrir durante el proceso de separación de datos con plantillas Excel.

### 🎯 Casos Especiales Identificados

#### **1. Manejo de Valores Nulos en Columna de Separación**

**Caso**: La columna de separación contiene valores `NaN`, `None`, o celdas vacías.

**Algoritmo**: `NullValueHandlingAlgorithm`

```python
class NullValueHandlingStrategy:
    def __init__(self):
        self.null_strategies = {
            'group_together': 'Agrupar todos los nulos en un archivo',
            'separate_file': 'Crear archivo separado para nulos',
            'exclude': 'Excluir filas con nulos de la exportación',
            'custom_value': 'Reemplazar con valor personalizado'
        }
    
    def handle_null_values_in_separator(self, df: pd.DataFrame, 
                                       separator_column: str,
                                       strategy: str = 'group_together',
                                       custom_value: str = 'N/A') -> Dict[str, pd.DataFrame]:
        """
        Manejar valores nulos en columna de separación
        
        Args:
            df: DataFrame original
            separator_column: Columna que contiene valores nulos
            strategy: Estrategia a aplicar
            custom_value: Valor personalizado para reemplazar nulos
        
        Returns:
            Dict con grupos resultantes
        """
        
        # Detectar valores nulos
        null_mask = df[separator_column].isnull() | (df[separator_column] == '') | (df[separator_column] == 'nan')
        
        if not null_mask.any():
            # No hay nulos, proceder normalmente
            return {'normal_grouping': df}
        
        if strategy == 'group_together':
            # Crear un grupo especial para todos los nulos
            result = {}
            result['Valores_Nulos'] = df[null_mask].copy()
            result['Valores_Nulos'][separator_column] = 'N/A'
            
            # Resto de datos sin nulos
            normal_data = df[~null_mask].copy()
            if not normal_data.empty:
                # Agrupar normalmente
                grouped_normal = normal_data.groupby(separator_column)
                for name, group in grouped_normal:
                    group_copy = group.copy()
                    group_copy[separator_column] = name
                    result[f'Grupo_{name}'] = group_copy
            
            return result
            
        elif strategy == 'separate_file':
            # Los nulos van a un archivo separado
            result = {}
            result['Con_Valores'] = df[~null_mask].copy()
            result['Sin_Valores'] = df[null_mask].copy()
            return result
            
        elif strategy == 'exclude':
            # Excluir filas con nulos
            result = {}
            result['Datos_Validos'] = df[~null_mask].copy()
            result['Filas_Excluidas'] = df[null_mask].copy()
            return result
            
        elif strategy == 'custom_value':
            # Reemplazar nulos con valor personalizado
            df_replaced = df.copy()
            df_replaced[separator_column] = df_replaced[separator_column].fillna(custom_value)
            
            # Agrupar con valores reemplazados
            result = {}
            grouped = df_replaced.groupby(separator_column)
            for name, group in grouped:
                result[f'Grupo_{name}'] = group.copy()
            
            return result

def detect_null_patterns(series: pd.Series) -> Dict[str, Any]:
    """Detectar patrones de valores nulos en la serie"""
    total_rows = len(series)
    null_count = series.isnull().sum()
    empty_string_count = (series == '').sum()
    whitespace_count = series.str.strip().eq('').sum() if series.dtype == 'object' else 0
    nan_string_count = (series.astype(str).str.lower().eq('nan')).sum()
    
    patterns = {
        'total_rows': total_rows,
        'null_count': null_count,
        'empty_strings': empty_string_count,
        'whitespace_only': whitespace_count,
        'nan_strings': nan_string_count,
        'total_null_like': null_count + empty_string_count + whitespace_count + nan_string_count,
        'null_percentage': (null_count / total_rows) * 100 if total_rows > 0 else 0
    }
    
    return patterns
```

#### **2. Resolución de Nombres de Archivos Duplicados**

**Caso**: El proceso genera nombres de archivo idénticos (mismo valor de columna, collisions de templates).

**Algoritmo**: `FilenameConflictResolutionAlgorithm`

```python
class FilenameConflictResolver:
    def __init__(self):
        self.resolution_strategies = {
            'auto_number': 'Agregar números secuenciales (01, 02, 03...)',
            'timestamp': 'Agregar timestamp',
            'sequential_counter': 'Contador incremental global',
            'hash_suffix': 'Hash corto del contenido',
            'user_choice': 'Preguntar al usuario'
        }
    
    def resolve_filename_conflicts(self, target_filenames: List[str], 
                                  strategy: str = 'auto_number',
                                  existing_files: Set[str] = None) -> List[str]:
        """
        Resolver conflictos de nombres de archivo
        
        Args:
            target_filenames: Lista de nombres deseados
            strategy: Estrategia de resolución
            existing_files: Archivos ya existentes en destino
        
        Returns:
            Lista de nombres únicos
        """
        if existing_files is None:
            existing_files = set()
        
        resolved_names = []
        name_counter = {}
        
        for filename in target_filenames:
            # Verificar si el nombre ya existe
            if filename not in existing_files and filename not in resolved_names:
                resolved_names.append(filename)
                name_counter[filename] = 1
                continue
            
            # Resolver conflicto
            resolved_name = self._resolve_single_conflict(
                filename, resolved_names, existing_files, strategy
            )
            resolved_names.append(resolved_name)
            name_counter[resolved_name] = 1
        
        return resolved_names
    
    def _resolve_single_conflict(self, original_name: str, 
                                used_names: List[str], 
                                existing_files: Set[str], 
                                strategy: str) -> str:
        """Resolver un solo conflicto de nombre"""
        
        if strategy == 'auto_number':
            # Agregar número secuencial antes de la extensión
            name_part, ext = os.path.splitext(original_name)
            counter = 1
            
            while True:
                new_name = f"{name_part}_{counter:02d}{ext}"
                if new_name not in used_names and new_name not in existing_files:
                    return new_name
                counter += 1
                
                # Límite de seguridad
                if counter > 999:
                    # Fallback a timestamp
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    return f"{name_part}_{timestamp}{ext}"
        
        elif strategy == 'timestamp':
            # Agregar timestamp
            name_part, ext = os.path.splitext(original_name)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            return f"{name_part}_{timestamp}{ext}"
        
        elif strategy == 'hash_suffix':
            # Agregar hash corto del contenido
            name_part, ext = os.path.splitext(original_name)
            content_hash = self._generate_short_hash()
            return f"{name_part}_{content_hash}{ext}"
        
        elif strategy == 'sequential_counter':
            # Contador incremental global
            base_name = original_name
            if base_name not in existing_files:
                return base_name
            
            counter = 1
            while True:
                new_name = f"{base_name}_{counter}"
                if new_name not in existing_files and new_name not in used_names:
                    return new_name
                counter += 1
        
        return original_name  # Fallback
    
    def _generate_short_hash(self, length: int = 6) -> str:
        """Generar hash corto para nombres de archivo"""
        import hashlib
        import time
        timestamp = str(int(time.time() * 1000000))  # microsecond precision
        content = f"{timestamp}_{random.randint(1000, 9999)}"
        hash_obj = hashlib.md5(content.encode())
        return hash_obj.hexdigest()[:length]
```

#### **3. Manejo de Plantillas Excel Corruptas o Inexistentes**

**Caso**: El archivo de plantilla no existe, está corrupto, o no es un Excel válido.

**Algoritmo**: `TemplateValidationAndRecoveryAlgorithm`

```python
class TemplateValidationAndRecovery:
    def __init__(self):
        self.template_errors = {
            'file_not_found': 'Archivo de plantilla no encontrado',
            'invalid_format': 'Archivo no es un Excel válido',
            'corrupt_file': 'Archivo corrupto o ilegible',
            'locked_file': 'Archivo bloqueado por otro proceso',
            'insufficient_permissions': 'Permisos insuficientes para leer archivo',
            'version_incompatible': 'Versión de Excel no compatible'
        }
    
    def validate_and_recover_template(self, template_path: str) -> TemplateValidationResult:
        """
        Validar plantilla Excel y sugerir recovery
        
        Args:
            template_path: Ruta al archivo de plantilla
        
        Returns:
            TemplateValidationResult con resultado de validación
        """
        result = TemplateValidationResult()
        result.template_path = template_path
        
        # FASE 1: Verificación básica de archivo
        basic_check = self._basic_file_check(template_path)
        if not basic_check.is_valid:
            result.merge(basic_check)
            return result
        
        # FASE 2: Validación de formato Excel
        excel_check = self._validate_excel_format(template_path)
        if not excel_check.is_valid:
            result.merge(excel_check)
            return result
        
        # FASE 3: Verificación de integridad
        integrity_check = self._check_excel_integrity(template_path)
        if not integrity_check.is_valid:
            result.merge(integrity_check)
            return result
        
        # FASE 4: Análisis de contenido
        content_analysis = self._analyze_template_content(template_path)
        result.content_analysis = content_analysis
        
        # Si todo está bien
        result.is_valid = True
        result.recovery_suggestions = []
        
        return result
    
    def _basic_file_check(self, template_path: str) -> ValidationResult:
        """Verificación básica de existencia y permisos"""
        result = ValidationResult()
        
        # Verificar existencia
        if not os.path.exists(template_path):
            result.add_error(f"Archivo no encontrado: {template_path}")
            result.recovery_suggestions.append("Verificar que la ruta del archivo sea correcta")
            result.recovery_suggestions.append("Asegurarse de que el archivo no haya sido movido o eliminado")
            return result
        
        # Verificar que es un archivo (no directorio)
        if not os.path.isfile(template_path):
            result.add_error(f"La ruta no es un archivo: {template_path}")
            return result
        
        # Verificar permisos de lectura
        if not os.access(template_path, os.R_OK):
            result.add_error(f"Sin permisos de lectura: {template_path}")
            result.recovery_suggestions.append("Verificar permisos del archivo")
            result.recovery_suggestions.append("Ejecutar como administrador si es necesario")
            return result
        
        # Verificar tamaño razonable
        try:
            file_size = os.path.getsize(template_path)
            if file_size == 0:
                result.add_error("Archivo de plantilla está vacío")
                result.recovery_suggestions.append("Seleccionar un archivo Excel válido con contenido")
                return result
            elif file_size > 100 * 1024 * 1024:  # 100MB
                result.add_warning(f"Archivo muy grande ({file_size / 1024 / 1024:.1f}MB)")
                result.recovery_suggestions.append("Considerar usar una plantilla más pequeña")
        except Exception as e:
            result.add_error(f"Error al verificar archivo: {str(e)}")
            return result
        
        return result
    
    def _validate_excel_format(self, template_path: str) -> ValidationResult:
        """Validar que el archivo es un Excel válido"""
        result = ValidationResult()
        
        try:
            # Intentar cargar con openpyxl
            workbook = openpyxl.load_workbook(template_path, data_only=False)
            workbook.close()
            
            # Verificar extensión
            _, ext = os.path.splitext(template_path)
            if ext.lower() not in ['.xlsx', '.xlsm']:
                result.add_warning(f"Extensión inesperada: {ext}")
            
            return result
            
        except openpyxl.utils.exceptions.InvalidFileException:
            result.add_error("Archivo no es un Excel válido (.xlsx/.xlsm)")
            result.recovery_suggestions.append("Convertir archivo a formato .xlsx")
            result.recovery_suggestions.append("Usar Excel para re-guardar el archivo")
            
        except openpyxl.utils.exceptions.ReadOnlyWorkbookException:
            result.add_error("Archivo Excel está en modo solo lectura")
            result.recovery_suggestions.append("Cerrar el archivo en Excel si está abierto")
            result.recovery_suggestions.append("Verificar que el archivo no esté bloqueado")
            
        except Exception as e:
            result.add_error(f"Error al leer archivo Excel: {str(e)}")
            result.recovery_suggestions.append("Intentar abrir y re-guardar el archivo en Excel")
        
        return result
    
    def suggest_default_template(self, template_path: str) -> Optional[str]:
        """Sugerir plantilla por defecto en caso de error"""
        default_templates = {
            'reporte_ventas.xlsx': self._create_default_sales_template,
            'reporte_financiero.xlsx': self._create_default_financial_template,
            'datos_experimentales.xlsx': self._create_default_scientific_template
        }
        
        # Crear plantilla por defecto en directorio temporal
        temp_dir = tempfile.gettempdir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for template_name, creator_func in default_templates.items():
            try:
                template_path = os.path.join(temp_dir, f"default_{template_name}")
                creator_func(template_path)
                return template_path
            except Exception as e:
                print(f"Error creando plantilla por defecto {template_name}: {e}")
                continue
        
        return None
    
    def _create_default_sales_template(self, file_path: str):
        """Crear plantilla por defecto para reportes de ventas"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Ventas"
        
        # Encabezados típicos de ventas
        headers = ['Fecha', 'Región', 'Vendedor', 'Producto', 'Cantidad', 'Precio Unitario', 'Total', 'Comisión']
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)
            ws.cell(row=1, column=col).font = openpyxl.styles.Font(bold=True)
            ws.cell(row=1, column=col).fill = openpyxl.styles.PatternFill(
                start_color="CCCCCC", end_color="CCCCCC", fill_type="solid"
            )
        
        # Agregar algunas filas de ejemplo
        for row in range(2, 12):
            ws.cell(row=row, column=1, value=f"2024-01-{row-1:02d}")
            ws.cell(row=row, column=5, value=100 + row * 10)
            ws.cell(row=row, column=6, value=25.50 + row * 2)
            ws.cell(row=row, column=7, value=f"=E{row}*F{row}")
        
        wb.save(file_path)
    
    def _create_default_financial_template(self, file_path: str):
        """Crear plantilla por defecto para reportes financieros"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Financiero"
        
        headers = ['Período', 'Categoría', 'Subcategoría', 'Ingresos', 'Gastos', 'Utilidad', 'Margen %', 'Crecimiento %']
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)
            ws.cell(row=1, column=col).font = openpyxl.styles.Font(bold=True)
            ws.cell(row=1, column=col).fill = openpyxl.styles.PatternFill(
                start_color="E6F3FF", end_color="E6F3FF", fill_type="solid"
            )
        
        wb.save(file_path)
    
    def _create_default_scientific_template(self, file_path: str):
        """Crear plantilla por defecto para datos científicos"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Datos"
        
        headers = ['Experimento', 'Muestra', 'Parámetro', 'Valor', 'Unidad', 'Precisión', 'Fecha Medición', 'Observaciones']
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)
            ws.cell(row=1, column=col).font = openpyxl.styles.Font(bold=True)
            ws.cell(row=1, column=col).fill = openpyxl.styles.PatternFill(
                start_color="F0F8E6", end_color="F0F8E6", fill_type="solid"
            )
        
        wb.save(file_path)
```

#### **4. Conflictos de Mapeo de Columnas**

**Caso**: Mapeo de columnas DataFrame → Excel causa conflictos, columnas sin correspondencia, o tipos incompatibles.

**Algoritmo**: `ColumnMappingConflictResolver`

```python
class ColumnMappingConflictResolver:
    def __init__(self):
        self.conflict_types = {
            'missing_mapping': 'Columna DataFrame sin correspondencia en Excel',
            'duplicate_mapping': 'Múltiples columnas DataFrame mapeadas a misma columna Excel',
            'type_incompatibility': 'Tipo de dato incompatible entre DataFrame y Excel',
            'excel_column_invalid': 'Columna Excel especificada no existe en plantilla',
            'data_overflow': 'Datos no caben en celdas Excel'
        }
    
    def resolve_mapping_conflicts(self, df_columns: List[str],
                                 excel_columns: List[str],
                                 requested_mapping: Dict[str, str]) -> MappingResolutionResult:
        """
        Resolver conflictos en mapeo de columnas
        
        Args:
            df_columns: Columnas del DataFrame
            excel_columns: Columnas disponibles en Excel
            requested_mapping: Mapeo solicitado por usuario
        
        Returns:
            MappingResolutionResult con mapeo resuelto
        """
        result = MappingResolutionResult()
        result.original_mapping = requested_mapping.copy()
        
        # FASE 1: Validación de mapeo solicitado
        validation_errors = self._validate_requested_mapping(
            df_columns, excel_columns, requested_mapping
        )
        result.validation_errors = validation_errors
        
        # FASE 2: Detectar conflictos específicos
        conflicts = self._detect_mapping_conflicts(df_columns, excel_columns, requested_mapping)
        result.conflicts = conflicts
        
        # FASE 3: Resolver conflictos automáticamente
        resolved_mapping = self._auto_resolve_conflicts(
            df_columns, excel_columns, requested_mapping, conflicts
        )
        result.resolved_mapping = resolved_mapping
        
        # FASE 4: Optimización final
        optimized_mapping = self._optimize_mapping_layout(resolved_mapping, excel_columns)
        result.final_mapping = optimized_mapping
        
        result.success = len(result.validation_errors) == 0 or len(result.final_mapping) > 0
        
        return result
    
    def _detect_mapping_conflicts(self, df_columns: List[str],
                                 excel_columns: List[str],
                                 mapping: Dict[str, str]) -> List[MappingConflict]:
        """Detectar conflictos específicos en el mapeo"""
        conflicts = []
        
        # Verificar columnas Excel solicitadas que no existen
        for df_col, excel_col in mapping.items():
            if excel_col not in excel_columns:
                conflict = MappingConflict(
                    type='excel_column_invalid',
                    description=f"Columna Excel '{excel_col}' no existe en plantilla",
                    affected_columns=[df_col],
                    severity='error'
                )
                conflicts.append(conflict)
        
        # Verificar mapeos duplicados
        excel_col_usage = {}
        for df_col, excel_col in mapping.items():
            if excel_col not in excel_col_usage:
                excel_col_usage[excel_col] = []
            excel_col_usage[excel_col].append(df_col)
        
        for excel_col, df_cols in excel_col_usage.items():
            if len(df_cols) > 1:
                conflict = MappingConflict(
                    type='duplicate_mapping',
                    description=f"Múltiples columnas mapeadas a '{excel_col}': {', '.join(df_cols)}",
                    affected_columns=df_cols,
                    severity='error'
                )
                conflicts.append(conflict)
        
        # Verificar columnas DataFrame sin mapear
        mapped_df_cols = set(mapping.keys())
        unmapped_df_cols = set(df_columns) - mapped_df_cols
        
        if unmapped_df_cols:
            conflict = MappingConflict(
                type='missing_mapping',
                description=f"Columnas DataFrame sin mapear: {', '.join(unmapped_df_cols)}",
                affected_columns=list(unmapped_df_cols),
                severity='warning'
            )
            conflicts.append(conflict)
        
        return conflicts
    
    def _auto_resolve_conflicts(self, df_columns: List[str],
                               excel_columns: List[str],
                               mapping: Dict[str, str],
                               conflicts: List[MappingConflict]) -> Dict[str, str]:
        """Resolver conflictos automáticamente"""
        resolved = mapping.copy()
        
        for conflict in conflicts:
            if conflict.type == 'excel_column_invalid':
                # Encontrar columna Excel más similar
                for df_col in conflict.affected_columns:
                    if df_col in resolved:
                        similar_col = self._find_similar_excel_column(
                            df_col, excel_columns, resolved.values()
                        )
                        if similar_col:
                            resolved[df_col] = similar_col
            
            elif conflict.type == 'duplicate_mapping':
                # Reasignar columnas duplicadas
                excel_col_usage = {}
                for df_col, excel_col in resolved.items():
                    if excel_col not in excel_col_usage:
                        excel_col_usage[excel_col] = []
                    excel_col_usage[excel_col].append(df_col)
                
                for excel_col, df_cols in excel_col_usage.items():
                    if len(df_cols) > 1:
                        # Reasignar desde la segunda columna
                        available_cols = [col for col in excel_columns if col not in resolved.values()]
                        for i, df_col in enumerate(df_cols[1:], 1):
                            if available_cols:
                                resolved[df_col] = available_cols.pop(0)
                            else:
                                # Si no hay más columnas, usar índice numérico
                                resolved[df_col] = f"{excel_col}_{i}"
        
        # Completar mapeos faltantes automáticamente
        mapped_cols = set(resolved.keys())
        unmapped_cols = set(df_columns) - mapped_cols
        
        available_excel_cols = [col for col in excel_columns if col not in resolved.values()]
        
        for i, df_col in enumerate(unmapped_cols):
            if i < len(available_excel_cols):
                resolved[df_col] = available_excel_cols[i]
            else:
                # Crear columnas dinámicamente
                resolved[df_col] = self._generate_dynamic_excel_column(i)
        
        return resolved
    
    def _find_similar_excel_column(self, df_col: str,
                                  excel_columns: List[str],
                                  used_columns: List[str]) -> Optional[str]:
        """Encontrar columna Excel similar a columna DataFrame"""
        
        # Priorizar columnas no usadas
        available_cols = [col for col in excel_columns if col not in used_columns]
        
        # Buscar coincidencia exacta (case-insensitive)
        for col in available_cols:
            if col.lower() == df_col.lower():
                return col
        
        # Buscar coincidencia parcial
        for col in available_cols:
            if df_col.lower() in col.lower() or col.lower() in df_col.lower():
                return col
        
        # Buscar por tipo de datos (heurística)
        type_mapping = {
            'fecha': ['A', 'B'],  # Primeras columnas para fechas
            'nombre': ['C', 'D'],  # Columnas medias para nombres
            'total': ['G', 'H'],   # Últimas columnas para totales
            'cantidad': ['E', 'F'], # Columnas centrales para cantidades
            'id': ['A', 'B'],      # Primeras columnas para IDs
            'codigo': ['A', 'B']
        }
        
        for keyword, preferred_cols in type_mapping.items():
            if keyword in df_col.lower():
                for col in preferred_cols:
                    if col in available_cols:
                        return col
        
        # Fallback: primera columna disponible
        return available_cols[0] if available_cols else None
    
    def _generate_dynamic_excel_column(self, index: int) -> str:
        """Generar nombre de columna Excel dinámico"""
        # A, B, C... Z, AA, AB, AC...
        if index < 26:
            return chr(ord('A') + index)
        else:
            first_letter = chr(ord('A') + (index // 26) - 1)
            second_letter = chr(ord('A') + (index % 26))
            return f"{first_letter}{second_letter}"
```

#### **5. Celdas Ocupadas en Plantilla Excel**

**Caso**: La celda inicial especificada o área de datos ya contiene información en la plantilla.

**Algoritmo**: `ExcelCellOccupancyHandler`

```python
class ExcelCellOccupancyHandler:
    def __init__(self):
        self.occupancy_strategies = {
            'overwrite': 'Sobrescribir contenido existente',
            'insert_shift': 'Insertar desplazando celdas existentes',
            'find_next_empty': 'Buscar siguiente celda vacía',
            'new_sheet': 'Crear nueva hoja para datos',
            'ask_user': 'Preguntar al usuario'
        }
    
    def handle_cell_occupancy(self, workbook_path: str, 
                            start_cell: str,
                            data_shape: tuple,
                            strategy: str = 'overwrite') -> CellOccupancyResult:
        """
        Manejar ocupación de celdas en plantilla Excel
        
        Args:
            workbook_path: Ruta al archivo Excel
            start_cell: Celda inicial (ej: 'A5')
            data_shape: Forma de los datos (filas, columnas)
            strategy: Estrategia para manejar ocupación
        
        Returns:
            CellOccupancyResult con resultado y celda final
        """
        result = CellOccupancyResult()
        
        try:
            workbook = openpyxl.load_workbook(workbook_path)
            sheet = workbook.active
            
            # Analizar ocupación actual
            occupancy_analysis = self._analyze_cell_occupancy(sheet, start_cell, data_shape)
            result.occupancy_analysis = occupancy_analysis
            
            if not occupancy_analysis.has_occupied_cells:
                # No hay ocupación, usar celda original
                result.final_start_cell = start_cell
                result.strategy_used = 'no_occupancy'
                result.success = True
                return result
            
            # Aplicar estrategia seleccionada
            if strategy == 'overwrite':
                result = self._handle_overwrite_strategy(sheet, occupancy_analysis, result)
            elif strategy == 'insert_shift':
                result = self._handle_insert_shift_strategy(sheet, occupancy_analysis, result)
            elif strategy == 'find_next_empty':
                result = self._handle_find_empty_strategy(sheet, start_cell, data_shape, result)
            elif strategy == 'new_sheet':
                result = self._handle_new_sheet_strategy(workbook, data_shape, result)
            elif strategy == 'ask_user':
                result = self._handle_user_choice_strategy(occupancy_analysis, result)
            
            workbook.close()
            return result
            
        except Exception as e:
            result.success = False
            result.error = f"Error manejando ocupación de celdas: {str(e)}"
            return result
    
    def _analyze_cell_occupancy(self, sheet: Worksheet, start_cell: str, 
                               data_shape: tuple) -> OccupancyAnalysis:
        """Analizar ocupación de celdas en área de datos"""
        analysis = OccupancyAnalysis()
        
        start_row, start_col = self._cell_coordinates_to_indices(start_cell)
        data_rows, data_cols = data_shape
        
        # Verificar área de datos
        occupied_cells = []
        for row_offset in range(data_rows):
            for col_offset in range(data_cols):
                cell_row = start_row + row_offset
                cell_col = start_col + col_offset
                cell = sheet.cell(row=cell_row, column=cell_col)
                
                if cell.value is not None and cell.value != '':
                    occupied_cells.append({
                        'row': cell_row,
                        'col': cell_col,
                        'coord': f"{openpyxl.utils.get_column_letter(cell_col)}{cell_row}",
                        'value': str(cell.value)[:50],  # Primeros 50 chars
                        'format': {
                            'font': str(cell.font),
                            'fill': str(cell.fill),
                            'border': str(cell.border)
                        }
                    })
        
        analysis.has_occupied_cells = len(occupied_cells) > 0
        analysis.occupied_cells = occupied_cells
        analysis.total_occupied = len(occupied_cells)
        analysis.occupancy_percentage = (len(occupied_cells) / (data_rows * data_cols)) * 100
        
        return analysis
    
    def _handle_overwrite_strategy(self, sheet: Worksheet, 
                                  analysis: OccupancyAnalysis, 
                                  result: CellOccupancyResult) -> CellOccupancyResult:
        """Manejar sobrescritura de contenido existente"""
        result.strategy_used = 'overwrite'
        result.warning = f"Se sobrescribirán {analysis.total_occupied} celdas existentes"
        
        # Crear backup del contenido original
        backup_content = []
        for cell_info in analysis.occupied_cells:
            backup_content.append({
                'coord': cell_info['coord'],
                'original_value': cell_info['value'],
                'original_format': cell_info['format']
            })
        
        result.backup_content = backup_content
        result.success = True
        result.final_start_cell = result.occupancy_analysis.start_cell
        
        return result
    
    def _handle_find_empty_strategy(self, sheet: Worksheet, start_cell: str,
                                   data_shape: tuple, 
                                   result: CellOccupancyResult) -> CellOccupancyResult:
        """Buscar siguiente área vacía"""
        result.strategy_used = 'find_next_empty'
        
        start_row, start_col = self._cell_coordinates_to_indices(start_cell)
        max_rows, max_cols = sheet.max_row, sheet.max_column
        
        # Buscar área vacía hacia abajo
        for search_row in range(start_row, max_rows + 1):
            for search_col in range(start_col, max_cols + 1):
                # Verificar si el área está vacía
                if self._is_area_empty(sheet, search_row, search_col, data_shape):
                    new_start_cell = openpyxl.utils.get_column_letter(search_col) + str(search_row)
                    result.final_start_cell = new_start_cell
                    result.success = True
                    return result
        
        # Si no se encuentra área vacía, sugerir nueva hoja
        result.warning = "No se encontró área vacía suficiente, considere usar estrategia 'new_sheet'"
        result.success = False
        
        return result
    
    def _is_area_empty(self, sheet: Worksheet, start_row: int, start_col: int, 
                      data_shape: tuple) -> bool:
        """Verificar si un área está completamente vacía"""
        data_rows, data_cols = data_shape
        
        for row_offset in range(data_rows):
            for col_offset in range(data_cols):
                cell = sheet.cell(row=start_row + row_offset, column=start_col + col_offset)
                if cell.value is not None and cell.value != '':
                    return False
        
        return True
    
    def _cell_coordinates_to_indices(self, cell_coord: str) -> tuple:
        """Convertir coordenada de celda (A1) a índices (1, 1)"""
        from openpyxl.utils import column_index_from_string, coordinate_to_tuple
        row, col = coordinate_to_tuple(cell_coord)
        return row, col
    
    def _handle_new_sheet_strategy(self, workbook: Workbook, 
                                  data_shape: tuple, 
                                  result: CellOccupancyResult) -> CellOccupancyResult:
        """Crear nueva hoja para los datos"""
        result.strategy_used = 'new_sheet'
        
        # Crear nueva hoja con nombre único
        sheet_names = [sheet.title for sheet in workbook.worksheets]
        new_sheet_name = self._generate_unique_sheet_name(sheet_names)
        
        new_sheet = workbook.create_sheet(title=new_sheet_name)
        result.new_sheet_name = new_sheet_name
        result.final_start_cell = 'A1'  # Usar A1 en nueva hoja
        result.success = True
        
        return result
    
    def _generate_unique_sheet_name(self, existing_names: List[str]) -> str:
        """Generar nombre único para nueva hoja"""
        base_name = "Datos_Separados"
        if base_name not in existing_names:
            return base_name
        
        counter = 1
        while True:
            new_name = f"{base_name}_{counter}"
            if new_name not in existing_names:
                return new_name
            counter += 1
```

### 🔧 Algoritmos de Recovery y Continuidad

#### **6. Algoritmo de Recovery por Fallas Parciales**

**Nombre**: `PartialFailureRecoveryAlgorithm`

**Propósito**: Continuar exportación después de fallas parciales en grupos individuales.

```python
class PartialFailureRecovery:
    def __init__(self, output_directory: str):
        self.output_directory = output_directory
        self.progress_file = os.path.join(output_directory, ".export_progress.json")
        self.completed_groups = set()
        self.failed_groups = {}
        self.temporary_files = []
    
    def execute_with_partial_recovery(self, export_function: Callable,
                                    groups_data: List[GroupData]) -> ExportResult:
        """
        Ejecutar exportación con recovery de fallas parciales
        
        Args:
            export_function: Función para exportar un grupo
            groups_data: Lista de grupos a procesar
        
        Returns:
            ExportResult con resumen completo
        """
        
        # FASE 1: Cargar progreso previo si existe
        previous_progress = self._load_previous_progress()
        
        # FASE 2: Filtrar grupos ya completados
        remaining_groups = [
            group for group in groups_data 
            if group.name not in previous_progress.completed_groups
        ]
        
        if not remaining_groups:
            # Todo ya está completado
            return self._generate_completion_result(previous_progress)
        
        # FASE 3: Procesar grupos restantes
        all_results = []
        all_results.extend(previous_progress.successful_exports)
        all_results.extend(previous_progress.failed_exports)
        
        for group in remaining_groups:
            try:
                # Verificar si operación fue cancelada
                if self._operation_cancelled():
                    break
                
                # Exportar grupo individual
                group_result = export_function(group)
                all_results.append(group_result)
                
                if group_result.success:
                    self.completed_groups.add(group.name)
                else:
                    self.failed_groups[group.name] = group_result.error
                
                # Guardar progreso
                self._save_progress(all_results)
                
                # Callback de progreso
                if hasattr(export_function, 'progress_callback'):
                    export_function.progress_callback(len(all_results), len(groups_data))
                    
            except Exception as e:
                error_result = ExportResult(
                    success=False,
                    group_name=group.name,
                    error=f"Error crítico en grupo {group.name}: {str(e)}"
                )
                all_results.append(error_result)
                self.failed_groups[group.name] = str(e)
        
        # FASE 4: Generar resultado final
        return self._generate_final_result(all_results)
    
    def _save_progress(self, results: List[ExportResult]):
        """Guardar progreso actual en archivo"""
        progress_data = {
            'timestamp': datetime.now().isoformat(),
            'completed_groups': list(self.completed_groups),
            'failed_groups': self.failed_groups,
            'successful_exports': [
                {
                    'group_name': r.group_name,
                    'file_path': r.file_path,
                    'rows_processed': r.rows_processed,
                    'timestamp': r.timestamp.isoformat() if r.timestamp else None
                }
                for r in results if r.success
            ],
            'failed_exports': [
                {
                    'group_name': r.group_name,
                    'error': r.error,
                    'timestamp': r.timestamp.isoformat() if r.timestamp else None
                }
                for r in results if not r.success
            ]
        }
        
        with open(self.progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)
    
    def _load_previous_progress(self) -> ExportProgress:
        """Cargar progreso previo"""
        if not os.path.exists(self.progress_file):
            return ExportProgress()
        
        try:
            with open(self.progress_file, 'r') as f:
                data = json.load(f)
            
            progress = ExportProgress()
            progress.completed_groups = set(data.get('completed_groups', []))
            progress.failed_groups = data.get('failed_groups', {})
            
            # Reconstruir resultados
            for success_data in data.get('successful_exports', []):
                result = ExportResult(
                    success=True,
                    group_name=success_data['group_name'],
                    file_path=success_data['file_path'],
                    rows_processed=success_data['rows_processed']
                )
                progress.successful_exports.append(result)
            
            for failure_data in data.get('failed_exports', []):
                result = ExportResult(
                    success=False,
                    group_name=failure_data['group_name'],
                    error=failure_data['error']
                )
                progress.failed_exports.append(result)
            
            return progress
            
        except Exception as e:
            print(f"Error cargando progreso previo: {e}")
            return ExportProgress()
    
    def cleanup_progress_file(self):
        """Limpiar archivo de progreso después de completarse exitosamente"""
        if os.path.exists(self.progress_file):
            os.remove(self.progress_file)
```

### 📊 Métricas y Monitoreo de Casos Especiales

#### **Métricas de Éxito para Casos Especiales**

| Caso Especial | Métrica de Éxito | Target |
|---------------|------------------|--------|
| **Valores Nulos** | Porcentaje de grupos con nulos procesados correctamente | > 98% |
| **Nombres Duplicados** | Resolución automática sin intervención manual | > 95% |
| **Plantillas Corruptas** | Recovery automático con plantilla por defecto | > 90% |
| **Conflictos de Mapeo** | Resolución automática de mapeos | > 95% |
| **Celdas Ocupadas** | Detección y resolución correcta | > 98% |
| **Fallas Parciales** | Recovery exitoso de exports parciales | > 95% |

#### **Logging y Auditoría de Casos Especiales**

```python
class SpecialCaseLogger:
    def __init__(self, log_file: str):
        self.log_file = log_file
        self.logger = self._setup_logger()
    
    def log_null_handling(self, column_name: str, null_count: int, strategy: str):
        """Log de manejo de valores nulos"""
        self.logger.info(f"Null handling | Column: {column_name} | Nulls: {null_count} | Strategy: {strategy}")
    
    def log_filename_conflict(self, original_name: str, resolved_name: str, strategy: str):
        """Log de resolución de conflictos de nombres"""
        self.logger.info(f"Filename conflict | Original: {original_name} | Resolved: {resolved_name} | Strategy: {strategy}")
    
    def log_template_error(self, template_path: str, error_type: str, recovery_action: str):
        """Log de errores de plantilla"""
        self.logger.warning(f"Template error | Path: {template_path} | Error: {error_type} | Recovery: {recovery_action}")
    
    def log_mapping_conflict(self, conflict_type: str, affected_columns: List[str], resolution: str):
        """Log de conflictos de mapeo"""
        self.logger.info(f"Mapping conflict | Type: {conflict_type} | Columns: {affected_columns} | Resolution: {resolution}")
    
    def log_occupancy_resolution(self, start_cell: str, final_cell: str, strategy: str):
        """Log de resolución de ocupación de celdas"""
        self.logger.info(f"Cell occupancy | Start: {start_cell} | Final: {final_cell} | Strategy: {strategy}")
    
    def _setup_logger(self):
        """Configurar logger para casos especiales"""
        import logging
        
        logger = logging.getLogger('special_cases')
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
```

### 🚨 Alertas y Escalación

#### **Sistema de Alertas para Casos Críticos**

```python
class SpecialCaseAlertSystem:
    def __init__(self):
        self.alert_thresholds = {
            'null_percentage': 50,  # Alert si > 50% de valores son nulos
            'conflict_rate': 30,    # Alert si > 30% de nombres tienen conflictos
            'template_error_rate': 10,  # Alert si > 10% de plantillas fallan
            'mapping_conflict_rate': 25,  # Alert si > 25% de mapeos tienen conflictos
            'occupancy_rate': 80    # Alert si > 80% de celdas están ocupadas
        }
    
    def check_alert_conditions(self, analysis_results: Dict[str, Any]) -> List[Alert]:
        """Verificar condiciones de alerta"""
        alerts = []
        
        # Verificar porcentaje de nulos
        null_percentage = analysis_results.get('null_percentage', 0)
        if null_percentage > self.alert_thresholds['null_percentage']:
            alerts.append(Alert(
                level='warning',
                type='high_null_percentage',
                message=f"Alto porcentaje de valores nulos: {null_percentage:.1f}%",
                recommendation="Considerar limpiar datos o cambiar estrategia de separación"
            ))
        
        # Verificar tasa de conflictos de nombres
        conflict_rate = analysis_results.get('filename_conflict_rate', 0)
        if conflict_rate > self.alert_thresholds['conflict_rate']:
            alerts.append(Alert(
                level='warning',
                type='high_conflict_rate',
                message=f"Alta tasa de conflictos de nombres: {conflict_rate:.1f}%",
                recommendation="Revisar plantilla de nombres o ajustar estrategia de resolución"
            ))
        
        # Verificar errores de plantilla
        template_error_rate = analysis_results.get('template_error_rate', 0)
        if template_error_rate > self.alert_thresholds['template_error_rate']:
            alerts.append(Alert(
                level='critical',
                type='high_template_error_rate',
                message=f"Alta tasa de errores de plantilla: {template_error_rate:.1f}%",
                recommendation="Verificar integridad de archivos de plantilla"
            ))
        
        return alerts
```

### ✅ Criterios de Validación para Casos Especiales

#### **Testing de Casos Especiales**

1. **Unit Tests Específicos**:
   - ✅ Manejo de nulos con todas las estrategias
   - ✅ Resolución de conflictos de nombres con diferentes escenarios
   - ✅ Validación de plantillas corruptas y recovery
   - ✅ Conflictos de mapeo con múltiples configuraciones
   - ✅ Ocupación de celdas con diferentes patrones

2. **Integration Tests**:
   - ✅ Casos especiales funcionando con algoritmos principales
   - ✅ Recovery completo después de fallas parciales
   - ✅ Logging y auditoría funcionando correctamente

3. **Performance Tests**:
   - ✅ Tiempo de resolución de casos especiales < 30% del tiempo total
   - ✅ Memory overhead de casos especiales < 100MB
   - ✅ Escalabilidad con aumento en casos especiales

4. **User Experience Tests**:
   - ✅ Mensajes de error claros y accionables
   - ✅ Recovery automático sin intervención manual en > 95% casos
   - ✅ Tiempo de respuesta para decisiones de usuario < 2 segundos

---

**CONCLUSIÓN**: El manejo sistemático de casos especiales proporciona robustez y confiabilidad al sistema de separación de datos, asegurando que la funcionalidad sea usable en escenarios reales con datos imperfectos y configuraciones variables. Los algoritmos de recovery y resolución automática minimizan la necesidad de intervención manual y mejoran significativamente la experiencia del usuario.