"""
Base Pivot Table Module - Core functionality for pivot table operations

Provides the base class and core pivot table functionality with support for
advanced filtering and aggregation operations.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union, Tuple
import logging
from datetime import datetime
from abc import ABC, abstractmethod

# Configurar logging
logger = logging.getLogger(__name__)


class BasePivotTable(ABC):
    """
    Clase base abstracta para implementaciones de tabla pivote
    Proporciona funcionalidad común para Simple y Combined pivot tables
    """
    
    def __init__(self, name: str, description: str):
        """
        Inicializar tabla pivote base
        
        Args:
            name: Nombre de la tabla pivote
            description: Descripción de la funcionalidad
        """
        self.name = name
        self.description = description
        self.pivot_params = {}
        self.filter_params = {}
        self.aggregation_params = {}
        
        # Configuración de funciones de agregación válidas
        self.valid_aggfuncs = [
            'sum', 'mean', 'count', 'min', 'max', 'std', 'var', 'median', 
            'first', 'last', 'size', 'nunique'
        ]
        
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validar que el DataFrame sea adecuado para pivoteo
        
        Args:
            df: DataFrame a validar
            
        Returns:
            bool: True si es válido
            
        Raises:
            ValueError: Si el DataFrame no es válido
        """
        if df is None or df.empty:
            raise ValueError("El DataFrame está vacío o es None")
            
        if len(df.columns) == 0:
            raise ValueError("El DataFrame no tiene columnas")
            
        logger.info(f"DataFrame válido para pivoteo: {df.shape}")
        return True
        
    def validate_columns_exist(self, df: pd.DataFrame, columns: List[str]) -> bool:
        """
        Validar que las columnas especificadas existen en el DataFrame
        
        Args:
            df: DataFrame a validar
            columns: Lista de columnas a verificar
            
        Returns:
            bool: True si todas las columnas existen
            
        Raises:
            ValueError: Si alguna columna no existe
        """
        missing_columns = [col for col in columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Columnas no encontradas: {missing_columns}")
        return True
        
    def normalize_parameter(self, param: Union[str, List[str]]) -> List[str]:
        """
        Normalizar un parámetro a lista de strings
        
        Args:
            param: Parámetro que puede ser string o lista
            
        Returns:
            List[str]: Lista de strings normalizada
        """
        if isinstance(param, str):
            return [param]
        return param
        
    def apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Aplicar filtros al DataFrame antes del pivoteo
        
        Args:
            df: DataFrame original
            filters: Diccionario de filtros a aplicar
            
        Returns:
            pd.DataFrame: DataFrame filtrado
        """
        filtered_df = df.copy()
        
        for column, filter_config in filters.items():
            if column not in filtered_df.columns:
                continue
                
            filter_type = filter_config.get('type', 'equals')
            filter_value = filter_config.get('value')
            filter_operator = filter_config.get('operator', 'and')  # 'and' o 'or'
            
            if filter_type == 'equals':
                filtered_df = filtered_df[filtered_df[column] == filter_value]
            elif filter_type == 'not_equals':
                filtered_df = filtered_df[filtered_df[column] != filter_value]
            elif filter_type == 'contains':
                filtered_df = filtered_df[filtered_df[column].str.contains(str(filter_value), na=False)]
            elif filter_type == 'not_contains':
                filtered_df = filtered_df[~filtered_df[column].str.contains(str(filter_value), na=False)]
            elif filter_type == 'greater_than':
                filtered_df = filtered_df[filtered_df[column] > filter_value]
            elif filter_type == 'less_than':
                filtered_df = filtered_df[filtered_df[column] < filter_value]
            elif filter_type == 'greater_equal':
                filtered_df = filtered_df[filtered_df[column] >= filter_value]
            elif filter_type == 'less_equal':
                filtered_df = filtered_df[filtered_df[column] <= filter_value]
            elif filter_type == 'between':
                if isinstance(filter_value, (list, tuple)) and len(filter_value) == 2:
                    filtered_df = filtered_df[
                        (filtered_df[column] >= filter_value[0]) & 
                        (filtered_df[column] <= filter_value[1])
                    ]
            elif filter_type == 'in_list':
                if isinstance(filter_value, list):
                    filtered_df = filtered_df[filtered_df[column].isin(filter_value)]
            elif filter_type == 'not_in_list':
                if isinstance(filter_value, list):
                    filtered_df = filtered_df[~filtered_df[column].isin(filter_value)]
                    
        return filtered_df
        
    def execute_basic_pivot(self, df: pd.DataFrame, index: List[str], columns: List[str], 
                          values: List[str], aggfunc: Union[str, List[str]], 
                          fill_value: Any = None, dropna: bool = True, 
                          margins: bool = False, margins_name: str = 'All') -> pd.DataFrame:
        """
        Ejecutar pivoteo básico usando pandas pivot_table
        
        Args:
            df: DataFrame a pivotear
            index: Columnas para índice
            columns: Columnas para columnas del pivote
            values: Columnas para valores
            aggfunc: Función(es) de agregación
            fill_value: Valor para rellenar celdas vacías
            dropna: Si eliminar filas con todos los valores NaN
            margins: Si calcular totales
            margins_name: Nombre para la fila/columna de totales
            
        Returns:
            pd.DataFrame: Resultado del pivoteo
        """
        try:
            # Normalizar parámetros
            index = self.normalize_parameter(index)
            columns = self.normalize_parameter(columns)
            values = self.normalize_parameter(values)
            aggfunc = self.normalize_parameter(aggfunc)
            
            # Validar que las columnas existen
            all_columns = set(index + columns + values)
            self.validate_columns_exist(df, list(all_columns))
            
            # Si hay múltiples valores, pivotar cada uno
            if len(values) > 1:
                return self._execute_multi_value_pivot(
                    df, index, columns, values, aggfunc, 
                    fill_value, dropna, margins, margins_name
                )
            else:
                return self._execute_single_value_pivot(
                    df, index, columns, values[0], aggfunc,
                    fill_value, dropna, margins, margins_name
                )
                
        except Exception as e:
            logger.error(f"Error en pivoteo básico: {str(e)}")
            raise
            
    def _execute_single_value_pivot(self, df: pd.DataFrame, index: List[str], 
                                  columns: List[str], value: str, aggfunc: Union[str, List[str]], 
                                  fill_value: Any = None, dropna: bool = True, 
                                  margins: bool = False, margins_name: str = 'All') -> pd.DataFrame:
        """Ejecutar pivoteo para un solo valor"""
        try:
            result_df = pd.pivot_table(
                df, 
                index=index, 
                columns=columns, 
                values=value, 
                aggfunc=aggfunc,
                fill_value=fill_value,
                dropna=dropna,
                margins=margins,
                margins_name=margins_name
            )
            
            # Resetear índice
            result_df = result_df.reset_index()
                
            return result_df
            
        except Exception as e:
            logger.error(f"Error al crear tabla pivote para valor único: {str(e)}")
            return pd.DataFrame()
            
    def _execute_multi_value_pivot(self, df: pd.DataFrame, index: List[str],
                                 columns: List[str], values: List[str], aggfunc: List[str],
                                 fill_value: Any = None, dropna: bool = True,
                                 margins: bool = False, margins_name: str = 'All') -> pd.DataFrame:
        """Ejecutar pivoteo para múltiples valores con estrategia mejorada"""
        try:
            # Estrategia 1: Intentar usar pandas pivot_table con diccionario de agregaciones
            if len(values) <= 3 and len(aggfunc) <= 3:  # Limitar complejidad
                try:
                    # Crear diccionario de agregaciones: {valor: función o [funciones]}
                    if len(aggfunc) == 1 and len(values) > 1:
                        # Mismo valor para todos los valores
                        agg_dict = {val: aggfunc[0] for val in values}
                    elif len(aggfunc) == len(values):
                        # Función diferente para cada valor
                        agg_dict = {values[i]: aggfunc[i] for i in range(len(values))}
                    elif len(aggfunc) < len(values):
                        # Usar la primera función para los valores restantes
                        agg_dict = {}
                        for i, val in enumerate(values):
                            if i < len(aggfunc):
                                agg_dict[val] = aggfunc[i]
                            else:
                                agg_dict[val] = aggfunc[0]
                    else:
                        # Más funciones que valores, usar solo las necesarias
                        agg_dict = {values[i]: aggfunc[i] for i in range(len(values))}
                    
                    # Crear pivote con diccionario de agregaciones
                    result_df = pd.pivot_table(
                        df,
                        index=index,
                        columns=columns,
                        values=values,
                        aggfunc=agg_dict,
                        fill_value=fill_value,
                        dropna=dropna,
                        margins=margins,
                        margins_name=margins_name
                    )
                    
                    # Resetear índice
                    result_df = result_df.reset_index()
                    
                    # Aplanar columnas multi-nivel
                    if isinstance(result_df.columns, pd.MultiIndex):
                        result_df.columns = ['_'.join([str(x) for x in col if str(x) != ''])
                                           for col in result_df.columns.values]
                    
                    logger.info(f"Pivote multi-valor exitoso con pandas: {result_df.shape}")
                    return result_df
                    
                except Exception as pandas_error:
                    logger.warning(f"Pandas pivot falló: {str(pandas_error)}, usando estrategia alternativa")
            
            # Estrategia 2: Merge individual mejorado
            result_dfs = []
            
            for i, value_col in enumerate(values):
                current_aggfunc = aggfunc[i] if i < len(aggfunc) else aggfunc[0]
                
                try:
                    # Crear pivote individual
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
                    
                    # Resetear índice
                    pivot_df = pivot_df.reset_index()
                    
                    # Renombrar columnas (excluyendo índices)
                    new_columns = []
                    for col in pivot_df.columns:
                        if col in index:
                            new_columns.append(col)
                        else:
                            new_columns.append(f"{value_col}_{col}")
                    pivot_df.columns = new_columns
                    
                    result_dfs.append(pivot_df)
                    
                except Exception as e:
                    logger.warning(f"Error pivotando valor '{value_col}': {str(e)}")
                    # Crear DataFrame con estructura básica
                    base_columns = index + [f"{value_col}_{col}" for col in columns
                                         if col != margins_name and str(col) != margins_name]
                    empty_df = pd.DataFrame(columns=base_columns)
                    result_dfs.append(empty_df)
            
            # Merge de resultados individuales con estrategia más robusta
            if result_dfs:
                valid_dfs = [df for df in result_dfs if not df.empty]
                
                if not valid_dfs:
                    return pd.DataFrame()
                
                if len(valid_dfs) == 1:
                    return valid_dfs[0]
                
                # Merge paso a paso con manejo robusto
                result_df = valid_dfs[0].copy()
                
                for i, df_to_merge in enumerate(valid_dfs[1:], 1):
                    try:
                        # Preparar para merge: asegurar que las columnas índice coincidan
                        common_index_cols = [col for col in index if col in result_df.columns and col in df_to_merge.columns]
                        
                        if common_index_cols:
                            # Crear una clave única para el merge
                            result_df['_merge_key'] = result_df[common_index_cols].astype(str).agg('|'.join, axis=1)
                            df_to_merge['_merge_key'] = df_to_merge[common_index_cols].astype(str).agg('|'.join, axis=1)
                            
                            # Merge por clave
                            merged = result_df.merge(df_to_merge, on='_merge_key', how='outer', suffixes=('', f'_dup{i}'))
                            
                            # Limpiar duplicados y la clave temporal
                            merged = merged.drop(columns=['_merge_key'])
                            duplicate_cols = [col for col in merged.columns if col.endswith(f'_dup{i}')]
                            if duplicate_cols:
                                merged = merged.drop(columns=duplicate_cols)
                            
                            result_df = merged
                        else:
                            # Si no hay índices comunes, concatenar
                            result_df = pd.concat([result_df, df_to_merge], ignore_index=True, sort=False)
                            
                    except Exception as merge_error:
                        logger.warning(f"Error en merge {i}: {str(merge_error)}, usando concatenación")
                        result_df = pd.concat([result_df, df_to_merge], ignore_index=True, sort=False)
                
                return result_df
            else:
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error crítico en pivoteo multi-valor: {str(e)}")
            return pd.DataFrame()
            
    @abstractmethod
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Ejecutar la tabla pivote con parámetros específicos
        
        Args:
            df: DataFrame a pivotear
            parameters: Parámetros específicos de la implementación
            
        Returns:
            pd.DataFrame: Resultado del pivoteo
        """
        pass
        
    def get_description(self) -> str:
        """Obtener descripción de la tabla pivote"""
        return self.description
        
    def get_name(self) -> str:
        """Obtener nombre de la tabla pivote"""
        return self.name


class SimplePivotTable(BasePivotTable):
    """
    Implementación de tabla pivote simple
    Una columna para filas, una para columnas, una para valores, una función de agregación
    """
    
    def __init__(self):
        """Inicializar tabla pivote simple"""
        super().__init__(
            "simple_pivot",
            "Pivoteo simple: una columna para filas, una para columnas, una para valores"
        )
        
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Ejecutar pivoteo simple
        
        Args:
            df: DataFrame a pivotear
            parameters: Parámetros del pivoteo simple
                      - index: Columna para filas
                      - columns: Columna para columnas
                      - values: Columna para valores
                      - aggfunc: Función de agregación
                      - filters: Filtros a aplicar (opcional)
                      
        Returns:
            pd.DataFrame: Resultado del pivoteo
        """
        if parameters is None:
            parameters = {}
            
        try:
            # Validar DataFrame
            self.validate_data(df)
            
            # Obtener parámetros
            index = parameters.get('index')
            columns = parameters.get('columns') 
            values = parameters.get('values')
            aggfunc = parameters.get('aggfunc', 'mean')
            filters = parameters.get('filters', {})
            fill_value = parameters.get('fill_value')
            dropna = parameters.get('dropna', True)
            margins = parameters.get('margins', False)
            margins_name = parameters.get('margins_name', 'All')
            
            # Validar parámetros requeridos
            if not all([index, columns, values]):
                raise ValueError("Los parámetros index, columns y values son requeridos")
                
            # Normalizar a listas
            index = self.normalize_parameter(index)
            columns = self.normalize_parameter(columns)
            values = self.normalize_parameter(values)
            aggfunc = self.normalize_parameter(aggfunc)
            
            # Aplicar filtros si existen
            if filters:
                df = self.apply_filters(df, filters)
                logger.info(f" filtros aplicados, DataFrame resultante: {df.shape}")
            
            # Ejecutar pivoteo
            result_df = self.execute_basic_pivot(
                df, index, columns, values, aggfunc,
                fill_value, dropna, margins, margins_name
            )
            
            # Guardar parámetros
            self.pivot_params = {
                'index': index,
                'columns': columns,
                'values': values,
                'aggfunc': aggfunc,
                'filters': filters,
                'fill_value': fill_value,
                'dropna': dropna,
                'margins': margins,
                'margins_name': margins_name,
                'result_shape': result_df.shape
            }
            
            logger.info(f"Pivoteo simple completado, shape: {result_df.shape}")
            return result_df
            
        except Exception as e:
            logger.error(f"Error en pivoteo simple: {str(e)}")
            raise


class CombinedPivotTable(BasePivotTable):
    """
    Implementación de tabla pivote combinada
    Múltiples columnas para filas/columnas/valores, múltiples funciones de agregación
    """
    
    def __init__(self):
        """Inicializar tabla pivote combinada"""
        super().__init__(
            "combined_pivot",
            "Pivoteo combinado: múltiples columnas para filas, columnas, valores y agregaciones"
        )
        
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Ejecutar pivoteo combinado
        
        Args:
            df: DataFrame a pivotear
            parameters: Parámetros del pivoteo combinado
                      - index: Lista de columnas para filas
                      - columns: Lista de columnas para columnas
                      - values: Lista de columnas para valores
                      - aggfuncs: Lista de funciones de agregación
                      - filters: Filtros múltiples a aplicar (opcional)
                      
        Returns:
            pd.DataFrame: Resultado del pivoteo
        """
        if parameters is None:
            parameters = {}
            
        try:
            # Validar DataFrame
            self.validate_data(df)
            
            # Obtener parámetros
            index = parameters.get('index', [])
            columns = parameters.get('columns', [])
            values = parameters.get('values', [])
            aggfuncs = parameters.get('aggfuncs', ['mean'])
            filters = parameters.get('filters', {})
            fill_value = parameters.get('fill_value')
            dropna = parameters.get('dropna', True)
            margins = parameters.get('margins', False)
            margins_name = parameters.get('margins_name', 'All')
            
            # Normalizar a listas
            index = self.normalize_parameter(index)
            columns = self.normalize_parameter(columns)
            values = self.normalize_parameter(values)
            aggfuncs = self.normalize_parameter(aggfuncs)
            
            # Validar que hay al menos una configuración
            if not any([index, columns, values]):
                raise ValueError("Al menos una de las opciones (index, columns, values) debe estar configurada")
            
            # Validar funciones de agregación
            invalid_aggfuncs = [f for f in aggfuncs if f not in self.valid_aggfuncs]
            if invalid_aggfuncs:
                raise ValueError(f"Funciones de agregación no válidas: {invalid_aggfuncs}")
            
            # Aplicar filtros múltiples si existen
            if filters:
                df = self.apply_filters(df, filters)
                logger.info(f"Filtros múltiples aplicados, DataFrame resultante: {df.shape}")
            
            # Ejecutar pivoteo
            result_df = self.execute_basic_pivot(
                df, index, columns, values, aggfuncs,
                fill_value, dropna, margins, margins_name
            )
            
            # Guardar parámetros
            self.pivot_params = {
                'index': index,
                'columns': columns,
                'values': values,
                'aggfuncs': aggfuncs,
                'filters': filters,
                'fill_value': fill_value,
                'dropna': dropna,
                'margins': margins,
                'margins_name': margins_name,
                'result_shape': result_df.shape
            }
            
            logger.info(f"Pivoteo combinado completado, shape: {result_df.shape}")
            return result_df
            
        except Exception as e:
            logger.error(f"Error en pivoteo combinado: {str(e)}")
            raise