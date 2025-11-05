"""
Transformaciones matemáticas avanzadas
Incluye logaritmos, escalado, normalización y otras operaciones matemáticas
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union, Tuple
import logging
from datetime import datetime
import warnings

from .base_transformation import BaseTransformation

# Configurar logging
logger = logging.getLogger(__name__)

# Suprimir warnings de numpy para operaciones matemáticas
warnings.filterwarnings('ignore', category=RuntimeWarning)


class MathematicalTransformation(BaseTransformation):
    """
    Clase base para transformaciones matemáticas
    """
    
    def __init__(self, name: str, description: str, columns: Union[str, List[str]]):
        """
        Inicializar transformación matemática
        
        Args:
            name: Nombre de la transformación
            description: Descripción de la transformación
            columns: Columna o lista de columnas a transformar
        """
        super().__init__(name, description)
        self.columns = [columns] if isinstance(columns, str) else columns
        
        # Configuración de manejo de valores inválidos
        self.handle_invalid_values = 'coerce'  # 'coerce', 'skip', 'error'
        self.invalid_value_replacement = 0
        
    def validate_data(self, df: pd.DataFrame) -> bool:
        """Validar que las columnas sean numéricas"""
        super().validate_data(df)
        
        # Verificar que las columnas existen
        missing_columns = [col for col in self.columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Columnas no encontradas: {missing_columns}")
        
        # Verificar que las columnas son numéricas
        non_numeric_columns = []
        for col in self.columns:
            if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
                non_numeric_columns.append(col)
        
        if non_numeric_columns:
            raise ValueError(f"Las siguientes columnas no son numéricas: {non_numeric_columns}")
        
        return True
    
    def _handle_invalid_values(self, series: pd.Series) -> pd.Series:
        """
        Manejar valores inválidos en series numéricas
        
        Args:
            series: Serie de pandas con posibles valores inválidos
            
        Returns:
            Serie con valores inválidos manejados
        """
        if self.handle_invalid_values == 'coerce':
            # Reemplazar NaN e infinitos
            series = series.replace([np.inf, -np.inf], np.nan)
            series = series.fillna(self.invalid_value_replacement)
        elif self.handle_invalid_values == 'skip':
            # Remover filas con valores inválidos
            series = series.replace([np.inf, -np.inf], np.nan)
            series = series.dropna()
        elif self.handle_invalid_values == 'error':
            # No modificar, dejar que se propague el error
            pass
        
        return series


class LogarithmicTransformation(MathematicalTransformation):
    """
    Transformación logarítmica (log, log10, log2, ln)
    """
    
    def __init__(self, columns: Union[str, List[str]], log_type: str = 'natural', 
                 base: float = None, offset: float = 0):
        """
        Inicializar transformación logarítmica
        
        Args:
            columns: Columna o lista de columnas a transformar
            log_type: Tipo de logaritmo ('natural', 'log10', 'log2', 'custom')
            base: Base para logaritmo personalizado (solo si log_type='custom')
            offset: Offset a sumar antes del logaritmo para manejar valores <= 0
        """
        self.log_type = log_type
        self.base = base
        self.offset = offset
        
        if log_type == 'natural':
            func_name = 'ln'
            description = f"Logaritmo natural en {len(columns)} columna(s)"
        elif log_type == 'log10':
            func_name = 'log10'
            description = f"Logaritmo base 10 en {len(columns)} columna(s)"
        elif log_type == 'log2':
            func_name = 'log2'
            description = f"Logaritmo base 2 en {len(columns)} columna(s)"
        else:
            func_name = f"log(base={base})"
            description = f"Logaritmo base {base} en {len(columns)} columna(s)"
        
        super().__init__("logarithmic", description, columns)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar transformación logarítmica"""
        if parameters is None:
            parameters = {}
            
        try:
            df_transformed = df.copy()
            
            log_type = parameters.get('log_type', self.log_type)
            base = parameters.get('base', self.base)
            offset = parameters.get('offset', self.offset)
            columns = parameters.get('columns', self.columns)
            
            for column in columns:
                if column not in df_transformed.columns:
                    raise ValueError(f"Columna '{column}' no existe")
                
                # Verificar que la columna es numérica antes de aplicar logaritmo
                series = df_transformed[column]
                if not pd.api.types.is_numeric_dtype(series):
                    raise ValueError(f"La columna '{column}' debe ser numérica para aplicar logaritmo")
                
                # Aplicar offset si es necesario
                if offset != 0:
                    series = series + offset
                
                # Aplicar logaritmo
                if log_type == 'natural':
                    result = np.log(series)
                elif log_type == 'log10':
                    result = np.log10(series)
                elif log_type == 'log2':
                    result = np.log2(series)
                elif log_type == 'custom':
                    if base is None or base <= 0 or base == 1:
                        raise ValueError("Base debe ser un número positivo diferente de 1")
                    result = np.log(series) / np.log(base)
                else:
                    raise ValueError(f"Tipo de logaritmo no válido: {log_type}")
                
                # Manejar valores inválidos
                result = self._handle_invalid_values(result)
                
                # Reemplazar columna original
                df_transformed[column] = result
                
                logger.info(f"Logaritmo {log_type} aplicado a columna '{column}'")
            
            return df_transformed
            
        except Exception as e:
            logger.error(f"Error en transformación logarítmica: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de transformación logarítmica"""
        log_type = parameters.get('log_type', self.log_type)
        
        if log_type == 'custom':
            base = parameters.get('base', self.base)
            if base is None or base <= 0 or base == 1:
                return False
        
        return True


class ExponentialTransformation(MathematicalTransformation):
    """
    Transformación exponencial (exp, power, sqrt)
    """
    
    def __init__(self, columns: Union[str, List[str]], operation: str = 'exp', exponent: float = 2):
        """
        Inicializar transformación exponencial
        
        Args:
            columns: Columna o lista de columnas a transformar
            operation: Tipo de operación ('exp', 'power', 'sqrt', 'square')
            exponent: Exponente para operación 'power'
        """
        self.operation = operation
        self.exponent = exponent
        
        if operation == 'exp':
            description = f"Exponencial (e^x) en {len(columns)} columna(s)"
        elif operation == 'power':
            description = f"Potencia (x^{exponent}) en {len(columns)} columna(s)"
        elif operation == 'sqrt':
            description = f"Raíz cuadrada en {len(columns)} columna(s)"
        elif operation == 'square':
            description = f"Cuadrado (x^2) en {len(columns)} columna(s)"
        else:
            description = f"Operación {operation} en {len(columns)} columna(s)"
        
        super().__init__("exponential", description, columns)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar transformación exponencial"""
        if parameters is None:
            parameters = {}
            
        try:
            df_transformed = df.copy()
            
            operation = parameters.get('operation', self.operation)
            exponent = parameters.get('exponent', self.exponent)
            columns = parameters.get('columns', self.columns)
            
            for column in columns:
                if column not in df_transformed.columns:
                    raise ValueError(f"Columna '{column}' no existe")
                
                series = df_transformed[column]
                
                # Aplicar operación
                if operation == 'exp':
                    result = np.exp(series)
                elif operation == 'power':
                    result = np.power(series, exponent)
                elif operation == 'sqrt':
                    result = np.sqrt(series)
                elif operation == 'square':
                    result = np.square(series)
                else:
                    raise ValueError(f"Operación no válida: {operation}")
                
                # Manejar valores inválidos (especialmente para sqrt)
                if operation in ['sqrt']:
                    result = self._handle_invalid_values(result)
                
                # Reemplazar columna
                df_transformed[column] = result
                
                logger.info(f"Transformación {operation} aplicada a columna '{column}'")
            
            return df_transformed
            
        except Exception as e:
            logger.error(f"Error en transformación exponencial: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de transformación exponencial"""
        operation = parameters.get('operation', self.operation)
        
        if operation == 'power':
            exponent = parameters.get('exponent', self.exponent)
            if not isinstance(exponent, (int, float)) or np.isnan(exponent):
                return False
        
        return True


class ScalingTransformation(MathematicalTransformation):
    """
    Transformaciones de escalado (MinMax, Standard, Robust, etc.)
    """
    
    def __init__(self, columns: Union[str, List[str]], scaler_type: str = 'minmax',
                 feature_range: Tuple[float, float] = (0, 1), 
                 with_mean: bool = True, with_std: bool = True):
        """
        Inicializar transformación de escalado
        
        Args:
            columns: Columna o lista de columnas a escalar
            scaler_type: Tipo de escalado ('minmax', 'standard', 'robust', 'maxabs')
            feature_range: Rango objetivo para MinMaxScaler
            with_mean: Centrar con la media (StandardScaler)
            with_std: Escalar con desviación estándar (StandardScaler)
        """
        self.scaler_type = scaler_type
        self.feature_range = feature_range
        self.with_mean = with_mean
        self.with_std = with_std
        
        description = f"Escalado {scaler_type} en {len(columns)} columna(s)"
        
        super().__init__("scaling", description, columns)
        
        # Almacenar parámetros de escalado para posible desescalado
        self._scaling_params = {}
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar transformación de escalado"""
        if parameters is None:
            parameters = {}
            
        try:
            df_transformed = df.copy()
            
            scaler_type = parameters.get('scaler_type', self.scaler_type)
            feature_range = parameters.get('feature_range', self.feature_range)
            with_mean = parameters.get('with_mean', self.with_mean)
            with_std = parameters.get('with_std', self.with_std)
            columns = parameters.get('columns', self.columns)
            
            # Aplicar escalado por columna
            for column in columns:
                if column not in df_transformed.columns:
                    raise ValueError(f"Columna '{column}' no existe")
                
                series = df_transformed[column]
                original_series = series.copy()  # Para guardar parámetros
                
                # Aplicar escalado según el tipo
                if scaler_type == 'minmax':
                    result = self._minmax_scale(series, feature_range)
                elif scaler_type == 'standard':
                    result = self._standard_scale(series, with_mean, with_std)
                elif scaler_type == 'robust':
                    result = self._robust_scale(series)
                elif scaler_type == 'maxabs':
                    result = self._maxabs_scale(series)
                else:
                    raise ValueError(f"Tipo de escalado no válido: {scaler_type}")
                
                # Guardar parámetros para posible desescalado
                self._scaling_params[column] = {
                    'scaler_type': scaler_type,
                    'original_series': original_series,
                    'feature_range': feature_range,
                    'with_mean': with_mean,
                    'with_std': with_std
                }
                
                # Reemplazar columna
                df_transformed[column] = result
                
                logger.info(f"Escalado {scaler_type} aplicado a columna '{column}'")
            
            return df_transformed
            
        except Exception as e:
            logger.error(f"Error en transformación de escalado: {str(e)}")
            raise
    
    def _minmax_scale(self, series: pd.Series, feature_range: Tuple[float, float]) -> pd.Series:
        """Escalado Min-Max"""
        min_val = series.min()
        max_val = series.max()
        
        if min_val == max_val:
            # Si todos los valores son iguales, retornar valores del rango
            return pd.Series([feature_range[0]] * len(series), index=series.index)
        
        # Aplicar escalado
        scaled = (series - min_val) / (max_val - min_val)
        scaled = scaled * (feature_range[1] - feature_range[0]) + feature_range[0]
        
        return scaled
    
    def _standard_scale(self, series: pd.Series, with_mean: bool, with_std: bool) -> pd.Series:
        """Escalado estándar (z-score)"""
        if with_mean:
            series = series - series.mean()
        if with_std and series.std() != 0:
            series = series / series.std()
        
        return series
    
    def _robust_scale(self, series: pd.Series) -> pd.Series:
        """Escalado robusto usando mediana e IQR"""
        median = series.median()
        q75 = series.quantile(0.75)
        q25 = series.quantile(0.25)
        iqr = q75 - q25
        
        if iqr == 0:
            return series - median  # Solo centrar
        
        return (series - median) / iqr
    
    def _maxabs_scale(self, series: pd.Series) -> pd.Series:
        """Escalado por valor absoluto máximo"""
        max_abs = series.abs().max()
        
        if max_abs == 0:
            return series  # Sin cambios si todos son cero
        
        return series / max_abs
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de escalado"""
        scaler_type = parameters.get('scaler_type', self.scaler_type)
        
        if scaler_type == 'minmax':
            feature_range = parameters.get('feature_range', self.feature_range)
            if not (isinstance(feature_range, (list, tuple)) and len(feature_range) == 2):
                return False
            if feature_range[0] >= feature_range[1]:
                return False
        
        return True


class NormalizationTransformation(MathematicalTransformation):
    """
    Transformación de normalización (L1, L2, max)
    """
    
    def __init__(self, columns: Union[str, List[str]], norm: str = 'l2', axis: int = 0):
        """
        Inicializar transformación de normalización
        
        Args:
            columns: Columna o lista de columnas a normalizar
            norm: Tipo de normalización ('l1', 'l2', 'max')
            axis: Eje para normalización (0=filas, 1=columnas)
        """
        self.norm = norm
        self.axis = axis
        
        description = f"Normalización {norm} en eje {axis} para {len(columns)} columna(s)"
        
        super().__init__("normalization", description, columns)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar transformación de normalización"""
        if parameters is None:
            parameters = {}
            
        try:
            df_transformed = df.copy()
            
            norm = parameters.get('norm', self.norm)
            axis = parameters.get('axis', self.axis)
            columns = parameters.get('columns', self.columns)
            
            if axis == 0:
                # Normalizar por filas (cada fila suma 1 o tiene norma 1)
                for i, row in df_transformed.iterrows():
                    row_values = row[columns]
                    if self.norm == 'l1':
                        row_sum = row_values.abs().sum()
                        if row_sum != 0:
                            df_transformed.loc[i, columns] = row_values / row_sum
                    elif self.norm == 'l2':
                        row_norm = np.sqrt((row_values ** 2).sum())
                        if row_norm != 0:
                            df_transformed.loc[i, columns] = row_values / row_norm
                    elif self.norm == 'max':
                        row_max = row_values.abs().max()
                        if row_max != 0:
                            df_transformed.loc[i, columns] = row_values / row_max
            else:
                # Normalizar por columnas (cada columna tiene norma 1)
                for column in columns:
                    series = df_transformed[column]
                    
                    if norm == 'l1':
                        col_sum = series.abs().sum()
                        if col_sum != 0:
                            df_transformed[column] = series / col_sum
                    elif norm == 'l2':
                        col_norm = np.sqrt((series ** 2).sum())
                        if col_norm != 0:
                            df_transformed[column] = series / col_norm
                    elif norm == 'max':
                        col_max = series.abs().max()
                        if col_max != 0:
                            df_transformed[column] = series / col_max
            
            logger.info(f"Normalización {norm} aplicada en eje {axis}")
            
            return df_transformed
            
        except Exception as e:
            logger.error(f"Error en transformación de normalización: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de normalización"""
        norm = parameters.get('norm', self.norm)
        axis = parameters.get('axis', self.axis)
        
        if norm not in ['l1', 'l2', 'max']:
            return False
        
        if axis not in [0, 1]:
            return False
        
        return True


class CustomMathTransformation(MathematicalTransformation):
    """
    Transformación matemática personalizada usando funciones lambda o callables
    """
    
    def __init__(self, columns: Union[str, List[str]], function: callable, 
                 function_args: Dict[str, Any] = None, new_column_suffix: str = "_transformed"):
        """
        Inicializar transformación matemática personalizada
        
        Args:
            columns: Columna o lista de columnas a transformar
            function: Función a aplicar
            function_args: Argumentos adicionales para la función
            new_column_suffix: Sufijo para nombres de nuevas columnas
        """
        self.function = function
        self.function_args = function_args or {}
        self.new_column_suffix = new_column_suffix
        
        description = f"Transformación personalizada en {len(columns)} columna(s)"
        
        super().__init__("custom_math", description, columns)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar transformación matemática personalizada"""
        if parameters is None:
            parameters = {}
            
        try:
            df_transformed = df.copy()
            
            function = parameters.get('function', self.function)
            function_args = parameters.get('function_args', self.function_args)
            columns = parameters.get('columns', self.columns)
            
            for column in columns:
                if column not in df_transformed.columns:
                    raise ValueError(f"Columna '{column}' no existe")
                
                series = df_transformed[column]
                
                try:
                    # Aplicar función
                    result = function(series, **function_args)
                    
                    # Determinar nombre de columna de resultado
                    result_column = f"{column}{self.new_column_suffix}"
                    
                    # Manejar diferentes tipos de retorno
                    if isinstance(result, pd.Series):
                        if len(result) == len(series):
                            df_transformed[result_column] = result
                        else:
                            # Si el resultado tiene diferente longitud, usar índice
                            df_transformed[result_column] = result.reindex(series.index)
                    else:
                        # Scalar - replicar
                        df_transformed[result_column] = result
                    
                    logger.info(f"Transformación personalizada aplicada a '{column}' -> '{result_column}'")
                    
                except Exception as e:
                    logger.error(f"Error aplicando función personalizada a '{column}': {str(e)}")
                    raise
            
            return df_transformed
            
        except Exception as e:
            logger.error(f"Error en transformación matemática personalizada: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de transformación personalizada"""
        if 'function' not in parameters and self.function is None:
            return False
        
        if not callable(parameters.get('function', self.function)):
            return False
        
        return True


# Funciones de utilidad para crear transformaciones matemáticas
def create_log_transformation(columns: Union[str, List[str]], 
                             log_type: str = 'natural', 
                             base: float = None) -> LogarithmicTransformation:
    """Crear transformación logarítmica"""
    return LogarithmicTransformation(columns, log_type, base)


def create_exponential_transformation(columns: Union[str, List[str]], 
                                    operation: str = 'exp', 
                                    exponent: float = 2) -> ExponentialTransformation:
    """Crear transformación exponencial"""
    return ExponentialTransformation(columns, operation, exponent)


def create_scaling_transformation(columns: Union[str, List[str]], 
                                scaler_type: str = 'minmax',
                                feature_range: Tuple[float, float] = (0, 1)) -> ScalingTransformation:
    """Crear transformación de escalado"""
    return ScalingTransformation(columns, scaler_type, feature_range)


def create_normalization_transformation(columns: Union[str, List[str]], 
                                      norm: str = 'l2') -> NormalizationTransformation:
    """Crear transformación de normalización"""
    return NormalizationTransformation(columns, norm)


def create_custom_math_transformation(columns: Union[str, List[str]], 
                                    function: callable) -> CustomMathTransformation:
    """Crear transformación matemática personalizada"""
    return CustomMathTransformation(columns, function)