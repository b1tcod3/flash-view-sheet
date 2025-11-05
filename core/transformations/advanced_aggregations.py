"""
Transformaciones de agregación avanzadas
Incluye múltiples funciones de agregación, pivoteo avanzado, rolling windows y groupby con transformaciones
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union, Tuple
import logging
from datetime import datetime

from .base_transformation import BaseTransformation

# Configurar logging
logger = logging.getLogger(__name__)


class AdvancedAggregationTransformation(BaseTransformation):
    """
    Clase base para transformaciones de agregación avanzadas
    """
    
    def __init__(self, name: str, description: str):
        """
        Inicializar transformación de agregación avanzada
        
        Args:
            name: Nombre de la transformación
            description: Descripción de la transformación
        """
        super().__init__(name, description)
        
        # Almacenar parámetros para posible refactorización
        self._aggregation_params = {}
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """Validar que el DataFrame sea adecuado para agregación"""
        super().validate_data(df)
        
        # Validaciones específicas pueden ser sobrecargadas por subclases
        return True


class MultiFunctionAggregationTransformation(AdvancedAggregationTransformation):
    """
    Transformación para aplicar múltiples funciones de agregación
    """
    
    def __init__(self, groupby_columns: List[str], aggregation_functions: Dict[str, List[str]]):
        """
        Inicializar transformación de agregación con múltiples funciones
        
        Args:
            groupby_columns: Lista de columnas para agrupar
            aggregation_functions: Diccionario con columnas y funciones a aplicar
                                Formato: {'col1': ['sum', 'mean'], 'col2': ['count', 'max']}
        """
        self.groupby_columns = groupby_columns
        self.aggregation_functions = aggregation_functions
        
        group_desc = ", ".join(groupby_columns) if groupby_columns else "todas las filas"
        func_desc = ", ".join([f"{col}:{funcs}" for col, funcs in aggregation_functions.items()])
        
        description = f"Aplicar múltiples funciones de agregación por {group_desc}: {func_desc}"
        
        super().__init__("multi_function_aggregation", description)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar agregación con múltiples funciones"""
        if parameters is None:
            parameters = {}
            
        try:
            # Obtener parámetros
            groupby_columns = parameters.get('groupby_columns', self.groupby_columns)
            aggregation_functions = parameters.get('aggregation_functions', self.aggregation_functions)
            
            # Validar que las columnas de grouping existen
            missing_columns = [col for col in groupby_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Columnas de grouping no encontradas: {missing_columns}")
            
            # Validar que las columnas a agregar existen
            missing_agg_columns = [col for col in aggregation_functions.keys() if col not in df.columns]
            if missing_agg_columns:
                raise ValueError(f"Columnas de agregación no encontradas: {missing_agg_columns}")
            
            # Preparar el diccionario de funciones para pandas
            agg_dict = {}
            for col, funcs in aggregation_functions.items():
                if isinstance(funcs, str):
                    agg_dict[col] = [funcs]
                else:
                    agg_dict[col] = funcs
            
            # Aplicar agregación
            if groupby_columns:
                # Agregación por grupos
                result_df = df.groupby(groupby_columns).agg(agg_dict).reset_index()
            else:
                # Agregación global
                result_df = df.agg(agg_dict).to_frame().T
                
                # Si hay columnas de grouping, añadir una columna 'All' para indicar agregación global
                for col in groupby_columns:
                    result_df[col] = 'All'
            
            # Aplanar columnas si hay múltiples funciones
            flat_columns = []
            for col in result_df.columns:
                if isinstance(col, tuple):
                    flat_columns.append('_'.join(col))
                else:
                    flat_columns.append(col)
            
            result_df.columns = flat_columns
            
            # Guardar parámetros para posible refactorización
            self._aggregation_params = {
                'groupby_columns': groupby_columns,
                'aggregation_functions': aggregation_functions,
                'result_columns': result_df.columns.tolist()
            }
            
            logger.info(f"Aplicadas múltiples funciones de agregación: {list(aggregation_functions.keys())}")
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error en agregación con múltiples funciones: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de agregación múltiple"""
        groupby_columns = parameters.get('groupby_columns', self.groupby_columns)
        aggregation_functions = parameters.get('aggregation_functions', self.aggregation_functions)
        
        if not isinstance(groupby_columns, list):
            return False
        
        if not isinstance(aggregation_functions, dict) or not aggregation_functions:
            return False
        
        # Verificar que las funciones son válidas
        valid_functions = ['sum', 'mean', 'count', 'min', 'max', 'std', 'var', 'median', 
                          'first', 'last', 'size', 'nunique']
        
        for col, funcs in aggregation_functions.items():
            if isinstance(funcs, str):
                if funcs not in valid_functions:
                    return False
            else:
                for func in funcs:
                    if func not in valid_functions:
                        return False
        
        return True


class AdvancedPivotingTransformation(AdvancedAggregationTransformation):
    """
    Transformación para pivoteo avanzado con múltiples índices/columnas
    """
    
    def __init__(self, index: Union[str, List[str]], columns: Union[str, List[str]], 
                 values: Union[str, List[str]], aggfunc: Union[str, List[str]] = 'mean',
                 fill_value: Any = None, dropna: bool = True, margins: bool = False,
                 margins_name: str = 'All'):
        """
        Inicializar transformación de pivoteo avanzado
        
        Args:
            index: Columna o lista de columnas para el índice
            columns: Columna o lista de columnas para las columnas del pivote
            values: Columna o lista de columnas para los valores
            aggfunc: Función o lista de funciones de agregación
            fill_value: Valor para rellenar celdas vacías
            dropna: Si eliminar filas con todos los valores NaN
            margins: Si calcular totales
            margins_name: Nombre para la fila/columna de totales
        """
        self.index = [index] if isinstance(index, str) else index
        self.columns = [columns] if isinstance(columns, str) else columns
        self.values = [values] if isinstance(values, str) else values
        self.aggfunc = [aggfunc] if isinstance(aggfunc, str) else aggfunc
        self.fill_value = fill_value
        self.dropna = dropna
        self.margins = margins
        self.margins_name = margins_name
        
        index_desc = ", ".join(self.index) if len(self.index) > 1 else self.index[0] if self.index else "None"
        columns_desc = ", ".join(self.columns) if len(self.columns) > 1 else self.columns[0] if self.columns else "None"
        values_desc = ", ".join(self.values) if len(self.values) > 1 else self.values[0] if self.values else "None"
        
        description = f"Pivoteo avanzado: índice={index_desc}, columnas={columns_desc}, valores={values_desc}"
        
        super().__init__("advanced_pivoting", description)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar pivoteo avanzado"""
        if parameters is None:
            parameters = {}
            
        try:
            # Obtener parámetros
            index = parameters.get('index', self.index)
            columns = parameters.get('columns', self.columns)
            values = parameters.get('values', self.values)
            aggfunc = parameters.get('aggfunc', self.aggfunc)
            fill_value = parameters.get('fill_value', self.fill_value)
            dropna = parameters.get('dropna', self.dropna)
            margins = parameters.get('margins', self.margins)
            margins_name = parameters.get('margins_name', self.margins_name)
            
            # Validar que las columnas existen
            all_columns = set(index + columns + values)
            missing_columns = [col for col in all_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Columnas no encontradas: {missing_columns}")
            
            # Convertir a listas si es necesario
            index = [index] if isinstance(index, str) else index
            columns = [columns] if isinstance(columns, str) else columns
            values = [values] if isinstance(values, str) else values
            aggfunc = [aggfunc] if isinstance(aggfunc, str) else aggfunc
            
            # Si hay múltiples valores, pivotar cada uno
            if len(values) > 1:
                result_dfs = []
                
                for value_col in values:
                    # Usar solo una función de agregación si no se especifica
                    current_aggfunc = aggfunc[0] if len(aggfunc) == 1 else 'mean'
                    
                    # Crear pivote
                    try:
                        pivot_df = pd.pivot_table(
                            df, 
                            index=index, 
                            columns=columns, 
                            values=value_col, 
                            aggfunc=current_aggfunc,
                            fill_value=fill_value,
                            dropna=dropna,
                            margins=margins,
                            margins_name=margins_name
                        )
                        
                        # Resetear índice y añadir prefijo
                        pivot_df = pivot_df.reset_index()
                        pivot_df.columns = [f"{value_col}_{col}" if col not in index else col 
                                          for col in pivot_df.columns]
                        
                        result_dfs.append(pivot_df)
                        
                    except Exception as e:
                        logger.warning(f"Error al pivotar valor '{value_col}': {str(e)}")
                
                # Combinar los resultados
                if result_dfs:
                    # Usar merge si hay columnas de índice
                    if index:
                        result_df = result_dfs[0]
                        for df_to_merge in result_dfs[1:]:
                            result_df = result_df.merge(df_to_merge, on=index, how='outer')
                    else:
                        # Concatenar horizontalmente si no hay índice
                        result_df = pd.concat(result_dfs, axis=1)
                else:
                    result_df = pd.DataFrame()
            else:
                # Pivotear con un solo valor
                try:
                    result_df = pd.pivot_table(
                        df, 
                        index=index, 
                        columns=columns, 
                        values=values[0], 
                        aggfunc=aggfunc,
                        fill_value=fill_value,
                        dropna=dropna,
                        margins=margins,
                        margins_name=margins_name
                    )
                    
                    # Resetear índice
                    if margins:
                        result_df = result_df.reset_index()
                    else:
                        result_df = result_df.reset_index()
                        
                except Exception as e:
                    logger.error(f"Error al crear tabla pivote: {str(e)}")
                    result_df = pd.DataFrame()
            
            # Guardar parámetros para posible refactorización
            self._aggregation_params = {
                'index': index,
                'columns': columns,
                'values': values,
                'aggfunc': aggfunc,
                'fill_value': fill_value,
                'dropna': dropna,
                'margins': margins,
                'margins_name': margins_name,
                'result_columns': result_df.columns.tolist() if not result_df.empty else []
            }
            
            logger.info(f"Pivoteo avanzado completado, shape: {result_df.shape}")
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error en pivoteo avanzado: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de pivoteo avanzado"""
        index = parameters.get('index', self.index)
        columns = parameters.get('columns', self.columns)
        values = parameters.get('values', self.values)
        aggfunc = parameters.get('aggfunc', self.aggfunc)
        
        if not isinstance(index, list) or not index:
            return False
        
        if not isinstance(columns, list) or not columns:
            return False
        
        if not isinstance(values, list) or not values:
            return False
        
        valid_aggfuncs = ['sum', 'mean', 'count', 'min', 'max', 'std', 'var', 'median', 
                         'first', 'last', 'size', 'nunique']
        
        # Validar que aggfunc es válido
        if isinstance(aggfunc, str):
            if aggfunc not in valid_aggfuncs:
                return False
        else:
            for func in aggfunc:
                if func not in valid_aggfuncs:
                    return False
        
        return True


class RollingWindowTransformation(AdvancedAggregationTransformation):
    """
    Transformación para aplicar rolling windows (ventanas deslizantes)
    """
    
    def __init__(self, columns: List[str], window_size: int, aggregation_function: str = 'mean',
                 min_periods: int = None, center: bool = False, closed: str = 'left'):
        """
        Inicializar transformación de rolling window
        
        Args:
            columns: Lista de columnas a aplicar la ventana
            window_size: Tamaño de la ventana
            aggregation_function: Función de agregación ('mean', 'sum', 'std', etc.)
            min_periods: Número mínimo de valores en la ventana
            center: Si centrar la ventana
            closed: Cómo definir los límites de la ventana ('left', 'right', 'both', 'neither')
        """
        self.columns = columns
        self.window_size = window_size
        self.aggregation_function = aggregation_function
        self.min_periods = min_periods
        self.center = center
        self.closed = closed
        
        column_desc = ", ".join(columns) if len(columns) <= 3 else f"{len(columns)} columnas"
        description = f"Aplicar rolling window de tamaño {window_size} con {aggregation_function} a {column_desc}"
        
        super().__init__("rolling_window", description)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar transformación de rolling window"""
        if parameters is None:
            parameters = {}
            
        try:
            # Obtener parámetros
            columns = parameters.get('columns', self.columns)
            window_size = parameters.get('window_size', self.window_size)
            aggregation_function = parameters.get('aggregation_function', self.aggregation_function)
            min_periods = parameters.get('min_periods', self.min_periods)
            center = parameters.get('center', self.center)
            closed = parameters.get('closed', self.closed)
            
            # Validar que las columnas existen
            missing_columns = [col for col in columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Columnas no encontradas: {missing_columns}")
            
            # Validar que las columnas son numéricas
            non_numeric_columns = [col for col in columns 
                                 if col in df.columns and not pd.api.types.is_numeric_dtype(df[col])]
            if non_numeric_columns:
                raise ValueError(f"Las siguientes columnas no son numéricas: {non_numeric_columns}")
            
            # Crear DataFrame resultado
            result_df = df.copy()
            
            # Aplicar rolling window a cada columna
            for col in columns:
                try:
                    # Crear la ventana deslizante
                    rolling = df[col].rolling(
                        window=window_size,
                        min_periods=min_periods,
                        center=center,
                        closed=closed
                    )
                    
                    # Aplicar la función de agregación
                    if aggregation_function == 'mean':
                        result_col = rolling.mean()
                    elif aggregation_function == 'sum':
                        result_col = rolling.sum()
                    elif aggregation_function == 'std':
                        result_col = rolling.std()
                    elif aggregation_function == 'var':
                        result_col = rolling.var()
                    elif aggregation_function == 'min':
                        result_col = rolling.min()
                    elif aggregation_function == 'max':
                        result_col = rolling.max()
                    elif aggregation_function == 'median':
                        result_col = rolling.median()
                    elif aggregation_function == 'first':
                        result_col = rolling.first()
                    elif aggregation_function == 'last':
                        result_col = rolling.last()
                    elif aggregation_function == 'count':
                        result_col = rolling.count()
                    else:
                        raise ValueError(f"Función de agregación '{aggregation_function}' no soportada")
                    
                    # Crear nombre para la columna resultado
                    result_column_name = f"{col}_{aggregation_function}_w{window_size}"
                    
                    # Asignar resultado
                    result_df[result_column_name] = result_col
                    
                    logger.info(f"Rolling window aplicado a columna '{col}', resultado en '{result_column_name}'")
                    
                except Exception as e:
                    logger.error(f"Error al aplicar rolling window a '{col}': {str(e)}")
                    raise
            
            # Guardar parámetros para posible refactorización
            self._aggregation_params = {
                'columns': columns,
                'window_size': window_size,
                'aggregation_function': aggregation_function,
                'min_periods': min_periods,
                'center': center,
                'closed': closed
            }
            
            logger.info(f"Rolling window de tamaño {window_size} aplicado a {len(columns)} columna(s)")
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error en rolling window: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de rolling window"""
        columns = parameters.get('columns', self.columns)
        window_size = parameters.get('window_size', self.window_size)
        aggregation_function = parameters.get('aggregation_function', self.aggregation_function)
        min_periods = parameters.get('min_periods', self.min_periods)
        center = parameters.get('center', self.center)
        closed = parameters.get('closed', self.closed)
        
        if not isinstance(columns, list) or not columns:
            return False
        
        if not isinstance(window_size, int) or window_size < 1:
            return False
        
        if min_periods is not None and (not isinstance(min_periods, int) or min_periods < 1):
            return False
        
        valid_aggfuncs = ['mean', 'sum', 'std', 'var', 'min', 'max', 'median', 
                         'first', 'last', 'count']
        
        if aggregation_function not in valid_aggfuncs:
            return False
        
        if not isinstance(center, bool):
            return False
        
        if closed not in ['left', 'right', 'both', 'neither']:
            return False
        
        return True


class ExpandingWindowTransformation(AdvancedAggregationTransformation):
    """
    Transformación para aplicar expanding windows (ventanas expansivas)
    """
    
    def __init__(self, columns: List[str], min_periods: int = 1, center: bool = False,
                 aggregation_function: str = 'mean'):
        """
        Inicializar transformación de expanding window
        
        Args:
            columns: Lista de columnas a aplicar la ventana
            min_periods: Número mínimo de valores en la ventana
            center: Si centrar la ventana
            aggregation_function: Función de agregación ('mean', 'sum', 'std', etc.)
        """
        self.columns = columns
        self.min_periods = min_periods
        self.center = center
        self.aggregation_function = aggregation_function
        
        column_desc = ", ".join(columns) if len(columns) <= 3 else f"{len(columns)} columnas"
        description = f"Aplicar expanding window con {aggregation_function} a {column_desc}"
        
        super().__init__("expanding_window", description)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar transformación de expanding window"""
        if parameters is None:
            parameters = {}
            
        try:
            # Obtener parámetros
            columns = parameters.get('columns', self.columns)
            min_periods = parameters.get('min_periods', self.min_periods)
            center = parameters.get('center', self.center)
            aggregation_function = parameters.get('aggregation_function', self.aggregation_function)
            
            # Validar que las columnas existen
            missing_columns = [col for col in columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Columnas no encontradas: {missing_columns}")
            
            # Validar que las columnas son numéricas
            non_numeric_columns = [col for col in columns 
                                 if col in df.columns and not pd.api.types.is_numeric_dtype(df[col])]
            if non_numeric_columns:
                raise ValueError(f"Las siguientes columnas no son numéricas: {non_numeric_columns}")
            
            # Crear DataFrame resultado
            result_df = df.copy()
            
            # Aplicar expanding window a cada columna
            for col in columns:
                try:
                    # Crear la ventana expansiva
                    expanding = df[col].expanding(
                        min_periods=min_periods,
                        center=center
                    )
                    
                    # Aplicar la función de agregación
                    if aggregation_function == 'mean':
                        result_col = expanding.mean()
                    elif aggregation_function == 'sum':
                        result_col = expanding.sum()
                    elif aggregation_function == 'std':
                        result_col = expanding.std()
                    elif aggregation_function == 'var':
                        result_col = expanding.var()
                    elif aggregation_function == 'min':
                        result_col = expanding.min()
                    elif aggregation_function == 'max':
                        result_col = expanding.max()
                    elif aggregation_function == 'median':
                        result_col = expanding.median()
                    elif aggregation_function == 'first':
                        result_col = expanding.first()
                    elif aggregation_function == 'last':
                        result_col = expanding.last()
                    elif aggregation_function == 'count':
                        result_col = expanding.count()
                    else:
                        raise ValueError(f"Función de agregación '{aggregation_function}' no soportada")
                    
                    # Crear nombre para la columna resultado
                    result_column_name = f"{col}_{aggregation_function}_expanding"
                    
                    # Asignar resultado
                    result_df[result_column_name] = result_col
                    
                    logger.info(f"Expanding window aplicado a columna '{col}', resultado en '{result_column_name}'")
                    
                except Exception as e:
                    logger.error(f"Error al aplicar expanding window a '{col}': {str(e)}")
                    raise
            
            # Guardar parámetros para posible refactorización
            self._aggregation_params = {
                'columns': columns,
                'min_periods': min_periods,
                'center': center,
                'aggregation_function': aggregation_function
            }
            
            logger.info(f"Expanding window aplicado a {len(columns)} columna(s)")
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error en expanding window: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de expanding window"""
        columns = parameters.get('columns', self.columns)
        min_periods = parameters.get('min_periods', self.min_periods)
        center = parameters.get('center', self.center)
        aggregation_function = parameters.get('aggregation_function', self.aggregation_function)
        
        if not isinstance(columns, list) or not columns:
            return False
        
        if not isinstance(min_periods, int) or min_periods < 1:
            return False
        
        valid_aggfuncs = ['mean', 'sum', 'std', 'var', 'min', 'max', 'median', 
                         'first', 'last', 'count']
        
        if aggregation_function not in valid_aggfuncs:
            return False
        
        if not isinstance(center, bool):
            return False
        
        return True


class GroupByTransformationTransformation(AdvancedAggregationTransformation):
    """
    Transformación para realizar groupby con transformaciones
    """
    
    def __init__(self, groupby_columns: List[str], transformation_function: str,
                 transformation_columns: List[str], new_column_suffix: str = "_grouped"):
        """
        Inicializar transformación de groupby con transformaciones
        
        Args:
            groupby_columns: Lista de columnas para agrupar
            transformation_function: Función de transformación ('rank', 'diff', 'shift', 'cumsum', 'cumprod', 'cummax', 'cummin')
            transformation_columns: Lista de columnas a transformar
            new_column_suffix: Sufijo para nombres de nuevas columnas
        """
        self.groupby_columns = groupby_columns
        self.transformation_function = transformation_function
        self.transformation_columns = transformation_columns
        self.new_column_suffix = new_column_suffix
        
        group_desc = ", ".join(groupby_columns) if groupby_columns else "todas las filas"
        column_desc = ", ".join(transformation_columns) if len(transformation_columns) <= 3 else f"{len(transformation_columns)} columnas"
        
        description = f"Aplicar transformación {transformation_function} por grupos ({group_desc}) en {column_desc}"
        
        super().__init__("groupby_transformation", description)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar groupby con transformaciones"""
        if parameters is None:
            parameters = {}
            
        try:
            # Obtener parámetros
            groupby_columns = parameters.get('groupby_columns', self.groupby_columns)
            transformation_function = parameters.get('transformation_function', self.transformation_function)
            transformation_columns = parameters.get('transformation_columns', self.transformation_columns)
            new_column_suffix = parameters.get('new_column_suffix', self.new_column_suffix)
            
            # Validar que las columnas de grouping existen
            missing_columns = [col for col in groupby_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Columnas de grouping no encontradas: {missing_columns}")
            
            # Validar que las columnas a transformar existen
            missing_agg_columns = [col for col in transformation_columns if col not in df.columns]
            if missing_agg_columns:
                raise ValueError(f"Columnas de transformación no encontradas: {missing_agg_columns}")
            
            # Validar que las columnas a transformar son numéricas
            non_numeric_columns = [col for col in transformation_columns 
                                 if col in df.columns and not pd.api.types.is_numeric_dtype(df[col])]
            if non_numeric_columns and transformation_function in ['diff', 'shift', 'cumsum', 'cumprod', 'cummax', 'cummin']:
                raise ValueError(f"Las siguientes columnas no son numéricas: {non_numeric_columns}")
            
            # Crear DataFrame resultado
            result_df = df.copy()
            
            # Aplicar transformación por grupos
            for col in transformation_columns:
                try:
                    # Realizar groupby y aplicar la transformación
                    if transformation_function == 'rank':
                        # Calcular rango dentro de cada grupo
                        result_col = df.groupby(groupby_columns)[col].rank(pct=True)
                    elif transformation_function == 'diff':
                        # Calcular diferencia con el valor anterior en el grupo
                        result_col = df.groupby(groupby_columns)[col].diff()
                    elif transformation_function == 'shift':
                        # Desplazar valores dentro de cada grupo
                        result_col = df.groupby(groupby_columns)[col].shift()
                    elif transformation_function == 'cumsum':
                        # Calcular suma acumulativa dentro de cada grupo
                        result_col = df.groupby(groupby_columns)[col].cumsum()
                    elif transformation_function == 'cumprod':
                        # Calcular producto acumulativo dentro de cada grupo
                        result_col = df.groupby(groupby_columns)[col].cumprod()
                    elif transformation_function == 'cummax':
                        # Calcular máximo acumulativo dentro de cada grupo
                        result_col = df.groupby(groupby_columns)[col].cummax()
                    elif transformation_function == 'cummin':
                        # Calcular mínimo acumulativo dentro de cada grupo
                        result_col = df.groupby(groupby_columns)[col].cummin()
                    else:
                        raise ValueError(f"Función de transformación '{transformation_function}' no soportada")
                    
                    # Crear nombre para la columna resultado
                    result_column_name = f"{col}_{transformation_function}{new_column_suffix}"
                    
                    # Asignar resultado
                    result_df[result_column_name] = result_col
                    
                    logger.info(f"Transformación {transformation_function} aplicada a columna '{col}' por grupos, resultado en '{result_column_name}'")
                    
                except Exception as e:
                    logger.error(f"Error al aplicar transformación {transformation_function} a '{col}': {str(e)}")
                    raise
            
            # Guardar parámetros para posible refactorización
            self._aggregation_params = {
                'groupby_columns': groupby_columns,
                'transformation_function': transformation_function,
                'transformation_columns': transformation_columns,
                'new_column_suffix': new_column_suffix
            }
            
            logger.info(f"Transformación {transformation_function} aplicada a {len(transformation_columns)} columna(s) por grupos")
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error en groupby con transformaciones: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de groupby con transformaciones"""
        groupby_columns = parameters.get('groupby_columns', self.groupby_columns)
        transformation_function = parameters.get('transformation_function', self.transformation_function)
        transformation_columns = parameters.get('transformation_columns', self.transformation_columns)
        new_column_suffix = parameters.get('new_column_suffix', self.new_column_suffix)
        
        if not isinstance(groupby_columns, list):
            return False
        
        if not isinstance(transformation_columns, list) or not transformation_columns:
            return False
        
        valid_functions = ['rank', 'diff', 'shift', 'cumsum', 'cumprod', 'cummax', 'cummin']
        
        if transformation_function not in valid_functions:
            return False
        
        if not isinstance(new_column_suffix, str):
            return False
        
        return True


# Funciones de utilidad para crear transformaciones de agregación avanzada
def create_multi_function_aggregation(groupby_columns: List[str], 
                                      aggregation_functions: Dict[str, List[str]]) -> MultiFunctionAggregationTransformation:
    """Crear transformación de agregación con múltiples funciones"""
    return MultiFunctionAggregationTransformation(groupby_columns, aggregation_functions)


def create_advanced_pivoting(index: Union[str, List[str]], 
                            columns: Union[str, List[str]], 
                            values: Union[str, List[str]], 
                            aggfunc: Union[str, List[str]] = 'mean') -> AdvancedPivotingTransformation:
    """Crear transformación de pivoteo avanzado"""
    return AdvancedPivotingTransformation(index, columns, values, aggfunc)


def create_rolling_window(columns: List[str], 
                          window_size: int, 
                          aggregation_function: str = 'mean') -> RollingWindowTransformation:
    """Crear transformación de rolling window"""
    return RollingWindowTransformation(columns, window_size, aggregation_function)


def create_expanding_window(columns: List[str], 
                           min_periods: int = 1,
                           aggregation_function: str = 'mean') -> ExpandingWindowTransformation:
    """Crear transformación de expanding window"""
    return ExpandingWindowTransformation(columns, min_periods, aggregation_function)


def create_groupby_transformation(groupby_columns: List[str], 
                                 transformation_function: str,
                                 transformation_columns: List[str]) -> GroupByTransformationTransformation:
    """Crear transformación de groupby con transformaciones"""
    return GroupByTransformationTransformation(groupby_columns, transformation_function, transformation_columns)