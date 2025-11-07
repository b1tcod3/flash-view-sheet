"""
Pivot Filters Module - Advanced filtering system for pivot tables

Provides sophisticated filtering capabilities for pivot table operations
with support for multiple filter types, AND/OR logic, and complex conditions.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Union, Optional, Callable
import logging
from datetime import datetime
import re

# Configurar logging
logger = logging.getLogger(__name__)


class PivotFilter:
    """
    Clase individual para representar un filtro
    """
    
    def __init__(self, column: str, filter_type: str, value: Any = None, 
                 operator: str = 'and', parameters: Dict[str, Any] = None):
        """
        Inicializar filtro
        
        Args:
            column: Nombre de la columna a filtrar
            filter_type: Tipo de filtro
            value: Valor o valores para el filtro
            operator: Operador lógico ('and', 'or')
            parameters: Parámetros adicionales del filtro
        """
        self.column = column
        self.filter_type = filter_type
        self.value = value
        self.operator = operator
        self.parameters = parameters or {}
        
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplicar filtro al DataFrame
        
        Args:
            df: DataFrame a filtrar
            
        Returns:
            pd.DataFrame: DataFrame filtrado
        """
        if self.column not in df.columns:
            logger.warning(f"Columna '{self.column}' no encontrada en el DataFrame")
            return df
            
        try:
            if self.filter_type == 'equals':
                return df[df[self.column] == self.value]
            elif self.filter_type == 'not_equals':
                return df[df[self.column] != self.value]
            elif self.filter_type == 'contains':
                return df[df[self.column].astype(str).str.contains(str(self.value), na=False)]
            elif self.filter_type == 'not_contains':
                return df[~df[self.column].astype(str).str.contains(str(self.value), na=False)]
            elif self.filter_type == 'starts_with':
                return df[df[self.column].astype(str).str.startswith(str(self.value), na=False)]
            elif self.filter_type == 'ends_with':
                return df[df[self.column].astype(str).str.endswith(str(self.value), na=False)]
            elif self.filter_type == 'greater_than':
                return df[df[self.column] > self.value]
            elif self.filter_type == 'less_than':
                return df[df[self.column] < self.value]
            elif self.filter_type == 'greater_equal':
                return df[df[self.column] >= self.value]
            elif self.filter_type == 'less_equal':
                return df[df[self.column] <= self.value]
            elif self.filter_type == 'between':
                if isinstance(self.value, (list, tuple)) and len(self.value) == 2:
                    return df[(df[self.column] >= self.value[0]) & (df[self.column] <= self.value[1])]
            elif self.filter_type == 'in_list':
                if isinstance(self.value, list):
                    return df[df[self.column].isin(self.value)]
            elif self.filter_type == 'not_in_list':
                if isinstance(self.value, list):
                    return df[~df[self.column].isin(self.value)]
            elif self.filter_type == 'is_null':
                return df[df[self.column].isnull()]
            elif self.filter_type == 'not_null':
                return df[df[self.column].notnull()]
            elif self.filter_type == 'is_empty':
                return df[df[self.column].astype(str).str.strip() == '']
            elif self.filter_type == 'not_empty':
                return df[df[self.column].astype(str).str.strip() != '']
            elif self.filter_type == 'regex':
                return df[df[self.column].astype(str).str.match(str(self.value), na=False)]
            elif self.filter_type == 'date_range':
                return self._apply_date_range_filter(df)
            elif self.filter_type == 'numeric_range':
                return self._apply_numeric_range_filter(df)
            elif self.filter_type == 'custom':
                return self._apply_custom_filter(df)
            else:
                logger.warning(f"Tipo de filtro '{self.filter_type}' no soportado")
                return df
                
        except Exception as e:
            logger.error(f"Error aplicando filtro '{self.filter_type}' en columna '{self.column}': {str(e)}")
            return df
            
    def _apply_date_range_filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplicar filtro de rango de fechas"""
        try:
            # Convertir columna a datetime si no lo es
            if not pd.api.types.is_datetime64_any_dtype(df[self.column]):
                df[self.column] = pd.to_datetime(df[self.column])
                
            start_date = self.parameters.get('start_date', self.value[0] if isinstance(self.value, list) else None)
            end_date = self.parameters.get('end_date', self.value[1] if isinstance(self.value, list) else None)
            
            if start_date and end_date:
                start_date = pd.to_datetime(start_date) if isinstance(start_date, str) else start_date
                end_date = pd.to_datetime(end_date) if isinstance(end_date, str) else end_date
                return df[(df[self.column] >= start_date) & (df[self.column] <= end_date)]
            elif start_date:
                start_date = pd.to_datetime(start_date) if isinstance(start_date, str) else start_date
                return df[df[self.column] >= start_date]
            elif end_date:
                end_date = pd.to_datetime(end_date) if isinstance(end_date, str) else end_date
                return df[df[self.column] <= end_date]
            else:
                return df
                
        except Exception as e:
            logger.error(f"Error en filtro de rango de fechas: {str(e)}")
            return df
            
    def _apply_numeric_range_filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplicar filtro de rango numérico"""
        try:
            min_val = self.parameters.get('min', self.value[0] if isinstance(self.value, list) else None)
            max_val = self.parameters.get('max', self.value[1] if isinstance(self.value, list) else None)
            
            if min_val is not None and max_val is not None:
                return df[(df[self.column] >= min_val) & (df[self.column] <= max_val)]
            elif min_val is not None:
                return df[df[self.column] >= min_val]
            elif max_val is not None:
                return df[df[self.column] <= max_val]
            else:
                return df
                
        except Exception as e:
            logger.error(f"Error en filtro de rango numérico: {str(e)}")
            return df
            
    def _apply_custom_filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplicar filtro personalizado"""
        try:
            custom_func = self.parameters.get('function')
            if custom_func and callable(custom_func):
                return df[custom_func(df[self.column])]
            else:
                logger.warning("Función personalizada no encontrada o no es callable")
                return df
        except Exception as e:
            logger.error(f"Error en filtro personalizado: {str(e)}")
            return df


class PivotFilterManager:
    """
    Gestor de filtros para tablas pivote
    Maneja múltiples filtros con lógica AND/OR
    """
    
    def __init__(self):
        """Inicializar gestor de filtros"""
        self.filters: List[PivotFilter] = []
        self.logic_operator = 'and'  # 'and' o 'or'
        
    def add_filter(self, column: str, filter_type: str, value: Any = None, 
                   operator: str = 'and', parameters: Dict[str, Any] = None) -> 'PivotFilterManager':
        """
        Añadir filtro al gestor
        
        Args:
            column: Nombre de la columna
            filter_type: Tipo de filtro
            value: Valor del filtro
            operator: Operador lógico para este filtro
            parameters: Parámetros adicionales
            
        Returns:
            PivotFilterManager: self para chaining
        """
        new_filter = PivotFilter(column, filter_type, value, operator, parameters)
        self.filters.append(new_filter)
        return self
        
    def add_filters_from_dict(self, filters_dict: Dict[str, Dict[str, Any]]) -> 'PivotFilterManager':
        """
        Añadir múltiples filtros desde diccionario
        
        Args:
            filters_dict: Diccionario de filtros
                         Formato: {column_name: {'type': 'equals', 'value': 'some_value'}}
                         
        Returns:
            PivotFilterManager: self para chaining
        """
        for column, filter_config in filters_dict.items():
            filter_type = filter_config.get('type', 'equals')
            value = filter_config.get('value')
            operator = filter_config.get('operator', 'and')
            parameters = filter_config.get('parameters', {})
            
            self.add_filter(column, filter_type, value, operator, parameters)
            
        return self
        
    def set_logic_operator(self, operator: str) -> 'PivotFilterManager':
        """
        Establecer operador lógico principal
        
        Args:
            operator: 'and' o 'or'
            
        Returns:
            PivotFilterManager: self para chaining
        """
        if operator.lower() in ['and', 'or']:
            self.logic_operator = operator.lower()
        else:
            logger.warning(f"Operador lógico '{operator}' no válido, usando 'and'")
            self.logic_operator = 'and'
            
        return self
        
    def clear_filters(self) -> 'PivotFilterManager':
        """
        Limpiar todos los filtros
        
        Returns:
            PivotFilterManager: self para chaining
        """
        self.filters.clear()
        return self
        
    def remove_filter_by_index(self, index: int) -> 'PivotFilterManager':
        """
        Remover filtro por índice
        
        Args:
            index: Índice del filtro a remover
            
        Returns:
            PivotFilterManager: self para chaining
        """
        if 0 <= index < len(self.filters):
            self.filters.pop(index)
        return self
        
    def get_filters(self) -> List[PivotFilter]:
        """
        Obtener lista de filtros
        
        Returns:
            List[PivotFilter]: Lista de filtros
        """
        return self.filters.copy()
        
    def apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplicar todos los filtros al DataFrame
        
        Args:
            df: DataFrame a filtrar
            
        Returns:
            pd.DataFrame: DataFrame filtrado
        """
        if not self.filters:
            logger.info("No hay filtros para aplicar")
            return df
            
        result_df = df.copy()
        
        # Agrupar filtros por operador lógico
        and_filters = [f for f in self.filters if f.operator == 'and']
        or_filters = [f for f in self.filters if f.operator == 'or']
        
        try:
            # Aplicar filtros AND
            for filter_obj in and_filters:
                result_df = filter_obj.apply(result_df)
                
            # Aplicar filtros OR
            if or_filters:
                if len(or_filters) == 1:
                    result_df = or_filters[0].apply(result_df)
                else:
                    # Combinar múltiples filtros OR
                    or_results = [filter_obj.apply(df) for filter_obj in or_filters]
                    result_df = pd.concat(or_results).drop_duplicates()
                    
            logger.info(f"Filtros aplicados: {len(and_filters)} AND, {len(or_filters)} OR")
            return result_df
            
        except Exception as e:
            logger.error(f"Error aplicando filtros: {str(e)}")
            return df
            
    def get_filter_summary(self) -> Dict[str, Any]:
        """
        Obtener resumen de filtros configurados
        
        Returns:
            Dict[str, Any]: Resumen de filtros
        """
        summary = {
            'total_filters': len(self.filters),
            'logic_operator': self.logic_operator,
            'and_filters': len([f for f in self.filters if f.operator == 'and']),
            'or_filters': len([f for f in self.filters if f.operator == 'or']),
            'filter_details': []
        }
        
        for i, filter_obj in enumerate(self.filters):
            filter_detail = {
                'index': i,
                'column': filter_obj.column,
                'type': filter_obj.filter_type,
                'value': filter_obj.value,
                'operator': filter_obj.operator,
                'parameters': filter_obj.parameters
            }
            summary['filter_details'].append(filter_detail)
            
        return summary
        
    def validate_filters(self, df: pd.DataFrame) -> List[str]:
        """
        Validar que todos los filtros son aplicables al DataFrame
        
        Args:
            df: DataFrame a validar
            
        Returns:
            List[str]: Lista de errores encontrados
        """
        errors = []
        
        for i, filter_obj in enumerate(self.filters):
            if filter_obj.column not in df.columns:
                errors.append(f"Filtro {i}: Columna '{filter_obj.column}' no encontrada")
                
            # Validaciones específicas por tipo de filtro
            if filter_obj.filter_type in ['greater_than', 'less_than', 'greater_equal', 'less_equal', 'between']:
                if not pd.api.types.is_numeric_dtype(df[filter_obj.column]):
                    errors.append(f"Filtro {i}: Columna '{filter_obj.column}' debe ser numérica")
                    
            elif filter_obj.filter_type in ['contains', 'not_contains', 'starts_with', 'ends_with', 'regex']:
                if not pd.api.types.is_string_dtype(df[filter_obj.column]) and not pd.api.types.is_object_dtype(df[filter_obj.column]):
                    errors.append(f"Filtro {i}: Columna '{filter_obj.column}' debe ser string")
                    
            elif filter_obj.filter_type == 'date_range':
                if not pd.api.types.is_datetime64_any_dtype(df[filter_obj.column]):
                    try:
                        pd.to_datetime(df[filter_obj.column].dropna().iloc[0])
                    except:
                        errors.append(f"Filtro {i}: Columna '{filter_obj.column}' debe ser fecha")
                        
        return errors


# Función de utilidad para crear filtros predefinidos
def create_standard_filters() -> Dict[str, Dict[str, Any]]:
    """
    Crear diccionarios de filtros estándar
    
    Returns:
        Dict[str, Dict[str, Any]]: Diccionario de filtros predefinidos
    """
    return {
        'equals': {'type': 'equals', 'description': 'Igual a'},
        'not_equals': {'type': 'not_equals', 'description': 'Diferente de'},
        'contains': {'type': 'contains', 'description': 'Contiene'},
        'not_contains': {'type': 'not_contains', 'description': 'No contiene'},
        'greater_than': {'type': 'greater_than', 'description': 'Mayor que'},
        'less_than': {'type': 'less_than', 'description': 'Menor que'},
        'between': {'type': 'between', 'description': 'Entre (rango)'},
        'in_list': {'type': 'in_list', 'description': 'En lista'},
        'is_null': {'type': 'is_null', 'description': 'Es nulo'},
        'not_null': {'type': 'not_null', 'description': 'No es nulo'},
        'is_empty': {'type': 'is_empty', 'description': 'Está vacío'},
        'not_empty': {'type': 'not_empty', 'description': 'No está vacío'},
        'date_range': {'type': 'date_range', 'description': 'Rango de fechas'},
        'numeric_range': {'type': 'numeric_range', 'description': 'Rango numérico'},
        'regex': {'type': 'regex', 'description': 'Expresión regular'}
    }