"""
Transformaciones de codificación categórica
Incluye label encoding, one-hot encoding, ordinal encoding y target encoding
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union, Tuple
import logging
from datetime import datetime
from sklearn.preprocessing import LabelEncoder as SklearnLabelEncoder

from .base_transformation import BaseTransformation

# Configurar logging
logger = logging.getLogger(__name__)


class CategoricalEncodingTransformation(BaseTransformation):
    """
    Clase base para transformaciones de codificación categórica
    """
    
    def __init__(self, name: str, description: str, columns: Union[str, List[str]]):
        """
        Inicializar transformación de codificación categórica
        
        Args:
            name: Nombre de la transformación
            description: Descripción de la transformación
            columns: Columna o lista de columnas a codificar
        """
        super().__init__(name, description)
        self.columns = [columns] if isinstance(columns, str) else columns
        
        # Mapeos de valores para codificación reversa
        self._encoding_mappings = {}
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """Validar que las columnas sean categóricas o de texto"""
        super().validate_data(df)
        
        # Verificar que las columnas existen
        missing_columns = [col for col in self.columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Columnas no encontradas: {missing_columns}")
        
        # Verificar que las columnas son categóricas o de texto
        non_categorical_columns = []
        for col in self.columns:
            if col in df.columns and not (pd.api.types.is_categorical_dtype(df[col]) or 
                                        pd.api.types.is_object_dtype(df[col]) or
                                        pd.api.types.is_string_dtype(df[col])):
                non_categorical_columns.append(col)
        
        if non_categorical_columns:
            raise ValueError(f"Las siguientes columnas no son categóricas o de texto: {non_categorical_columns}")
        
        return True
    
    def _get_unique_values(self, series: pd.Series) -> List[Any]:
        """Obtener valores únicos de una serie, incluyendo NaN"""
        if pd.api.types.is_categorical_dtype(series):
            return list(series.cat.categories)
        else:
            # Incluir NaN como un valor único para manejarlo explícitamente
            unique_values = series.dropna().unique().tolist()
            if series.isna().any():
                unique_values.append(None)  # Representar NaN como None
            return unique_values


class LabelEncodingTransformation(CategoricalEncodingTransformation):
    """
    Transformación de label encoding (codificación con etiquetas numéricas)
    """
    
    def __init__(self, columns: Union[str, List[str]], handle_unknown: str = 'error', 
                 handle_missing: str = 'error'):
        """
        Inicializar transformación de label encoding
        
        Args:
            columns: Columna o lista de columnas a codificar
            handle_unknown: Cómo manejar valores desconocidos ('error', 'use_encoded_value', 'ignore')
            handle_missing: Cómo manejar valores faltantes ('error', 'use_encoded_value', 'ignore')
        """
        self.handle_unknown = handle_unknown
        self.handle_missing = handle_missing
        
        columns_list = [columns] if isinstance(columns, str) else columns
        description = f"Label encoding en {len(columns_list)} columna(s)"
        
        super().__init__("label_encoding", description, columns_list)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar label encoding"""
        if parameters is None:
            parameters = {}
            
        try:
            df_encoded = df.copy()
            
            handle_unknown = parameters.get('handle_unknown', self.handle_unknown)
            handle_missing = parameters.get('handle_missing', self.handle_missing)
            columns = parameters.get('columns', self.columns)
            
            for column in columns:
                if column not in df_encoded.columns:
                    raise ValueError(f"Columna '{column}' no existe")
                
                series = df_encoded[column]
                
                # Crear y entrenar el codificador
                encoder = SklearnLabelEncoder()
                encoder.fit(series.astype(str))  # Convertir todo a string para manejar todos los tipos
                
                # Guardar el mapeo para posible decodificación
                self._encoding_mappings[column] = {
                    'classes': encoder.classes_.tolist(),
                    'handle_unknown': handle_unknown,
                    'handle_missing': handle_missing
                }
                
                # Aplicar codificación
                encoded_values = encoder.transform(series.astype(str))
                df_encoded[column] = encoded_values
                
                # Manejar valores desconocidos
                if handle_unknown == 'use_encoded_value':
                    # Ya manejado por el transformador
                    pass
                elif handle_unknown == 'ignore':
                    # Por ahora, no tenemos una implementación específica
                    logger.warning(f"Manejo de valores desconocidos 'ignore' no implementado completamente")
                
                # Manejar valores faltantes
                if series.isna().any():
                    if handle_missing == 'use_encoded_value':
                        # Reemplazar valores NaN con -1
                        mask = series.isna()
                        df_encoded.loc[mask, column] = -1
                    elif handle_missing == 'ignore':
                        # Mantener NaN
                        mask = series.isna()
                        df_encoded.loc[mask, column] = np.nan
                
                logger.info(f"Label encoding aplicado a columna '{column}'")
            
            return df_encoded
            
        except Exception as e:
            logger.error(f"Error en label encoding: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de label encoding"""
        handle_unknown = parameters.get('handle_unknown', self.handle_unknown)
        handle_missing = parameters.get('handle_missing', self.handle_missing)
        
        if handle_unknown not in ['error', 'use_encoded_value', 'ignore']:
            return False
        
        if handle_missing not in ['error', 'use_encoded_value', 'ignore']:
            return False
        
        return True
    
    def decode_values(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        Decodificar valores codificados a sus valores originales
        
        Args:
            df: DataFrame con valores codificados
            column: Columna a decodificar
            
        Returns:
            DataFrame con valores decodificados
        """
        if column not in self._encoding_mappings:
            raise ValueError(f"No hay mapeo de codificación para la columna '{column}'")
        
        mapping = self._encoding_mappings[column]
        classes = mapping['classes']
        
        # Crear un DataFrame de copia
        df_decoded = df.copy()
        
        # Mapear valores codificados a valores originales
        df_decoded[column] = df_decoded[column].map(
            {i: class_val for i, class_val in enumerate(classes)}
        )
        
        # Manejar valores especiales
        mask = df[column] == -1
        if mask.any():
            df_decoded.loc[mask, column] = None  # Valores faltantes
        
        return df_decoded


class OneHotEncodingTransformation(CategoricalEncodingTransformation):
    """
    Transformación de one-hot encoding (codificación one-hot)
    """
    
    def __init__(self, columns: Union[str, List[str]], drop_first: bool = False, 
                 prefix: str = None, prefix_sep: str = "_", handle_unknown: str = 'ignore',
                 handle_missing: str = 'ignore'):
        """
        Inicializar transformación de one-hot encoding
        
        Args:
            columns: Columna o lista de columnas a codificar
            drop_first: Si descartar la primera categoría (evita multicolinealidad)
            prefix: Prefijo para nombres de nuevas columnas (por defecto usa nombre de columna)
            prefix_sep: Separador entre prefijo y nombre de categoría
            handle_unknown: Cómo manejar valores desconocidos ('error', 'ignore')
            handle_missing: Cómo manejar valores faltantes ('error', 'ignore')
        """
        self.drop_first = drop_first
        self.prefix = prefix
        self.prefix_sep = prefix_sep
        self.handle_unknown = handle_unknown
        self.handle_missing = handle_missing
        
        columns_list = [columns] if isinstance(columns, str) else columns
        description = f"One-hot encoding en {len(columns_list)} columna(s)"
        
        super().__init__("one_hot_encoding", description, columns_list)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar one-hot encoding"""
        if parameters is None:
            parameters = {}
            
        try:
            df_encoded = df.copy()
            
            drop_first = parameters.get('drop_first', self.drop_first)
            prefix = parameters.get('prefix', self.prefix)
            prefix_sep = parameters.get('prefix_sep', self.prefix_sep)
            handle_unknown = parameters.get('handle_unknown', self.handle_unknown)
            handle_missing = parameters.get('handle_missing', self.handle_missing)
            columns = parameters.get('columns', self.columns)
            
            for column in columns:
                if column not in df_encoded.columns:
                    raise ValueError(f"Columna '{column}' no existe")
                
                series = df_encoded[column]
                
                # Manejar valores faltantes antes de codificar
                if series.isna().any():
                    if handle_missing == 'error':
                        raise ValueError(f"La columna '{column}' contiene valores faltantes")
                    elif handle_missing == 'ignore':
                        # Rellenar con una categoría especial
                        series = series.fillna('__MISSING__')
                
                # Obtener valores únicos para la codificación
                unique_values = self._get_unique_values(series)
                
                # Guardar el mapeo para posible decodificación
                self._encoding_mappings[column] = {
                    'unique_values': unique_values,
                    'drop_first': drop_first,
                    'prefix': prefix or column,
                    'prefix_sep': prefix_sep,
                    'handle_unknown': handle_unknown,
                    'handle_missing': handle_missing
                }
                
                # Aplicar one-hot encoding usando pandas get_dummies
                prefix_for_dummies = prefix if prefix else column
                dummies = pd.get_dummies(series, prefix=prefix_for_dummies, 
                                       prefix_sep=prefix_sep, 
                                       drop_first=drop_first)
                
                # Combinar con el DataFrame original
                df_encoded = pd.concat([df_encoded, dummies], axis=1)
                
                # Eliminar la columna original
                df_encoded = df_encoded.drop(column, axis=1)
                
                logger.info(f"One-hot encoding aplicado a columna '{column}', creando {len(dummies.columns)} nuevas columnas")
            
            return df_encoded
            
        except Exception as e:
            logger.error(f"Error en one-hot encoding: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de one-hot encoding"""
        drop_first = parameters.get('drop_first', self.drop_first)
        prefix_sep = parameters.get('prefix_sep', self.prefix_sep)
        handle_unknown = parameters.get('handle_unknown', self.handle_unknown)
        handle_missing = parameters.get('handle_missing', self.handle_missing)
        
        if not isinstance(drop_first, bool):
            return False
        
        if not isinstance(prefix_sep, str):
            return False
        
        if handle_unknown not in ['error', 'ignore']:
            return False
        
        if handle_missing not in ['error', 'ignore']:
            return False
        
        return True


class OrdinalEncodingTransformation(CategoricalEncodingTransformation):
    """
    Transformación de ordinal encoding (codificación ordinal)
    """
    
    def __init__(self, columns: Union[str, List[str]], encoding_map: Dict[str, List[Tuple]] = None,
                 handle_unknown: str = 'error', handle_missing: str = 'error'):
        """
        Inicializar transformación de ordinal encoding
        
        Args:
            columns: Columna o lista de columnas a codificar
            encoding_map: Diccionario con mapeos de valores a códigos (ej: {'col1': [('A', 1), ('B', 2), ('C', 3)]})
            handle_unknown: Cómo manejar valores desconocidos ('error', 'use_encoded_value', 'ignore')
            handle_missing: Cómo manejar valores faltantes ('error', 'use_encoded_value', 'ignore')
        """
        self.encoding_map = encoding_map or {}
        self.handle_unknown = handle_unknown
        self.handle_missing = handle_missing
        
        columns_list = [columns] if isinstance(columns, str) else columns
        description = f"Ordinal encoding en {len(columns_list)} columna(s)"
        
        super().__init__("ordinal_encoding", description, columns_list)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar ordinal encoding"""
        if parameters is None:
            parameters = {}
            
        try:
            df_encoded = df.copy()
            
            encoding_map = parameters.get('encoding_map', self.encoding_map)
            handle_unknown = parameters.get('handle_unknown', self.handle_unknown)
            handle_missing = parameters.get('handle_missing', self.handle_missing)
            columns = parameters.get('columns', self.columns)
            
            for column in columns:
                if column not in df_encoded.columns:
                    raise ValueError(f"Columna '{column}' no existe")
                
                series = df_encoded[column]
                
                # Crear mapeo de codificación si no existe
                if column not in encoding_map:
                    # Ordenar valores únicos para crear un mapeo ordinal automático
                    unique_values = self._get_unique_values(series)
                    # Filtrar None si existe (se maneja por separado para valores faltantes)
                    sorted_values = [v for v in unique_values if v is not None]
                    sorted_values.sort()
                    encoding_map[column] = [(v, i) for i, v in enumerate(sorted_values, 1)]
                
                # Convertir mapeo a diccionario para búsqueda rápida
                value_to_code = {str(v): code for v, code in encoding_map[column]}
                
                # Guardar el mapeo para posible decodificación
                self._encoding_mappings[column] = {
                    'encoding_map': encoding_map[column],
                    'value_to_code': value_to_code,
                    'handle_unknown': handle_unknown,
                    'handle_missing': handle_missing
                }
                
                # Aplicar codificación
                df_encoded[column] = series.astype(str).map(value_to_code)
                
                # Manejar valores desconocidos
                if handle_unknown == 'use_encoded_value':
                    # Reemplazar valores NaN resultantes de la búsqueda con -1
                    df_encoded[column] = df_encoded[column].fillna(-1).astype(int)
                elif handle_unknown == 'error':
                    # Verificar si hay valores NaN
                    if df_encoded[column].isna().any():
                        raise ValueError(f"La columna '{column}' contiene valores desconocidos")
                
                # Manejar valores faltantes
                mask = series.isna()
                if mask.any():
                    if handle_missing == 'use_encoded_value':
                        # Reemplazar valores faltantes con 0
                        df_encoded.loc[mask, column] = 0
                    elif handle_missing == 'ignore':
                        # Mantener NaN
                        df_encoded.loc[mask, column] = np.nan
                    elif handle_missing == 'error':
                        raise ValueError(f"La columna '{column}' contiene valores faltantes")
                
                logger.info(f"Ordinal encoding aplicado a columna '{column}'")
            
            return df_encoded
            
        except Exception as e:
            logger.error(f"Error en ordinal encoding: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de ordinal encoding"""
        handle_unknown = parameters.get('handle_unknown', self.handle_unknown)
        handle_missing = parameters.get('handle_missing', self.handle_missing)
        
        if handle_unknown not in ['error', 'use_encoded_value', 'ignore']:
            return False
        
        if handle_missing not in ['error', 'use_encoded_value', 'ignore']:
            return False
        
        return True
    
    def decode_values(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        Decodificar valores codificados a sus valores originales
        
        Args:
            df: DataFrame con valores codificados
            column: Columna a decodificar
            
        Returns:
            DataFrame con valores decodificados
        """
        if column not in self._encoding_mappings:
            raise ValueError(f"No hay mapeo de codificación para la columna '{column}'")
        
        mapping = self._encoding_mappings[column]
        code_to_value = {code: v for v, code in mapping['encoding_map']}
        
        # Crear un DataFrame de copia
        df_decoded = df.copy()
        
        # Mapear códigos a valores originales
        df_decoded[column] = df_decoded[column].map(code_to_value)
        
        # Manejar valores especiales
        if mapping['handle_missing'] == 'use_encoded_value':
            # Valores 0 representan valores faltantes
            mask = df[column] == 0
            if mask.any():
                df_decoded.loc[mask, column] = None
        
        if mapping['handle_unknown'] == 'use_encoded_value':
            # Valores -1 representan valores desconocidos
            mask = df[column] == -1
            if mask.any():
                df_decoded.loc[mask, column] = None
        
        return df_decoded


class TargetEncodingTransformation(CategoricalEncodingTransformation):
    """
    Transformación de target encoding (codificación basada en la variable objetivo)
    """
    
    def __init__(self, columns: Union[str, List[str]], target_column: str, 
                 smoothing: float = 1.0, noise: float = 0.0, cv: int = 5):
        """
        Inicializar transformación de target encoding
        
        Args:
            columns: Columna o lista de columnas a codificar
            target_column: Nombre de la columna objetivo (variable a predecir)
            smoothing: Parámetro de suavizado para reducir overfitting
            noise: Ruido a añadir a la codificación para reducir overfitting
            cv: Número de pliegues para validación cruzada en el target encoding
        """
        self.target_column = target_column
        self.smoothing = smoothing
        self.noise = noise
        self.cv = cv
        
        columns_list = [columns] if isinstance(columns, str) else columns
        description = f"Target encoding en {len(columns_list)} columna(s) con target '{target_column}'"
        
        super().__init__("target_encoding", description, columns_list)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar target encoding"""
        if parameters is None:
            parameters = {}
            
        try:
            df_encoded = df.copy()
            
            target_column = parameters.get('target_column', self.target_column)
            smoothing = parameters.get('smoothing', self.smoothing)
            noise = parameters.get('noise', self.noise)
            cv = parameters.get('cv', self.cv)
            columns = parameters.get('columns', self.columns)
            
            # Validar que la columna objetivo existe
            if target_column not in df_encoded.columns:
                raise ValueError(f"Columna objetivo '{target_column}' no existe")
            
            # Verificar que la columna objetivo es numérica
            if not pd.api.types.is_numeric_dtype(df_encoded[target_column]):
                raise ValueError(f"La columna objetivo '{target_column}' debe ser numérica")
            
            # Realizar target encoding con validación cruzada para reducir overfitting
            for column in columns:
                if column not in df_encoded.columns:
                    raise ValueError(f"Columna '{column}' no existe")
                
                series = df_encoded[column]
                
                # Crear mapeo de target encoding
                target_mapping = {}
                global_mean = df_encoded[target_column].mean()
                
                # Dividir datos en pliegues para validación cruzada
                df_temp = df_encoded[[column, target_column]].copy()
                df_temp['fold'] = np.random.randint(0, cv, size=len(df_temp))
                
                for fold in range(cv):
                    # Datos de entrenamiento para este pliegue
                    train_data = df_temp[df_temp['fold'] != fold]
                    
                    # Calcular media de target por categoría en datos de entrenamiento
                    category_means = train_data.groupby(column)[target_column].agg(['mean', 'count'])
                    
                    # Aplicar suavizado
                    smoothed_means = {}
                    for category, row in category_means.iterrows():
                        count = row['count']
                        mean = row['mean']
                        # Fórmula de suavizado: (mean * count + global_mean * smoothing) / (count + smoothing)
                        smoothed_mean = (mean * count + global_mean * smoothing) / (count + smoothing)
                        smoothed_means[category] = smoothed_mean
                    
                    # Aplicar codificación a datos de prueba de este pliegue
                    test_mask = df_temp['fold'] == fold
                    test_data = df_temp[test_mask]
                    
                    for category, value in test_data[column].items():
                        if category in smoothed_means:
                            target_mapping[category] = smoothed_means[category]
                        else:
                            # Categorías no vistas en entrenamiento, usar media global
                            target_mapping[category] = global_mean
                
                # Aplicar codificación final a todo el dataset
                df_encoded[column] = series.map(target_mapping).fillna(global_mean)
                
                # Añadir ruido si se especifica
                if noise > 0:
                    noise_values = np.random.normal(0, noise, size=len(df_encoded))
                    df_encoded[column] = df_encoded[column] + noise_values
                
                # Guardar el mapeo para posible decodificación
                self._encoding_mappings[column] = {
                    'target_mapping': target_mapping,
                    'global_mean': global_mean,
                    'smoothing': smoothing,
                    'noise': noise
                }
                
                logger.info(f"Target encoding aplicado a columna '{column}'")
            
            return df_encoded
            
        except Exception as e:
            logger.error(f"Error en target encoding: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de target encoding"""
        target_column = parameters.get('target_column', self.target_column)
        smoothing = parameters.get('smoothing', self.smoothing)
        noise = parameters.get('noise', self.noise)
        cv = parameters.get('cv', self.cv)
        
        if not target_column or not isinstance(target_column, str):
            return False
        
        if not isinstance(smoothing, (int, float)) or smoothing < 0:
            return False
        
        if not isinstance(noise, (int, float)) or noise < 0:
            return False
        
        if not isinstance(cv, int) or cv < 2:
            return False
        
        return True


# Funciones de utilidad para crear transformaciones de codificación
def create_label_encoding(columns: Union[str, List[str]], 
                          handle_unknown: str = 'error', 
                          handle_missing: str = 'error') -> LabelEncodingTransformation:
    """Crear transformación de label encoding"""
    return LabelEncodingTransformation(columns, handle_unknown, handle_missing)


def create_one_hot_encoding(columns: Union[str, List[str]], 
                            drop_first: bool = False, 
                            prefix: str = None,
                            prefix_sep: str = "_") -> OneHotEncodingTransformation:
    """Crear transformación de one-hot encoding"""
    return OneHotEncodingTransformation(columns, drop_first, prefix, prefix_sep)


def create_ordinal_encoding(columns: Union[str, List[str]], 
                            encoding_map: Dict[str, List[Tuple]] = None) -> OrdinalEncodingTransformation:
    """Crear transformación de ordinal encoding"""
    return OrdinalEncodingTransformation(columns, encoding_map)


def create_target_encoding(columns: Union[str, List[str]], 
                           target_column: str, 
                           smoothing: float = 1.0,
                           noise: float = 0.0) -> TargetEncodingTransformation:
    """Crear transformación de target encoding"""
    return TargetEncodingTransformation(columns, target_column, smoothing, noise)