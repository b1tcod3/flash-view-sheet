"""
Servicio de Tablas Pivote - PivotService

Servicio centralizado para operaciones de tablas pivote
en Flash View Sheet.
"""

import pandas as pd
from PySide6.QtWidgets import QMessageBox


class PivotService:
    """
    Servicio para operaciones de tablas pivote.
    
    Responsabilidades:
    - Crear tablas pivote simples y combinadas
    - Crear agregaciones cuando el pivote no es posible
    - Gestión de configuraciones de pivote
    """
    
    def __init__(self):
        """Inicializar el servicio de pivote"""
        self.last_result = None
        self.last_config = None
    
    def create_simple_pivot(self, df, index, columns=None, values=None, aggfunc='sum'):
        """
        Crear una tabla pivote simple.
        
        Args:
            df: DataFrame source
            index: Columna(s) para índice
            columns: Columna(s) para columnas pivote
            values: Columna(s) a agregar
            aggfunc: Función de agregación
        
        Returns:
            DataFrame con la tabla pivote
        """
        if df is None or df.empty:
            return None
        
        try:
            pivot_df = pd.pivot_table(
                df,
                index=index,
                columns=columns,
                values=values,
                aggfunc=aggfunc,
                margins=False,
                dropna=True
            )
            
            self.last_result = pivot_df
            self.last_config = {
                'type': 'simple_pivot',
                'index': index,
                'columns': columns,
                'values': values,
                'aggfunc': aggfunc
            }
            
            return pivot_df
            
        except Exception as e:
            raise Exception(f"Error creando tabla pivote: {str(e)}")
    
    def create_combined_pivot(self, df, index, columns, values, aggfuncs=None):
        """
        Crear una tabla pivote combinada con múltiples valores y funciones.
        
        Args:
            df: DataFrame source
            index: Columna(s) para índice
            columns: Columna(s) para columnas pivote
            values: Lista de columnas a agregar
            aggfuncs: Lista de funciones de agregación
        
        Returns:
            DataFrame con la tabla pivote combinada
        """
        if df is None or df.empty:
            return None
        
        if aggfuncs is None:
            aggfuncs = ['sum', 'mean', 'count']
        
        try:
            result_dfs = []
            
            for val_col in values:
                for agg in aggfuncs:
                    try:
                        pivot_df = pd.pivot_table(
                            df,
                            index=index,
                            columns=columns,
                            values=val_col,
                            aggfunc=agg,
                            margins=False,
                            dropna=True
                        )
                        
                        # Renombrar columnas con sufijo
                        if pivot_df is not None and not pivot_df.empty:
                            pivot_df = pivot_df.add_suffix(f'_{agg}')
                            result_dfs.append(pivot_df)
                            
                    except Exception:
                        continue
            
            if result_dfs:
                # Combinar todos los DataFrames
                combined = pd.concat(result_dfs, axis=1)
                self.last_result = combined
                self.last_config = {
                    'type': 'combined_pivot',
                    'index': index,
                    'columns': columns,
                    'values': values,
                    'aggfuncs': aggfuncs
                }
                return combined
            
            return None
            
        except Exception as e:
            raise Exception(f"Error creando tabla pivote combinada: {str(e)}")
    
    def create_simple_aggregation(self, df, index, values, aggfunc='mean'):
        """
        Crear agregación simple por filas cuando no hay columnas para pivot.
        
        Args:
            df: DataFrame source
            index: Columna(s) para grouping
            values: Columna(s) a agregar
            aggfunc: Función de agregación
        
        Returns:
            DataFrame agregado
        """
        if df is None or df.empty:
            return None
        
        try:
            if isinstance(index, str):
                index = [index]
            if isinstance(values, str):
                values = [values]
            
            agg_dict = {col: aggfunc for col in values}
            
            agg_df = df.groupby(index).agg(agg_dict).reset_index()
            
            # Simplificar nombres de columnas
            if aggfunc != 'sum':
                new_cols = []
                for col in agg_df.columns:
                    if col in index:
                        new_cols.append(col)
                    else:
                        new_cols.append(f"{col}_{aggfunc}")
                agg_df.columns = new_cols
            
            self.last_result = agg_df
            self.last_config = {
                'type': 'simple_aggregation',
                'index': index,
                'values': values,
                'aggfunc': aggfunc
            }
            
            return agg_df
            
        except Exception as e:
            raise Exception(f"Error creando agregación simple: {str(e)}")
    
    def create_fallback_aggregation(self, df, index, values, aggfunc='mean'):
        """
        Crear agregación de fallback cuando el pivote no es posible.
        
        Args:
            df: DataFrame source
            index: Columna(s) para grouping (puede ser vacío para agregación global)
            values: Columna(s) a agregar
            aggfunc: Función de agregación
        
        Returns:
            DataFrame agregado
        """
        if df is None or df.empty:
            return None
        
        try:
            # Normalizar index
            if index:
                if isinstance(index, str):
                    groupby_columns = [index]
                elif isinstance(index, list):
                    groupby_columns = index[:2]  # Limitar a 2 columnas para evitar dimensionalidad excesiva
                else:
                    groupby_columns = []
            else:
                groupby_columns = []
            
            # Normalizar values
            if isinstance(values, str):
                values_columns = [values]
            elif isinstance(values, list):
                values_columns = values
            else:
                values_columns = []
            
            # Si no hay valores específicos, usar columnas numéricas
            if not values_columns:
                values_columns = [col for col in df.columns 
                                if df[col].dtype in ['int64', 'float64']]
                if not values_columns:
                    values_columns = df.columns.tolist()
            
            # Filtrar solo columnas que existen
            values_columns = [col for col in values_columns if col in df.columns]
            
            if not values_columns:
                raise ValueError("No se encontraron columnas válidas para agregar")
            
            # Crear diccionario de agregación
            if isinstance(aggfunc, list):
                agg_function = aggfunc[0] if aggfunc else 'mean'
            else:
                agg_function = aggfunc if aggfunc else 'mean'
            
            agg_dict = {col: agg_function for col in values_columns}
            
            if groupby_columns:
                # Agregación por grupos
                agg_df = df.groupby(groupby_columns)[values_columns].agg(agg_function).reset_index()
            else:
                # Agregación global
                agg_df = df[values_columns].agg(agg_function).to_frame().T.reset_index(drop=True)
            
            self.last_result = agg_df
            self.last_config = {
                'type': 'fallback_aggregation',
                'index': groupby_columns,
                'values': values_columns,
                'aggfunc': agg_function
            }
            
            return agg_df
            
        except Exception as e:
            raise Exception(f"Error creando agregación de fallback: {str(e)}")
    
    def execute_pivot_with_fallback(self, df, config):
        """
        Ejecutar pivote con fallback a agregación si falla.
        
        Args:
            df: DataFrame source
            config: Configuración de pivote
        
        Returns:
            DataFrame con el resultado
        """
        if df is None or df.empty:
            return None
        
        is_pivot = config.get('is_pivot', True)
        
        if is_pivot:
            # Intentar pivote primero
            try:
                if config.get('columns') or config.get('pivot_columns'):
                    # Es un pivote con columnas
                    result = self.create_combined_pivot(
                        df,
                        config.get('index', config.get('rows')),
                        config.get('columns', config.get('pivot_columns')),
                        config.get('values', []),
                        config.get('aggfuncs', [config.get('aggfunc', 'mean')])
                    )
                else:
                    # Es una agregación simple sin columnas pivot
                    result = self.create_simple_aggregation(
                        df,
                        config.get('index', config.get('rows')),
                        config.get('values', []),
                        config.get('aggfunc', 'mean')
                    )
                
                if result is not None and not result.empty:
                    return result
                    
            except Exception as e:
                print(f"Pivote falló, usando agregación: {str(e)}")
        
        # Fallback a agregación
        return self.create_fallback_aggregation(
            df,
            config.get('index', config.get('rows')),
            config.get('values', []),
            config.get('aggfunc', config.get('aggfuncs', ['mean']))
        )
    
    def get_crosstab(self, df, index, columns, normalize=False):
        """
        Crear tabla de contingencia (crosstab).
        
        Args:
            df: DataFrame source
            index: Columna(s) para filas
            columns: Columna para columnas
            normalize: Si normalizar los valores
        
        Returns:
            DataFrame crosstab
        """
        if df is None or df.empty:
            return None
        
        try:
            if normalize:
                crosstab_df = pd.crosstab(
                    df[index],
                    df[columns],
                    normalize='all'
                ) * 100  # Porcentajes
                crosstab_df = crosstab_df.round(2)
            else:
                crosstab_df = pd.crosstab(
                    df[index],
                    df[columns]
                )
            
            self.last_result = crosstab_df
            self.last_config = {
                'type': 'crosstab',
                'index': index,
                'columns': columns,
                'normalize': normalize
            }
            
            return crosstab_df
            
        except Exception as e:
            raise Exception(f"Error creando crosstab: {str(e)}")
    
    def get_pivot_stats(self):
        """Obtener estadísticas del último pivote/aggregación"""
        if self.last_result is None:
            return None
        
        return {
            'rows': len(self.last_result),
            'columns': len(self.last_result.columns),
            'shape': self.last_result.shape,
            'config': self.last_config
        }
    
    # ==================== MÉTODOS DE INTERFAZ SIMPLIFICADA ====================
    
    def execute_simple(self, df, config):
        """
        Ejecutar pivote simple con fallback a agregación.
        
        Args:
            df: DataFrame source
            config: Configuración con keys: index, values, aggfunc, is_pivot
        
        Returns:
            DataFrame resultado
        """
        is_pivot = config.get('is_pivot', True)
        
        if is_pivot:
            try:
                result = self.create_simple_pivot(
                    df,
                    index=config.get('index', config.get('rows')),
                    columns=config.get('columns'),
                    values=config.get('values'),
                    aggfunc=config.get('aggfunc', 'sum')
                )
                if result is not None and not result.empty:
                    return result
            except Exception as e:
                print(f"Pivote simple falló: {e}")
        
        # Fallback a agregación simple
        return self.create_simple_aggregation(
            df,
            index=config.get('index', config.get('rows')),
            values=config.get('values'),
            aggfunc=config.get('aggfunc', 'mean')
        )
    
    def execute_combined(self, df, config):
        """
        Ejecutar pivote combinada con fallback a agregación.
        
        Args:
            df: DataFrame source
            config: Configuración con keys: index, columns, values, aggfuncs
        
        Returns:
            DataFrame resultado
        """
        try:
            result = self.create_combined_pivot(
                df,
                index=config.get('index', config.get('rows')),
                columns=config.get('columns'),
                values=config.get('values', []),
                aggfuncs=config.get('aggfuncs', config.get('aggfunc', ['sum', 'mean']))
            )
            if result is not None and not result.empty:
                return result
        except Exception as e:
            print(f"Pivote combinada falló: {e}")
        
        # Fallback a agregación
        return self.create_fallback_aggregation(
            df,
            index=config.get('index', config.get('rows')),
            values=config.get('values', []),
            aggfunc=config.get('aggfunc', config.get('aggfuncs', ['mean']))
        )
    
    # ==================== UTILIDADES ====================
    
    def get_aggregation_functions(self):
        """Obtener lista de funciones de agregación disponibles"""
        return [
            ('Suma', 'sum'),
            ('Promedio', 'mean'),
            ('Mediana', 'median'),
            ('Mínimo', 'min'),
            ('Máximo', 'max'),
            ('Desviación estándar', 'std'),
            ('Recuento', 'count'),
            ('Primer valor', 'first'),
            ('Último valor', 'last'),
        ]
    
    def validate_pivot_config(self, df, config):
        """
        Validar configuración de pivote.
        
        Args:
            df: DataFrame source
            config: Configuración a validar
        
        Returns:
            Dict con is_valid y message
        """
        if df is None or df.empty:
            return {'is_valid': False, 'message': 'No hay datos'}
        
        index = config.get('index', config.get('rows', []))
        values = config.get('values', [])
        
        if isinstance(index, str):
            index = [index]
        if isinstance(values, str):
            values = [values]
        
        # Verificar columnas de índice
        missing_index = [col for col in index if col not in df.columns]
        if missing_index:
            return {
                'is_valid': False,
                'message': f"Faltan columnas de índice: {', '.join(missing_index)}"
            }
        
        # Verificar columnas de valores
        if values:
            missing_values = [col for col in values if col not in df.columns]
            if missing_values:
                return {
                    'is_valid': False,
                    'message': f"Faltan columnas de valores: {', '.join(missing_values)}"
                }
        
        # Verificar tipos de datos para valores
        numeric_cols = [col for col in values if col in df.columns 
                       if df[col].dtype in ['int64', 'float64']]
        if not numeric_cols and values:
            return {
                'is_valid': False,
                'message': 'Las columnas de valores no son numéricas'
            }
        
        return {'is_valid': True, 'message': 'Configuración válida'}
