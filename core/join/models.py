"""
Modelos de datos para funcionalidad de cruce de datos (join)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Tuple
import pandas as pd


class JoinType(Enum):
    """Tipos de join soportados"""
    INNER = "inner"
    LEFT = "left"
    RIGHT = "right"
    CROSS = "cross"


@dataclass
class JoinConfig:
    """Configuración para operación de join"""
    join_type: JoinType   # INNER, LEFT, RIGHT, CROSS
    left_keys: List[str] = field(default_factory=list)  # Columnas del dataset izquierdo
    right_keys: List[str] = field(default_factory=list)  # Columnas del dataset derecho
    suffixes: Tuple[str, str] = ('_left', '_right')  # Sufijos para columnas duplicadas
    validate_integrity: bool = True  # Validar integridad referencial
    sort_results: bool = True  # Ordenar resultados
    indicator: bool = False  # Añadir columna _merge
    how: str = 'left'  # Método de join (pandas)
    include_columns: List[str] = field(default_factory=list)  # Columnas a incluir en resultado (vacío = todas)


@dataclass
class JoinResult:
    """Resultado de operación de join"""
    data: pd.DataFrame  # Datos resultantes
    metadata: 'JoinMetadata'  # Metadatos del cruce
    config: 'JoinConfig' = None  # Configuración usada para el join
    success: bool = True
    error_message: str = ""
    processing_time: float = 0.0


@dataclass
class JoinMetadata:
    """Metadatos del cruce realizado"""
    left_rows: int  # Filas en dataset izquierdo
    right_rows: int  # Filas en dataset derecho
    result_rows: int  # Filas en resultado
    join_type: JoinType
    join_keys: List[str]
    matched_rows: int  # Filas con coincidencias
    left_only_rows: int  # Filas solo en izquierdo
    right_only_rows: int  # Filas solo en derecho
    memory_usage_mb: float
    processing_time_seconds: float
    timestamp: datetime


@dataclass
class ValidationResult:
    """Resultado de validación"""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)