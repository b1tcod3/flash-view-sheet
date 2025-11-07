"""
Pivot Aggregations Module - Advanced aggregation management for pivot tables

Provides comprehensive aggregation capabilities including custom functions,
multiple aggregation types, and advanced statistical operations.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Union, Optional, Callable, Tuple
import logging
from datetime import datetime
import warnings

# Configurar logging
logger = logging.getLogger(__name__)


class PivotAggregation:
    """
    Clase para representar una función de agregación individual
    """
    
    def __init__(self, function: Union[str, Callable], column: str, 
                 new_column_name: str = None, parameters: Dict[str, Any] = None):
        """
        Inicializar agregación
        
        Args:
            function: Función de agregación (nombre string o callable)
            column: Columna a agregar
            new_column_name: Nombre para la columna resultado
            parameters: Parámetros para la función
        """
        self.function = function
        self.column = column
        self.new_column_name = new_column_name
        self.parameters = parameters or {}
        
    def get_result_name(self, default_suffix: str = None) -> str:
        """
        Obtener nombre para la columna resultado
        
        Args:
            default_suffix: Sufijo por defecto si no hay nombre personalizado
            
        Returns:
            str: Nombre de la columna resultado
        """
        if self.new_column_name:
            return self.new_column_name
            
        if isinstance(self.function, str):
            func_name = self.function
        else:
            func_name = getattr(self.function, '__name__', str(self.function))
            
        if default_suffix:
            return f"{self.column}_{default_suffix}_{func_name}"
        else:
            return f"{self.column}_{func_name}"
            
    def apply(self, data: pd.Series) -> Any:
        """
        Aplicar agregación a los datos
        
        Args:
            data: Serie de datos a agregar
            
        Returns:
            Any: Resultado de la agregación
        """
        try:
            if callable(self.function):
                if self.parameters:
                    return self.function(data, **self.parameters)
                else:
                    return self.function(data)
            else:
                return self._apply_named_function(data)
        except Exception as e:
            logger.error(f"Error aplicando agregación '{self.function}' a columna '{self.column}': {str(e)}")
            return np.nan
            
    def _apply_named_function(self, data: pd.Series) -> Any:
        """Aplicar función de agregación por nombre"""
        # Funciones básicas de pandas
        basic_functions = {
            'sum': lambda x: x.sum(),
            'mean': lambda x: x.mean(),
            'median': lambda x: x.median(),
            'mode': lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan,
            'count': lambda x: x.count(),
            'size': lambda x: x.size,
            'min': lambda x: x.min(),
            'max': lambda x: x.max(),
            'std': lambda x: x.std(),
            'var': lambda x: x.var(),
            'first': lambda x: x.first(),
            'last': lambda x: x.last(),
            'prod': lambda x: x.prod()
        }
        
        # Funciones adicionales con pandas
        extended_functions = {
            'nunique': lambda x: x.nunique(),
            'unique': lambda x: x.unique().tolist(),
            'values': lambda x: x.values.tolist(),
            'skew': lambda x: x.skew(),
            'kurtosis': lambda x: x.kurtosis(),
            'quantile': lambda x: x.quantile(self.parameters.get('q', 0.5))
        }
        
        all_functions = {**basic_functions, **extended_functions}
        
        if self.function in all_functions:
            return all_functions[self.function](data)
        else:
            # Intentar con método directo de pandas si existe
            if hasattr(data, self.function):
                method = getattr(data, self.function)
                if callable(method):
                    if self.parameters:
                        return method(**self.parameters)
                    else:
                        return method()
                        
            logger.warning(f"Función de agregación '{self.function}' no encontrada")
            return np.nan


class PivotAggregationManager:
    """
    Gestor de agregaciones para tablas pivote
    Maneja múltiples funciones de agregación y tipos de datos
    """
    
    def __init__(self):
        """Inicializar gestor de agregaciones"""
        self.aggregations: List[PivotAggregation] = []
        self.aggregation_types = {
            'basic': ['sum', 'mean', 'median', 'count', 'min', 'max', 'std', 'var'],
            'extended': ['first', 'last', 'size', 'nunique', 'unique', 'skew', 'kurtosis'],
            'quantile': ['quantile', 'percentile'],
            'custom': ['custom']
        }
        
        # Funciones de agregación predefinidas
        self.predefined_aggregations = {
            'sum': 'Suma',
            'mean': 'Promedio',
            'median': 'Mediana',
            'count': 'Conteo',
            'min': 'Mínimo',
            'max': 'Máximo',
            'std': 'Desviación Estándar',
            'var': 'Varianza',
            'first': 'Primero',
            'last': 'Último',
            'size': 'Tamaño',
            'nunique': 'Valores Únicos',
            'skew': 'Sesgo',
            'kurtosis': 'Curtosis',
            'quantile': 'Cuantil',
            'custom': 'Personalizada'
        }
        
    def add_aggregation(self, function: Union[str, Callable], column: str, 
                       new_column_name: str = None, parameters: Dict[str, Any] = None) -> 'PivotAggregationManager':
        """
        Añadir agregación al gestor
        
        Args:
            function: Función de agregación
            column: Columna a agregar
            new_column_name: Nombre personalizado para resultado
            parameters: Parámetros para la función
            
        Returns:
            PivotAggregationManager: self para chaining
        """
        new_agg = PivotAggregation(function, column, new_column_name, parameters)
        self.aggregations.append(new_agg)
        return self
        
    def add_multiple_aggregations(self, functions: List[str], column: str, 
                                 prefix: str = None) -> 'PivotAggregationManager':
        """
        Añadir múltiples agregaciones para una columna
        
        Args:
            functions: Lista de funciones de agregación
            column: Columna a agregar
            prefix: Prefijo para nombres de columnas resultado
            
        Returns:
            PivotAggregationManager: self para chaining
        """
        for func in functions:
            if prefix:
                new_column_name = f"{prefix}_{func}_{column}"
            else:
                new_column_name = f"{column}_{func}"
            self.add_aggregation(func, column, new_column_name)
            
        return self
        
    def add_aggregation_for_columns(self, aggregation_function: str, columns: List[str]) -> 'PivotAggregationManager':
        """
        Añadir una agregación para múltiples columnas
        
        Args:
            aggregation_function: Función de agregación
            columns: Lista de columnas
            
        Returns:
            PivotAggregationManager: self para chaining
        """
        for column in columns:
            new_column_name = f"{column}_{aggregation_function}"
            self.add_aggregation(aggregation_function, column, new_column_name)
            
        return self
        
    def clear_aggregations(self) -> 'PivotAggregationManager':
        """
        Limpiar todas las agregaciones
        
        Returns:
            PivotAggregationManager: self para chaining
        """
        self.aggregations.clear()
        return self
        
    def remove_aggregation_by_index(self, index: int) -> 'PivotAggregationManager':
        """
        Remover agregación por índice
        
        Args:
            index: Índice de la agregación a remover
            
        Returns:
            PivotAggregationManager: self para chaining
        """
        if 0 <= index < len(self.aggregations):
            self.aggregations.pop(index)
        return self
        
    def get_aggregations(self) -> List[PivotAggregation]:
        """
        Obtener lista de agregaciones
        
        Returns:
            List[PivotAggregation]: Lista de agregaciones
        """
        return self.aggregations.copy()
        
    def apply_aggregations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplicar todas las agregaciones al DataFrame
        
        Args:
            df: DataFrame a agregar
            
        Returns:
            pd.DataFrame: DataFrame con agregaciones aplicadas
        """
        if not self.aggregations:
            logger.info("No hay agregaciones para aplicar")
            return df
            
        result_data = {}
        
        for agg in self.aggregations:
            if agg.column not in df.columns:
                logger.warning(f"Columna '{agg.column}' no encontrada para agregación")
                continue
                
            try:
                result_data[agg.get_result_name()] = agg.apply(df[agg.column])
            except Exception as e:
                logger.error(f"Error aplicando agregación a '{agg.column}': {str(e)}")
                result_data[agg.get_result_name()] = np.nan
                
        result_df = pd.DataFrame([result_data])
        logger.info(f"Aplicadas {len(self.aggregations)} agregaciones")
        return result_df
        
    def get_valid_aggregations(self, data_type: str = 'numeric') -> List[str]:
        """
        Obtener funciones de agregación válidas para un tipo de datos
        
        Args:
            data_type: Tipo de datos ('numeric', 'string', 'datetime', 'any')
            
        Returns:
            List[str]: Lista de funciones válidas
        """
        if data_type == 'numeric':
            return self.aggregation_types['basic'] + self.aggregation_types['extended'] + ['quantile']
        elif data_type == 'string':
            return ['count', 'nunique', 'unique', 'size', 'first', 'last', 'max', 'min']
        elif data_type == 'datetime':
            return ['count', 'min', 'max', 'first', 'last', 'size', 'nunique']
        else:  # 'any'
            return self.aggregation_types['basic'] + ['nunique', 'size', 'first', 'last']
            
    def get_aggregation_info(self, function: str) -> Dict[str, Any]:
        """
        Obtener información sobre una función de agregación
        
        Args:
            function: Nombre de la función
            
        Returns:
            Dict[str, Any]: Información de la función
        """
        info = {
            'name': function,
            'display_name': self.predefined_aggregations.get(function, function),
            'category': 'unknown',
            'requires_parameters': False,
            'parameter_info': {}
        }
        
        # Determinar categoría
        for category, functions in self.aggregation_types.items():
            if function in functions:
                info['category'] = category
                break
                
        # Información específica por función
        if function == 'quantile':
            info['requires_parameters'] = True
            info['parameter_info'] = {'q': 'Valor del cuantil (0.0-1.0)'}
        elif function == 'custom':
            info['requires_parameters'] = False  # Depends on custom function
            info['parameter_info'] = {'function': 'Función personalizada callable'}
            
        return info
        
    def create_custom_aggregation(self, custom_function: Callable, 
                                 column: str, new_column_name: str = None,
                                 parameters: Dict[str, Any] = None) -> 'PivotAggregationManager':
        """
        Crear agregación con función personalizada
        
        Args:
            custom_function: Función callable personalizada
            column: Columna a agregar
            new_column_name: Nombre para resultado
            parameters: Parámetros para la función
            
        Returns:
            PivotAggregationManager: self para chaining
        """
        return self.add_aggregation('custom', column, new_column_name, {
            'function': custom_function,
            **(parameters or {})
        })
        
    def get_aggregation_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen de agregaciones configuradas
        
        Returns:
            Dict[str, Any]: Resumen de agregaciones
        """
        summary = {
            'total_aggregations': len(self.aggregations),
            'aggregations_by_function': {},
            'aggregations_by_column': {},
            'custom_aggregations': 0
        }
        
        for agg in self.aggregations:
            # Por función
            func = agg.function if isinstance(agg.function, str) else 'custom'
            if func not in summary['aggregations_by_function']:
                summary['aggregations_by_function'][func] = 0
            summary['aggregations_by_function'][func] += 1
            
            # Por columna
            if agg.column not in summary['aggregations_by_column']:
                summary['aggregations_by_column'][agg.column] = 0
            summary['aggregations_by_column'][agg.column] += 1
            
            # Contar custom
            if func == 'custom':
                summary['custom_aggregations'] += 1
                
        return summary


# Funciones de utilidad para crear agregaciones predefinidas
def create_standard_aggregations() -> List[Dict[str, str]]:
    """
    Crear lista de agregaciones estándar para UI
    
    Returns:
        List[Dict[str, str]]: Lista de agregaciones con información para UI
    """
    return [
        {'function': 'sum', 'display_name': 'Suma', 'category': 'numeric'},
        {'function': 'mean', 'display_name': 'Promedio', 'category': 'numeric'},
        {'function': 'median', 'display_name': 'Mediana', 'category': 'numeric'},
        {'function': 'count', 'display_name': 'Conteo', 'category': 'general'},
        {'function': 'min', 'display_name': 'Mínimo', 'category': 'numeric'},
        {'function': 'max', 'display_name': 'Máximo', 'category': 'numeric'},
        {'function': 'std', 'display_name': 'Desviación Estándar', 'category': 'numeric'},
        {'function': 'var', 'display_name': 'Varianza', 'category': 'numeric'},
        {'function': 'first', 'display_name': 'Primero', 'category': 'general'},
        {'function': 'last', 'display_name': 'Último', 'category': 'general'},
        {'function': 'nunique', 'display_name': 'Valores Únicos', 'category': 'general'},
        {'function': 'size', 'display_name': 'Tamaño', 'category': 'general'},
        {'function': 'quantile', 'display_name': 'Cuantil', 'category': 'numeric'}
    ]


def create_weighted_average_function() -> Callable:
    """
    Crear función de promedio ponderado
    
    Returns:
        Callable: Función de promedio ponderado
    """
    def weighted_average(data: pd.Series, weights: pd.Series) -> float:
        """Calcular promedio ponderado"""
        try:
            return np.average(data, weights=weights)
        except:
            return np.nan
    return weighted_average


def create_rolling_aggregation_function(window: int, func: str = 'mean') -> Callable:
    """
    Crear función de agregación rolling
    
    Args:
        window: Tamaño de la ventana
        func: Función de agregación
        
    Returns:
        Callable: Función rolling
    """
    def rolling_agg(data: pd.Series) -> Any:
        """Agregación rolling"""
        try:
            rolling_obj = data.rolling(window=window)
            if func == 'mean':
                return rolling_obj.mean().iloc[-1]
            elif func == 'sum':
                return rolling_obj.sum().iloc[-1]
            elif func == 'std':
                return rolling_obj.std().iloc[-1]
            elif func == 'count':
                return rolling_obj.count().iloc[-1]
            else:
                return rolling_obj.agg(func).iloc[-1]
        except:
            return np.nan
    return rolling_agg


def create_growth_rate_function() -> Callable:
    """
    Crear función de tasa de crecimiento
    
    Returns:
        Callable: Función de tasa de crecimiento
    """
    def growth_rate(data: pd.Series) -> float:
        """Calcular tasa de crecimiento"""
        try:
            if len(data) < 2:
                return np.nan
            first_val = data.iloc[0]
            last_val = data.iloc[-1]
            if first_val == 0:
                return np.nan
            return ((last_val / first_val) - 1) * 100
        except:
            return np.nan
    return growth_rate