"""
Módulo de Transformaciones de Datos para Flash View Sheet
Implementa operaciones avanzadas de transformación usando patrones Command, Pipeline y Factory
"""

from .base_transformation import BaseTransformation, CompositeTransformation
from .transformation_manager import TransformationManager
from .column_transformations import (
    ColumnTransformation,
    RenameColumnsTransformation,
    CreateCalculatedColumnTransformation,
    ApplyFunctionTransformation,
    DropColumnsTransformation
)
from .mathematical import (
    MathematicalTransformation,
    LogarithmicTransformation,
    ExponentialTransformation,
    ScalingTransformation,
    NormalizationTransformation,
    CustomMathTransformation
)
from .text_processing import (
    TextProcessingTransformation,
    TextCleaningTransformation,
    RegexExtractionTransformation,
    CaseConversionTransformation,
    PaddingTrimmingTransformation
)
from .date_time import (
    DateTimeTransformation,
    DateParsingTransformation,
    ComponentExtractionTransformation,
    DateDifferenceTransformation,
    TimeZoneTransformation
)
from .encoding import (
    CategoricalEncodingTransformation,
    LabelEncodingTransformation,
    OneHotEncodingTransformation,
    OrdinalEncodingTransformation,
    TargetEncodingTransformation
)
from .advanced_aggregations import (
    AdvancedAggregationTransformation,
    MultiFunctionAggregationTransformation,
    AdvancedPivotingTransformation,
    RollingWindowTransformation,
    ExpandingWindowTransformation,
    GroupByTransformationTransformation
)

__all__ = [
    'BaseTransformation',
    'CompositeTransformation',
    'TransformationManager',
    'ColumnTransformation',
    'RenameColumnsTransformation',
    'CreateCalculatedColumnTransformation',
    'ApplyFunctionTransformation',
    'DropColumnsTransformation',
    'MathematicalTransformation',
    'LogarithmicTransformation',
    'ExponentialTransformation',
    'ScalingTransformation',
    'NormalizationTransformation',
    'CustomMathTransformation',
    'TextProcessingTransformation',
    'TextCleaningTransformation',
    'RegexExtractionTransformation',
    'CaseConversionTransformation',
    'PaddingTrimmingTransformation',
    'DateTimeTransformation',
    'DateParsingTransformation',
    'ComponentExtractionTransformation',
    'DateDifferenceTransformation',
    'TimeZoneTransformation',
    'CategoricalEncodingTransformation',
    'LabelEncodingTransformation',
    'OneHotEncodingTransformation',
    'OrdinalEncodingTransformation',
    'TargetEncodingTransformation',
    'AdvancedAggregationTransformation',
    'MultiFunctionAggregationTransformation',
    'AdvancedPivotingTransformation',
    'RollingWindowTransformation',
    'ExpandingWindowTransformation',
    'GroupByTransformationTransformation'
]

# Versión del módulo
__version__ = '1.2.0'