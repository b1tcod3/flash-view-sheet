"""
Servicio de Filtros - FilterService

Servicio centralizado para operaciones de filtrado de datos
en Flash View Sheet.
"""

import pandas as pd
from PySide6.QtWidgets import QMessageBox


class FilterService:
    """
    Servicio para operaciones de filtrado de datos.
    
    Responsabilidades:
    - Aplicar filtros a DataFrames
    - Limpiar filtros
    - Gestión de estados de filtro
    """
    
    def __init__(self):
        """Inicializar el servicio de filtros"""
        self.filter_history = []
    
    def apply_filter(self, df, column, term, case_sensitive=False):
        """
        Aplicar filtro a un DataFrame.
        
        Args:
            df: DataFrame a filtrar
            column: Nombre de la columna a filtrar
            term: Término de búsqueda
            case_sensitive: Si la búsqueda es sensible a mayúsculas
        
        Returns:
            DataFrame filtrado
        """
        if df is None or df.empty:
            return None
        
        if column not in df.columns:
            raise ValueError(f"La columna '{column}' no existe en el DataFrame")
        
        if not term:
            return df.copy()
        
        try:
            if case_sensitive:
                mask = df[column].astype(str).str.contains(term, regex=False)
            else:
                mask = df[column].astype(str).str.lower().str.contains(term.lower(), regex=False)
            
            filtered_df = df[mask].copy()
            
            # Guardar en historial
            self.filter_history.append({
                'column': column,
                'term': term,
                'case_sensitive': case_sensitive,
                'original_rows': len(df),
                'filtered_rows': len(filtered_df)
            })
            
            return filtered_df
            
        except Exception as e:
            raise Exception(f"Error aplicando filtro: {str(e)}")
    
    def apply_regex_filter(self, df, column, pattern):
        """
        Aplicar filtro con expresión regular.
        
        Args:
            df: DataFrame a filtrar
            column: Nombre de la columna
            pattern: Patrón de expresión regular
        
        Returns:
            DataFrame filtrado
        """
        if df is None or df.empty:
            return None
        
        if column not in df.columns:
            raise ValueError(f"La columna '{column}' no existe en el DataFrame")
        
        try:
            mask = df[column].astype(str).str.contains(pattern, regex=True)
            filtered_df = df[mask].copy()
            
            self.filter_history.append({
                'column': column,
                'term': pattern,
                'regex': True,
                'original_rows': len(df),
                'filtered_rows': len(filtered_df)
            })
            
            return filtered_df
            
        except Exception as e:
            raise Exception(f"Error aplicando filtro regex: {str(e)}")
    
    def apply_numeric_filter(self, df, column, operator, value):
        """
        Aplicar filtro numérico.
        
        Args:
            df: DataFrame a filtrar
            column: Nombre de la columna
            operator: Operador ('>', '<', '>=', '<=', '==', '!=')
            value: Valor de comparación
        
        Returns:
            DataFrame filtrado
        """
        if df is None or df.empty:
            return None
        
        if column not in df.columns:
            raise ValueError(f"La columna '{column}' no existe en el DataFrame")
        
        try:
            value = float(value)
            
            if operator == '>':
                mask = df[column] > value
            elif operator == '<':
                mask = df[column] < value
            elif operator == '>=':
                mask = df[column] >= value
            elif operator == '<=':
                mask = df[column] <= value
            elif operator == '==':
                mask = df[column] == value
            elif operator == '!=':
                mask = df[column] != value
            else:
                raise ValueError(f"Operador desconocido: {operator}")
            
            filtered_df = df[mask].copy()
            
            self.filter_history.append({
                'column': column,
                'operator': operator,
                'value': value,
                'type': 'numeric',
                'original_rows': len(df),
                'filtered_rows': len(filtered_df)
            })
            
            return filtered_df
            
        except Exception as e:
            raise Exception(f"Error aplicando filtro numérico: {str(e)}")
    
    def apply_date_filter(self, df, column, start_date=None, end_date=None):
        """
        Aplicar filtro por rango de fechas.
        
        Args:
            df: DataFrame a filtrar
            column: Nombre de la columna de fecha
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
        
        Returns:
            DataFrame filtrado
        """
        if df is None or df.empty:
            return None
        
        if column not in df.columns:
            raise ValueError(f"La columna '{column}' no existe en el DataFrame")
        
        try:
            # Convertir a datetime si no lo es
            if not pd.api.types.is_datetime64_any_dtype(df[column]):
                df[column] = pd.to_datetime(df[column], errors='coerce')
            
            mask = pd.Series([True] * len(df), index=df.index)
            
            if start_date:
                start = pd.to_datetime(start_date)
                mask = mask & (df[column] >= start)
            
            if end_date:
                end = pd.to_datetime(end_date)
                mask = mask & (df[column] <= end)
            
            filtered_df = df[mask].copy()
            
            self.filter_history.append({
                'column': column,
                'start_date': start_date,
                'end_date': end_date,
                'type': 'date',
                'original_rows': len(df),
                'filtered_rows': len(filtered_df)
            })
            
            return filtered_df
            
        except Exception as e:
            raise Exception(f"Error aplicando filtro de fecha: {str(e)}")
    
    def apply_value_filter(self, df, column, values, exclude=False):
        """
        Filtrar por valores específicos en una columna.
        
        Args:
            df: DataFrame a filtrar
            column: Nombre de la columna
            values: Lista de valores a filtrar
            exclude: Si True, excluye los valores en lugar de incluirlos
        
        Returns:
            DataFrame filtrado
        """
        if df is None or df.empty:
            return None
        
        if column not in df.columns:
            raise ValueError(f"La columna '{column}' no existe en el DataFrame")
        
        try:
            if exclude:
                mask = ~df[column].isin(values)
            else:
                mask = df[column].isin(values)
            
            filtered_df = df[mask].copy()
            
            self.filter_history.append({
                'column': column,
                'values': values,
                'exclude': exclude,
                'type': 'value_list',
                'original_rows': len(df),
                'filtered_rows': len(filtered_df)
            })
            
            return filtered_df
            
        except Exception as e:
            raise Exception(f"Error aplicando filtro de valores: {str(e)}")
    
    def clear_filters(self):
        """Limpiar el historial de filtros"""
        self.filter_history = []
    
    def get_filter_info(self):
        """Obtener información sobre el último filtro aplicado"""
        if self.filter_history:
            return self.filter_history[-1]
        return None
    
    def get_filter_summary(self):
        """Obtener resumen de todos los filtros aplicados"""
        if not self.filter_history:
            return "No hay filtros aplicados."
        
        summary = []
        for i, f in enumerate(self.filter_history, 1):
            if 'term' in f:
                summary.append(f"{i}. Columna '{f['column']}' contiene '{f['term']}'")
            elif 'operator' in f:
                summary.append(f"{i}. Columna '{f['column']}' {f['operator']} {f['value']}")
            elif 'start_date' in f:
                dates = f"{f['start_date']} - {f['end_date']}" if f['end_date'] else f['start_date']
                summary.append(f"{i}. Columna '{f['column']}' entre {dates}")
            elif 'values' in f:
                action = "excluye" if f['exclude'] else "incluye"
                summary.append(f"{i}. Columna '{f['column']}' {action} {len(f['values'])} valores")
        
        return "\n".join(summary)
    
    def get_unique_values(self, df, column, limit=100):
        """Obtener valores únicos de una columna"""
        if df is None or column not in df.columns:
            return []
        
        try:
            unique = df[column].dropna().unique()
            if len(unique) > limit:
                return list(unique[:limit]) + [f"... y {len(unique) - limit} más"]
            return list(unique)
        except Exception:
            return []
    
    def get_column_stats(self, df, column):
        """Obtener estadísticas de una columna para ayudar en filtrado"""
        if df is None or column not in df.columns:
            return None
        
        col = df[column]
        
        stats = {
            'count': len(col),
            'null_count': col.isna().sum(),
            'unique_count': col.nunique(),
            'dtype': str(col.dtype)
        }
        
        # Para columnas numéricas
        if pd.api.types.is_numeric_dtype(col):
            stats['min'] = col.min()
            stats['max'] = col.max()
            stats['mean'] = col.mean()
            stats['median'] = col.median()
        
        # Para columnas de texto
        if pd.api.types.is_string_dtype(col):
            stats['empty_count'] = (col == '').sum()
            stats['avg_length'] = col.astype(str).map(len).mean()
        
        return stats
