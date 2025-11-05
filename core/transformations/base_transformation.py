"""
Clase base para todas las transformaciones de datos
Implementa el patrón Command con funcionalidades comunes
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple, Union
import logging
import copy
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseTransformation(ABC):
    """
    Clase base abstracta para todas las transformaciones de datos.
    Implementa el patrón Command con capacidades de undo/redo y validación.
    """
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any] = None):
        """
        Inicializar transformación base
        
        Args:
            name: Nombre único de la transformación
            description: Descripción legible de la transformación
            parameters: Diccionario de parámetros por defecto
        """
        self.name = name
        self.description = description
        self.parameters = parameters or {}
        self.created_at = datetime.now()
        self.execution_count = 0
        self.last_execution_time = None
        self.is_reversible = True
        self._original_data = None  # Para operaciones reversibles
        self._validation_rules = {}
        
    @abstractmethod
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Ejecutar la transformación en el DataFrame
        
        Args:
            df: DataFrame de entrada
            parameters: Parámetros específicos para esta ejecución
            
        Returns:
            DataFrame transformado
            
        Raises:
            ValueError: Si los parámetros son inválidos
            TypeError: Si el DataFrame tiene tipos incorrectos
        """
        pass
    
    @abstractmethod
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validar parámetros de la transformación
        
        Args:
            parameters: Parámetros a validar
            
        Returns:
            True si los parámetros son válidos
            
        Raises:
            ValueError: Si los parámetros no son válidos
        """
        pass
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validar que el DataFrame sea adecuado para la transformación
        
        Args:
            df: DataFrame a validar
            
        Returns:
            True si el DataFrame es válido
            
        Raises:
            ValueError: Si el DataFrame no es válido
        """
        if df is None:
            raise TypeError("El parámetro debe ser un DataFrame de pandas")
        
        if df.empty:
            raise ValueError("El DataFrame no puede estar vacío")
        
        if not isinstance(df, pd.DataFrame):
            raise TypeError("El parámetro debe ser un DataFrame de pandas")
        
        # Validaciones específicas pueden ser sobrecargadas por subclases
        return True
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Obtener metadata de la transformación
        
        Returns:
            Diccionario con información de la transformación
        """
        return {
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters,
            'created_at': self.created_at.isoformat(),
            'execution_count': self.execution_count,
            'last_execution_time': self.last_execution_time.isoformat() if self.last_execution_time else None,
            'is_reversible': self.is_reversible,
            'validation_rules': self._validation_rules
        }
    
    def estimate_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Estimar el rendimiento de la transformación en el DataFrame dado
        
        Args:
            df: DataFrame de entrada
            
        Returns:
            Diccionario con información de rendimiento estimado
        """
        row_count = len(df)
        column_count = len(df.columns)
        memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
        
        # Estimaciones básicas basadas en el tamaño del dataset
        if row_count < 1000:
            complexity = "baja"
            estimated_time = "< 1s"
        elif row_count < 10000:
            complexity = "media"
            estimated_time = "1-5s"
        elif row_count < 100000:
            complexity = "alta"
            estimated_time = "5-30s"
        else:
            complexity = "muy alta"
            estimated_time = "> 30s"
        
        return {
            'estimated_complexity': complexity,
            'estimated_time': estimated_time,
            'row_count': row_count,
            'column_count': column_count,
            'memory_usage_mb': round(memory_usage, 2),
            'should_use_chunks': memory_usage > 100 or row_count > 50000
        }
    
    def _start_timing(self) -> float:
        """Iniciar medición de tiempo"""
        return datetime.now().timestamp()
    
    def _end_timing(self, start_time: float) -> float:
        """Finalizar medición de tiempo"""
        return datetime.now().timestamp() - start_time
    
    def _store_original_data(self, df: pd.DataFrame, parameters: Dict[str, Any]):
        """
        Almacenar datos originales para operaciones reversibles
        
        Args:
            df: DataFrame original
            parameters: Parámetros de la transformación
        """
        if self.is_reversible:
            self._original_data = {
                'data': copy.deepcopy(df),
                'parameters': copy.deepcopy(parameters)
            }
    
    def undo(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Deshacer la transformación (si es reversible)
        
        Args:
            df: DataFrame actual
            
        Returns:
            DataFrame en estado anterior
            
        Raises:
            NotImplementedError: Si la transformación no es reversible
        """
        if not self.is_reversible:
            raise NotImplementedError(f"La transformación '{self.name}' no es reversible")
        
        if self._original_data is None:
            raise ValueError("No hay datos originales almacenados para deshacer")
        
        logger.info(f"Deshaciendo transformación '{self.name}'")
        return copy.deepcopy(self._original_data['data'])
    
    def can_combine_with(self, other: 'BaseTransformation') -> bool:
        """
        Verificar si esta transformación puede combinarse con otra
        
        Args:
            other: Otra transformación
            
        Returns:
            True si pueden combinarse eficientemente
        """
        # Por defecto, las transformaciones no se combinan
        return False
    
    def get_dependencies(self) -> List[str]:
        """
        Obtener lista de dependencias de la transformación
        
        Returns:
            Lista de nombres de transformaciones de las que depende
        """
        return []
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', description='{self.description}')"


class CompositeTransformation(BaseTransformation):
    """
    Clase para transformaciones compuestas que combinan múltiples transformaciones
    """
    
    def __init__(self, name: str, description: str, transformations: List[BaseTransformation]):
        """
        Inicializar transformación compuesta
        
        Args:
            name: Nombre de la transformación compuesta
            description: Descripción
            transformations: Lista de transformaciones a ejecutar secuencialmente
        """
        super().__init__(name, description)
        self.transformations = transformations
        self.is_reversible = all(t.is_reversible for t in transformations)
    
    def execute(self, df: pd.DataFrame, parameters: Dict[str, Any] = None) -> pd.DataFrame:
        """Ejecutar todas las transformaciones en secuencia"""
        if parameters is None:
            parameters = {}
        
        result_df = df.copy()
        start_time = self._start_timing()
        
        try:
            # Ejecutar cada transformación
            for i, transformation in enumerate(self.transformations):
                logger.info(f"Ejecutando transformación {i+1}/{len(self.transformations)}: {transformation.name}")
                result_df = transformation.execute(result_df, parameters.get(transformation.name, {}))
            
            # Actualizar estadísticas
            self.execution_count += 1
            self.last_execution_time = datetime.fromtimestamp(start_time)
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error en transformación compuesta '{self.name}': {str(e)}")
            raise
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validar parámetros de todas las transformaciones"""
        for transformation in self.transformations:
            trans_params = parameters.get(transformation.name, {})
            if not transformation.validate_parameters(trans_params):
                return False
        return True
    
    def add_transformation(self, transformation: BaseTransformation):
        """Añadir una transformación a la secuencia"""
        self.transformations.append(transformation)
        self.is_reversible = self.is_reversible and transformation.is_reversible
    
    def remove_transformation(self, transformation: BaseTransformation):
        """Remover una transformación de la secuencia"""
        if transformation in self.transformations:
            self.transformations.remove(transformation)
            # Recalcular reversibilidad
            self.is_reversible = all(t.is_reversible for t in self.transformations)
    
    def set_reversible(self, reversible: bool):
        """Establecer reversibilidad de la transformación compuesta"""
        if len(self.transformations) > 0:
            # Solo permitir reversibilidad si todas las transformaciones son reversibles
            self.is_reversible = reversible and all(t.is_reversible for t in self.transformations)
        else:
            self.is_reversible = reversible
    
    def get_transformations(self) -> List[BaseTransformation]:
        """Obtener lista de transformaciones"""
        return self.transformations.copy()