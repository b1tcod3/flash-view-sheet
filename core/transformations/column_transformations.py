"""
Transformaciones específicas para operaciones de columnas
Incluye renombrado, creación, aplicación de funciones y eliminación
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union, Callable
import re
import logging
from datetime import datetime

from .base_transformation import BaseTransformation

# Configurar logging
logger = logging.getLogger(__name__)


class ColumnTransformation(BaseTransformation):
    """
    Clase base para transformaciones de columnas específicas
    """
    
    def __init__(self, name: str, description: str, columns: Union[str, List[str]]):
        """
        Inicializar transformación de columnas
        
        Args:
            name: Nombre de la transformación
            description: Descripción de la transformación
            columns: Columna o lista de columnas a transformar
        """
        super().__init__(name, description)
        self.columns = [columns] if isinstance(columns, str) else columns
        
    def validate_data(self, df: pd.DataFrame) -> bool:
        """Validar que las columnas existan en el DataFrame"""
        super().validate_data(df)
        
        missing_columns = [col for col in self.columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Columnas no encontradas en el DataFrame: {missing_columns}")
        
        return True


class RenameColumnsTransformation(ColumnTransformation):
    """
    Transformación para renombrar columnas
    """
    
    def __init__(self, column_mapping: Dict[str, str]):
        """
        Inicializar renombrado de columnas
        
        Args:
            column_mapping: Diccionario {columna_original: columna_nueva}
        """
        self.column_mapping = column_mapping
        columns = list(column_mapping.keys())
        description = f"Renombrar {len(columns)} columnas"
        
        super().__init__("rename_columns", description, columns)
        
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar renombrado de columnas"""
        if parameters is None:
            parameters = {}
            
        # Usar mapping de parámetros o el interno
        mapping = parameters.get('column_mapping', self.column_mapping)
        
        try:
            df_renamed = df.copy()
            
            # Renombrar columnas una por una con validación
            for old_name, new_name in mapping.items():
                if old_name not in df_renamed.columns:
                    raise ValueError(f"Columna '{old_name}' no existe en el DataFrame")
                
                if new_name in df_renamed.columns and new_name != old_name:
                    raise ValueError(f"Ya existe una columna con el nombre '{new_name}'")
                
                logger.info(f"Renombrando columna '{old_name}' a '{new_name}'")
                df_renamed = df_renamed.rename(columns={old_name: new_name})
            
            return df_renamed
            
        except Exception as e:
            logger.error(f"Error en renombrado de columnas: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de renombrado"""
        if 'column_mapping' not in parameters:
            return False
            
        mapping = parameters['column_mapping']
        
        if not isinstance(mapping, dict) or not mapping:
            return False
            
        # Verificar que no haya nombres duplicados
        new_names = list(mapping.values())
        if len(new_names) != len(set(new_names)):
            return False
            
        return True


class CreateCalculatedColumnTransformation(ColumnTransformation):
    """
    Transformación para crear columnas calculadas usando fórmulas o funciones
    """
    
    def __init__(self, target_column: str, formula: str = None, function: Callable = None, 
                 function_args: Dict[str, Any] = None, source_columns: List[str] = None):
        """
        Inicializar creación de columna calculada
        
        Args:
            target_column: Nombre de la nueva columna
            formula: Fórmula string (ej: "col1 + col2", "col1 * 2")
            function: Función personalizada a aplicar
            function_args: Argumentos para la función
            source_columns: Columnas fuente para la función
        """
        self.target_column = target_column
        self.formula = formula
        self.function = function
        self.function_args = function_args or {}
        self.source_columns = source_columns or []
        
        if formula:
            description = f"Crear columna '{target_column}' con fórmula: {formula}"
        else:
            description = f"Crear columna '{target_column}' con función personalizada"
            
        super().__init__("create_calculated_column", description, source_columns)
        
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar creación de columna calculada"""
        if parameters is None:
            parameters = {}
            
        try:
            df_new = df.copy()
            target_col = parameters.get('target_column', self.target_column)
            
            # Verificar que la columna objetivo no exista
            if target_col in df_new.columns:
                raise ValueError(f"Ya existe una columna con el nombre '{target_col}'")
            
            if self.formula:
                # Ejecutar fórmula
                df_new = self._execute_formula(df_new, target_col, self.formula, parameters)
            elif self.function:
                # Ejecutar función personalizada
                df_new = self._execute_function(df_new, target_col, self.function, 
                                              self.source_columns, self.function_args, parameters)
            else:
                raise ValueError("Debe especificar una fórmula o función")
            
            logger.info(f"Columna calculada '{target_col}' creada exitosamente")
            return df_new
            
        except Exception as e:
            logger.error(f"Error al crear columna calculada: {str(e)}")
            raise
    
    def _execute_formula(self, df: pd.DataFrame, target_col: str, formula: str, 
                        parameters: Dict[str, Any]) -> pd.DataFrame:
        """Ejecutar fórmula string de forma segura"""
        # Obtener fórmula de parámetros o usar la interna
        formula_str = parameters.get('formula', formula)
        
        # Validar que la fórmula solo contenga operaciones seguras
        allowed_chars = re.compile(r'^[0-9+\-*/().\s\w_]*$')
        if not allowed_chars.match(formula_str):
            raise ValueError("Fórmula contiene caracteres no permitidos")
        
        # Reemplazar nombres de columnas en el DataFrame
        for col in df.columns:
            safe_col_name = col.replace(' ', '_').replace('-', '_')
            formula_str = re.sub(r'\b' + re.escape(col) + r'\b', 
                               f'df["{col}"]', formula_str)
        
        # Evaluar de forma segura
        try:
            # Añadir df al contexto local
            local_vars = {'df': df, 'np': np}
            result_series = eval(formula_str, {"__builtins__": {}}, local_vars)
            
            # Si el resultado es un escalar, replicar para toda la columna
            if not hasattr(result_series, '__len__') or len(result_series) != len(df):
                if hasattr(result_series, '__iter__') and not isinstance(result_series, (str, bytes)):
                    result_series = pd.Series(result_series, index=df.index)
                else:
                    result_series = pd.Series([result_series] * len(df), index=df.index)
            
            df[target_col] = result_series
            return df
            
        except Exception as e:
            raise ValueError(f"Error al evaluar fórmula '{formula_str}': {str(e)}")
    
    def _execute_function(self, df: pd.DataFrame, target_col: str, func: Callable,
                         source_columns: List[str], func_args: Dict[str, Any],
                         parameters: Dict[str, Any]) -> pd.DataFrame:
        """Ejecutar función personalizada"""
        # Obtener función y argumentos de parámetros
        function = parameters.get('function', func)
        function_args = parameters.get('function_args', func_args)
        source_cols = parameters.get('source_columns', source_columns)
        
        # Preparar argumentos
        args = []
        if source_cols:
            args = [df[col] for col in source_cols]
        else:
            # Usar todo el DataFrame si no se especifican columnas
            args = [df]
        
        # Ejecutar función
        result = function(*args, **function_args)
        
        # Manejar diferentes tipos de retorno
        if isinstance(result, pd.Series):
            df[target_col] = result
        elif hasattr(result, '__len__') and len(result) == len(df):
            df[target_col] = result
        else:
            # Scalar - replicar
            df[target_col] = result
            
        return df
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de creación de columna"""
        target_col = parameters.get('target_column', self.target_column)
        
        if not target_col or not isinstance(target_col, str):
            return False
            
        if self.formula and 'formula' not in parameters and self.formula is None:
            return False
            
        if self.function and 'function' not in parameters and self.function is None:
            return False
            
        return True


class ApplyFunctionTransformation(ColumnTransformation):
    """
    Transformación para aplicar funciones a columnas existentes
    """
    
    def __init__(self, columns: Union[str, List[str]], function: Callable, 
                 function_args: Dict[str, Any] = None, new_column_name: str = None):
        """
        Inicializar aplicación de función
        
        Args:
            columns: Columna o lista de columnas a transformar
            function: Función a aplicar
            function_args: Argumentos adicionales para la función
            new_column_name: Nombre para la nueva columna (opcional)
        """
        self.function = function
        self.function_args = function_args or {}
        self.new_column_name = new_column_name
        
        columns_list = [columns] if isinstance(columns, str) else columns
        column_desc = ", ".join(columns_list[:3])
        if len(columns_list) > 3:
            column_desc += f" (+{len(columns_list)-3} más)"
            
        description = f"Aplicar función a columnas: {column_desc}"
        
        super().__init__("apply_function", description, columns_list)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar aplicación de función"""
        if parameters is None:
            parameters = {}
            
        try:
            df_transformed = df.copy()
            
            function = parameters.get('function', self.function)
            function_args = parameters.get('function_args', self.function_args)
            new_col_name = parameters.get('new_column_name', self.new_column_name)
            columns = parameters.get('columns', self.columns)
            
            # Aplicar función columna por columna
            for column in columns:
                if column not in df_transformed.columns:
                    raise ValueError(f"Columna '{column}' no existe")
                
                # Preparar argumentos para la función
                args = [df_transformed[column]]
                if len(columns) > 1:  # Multi-column function
                    args = [df_transformed[col] for col in columns]
                    break  # Solo una iteración para funciones multi-columna
                
                try:
                    result = function(*args, **function_args)
                    
                    # Determinar nombre de columna de resultado
                    if new_col_name:
                        result_column = new_col_name
                    else:
                        result_column = f"{column}_transformed"
                    
                    # Manejar diferentes tipos de retorno
                    if isinstance(result, pd.Series):
                        df_transformed[result_column] = result
                    else:
                        df_transformed[result_column] = result
                    
                    logger.info(f"Función aplicada a columna '{column}' -> '{result_column}'")
                    
                except Exception as e:
                    logger.error(f"Error aplicando función a columna '{column}': {str(e)}")
                    raise
            
            return df_transformed
            
        except Exception as e:
            logger.error(f"Error en aplicación de función: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de aplicación de función"""
        if 'function' not in parameters and self.function is None:
            return False
            
        columns = parameters.get('columns', self.columns)
        if not columns:
            return False
            
        return True


class DropColumnsTransformation(ColumnTransformation):
    """
    Transformación para eliminar columnas específicas
    """
    
    def __init__(self, columns: Union[str, List[str]] = None, pattern: str = None):
        """
        Inicializar eliminación de columnas
        
        Args:
            columns: Columna o lista de columnas a eliminar
            pattern: Patrón regex para eliminar columnas por patrón
        """
        self.pattern = pattern
        
        if pattern:
            description = f"Eliminar columnas que coincidan con patrón: {pattern}"
            columns = []  # Se determinarán en tiempo de ejecución
        elif columns:
            columns_list = [columns] if isinstance(columns, str) else columns
            description = f"Eliminar {len(columns_list)} columnas"
        else:
            description = "Eliminar columnas por patrón o lista"
            columns = []
            
        super().__init__("drop_columns", description, columns)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar eliminación de columnas"""
        if parameters is None:
            parameters = {}
            
        try:
            df_cleaned = df.copy()
            
            if self.pattern or parameters.get('pattern'):
                # Eliminar por patrón regex
                pattern_str = parameters.get('pattern', self.pattern)
                columns_to_drop = [col for col in df_cleaned.columns 
                                 if re.search(pattern_str, col)]
            else:
                # Eliminar columnas específicas
                columns_to_drop = parameters.get('columns', self.columns)
            
            if not columns_to_drop:
                logger.warning("No se encontraron columnas para eliminar")
                return df_cleaned
            
            # Validar que las columnas existen
            existing_columns = [col for col in columns_to_drop if col in df_cleaned.columns]
            missing_columns = [col for col in columns_to_drop if col not in df_cleaned.columns]
            
            if missing_columns:
                logger.warning(f"Algunas columnas no existían: {missing_columns}")
            
            if existing_columns:
                df_cleaned = df_cleaned.drop(columns=existing_columns)
                logger.info(f"Eliminadas {len(existing_columns)} columnas: {existing_columns}")
            
            return df_cleaned
            
        except Exception as e:
            logger.error(f"Error al eliminar columnas: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de eliminación"""
        if self.pattern or parameters.get('pattern'):
            return True  # Pattern se valida en tiempo de ejecución
            
        columns = parameters.get('columns', self.columns)
        if not columns:
            return False
            
        return True


# Funciones de utilidad para transformaciones comunes
def create_formula_transformation(column_mapping: Dict[str, str]) -> RenameColumnsTransformation:
    """Crear transformación de renombrado desde diccionario"""
    return RenameColumnsTransformation(column_mapping)


def create_calculated_column(target_column: str, formula: str, 
                           source_columns: List[str] = None) -> CreateCalculatedColumnTransformation:
    """Crear transformación de columna calculada con fórmula"""
    return CreateCalculatedColumnTransformation(target_column, formula=formula, 
                                               source_columns=source_columns)


def create_function_application(columns: Union[str, List[str]], function: Callable,
                              new_column_name: str = None) -> ApplyFunctionTransformation:
    """Crear transformación de aplicación de función"""
    return ApplyFunctionTransformation(columns, function, new_column_name=new_column_name)


def create_drop_columns(columns: Union[str, List[str]] = None, 
                       pattern: str = None) -> DropColumnsTransformation:
    """Crear transformación de eliminación de columnas"""
    return DropColumnsTransformation(columns, pattern)