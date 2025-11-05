"""
Gestor centralizado de transformaciones de datos
Coordina la ejecución, validación y gestión de pipelines de transformaciones
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Union, Type
import logging
import copy
import json
import os
from datetime import datetime
from collections import deque
import warnings

from .base_transformation import BaseTransformation, CompositeTransformation
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

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransformationManager:
    """
    Gestor centralizado para el sistema de transformaciones de datos.
    Proporciona una interfaz unificada para crear, ejecutar y gestionar pipelines de transformaciones.
    """
    
    def __init__(self, enable_history: bool = True, max_history_size: int = 50):
        """
        Inicializar el gestor de transformaciones
        
        Args:
            enable_history: Habilitar historial de operaciones
            max_history_size: Tamaño máximo del historial
        """
        self._transformations_registry = {}
        self._pipelines = {}
        self._current_pipeline = None
        self._history_enabled = enable_history
        self._history = deque(maxlen=max_history_size)
        self._redo_stack = deque()
        self._original_data_cache = {}
        self._performance_metrics = {}
        
        # Registrar transformaciones básicas
        self._register_basic_transformations()
        
        # Configuración de optimización
        self._chunk_threshold = 10000  # Filas para usar procesamiento por chunks
        self._parallel_threshold = 50000  # Filas para activar paralelización
        self._cache_enabled = True
        self._max_cache_size = 5
        
        logger.info("TransformationManager inicializado con historial habilitado" if enable_history else "TransformationManager inicializado sin historial")
    
    def _register_basic_transformations(self):
        """Registrar transformaciones básicas en el sistema"""
        try:
            # Transformaciones de columnas
            self.register_transformation(RenameColumnsTransformation, "rename_columns", "columns")
            self.register_transformation(CreateCalculatedColumnTransformation, "create_calculated_column", "columns")
            self.register_transformation(ApplyFunctionTransformation, "apply_function", "columns")
            self.register_transformation(DropColumnsTransformation, "drop_columns", "columns")
            
            # Transformaciones matemáticas
            self.register_transformation(LogarithmicTransformation, "logarithmic", "math")
            self.register_transformation(ExponentialTransformation, "exponential", "math")
            self.register_transformation(ScalingTransformation, "scaling", "math")
            self.register_transformation(NormalizationTransformation, "normalization", "math")
            self.register_transformation(CustomMathTransformation, "custom_math", "math")
            
            # Transformaciones de texto
            self.register_transformation(TextCleaningTransformation, "text_cleaning", "text")
            self.register_transformation(RegexExtractionTransformation, "regex_extraction", "text")
            self.register_transformation(CaseConversionTransformation, "case_conversion", "text")
            self.register_transformation(PaddingTrimmingTransformation, "padding_trimming", "text")
            
            # Transformaciones de fecha y tiempo
            self.register_transformation(DateParsingTransformation, "date_parsing", "date")
            self.register_transformation(ComponentExtractionTransformation, "component_extraction", "date")
            self.register_transformation(DateDifferenceTransformation, "date_difference", "date")
            self.register_transformation(TimeZoneTransformation, "time_zone", "date")
            
            # Transformaciones de codificación categórica
            self.register_transformation(LabelEncodingTransformation, "label_encoding", "encoding")
            self.register_transformation(OneHotEncodingTransformation, "one_hot_encoding", "encoding")
            self.register_transformation(OrdinalEncodingTransformation, "ordinal_encoding", "encoding")
            self.register_transformation(TargetEncodingTransformation, "target_encoding", "encoding")
            
            # Transformaciones de agregación avanzada
            self.register_transformation(MultiFunctionAggregationTransformation, "multi_function_aggregation", "aggregation")
            self.register_transformation(AdvancedPivotingTransformation, "advanced_pivoting", "aggregation")
            self.register_transformation(RollingWindowTransformation, "rolling_window", "aggregation")
            self.register_transformation(ExpandingWindowTransformation, "expanding_window", "aggregation")
            self.register_transformation(GroupByTransformationTransformation, "groupby_transformation", "aggregation")
            
            logger.info("Transformaciones básicas registradas correctamente")
        except Exception as e:
            logger.error(f"Error al registrar transformaciones básicas: {str(e)}")
            # No propagamos la excepción para permitir que el sistema continúe funcionando
            # con transformaciones básicas que pudieron haberse registrado correctamente
    
    def register_transformation(self, transformation_class: Type[BaseTransformation], 
                              name: str = None, category: str = "general"):
        """
        Registrar una nueva clase de transformación
        
        Args:
            transformation_class: Clase de transformación a registrar
            name: Nombre para el registro (usa el nombre de clase si no se especifica)
            category: Categoría de la transformación
        """
        if not issubclass(transformation_class, BaseTransformation):
            raise ValueError("La clase debe ser una subclase de BaseTransformation")
        
        registered_name = name or transformation_class.__name__
        
        if registered_name in self._transformations_registry:
            logger.warning(f"Transformación '{registered_name}' ya registrada, sobrescribiendo")
        
        self._transformations_registry[registered_name] = {
            'class': transformation_class,
            'category': category,
            'registered_at': datetime.now()
        }
        
        logger.info(f"Transformación '{registered_name}' registrada en categoría '{category}'")
    
    def create_transformation(self, transformation_name: str, parameters: Dict[str, Any] = None) -> BaseTransformation:
        """
        Crear una instancia de transformación
        
        Args:
            transformation_name: Nombre de la transformación registrada
            parameters: Parámetros para la transformación
            
        Returns:
            Instancia de la transformación
            
        Raises:
            ValueError: Si la transformación no está registrada
        """
        if transformation_name not in self._transformations_registry:
            raise ValueError(f"Transformación '{transformation_name}' no está registrada")
        
        transformation_info = self._transformations_registry[transformation_name]
        transformation_class = transformation_info['class']
        
        try:
            # Crear instancia con parámetros básicos
            instance = transformation_class(
                name=transformation_name,
                description=transformation_info.get('description', ''),
                parameters=parameters or {}
            )
            
            logger.info(f"Transformación '{transformation_name}' creada exitosamente")
            return instance
            
        except Exception as e:
            logger.error(f"Error al crear transformación '{transformation_name}': {str(e)}")
            raise
    
    def get_available_transformations(self, category: str = None) -> Dict[str, Dict[str, Any]]:
        """
        Obtener lista de transformaciones disponibles
        
        Args:
            category: Filtrar por categoría específica
            
        Returns:
            Diccionario con información de transformaciones disponibles
        """
        if category:
            return {name: info for name, info in self._transformations_registry.items() 
                   if info.get('category') == category}
        else:
            return self._transformations_registry.copy()
    
    def execute_transformation(self, df: pd.DataFrame, transformation_name: str, 
                             parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Ejecutar una transformación individual
        
        Args:
            df: DataFrame de entrada
            transformation_name: Nombre de la transformación a ejecutar
            parameters: Parámetros específicos para la transformación
            
        Returns:
            DataFrame transformado
            
        Raises:
            ValueError: Si la transformación no existe o los parámetros son inválidos
        """
        start_time = datetime.now()
        
        try:
            # Crear y validar la transformación
            transformation = self.create_transformation(transformation_name, parameters)
            
            # Validar datos de entrada
            transformation.validate_data(df)
            
            # Validar parámetros
            if not transformation.validate_parameters(parameters):
                raise ValueError(f"Parámetros inválidos para transformación '{transformation_name}'")
            
            # Almacenar datos originales si es reversible
            transformation._store_original_data(df, parameters)
            
            # Ejecutar transformación
            logger.info(f"Ejecutando transformación '{transformation_name}' en DataFrame con {len(df)} filas")
            result_df = transformation.execute(df, parameters)
            
            # Calcular métricas
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_metrics(transformation_name, execution_time, len(df))
            
            # Guardar en historial si está habilitado
            if self._history_enabled:
                self._save_to_history({
                    'operation': 'single_transformation',
                    'transformation_name': transformation_name,
                    'parameters': parameters,
                    'original_shape': df.shape,
                    'result_shape': result_df.shape,
                    'execution_time': execution_time,
                    'timestamp': datetime.now().isoformat()
                })
            
            logger.info(f"Transformación '{transformation_name}' completada en {execution_time:.2f}s")
            return result_df
            
        except Exception as e:
            logger.error(f"Error en transformación '{transformation_name}': {str(e)}")
            raise
    
    def execute_pipeline(self, df: pd.DataFrame, pipeline_steps: List[Dict[str, Any]], 
                        pipeline_name: str = None, use_optimization: bool = True) -> pd.DataFrame:
        """
        Ejecutar un pipeline de transformaciones
        
        Args:
            df: DataFrame de entrada
            pipeline_steps: Lista de pasos del pipeline
                Cada paso: {'transformation': 'nombre', 'parameters': {...}, 'name': 'paso1'}
            pipeline_name: Nombre del pipeline para el historial
            use_optimization: Aplicar optimizaciones de rendimiento
            
        Returns:
            DataFrame transformado
        """
        if not pipeline_steps:
            return df.copy()
        
        start_time = datetime.now()
        current_df = df.copy()
        pipeline_id = pipeline_name or f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Optimizaciones para datasets grandes
            if use_optimization and self._should_optimize_pipeline(len(df), len(pipeline_steps)):
                logger.info("Aplicando optimizaciones al pipeline")
                current_df = self._optimize_pipeline_execution(current_df, pipeline_steps)
            else:
                # Ejecución secuencial estándar
                executed_steps = []
                
                for i, step in enumerate(pipeline_steps):
                    step_name = step.get('name', f"step_{i+1}")
                    transformation_name = step['transformation']
                    parameters = step.get('parameters', {})
                    
                    logger.info(f"Ejecutando paso {i+1}/{len(pipeline_steps)}: {step_name}")
                    
                    # Validar compatibilidad con paso anterior
                    if not self._validate_step_compatibility(current_df, transformation_name, parameters):
                        logger.warning(f"Posible problema de compatibilidad en paso {step_name}")
                    
                    # Ejecutar transformación
                    original_shape = current_df.shape
                    current_df = self.execute_transformation(current_df, transformation_name, parameters)
                    
                    executed_steps.append({
                        'step': step_name,
                        'transformation': transformation_name,
                        'parameters': parameters,
                        'original_shape': original_shape,
                        'result_shape': current_df.shape
                    })
            
            # Guardar pipeline ejecutado
            total_time = (datetime.now() - start_time).total_seconds()
            self._save_pipeline(pipeline_id, pipeline_steps, executed_steps, total_time)
            
            # Guardar en historial
            if self._history_enabled:
                self._save_to_history({
                    'operation': 'pipeline_execution',
                    'pipeline_id': pipeline_id,
                    'steps_count': len(pipeline_steps),
                    'executed_steps': executed_steps,
                    'original_shape': df.shape,
                    'result_shape': current_df.shape,
                    'total_time': total_time,
                    'timestamp': datetime.now().isoformat()
                })
            
            logger.info(f"Pipeline '{pipeline_id}' completado con {len(pipeline_steps)} pasos en {total_time:.2f}s")
            return current_df
            
        except Exception as e:
            logger.error(f"Error en pipeline '{pipeline_id}': {str(e)}")
            raise
    
    def _should_optimize_pipeline(self, row_count: int, step_count: int) -> bool:
        """Determinar si se deben aplicar optimizaciones al pipeline"""
        return row_count > self._chunk_threshold or step_count > 5
    
    def _optimize_pipeline_execution(self, df: pd.DataFrame, pipeline_steps: List[Dict[str, Any]]) -> pd.DataFrame:
        """Aplicar optimizaciones al pipeline"""
        # Por ahora, ejecución secuencial con validación mejorada
        # En el futuro se puede implementar paralelización y chunking
        current_df = df.copy()
        
        for i, step in enumerate(pipeline_steps):
            transformation_name = step['transformation']
            parameters = step.get('parameters', {})
            
            # Validar datos antes de cada paso
            self._validate_data_for_step(current_df, step)
            
            current_df = self.execute_transformation(current_df, transformation_name, parameters)
        
        return current_df
    
    def _validate_step_compatibility(self, df: pd.DataFrame, transformation_name: str, parameters: Dict[str, Any]) -> bool:
        """Validar compatibilidad de un paso con el estado actual del DataFrame"""
        try:
            # Crear transformación temporal para validar
            transformation = self.create_transformation(transformation_name, parameters)
            return transformation.validate_data(df)
        except:
            return False
    
    def _validate_data_for_step(self, df: pd.DataFrame, step: Dict[str, Any]):
        """Validar datos para un paso específico del pipeline"""
        transformation_name = step['transformation']
        parameters = step.get('parameters', {})
        
        # Validaciones específicas por tipo de transformación
        if 'column' in parameters:
            if parameters['column'] not in df.columns:
                raise ValueError(f"Columna '{parameters['column']}' no existe en el DataFrame")
        
        if 'columns' in parameters:
            missing_cols = set(parameters['columns']) - set(df.columns)
            if missing_cols:
                raise ValueError(f"Columnas faltantes: {missing_cols}")
    
    def _update_performance_metrics(self, transformation_name: str, execution_time: float, row_count: int):
        """Actualizar métricas de rendimiento"""
        if transformation_name not in self._performance_metrics:
            self._performance_metrics[transformation_name] = {
                'total_executions': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'min_time': float('inf'),
                'max_time': 0.0,
                'total_rows_processed': 0
            }
        
        metrics = self._performance_metrics[transformation_name]
        metrics['total_executions'] += 1
        metrics['total_time'] += execution_time
        metrics['avg_time'] = metrics['total_time'] / metrics['total_executions']
        metrics['min_time'] = min(metrics['min_time'], execution_time)
        metrics['max_time'] = max(metrics['max_time'], execution_time)
        metrics['total_rows_processed'] += row_count
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Obtener reporte de rendimiento de las transformaciones"""
        return {
            'transformations': self._performance_metrics,
            'total_operations': sum(m['total_executions'] for m in self._performance_metrics.values()),
            'most_used_transformation': max(self._performance_metrics.items(), 
                                          key=lambda x: x[1]['total_executions'])[0] if self._performance_metrics else None,
            'fastest_transformation': min(self._performance_metrics.items(), 
                                        key=lambda x: x[1]['avg_time'])[0] if self._performance_metrics else None
        }
    
    def _save_pipeline(self, pipeline_id: str, steps: List[Dict], executed_steps: List[Dict], total_time: float):
        """Guardar pipeline ejecutado"""
        self._pipelines[pipeline_id] = {
            'steps': steps,
            'executed_steps': executed_steps,
            'total_time': total_time,
            'created_at': datetime.now().isoformat(),
            'execution_count': 1
        }
    
    def get_saved_pipelines(self) -> Dict[str, Dict[str, Any]]:
        """Obtener pipelines guardados"""
        return self._pipelines.copy()
    
    def _save_to_history(self, operation_data: Dict[str, Any]):
        """Guardar operación en el historial"""
        self._history.append(operation_data)
        # Limpiar redo stack cuando se hace una nueva operación
        self._redo_stack.clear()
    
    def get_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """Obtener historial de operaciones"""
        history = list(self._history)
        return history[-limit:] if limit else history
    
    def undo_last_operation(self) -> Optional[Dict[str, Any]]:
        """Deshacer la última operación"""
        if not self._history:
            return None
        
        last_operation = self._history.pop()
        self._redo_stack.append(last_operation)
        
        logger.info(f"Operación deshecha: {last_operation.get('operation', 'unknown')}")
        return last_operation
    
    def redo_last_operation(self) -> Optional[Dict[str, Any]]:
        """Rehacer la última operación deshecha"""
        if not self._redo_stack:
            return None
        
        operation = self._redo_stack.pop()
        self._history.append(operation)
        
        logger.info(f"Operación rehecha: {operation.get('operation', 'unknown')}")
        return operation
    
    def can_undo(self) -> bool:
        """Verificar si se puede deshacer"""
        return len(self._history) > 0
    
    def can_redo(self) -> bool:
        """Verificar si se puede rehacer"""
        return len(self._redo_stack) > 0
    
    def export_pipeline(self, pipeline_id: str, filepath: str) -> bool:
        """Exportar pipeline a archivo JSON"""
        if pipeline_id not in self._pipelines:
            raise ValueError(f"Pipeline '{pipeline_id}' no existe")
        
        try:
            pipeline_data = self._pipelines[pipeline_id]
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(pipeline_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Pipeline '{pipeline_id}' exportado a {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error al exportar pipeline: {str(e)}")
            return False
    
    def import_pipeline(self, filepath: str, pipeline_id: str = None) -> str:
        """Importar pipeline desde archivo JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                pipeline_data = json.load(f)
            
            # Generar ID si no se proporciona
            imported_id = pipeline_id or f"imported_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Validar estructura del pipeline
            if 'steps' not in pipeline_data:
                raise ValueError("Archivo de pipeline inválido: falta 'steps'")
            
            self._pipelines[imported_id] = pipeline_data
            logger.info(f"Pipeline importado como '{imported_id}' desde {filepath}")
            return imported_id
            
        except Exception as e:
            logger.error(f"Error al importar pipeline: {str(e)}")
            raise
    
    def clear_history(self):
        """Limpiar historial de operaciones"""
        self._history.clear()
        self._redo_stack.clear()
        logger.info("Historial de operaciones limpiado")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Obtener información del sistema de transformaciones"""
        return {
            'registered_transformations': len(self._transformations_registry),
            'saved_pipelines': len(self._pipelines),
            'history_size': len(self._history),
            'redo_size': len(self._redo_stack),
            'performance_metrics_available': len(self._performance_metrics) > 0,
            'configuration': {
                'chunk_threshold': self._chunk_threshold,
                'parallel_threshold': self._parallel_threshold,
                'cache_enabled': self._cache_enabled,
                'max_cache_size': self._max_cache_size
            }
        }


# Instancia global del gestor para uso en toda la aplicación
_global_transformation_manager = None


def get_transformation_manager() -> TransformationManager:
    """Obtener la instancia global del gestor de transformaciones"""
    global _global_transformation_manager
    if _global_transformation_manager is None:
        _global_transformation_manager = TransformationManager()
    return _global_transformation_manager


def reset_transformation_manager():
    """Resetear la instancia global del gestor (para testing)"""
    global _global_transformation_manager
    _global_transformation_manager = None