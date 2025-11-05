"""
Transformaciones avanzadas de procesamiento de texto
Incluye limpieza, extracción con regex, conversión de case y padding
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union, Callable
import re
import logging
from datetime import datetime
import string

from .base_transformation import BaseTransformation

# Configurar logging
logger = logging.getLogger(__name__)


class TextProcessingTransformation(BaseTransformation):
    """
    Clase base para transformaciones de procesamiento de texto
    """
    
    def __init__(self, name: str, description: str, columns: Union[str, List[str]]):
        """
        Inicializar transformación de texto
        
        Args:
            name: Nombre de la transformación
            description: Descripción de la transformación
            columns: Columna o lista de columnas a transformar
        """
        super().__init__(name, description)
        self.columns = [columns] if isinstance(columns, str) else columns
        
    def validate_data(self, df: pd.DataFrame) -> bool:
        """Validar que las columnas sean de tipo string o object"""
        super().validate_data(df)
        
        # Verificar que las columnas existen
        missing_columns = [col for col in self.columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Columnas no encontradas: {missing_columns}")
        
        # Verificar que las columnas son de texto
        text_columns = []
        for col in self.columns:
            if pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_object_dtype(df[col]):
                text_columns.append(col)
            else:
                logger.warning(f"La columna '{col}' no es de tipo texto, se convertirá")
        
        return True


class TextCleaningTransformation(TextProcessingTransformation):
    """
    Transformación para limpieza de texto (remover caracteres especiales, normalizar)
    """
    
    def __init__(self, columns: Union[str, List[str]], remove_special_chars: bool = True,
                 normalize_unicode: bool = True, remove_punctuation: bool = False,
                 remove_digits: bool = False, strip_whitespace: bool = True):
        """
        Inicializar limpieza de texto
        
        Args:
            columns: Columna o lista de columnas a limpiar
            remove_special_chars: Remover caracteres especiales
            normalize_unicode: Normalizar caracteres Unicode
            remove_punctuation: Remover puntuación
            remove_digits: Remover dígitos
            strip_whitespace: Eliminar espacios en blanco
        """
        self.remove_special_chars = remove_special_chars
        self.normalize_unicode = normalize_unicode
        self.remove_punctuation = remove_punctuation
        self.remove_digits = remove_digits
        self.strip_whitespace = strip_whitespace
        
        description = f"Limpiar texto en {len(columns)} columna(s)"
        super().__init__("text_cleaning", description, columns)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar limpieza de texto"""
        if parameters is None:
            parameters = {}
            
        try:
            df_cleaned = df.copy()
            
            remove_special_chars = parameters.get('remove_special_chars', self.remove_special_chars)
            normalize_unicode = parameters.get('normalize_unicode', self.normalize_unicode)
            remove_punctuation = parameters.get('remove_punctuation', self.remove_punctuation)
            remove_digits = parameters.get('remove_digits', self.remove_digits)
            strip_whitespace = parameters.get('strip_whitespace', self.strip_whitespace)
            columns = parameters.get('columns', self.columns)
            
            for column in columns:
                if column not in df_cleaned.columns:
                    raise ValueError(f"Columna '{column}' no existe")
                
                series = df_cleaned[column].astype(str)
                
                # Aplicar limpiezas en orden
                if normalize_unicode:
                    series = series.str.normalize('NFKD')
                
                if remove_special_chars:
                    # Remover caracteres que no sean letras, números o espacios
                    series = series.str.replace(r'[^\w\s]', '', regex=True)
                
                if remove_punctuation:
                    # Remover puntuación usando string.punctuation
                    translator = str.maketrans('', '', string.punctuation)
                    series = series.str.translate(translator)
                
                if remove_digits:
                    # Remover dígitos
                    series = series.str.replace(r'\d', '', regex=True)
                
                if strip_whitespace:
                    # Normalizar espacios múltiples y eliminar espacios al inicio/final
                    series = series.str.strip()
                    series = series.str.replace(r'\s+', ' ', regex=True)
                
                df_cleaned[column] = series
                logger.info(f"Texto limpiado en columna '{column}'")
            
            return df_cleaned
            
        except Exception as e:
            logger.error(f"Error en limpieza de texto: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de limpieza de texto"""
        # Todos los parámetros son opcionales y booleanos
        return True


class RegexExtractionTransformation(TextProcessingTransformation):
    """
    Transformación para extracción con regex
    """
    
    def __init__(self, columns: Union[str, List[str]], pattern: str, replacement: str = None,
                 extract_group: int = None, flags: int = 0):
        """
        Inicializar extracción con regex
        
        Args:
            columns: Columna o lista de columnas
            pattern: Patrón regex a buscar
            replacement: Texto de reemplazo (opcional)
            extract_group: Grupo específico a extraer (opcional)
            flags: Flags de regex (re.IGNORECASE, etc.)
        """
        self.pattern = pattern
        self.replacement = replacement
        self.extract_group = extract_group
        self.flags = flags
        
        action = "extraer" if replacement is None else "reemplazar"
        description = f"{action} con regex '{pattern}' en {len(columns)} columna(s)"
        super().__init__("regex_extraction", description, columns)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar extracción con regex"""
        if parameters is None:
            parameters = {}
            
        try:
            df_transformed = df.copy()
            
            pattern = parameters.get('pattern', self.pattern)
            replacement = parameters.get('replacement', self.replacement)
            extract_group = parameters.get('extract_group', self.extract_group)
            flags = parameters.get('flags', self.flags)
            columns = parameters.get('columns', self.columns)
            
            # Validar patrón regex
            try:
                re.compile(pattern, flags)
            except re.error as e:
                raise ValueError(f"Patrón regex inválido: {str(e)}")
            
            for column in columns:
                if column not in df_transformed.columns:
                    raise ValueError(f"Columna '{column}' no existe")
                
                series = df_transformed[column].astype(str)
                
                if replacement is not None:
                    # Reemplazar usando regex
                    result = series.str.replace(pattern, replacement, regex=True, flags=flags)
                elif extract_group is not None:
                    # Extraer grupo específico
                    def extract_group_func(text):
                        match = re.search(pattern, text, flags)
                        if match:
                            groups = match.groups()
                            if extract_group < len(groups):
                                return groups[extract_group]
                        return ''
                    
                    result = series.apply(extract_group_func)
                else:
                    # Extraer toda la coincidencia usando replace para obtener el match
                    def extract_match(text):
                        match = re.search(pattern, text, flags)
                        if match:
                            return match.group(0)
                        return ''
                    
                    result = series.apply(extract_match)
                
                df_transformed[column] = result
                logger.info(f"Extraction regex aplicada a columna '{column}'")
            
            return df_transformed
            
        except Exception as e:
            logger.error(f"Error en extracción regex: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de regex"""
        pattern = parameters.get('pattern', self.pattern)
        
        if not pattern or not isinstance(pattern, str):
            return False
        
        try:
            re.compile(pattern, parameters.get('flags', self.flags))
            return True
        except re.error:
            return False


class CaseConversionTransformation(TextProcessingTransformation):
    """
    Transformación para conversión de case (upper, lower, title, capitalize)
    """
    
    def __init__(self, columns: Union[str, List[str]], case_type: str = 'lower'):
        """
        Inicializar conversión de case
        
        Args:
            columns: Columna o lista de columnas
            case_type: Tipo de conversión ('upper', 'lower', 'title', 'capitalize')
        """
        self.case_type = case_type
        
        description = f"Convertir a {case_type} en {len(columns)} columna(s)"
        super().__init__("case_conversion", description, columns)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar conversión de case"""
        if parameters is None:
            parameters = {}
            
        try:
            df_transformed = df.copy()
            
            case_type = parameters.get('case_type', self.case_type)
            columns = parameters.get('columns', self.columns)
            
            if case_type not in ['upper', 'lower', 'title', 'capitalize']:
                raise ValueError(f"Tipo de conversión no válido: {case_type}")
            
            for column in columns:
                if column not in df_transformed.columns:
                    raise ValueError(f"Columna '{column}' no existe")
                
                series = df_transformed[column].astype(str)
                
                if case_type == 'upper':
                    result = series.str.upper()
                elif case_type == 'lower':
                    result = series.str.lower()
                elif case_type == 'title':
                    result = series.str.title()
                elif case_type == 'capitalize':
                    result = series.str.capitalize()
                
                df_transformed[column] = result
                logger.info(f"Conversión {case_type} aplicada a columna '{column}'")
            
            return df_transformed
            
        except Exception as e:
            logger.error(f"Error en conversión de case: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de conversión"""
        case_type = parameters.get('case_type', self.case_type)
        return case_type in ['upper', 'lower', 'title', 'capitalize']


class PaddingTrimmingTransformation(TextProcessingTransformation):
    """
    Transformación para padding y trimming de texto
    """
    
    def __init__(self, columns: Union[str, List[str]], width: int, fillchar: str = ' ',
                 side: str = 'right', strip: bool = False):
        """
        Inicializar padding/trimming
        
        Args:
            columns: Columna o lista de columnas
            width: Ancho objetivo
            fillchar: Carácter de relleno
            side: Lado ('left', 'right', 'both')
            strip: Si True, solo hacer trim sin padding
        """
        self.width = width
        self.fillchar = fillchar
        self.side = side
        self.strip = strip
        
        action = "trim" if strip else f"pad {side}"
        description = f"{action} texto a ancho {width} en {len(columns)} columna(s)"
        super().__init__("padding_trimming", description, columns)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar padding/trimming"""
        if parameters is None:
            parameters = {}
            
        try:
            df_transformed = df.copy()
            
            width = parameters.get('width', self.width)
            fillchar = parameters.get('fillchar', self.fillchar)
            side = parameters.get('side', self.side)
            strip = parameters.get('strip', self.strip)
            columns = parameters.get('columns', self.columns)
            
            if side not in ['left', 'right', 'both']:
                raise ValueError(f"Lado no válido: {side}")
            
            for column in columns:
                if column not in df_transformed.columns:
                    raise ValueError(f"Columna '{column}' no existe")
                
                series = df_transformed[column].astype(str)
                
                if strip:
                    # Solo trim
                    result = series.str.strip()
                else:
                    # Padding
                    if side == 'left':
                        result = series.str.pad(width, side='left', fillchar=fillchar)
                    elif side == 'right':
                        result = series.str.pad(width, side='right', fillchar=fillchar)
                    else:  # both
                        result = series.str.pad(width, side='both', fillchar=fillchar)
                
                df_transformed[column] = result
                logger.info(f"Padding/trimming aplicado a columna '{column}'")
            
            return df_transformed
            
        except Exception as e:
            logger.error(f"Error en padding/trimming: {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de padding/trimming"""
        width = parameters.get('width', self.width)
        side = parameters.get('side', self.side)
        fillchar = parameters.get('fillchar', self.fillchar)
        
        if not isinstance(width, int) or width <= 0:
            return False
        
        if side not in ['left', 'right', 'both']:
            return False
        
        if not isinstance(fillchar, str) or len(fillchar) != 1:
            return False
        
        return True


# Funciones de utilidad para crear transformaciones de texto
def create_text_cleaning(columns: Union[str, List[str]], **kwargs) -> TextCleaningTransformation:
    """Crear transformación de limpieza de texto"""
    return TextCleaningTransformation(columns, **kwargs)


def create_regex_extraction(columns: Union[str, List[str]], pattern: str, **kwargs) -> RegexExtractionTransformation:
    """Crear transformación de extracción con regex"""
    return RegexExtractionTransformation(columns, pattern, **kwargs)


def create_case_conversion(columns: Union[str, List[str]], case_type: str = 'lower') -> CaseConversionTransformation:
    """Crear transformación de conversión de case"""
    return CaseConversionTransformation(columns, case_type)


def create_padding_trimming(columns: Union[str, List[str]], width: int, **kwargs) -> PaddingTrimmingTransformation:
    """Crear transformación de padding/trimming"""
    return PaddingTrimmingTransformation(columns, width, **kwargs)