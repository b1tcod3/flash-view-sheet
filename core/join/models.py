"""
Modelos de datos para funcionalidad de cruce de datos (join)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

import pandas as pd

class JoinType(Enum):
    """Tipos de join soportados"""
    INNER = "inner"
    LEFT = "left"
    RIGHT = "right"
    OUTER = "outer"
    CROSS = "cross"

@dataclass
class JoinConfig:
    """Configuración para operación de join.

    Representa todos los parámetros necesarios para ejecutar un join
    entre dos datasets. El tipo de join se define con join_type y las
    columnas de unión con left_keys/right_keys.
    """
    join_type: JoinType
    left_keys: list[str] = field(default_factory=list)
    right_keys: list[str] = field(default_factory=list)
    suffixes: tuple[str, str] = ('_left', '_right')
    validate_integrity: bool = True
    sort_results: bool = True
    indicator: bool = False
    include_columns: list[str] = field(default_factory=list)
    integrity_mode: str | None = 'm:m'

@dataclass
class JoinResult:
    """Resultado de operación de join.

    Contiene el DataFrame resultante, metadatos del cruce y el estado
    de la operación. El tiempo de procesamiento se consulta a través
    de metadata.processing_time_seconds.
    """
    data: pd.DataFrame
    metadata: 'JoinMetadata'
    config: Optional['JoinConfig'] = None
    success: bool = True
    error_message: str = ""

@dataclass
class JoinMetadata:
    """Metadatos del cruce realizado.

    Captura estadísticas del join para informar al usuario:
    tamaños de datasets, filas resultantes, coincidencias,
    uso de memoria y tiempo de procesamiento.
    """
    left_rows: int
    right_rows: int
    result_rows: int
    join_type: JoinType
    join_keys: list[str]
    matched_rows: int
    left_only_rows: int
    right_only_rows: int
    memory_usage_mb: float
    processing_time_seconds: float
    timestamp: datetime

@dataclass
class ValidationResult:
    """Resultado de validación de configuración de join.

    is_valid indica si la configuración puede ejecutarse.
    errors bloquean la ejecución, warnings son informativos,
    suggestions proponen mejoras al usuario.
    """
    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)