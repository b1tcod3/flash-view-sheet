"""
Transformaciones para manejo de fechas y tiempo
Incluye parsing, extracción de componentes, cálculos de diferencias y zonas horarias
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union, Tuple
import logging
from datetime import datetime, timedelta
import pytz
from dateutil import parser
import warnings

from .base_transformation import BaseTransformation

# Configurar logging
logger = logging.getLogger(__name__)

# Suprimir warnings de dateutil
warnings.filterwarnings('ignore', category=UserWarning)


class DateTimeTransformation(BaseTransformation):
    """
    Clase base para transformaciones de fecha y tiempo
    """
    
    def __init__(self, name: str, description: str, columns: Union[str, List[str]]):
        """
        Inicializar transformación de fecha/tiempo
        
        Args:
            name: Nombre de la transformación
            description: Descripción de la transformación
            columns: Columna o lista de columnas a transformar
        """
        super().__init__(name, description)
        self.columns = [columns] if isinstance(columns, str) else columns
        
    def validate_data(self, df: pd.DataFrame) -> bool:
        """Validar que las columnas puedan convertirse a datetime"""
        super().validate_data(df)
        
        # Verificar que las columnas existen
        missing_columns = [col for col in self.columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Columnas no encontradas: {missing_columns}")
        
        return True
    
    def _convert_to_datetime(self, series: pd.Series) -> pd.Series:
        """
        Convertir serie a datetime de forma flexible
        
        Args:
            series: Serie de pandas
            
        Returns:
            Serie convertida a datetime
        """
        try:
            # Intentar conversión directa
            if pd.api.types.is_datetime64_any_dtype(series):
                return series
            
            # Intentar parsing automático
            return pd.to_datetime(series, errors='coerce')
            
        except Exception:
            # Como último recurso, intentar parsing manual
            def parse_date(x):
                try:
                    return parser.parse(str(x))
                except:
                    return pd.NaT
            
            return series.apply(parse_date)


class DateParsingTransformation(DateTimeTransformation):
    """
    Transformación para parsing de fechas con múltiples formatos
    """
    
    def __init__(self, columns: Union[str, List[str]], date_format: str = None,
                 infer_datetime_format: bool = True, errors: str = 'coerce'):
        """
        Inicializar parsing de fechas
        
        Args:
            columns: Columna o lista de columnas
            date_format: Formato específico de fecha (opcional)
            infer_datetime_format: Si inferir formato automáticamente
            errors: Manejo de errores ('coerce', 'ignore', 'raise')
        """
        self.date_format = date_format
        self.infer_datetime_format = infer_datetime_format
        self.errors = errors
        
        format_desc = date_format or "formato automático"
        description = f"Parsear fechas ({format_desc}) en {len(columns)} columna(s)"
        super().__init__("date_parsing", description, columns)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar parsing de fechas"""
        if parameters is None:
            parameters = {}
            
        try:
            df_parsed = df.copy()
            
            date_format = parameters.get('date_format', self.date_format)
            infer_format = parameters.get('infer_datetime_format', self.infer_datetime_format)
            errors = parameters.get('errors', self.errors)
            columns = parameters.get('columns', self.columns)
            
            for column in columns:
                if column not in df_parsed.columns:
                    raise ValueError(f"Columna '{column}' no existe")
                
                if date_format:
                    # Parsear con formato específico
                    result = pd.to_datetime(df_parsed[column], format=date_format, errors=errors)
                else:
                    # Parsear automáticamente
                    result = pd.to_datetime(
                        df_parsed[column], 
                        infer_datetime_format=infer_format, 
                        errors=errors
                    )
                
                df_parsed[column] = result
                logger.info(f"Fecha parseada en columna '{column}'")
            
            return df_parsed
            
        except Exception as e:
            logger.error(f"Error en parsing de fechas: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de parsing"""
        errors = parameters.get('errors', self.errors)
        return errors in ['coerce', 'ignore', 'raise']


class ComponentExtractionTransformation(DateTimeTransformation):
    """
    Transformación para extracción de componentes de fecha (año, mes, día, hora)
    """
    
    def __init__(self, columns: Union[str, List[str]], component: str, new_column_name: str = None):
        """
        Inicializar extracción de componentes
        
        Args:
            columns: Columna o lista de columnas de fecha
            component: Componente a extraer ('year', 'month', 'day', 'hour', 'minute', 'second')
            new_column_name: Nombre para la nueva columna (opcional)
        """
        self.component = component
        self.new_column_name = new_column_name
        
        description = f"Extraer {component} de fechas en {len(columns)} columna(s)"
        super().__init__("component_extraction", description, columns)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar extracción de componentes"""
        if parameters is None:
            parameters = {}
            
        try:
            df_extracted = df.copy()
            
            component = parameters.get('component', self.component)
            new_column_name = parameters.get('new_column_name', self.new_column_name)
            columns = parameters.get('columns', self.columns)
            
            for column in columns:
                if column not in df_extracted.columns:
                    raise ValueError(f"Columna '{column}' no existe")
                
                # Convertir a datetime si no lo está
                datetime_series = self._convert_to_datetime(df_extracted[column])
                
                # Extraer componente
                if component == 'year':
                    result = datetime_series.dt.year
                elif component == 'month':
                    result = datetime_series.dt.month
                elif component == 'day':
                    result = datetime_series.dt.day
                elif component == 'hour':
                    result = datetime_series.dt.hour
                elif component == 'minute':
                    result = datetime_series.dt.minute
                elif component == 'second':
                    result = datetime_series.dt.second
                elif component == 'dayofweek':
                    result = datetime_series.dt.dayofweek  # 0=Monday, 6=Sunday
                elif component == 'dayname':
                    result = datetime_series.dt.day_name()
                elif component == 'monthname':
                    result = datetime_series.dt.month_name()
                elif component == 'quarter':
                    result = datetime_series.dt.quarter
                elif component == 'week':
                    result = datetime_series.dt.isocalendar().week
                else:
                    raise ValueError(f"Componente no válido: {component}")
                
                # Determinar nombre de columna
                if new_column_name:
                    result_column = new_column_name
                else:
                    result_column = f"{column}_{component}"
                
                df_extracted[result_column] = result
                logger.info(f"Componente '{component}' extraído de columna '{column}' -> '{result_column}'")
            
            return df_extracted
            
        except Exception as e:
            logger.error(f"Error en extracción de componentes: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de extracción"""
        component = parameters.get('component', self.component)
        valid_components = [
            'year', 'month', 'day', 'hour', 'minute', 'second',
            'dayofweek', 'dayname', 'monthname', 'quarter', 'week'
        ]
        return component in valid_components


class DateDifferenceTransformation(DateTimeTransformation):
    """
    Transformación para cálculos de diferencia de fechas
    """
    
    def __init__(self, columns: Union[str, List[str]], reference_column: str = None,
                 time_unit: str = 'days', new_column_name: str = None):
        """
        Inicializar cálculo de diferencias
        
        Args:
            columns: Columna o lista de columnas de fecha
            reference_column: Columna de referencia (opcional)
            time_unit: Unidad de tiempo ('days', 'hours', 'minutes', 'seconds')
            new_column_name: Nombre para la nueva columna
        """
        self.reference_column = reference_column
        self.time_unit = time_unit
        self.new_column_name = new_column_name
        
        ref_desc = f" vs {reference_column}" if reference_column else " (desde epoch)"
        description = f"Calcular diferencia de fechas ({time_unit}) en {len(columns)} columna(s){ref_desc}"
        super().__init__("date_difference", description, columns)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar cálculo de diferencias de fecha"""
        if parameters is None:
            parameters = {}
            
        try:
            df_diff = df.copy()
            
            reference_column = parameters.get('reference_column', self.reference_column)
            time_unit = parameters.get('time_unit', self.time_unit)
            new_column_name = parameters.get('new_column_name', self.new_column_name)
            columns = parameters.get('columns', self.columns)
            
            if time_unit not in ['days', 'hours', 'minutes', 'seconds']:
                raise ValueError(f"Unidad de tiempo no válida: {time_unit}")
            
            for column in columns:
                if column not in df_diff.columns:
                    raise ValueError(f"Columna '{column}' no existe")
                
                # Convertir a datetime
                datetime_series = self._convert_to_datetime(df_diff[column])
                
                if reference_column:
                    # Diferencia con otra columna
                    if reference_column not in df_diff.columns:
                        raise ValueError(f"Columna de referencia '{reference_column}' no existe")
                    
                    ref_datetime = self._convert_to_datetime(df_diff[reference_column])
                    
                    # Calcular diferencia
                    time_diff = datetime_series - ref_datetime
                else:
                    # Diferencia desde epoch (1970-01-01)
                    epoch = pd.Timestamp('1970-01-01')
                    time_diff = datetime_series - epoch
                
                # Convertir a la unidad solicitada
                if time_unit == 'days':
                    result = time_diff.dt.days
                elif time_unit == 'hours':
                    result = time_diff.dt.total_seconds() / 3600
                elif time_unit == 'minutes':
                    result = time_diff.dt.total_seconds() / 60
                elif time_unit == 'seconds':
                    result = time_diff.dt.total_seconds()
                
                # Determinar nombre de columna
                if new_column_name:
                    result_column = new_column_name
                else:
                    ref_name = reference_column or 'epoch'
                    result_column = f"{column}_{ref_name}_{time_unit}_diff"
                
                df_diff[result_column] = result
                logger.info(f"Diferencia de fecha calculada: '{column}' vs '{ref_name}' -> '{result_column}'")
            
            return df_diff
            
        except Exception as e:
            logger.error(f"Error en cálculo de diferencia de fechas: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de diferencia"""
        time_unit = parameters.get('time_unit', self.time_unit)
        return time_unit in ['days', 'hours', 'minutes', 'seconds']


class TimeZoneTransformation(DateTimeTransformation):
    """
    Transformación para conversión de zonas horarias
    """
    
    def __init__(self, columns: Union[str, List[str]], target_timezone: str,
                 source_timezone: str = None, new_column_name: str = None):
        """
        Inicializar conversión de zona horaria
        
        Args:
            columns: Columna o lista de columnas de fecha
            target_timezone: Zona horaria objetivo
            source_timezone: Zona horaria fuente (opcional)
            new_column_name: Nombre para la nueva columna (opcional)
        """
        self.target_timezone = target_timezone
        self.source_timezone = source_timezone
        self.new_column_name = new_column_name
        
        src_desc = f" desde {source_timezone}" if source_timezone else ""
        description = f"Convertir a {target_timezone}{src_desc} en {len(columns)} columna(s)"
        super().__init__("timezone_conversion", description, columns)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar conversión de zona horaria"""
        if parameters is None:
            parameters = {}
            
        try:
            df_tz = df.copy()
            
            target_tz = parameters.get('target_timezone', self.target_timezone)
            source_tz = parameters.get('source_timezone', self.source_timezone)
            new_column_name = parameters.get('new_column_name', self.new_column_name)
            columns = parameters.get('columns', self.columns)
            
            # Validar zonas horarias
            try:
                pytz.timezone(target_tz)
            except:
                raise ValueError(f"Zona horaria objetivo inválida: {target_tz}")
            
            if source_tz:
                try:
                    pytz.timezone(source_tz)
                except:
                    raise ValueError(f"Zona horaria fuente inválida: {source_tz}")
            
            for column in columns:
                if column not in df_tz.columns:
                    raise ValueError(f"Columna '{column}' no existe")
                
                # Convertir a datetime
                datetime_series = self._convert_to_datetime(df_tz[column])
                
                if source_tz:
                    # Convertir desde zona específica
                    tz_aware = datetime_series.dt.tz_localize(source_tz)
                else:
                    # Asumir que ya tiene zona horaria o es naive
                    try:
                        tz_aware = datetime_series.dt.tz_localize(None)
                    except:
                        tz_aware = datetime_series
                
                # Convertir a zona objetivo
                result = tz_aware.dt.tz_convert(target_tz)
                
                # Determinar nombre de columna
                if new_column_name:
                    result_column = new_column_name
                else:
                    tz_suffix = target_tz.replace('/', '_').replace('-', '_')
                    result_column = f"{column}_{tz_suffix}"
                
                df_tz[result_column] = result
                logger.info(f"Zona horaria convertida: '{column}' -> '{target_tz}' en '{result_column}'")
            
            return df_tz
            
        except Exception as e:
            logger.error(f"Error en conversión de zona horaria: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de zona horaria"""
        target_tz = parameters.get('target_timezone', self.target_timezone)
        
        try:
            pytz.timezone(target_tz)
            return True
        except:
            return False


# Funciones de utilidad para crear transformaciones de fecha/tiempo
def create_date_parsing(columns: Union[str, List[str]], **kwargs) -> DateParsingTransformation:
    """Crear transformación de parsing de fechas"""
    return DateParsingTransformation(columns, **kwargs)


def create_component_extraction(columns: Union[str, List[str]], component: str, **kwargs) -> ComponentExtractionTransformation:
    """Crear transformación de extracción de componentes"""
    return ComponentExtractionTransformation(columns, component, **kwargs)


def create_date_difference(columns: Union[str, List[str]], time_unit: str = 'days', **kwargs) -> DateDifferenceTransformation:
    """Crear transformación de diferencia de fechas"""
    return DateDifferenceTransformation(columns, time_unit=time_unit, **kwargs)


def create_timezone_conversion(columns: Union[str, List[str]], target_timezone: str, **kwargs) -> TimeZoneTransformation:
    """Crear transformación de zona horaria"""
    return TimeZoneTransformation(columns, target_timezone, **kwargs)