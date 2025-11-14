"""
DataJoinManager: Clase principal para operaciones de cruce de datos
"""

import pandas as pd
import time
from datetime import datetime
from typing import List, Optional
import psutil
import os

from .models import JoinConfig, JoinResult, JoinMetadata, ValidationResult, JoinType
from .exceptions import JoinValidationError, JoinExecutionError, MemoryLimitExceededError, UnsupportedJoinError


class DataJoinManager:
    """Clase principal responsable de ejecutar operaciones de cruce entre datasets"""

    def __init__(self, left_df: pd.DataFrame, right_df: pd.DataFrame):
        """
        Inicializar DataJoinManager con los datasets

        Args:
            left_df: DataFrame del dataset izquierdo
            right_df: DataFrame del dataset derecho
        """
        self.left_df = left_df.copy()
        self.right_df = right_df.copy()

    def execute_join(self, config: JoinConfig) -> JoinResult:
        """
        Ejecutar operación de join según configuración

        Args:
            config: Configuración del join

        Returns:
            JoinResult con datos y metadatos
        """
        start_time = time.time()

        try:
            # Validar configuración
            validation = self.validate_join(config)
            if not validation.is_valid:
                # Para errores críticos, fallar
                return JoinResult(
                    data=pd.DataFrame(),
                    metadata=JoinMetadata(
                        left_rows=len(self.left_df),
                        right_rows=len(self.right_df),
                        result_rows=0,
                        join_type=config.join_type,
                        join_keys=config.left_keys + config.right_keys,
                        matched_rows=0,
                        left_only_rows=0,
                        right_only_rows=0,
                        memory_usage_mb=0.0,
                        processing_time_seconds=time.time() - start_time,
                        timestamp=datetime.now()
                    ),
                    config=config,
                    success=False,
                    error_message="; ".join(validation.errors),
                    processing_time=time.time() - start_time
                )

            # Verificar límites de memoria antes de ejecutar
            estimated_memory = self._estimate_memory_usage(config)
            available_memory = psutil.virtual_memory().available / 1024 / 1024  # MB

            # Determinar si usar chunking
            use_chunking = self._should_use_chunking(config, estimated_memory, available_memory)

            # Ejecutar join (con o sin chunking)
            try:
                if use_chunking:
                    result_df = self._perform_chunked_join(config)
                else:
                    result_df = self._perform_join(config)
            except Exception as e:
                raise JoinExecutionError(f"Error ejecutando join: {str(e)}")

            # Calcular metadatos
            metadata = self._calculate_metadata(config, result_df, start_time)

            return JoinResult(
                data=result_df,
                metadata=metadata,
                config=config,
                success=True,
                processing_time=time.time() - start_time
            )

        except Exception as e:
            return JoinResult(
                data=pd.DataFrame(),
                metadata=JoinMetadata(
                    left_rows=len(self.left_df),
                    right_rows=len(self.right_df),
                    result_rows=0,
                    join_type=config.join_type,
                    join_keys=config.left_keys + config.right_keys,
                    matched_rows=0,
                    left_only_rows=0,
                    right_only_rows=0,
                    memory_usage_mb=0.0,
                    processing_time_seconds=time.time() - start_time,
                    timestamp=datetime.now()
                ),
                config=config,
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )

    def validate_join(self, config: JoinConfig) -> ValidationResult:
        """
        Validar configuración de join

        Args:
            config: Configuración a validar

        Returns:
            ValidationResult con resultado de validación
        """
        result = ValidationResult()

        # Validar tipos de join
        if config.join_type not in [JoinType.INNER, JoinType.LEFT, JoinType.RIGHT, JoinType.CROSS]:
            raise UnsupportedJoinError(f"Tipo de join no soportado: {config.join_type}")

        # Para cross join, no se necesitan keys
        if config.join_type == JoinType.CROSS:
            if config.left_keys or config.right_keys:
                result.warnings.append("Cross join no requiere columnas de join")
            return result

        # Validar columnas de join
        if not config.left_keys:
            result.errors.append("Columnas de join del dataset izquierdo son requeridas")
            result.is_valid = False

        if not config.right_keys:
            result.errors.append("Columnas de join del dataset derecho son requeridas")
            result.is_valid = False

        if len(config.left_keys) != len(config.right_keys):
            result.errors.append("Número de columnas de join debe ser igual en ambos datasets")
            result.is_valid = False

        # Verificar existencia de columnas
        missing_left = [col for col in config.left_keys if col not in self.left_df.columns]
        if missing_left:
            result.errors.append(f"Columnas no encontradas en dataset izquierdo: {missing_left}")
            result.is_valid = False

        missing_right = [col for col in config.right_keys if col not in self.right_df.columns]
        if missing_right:
            result.errors.append(f"Columnas no encontradas en dataset derecho: {missing_right}")
            result.is_valid = False

        # Verificar compatibilidad de tipos (advertencia)
        if result.is_valid and config.validate_integrity:
            for left_key, right_key in zip(config.left_keys, config.right_keys):
                left_dtype = self.left_df[left_key].dtype
                right_dtype = self.right_df[right_key].dtype
                if left_dtype != right_dtype:
                    result.warnings.append(
                        f"Tipos de datos diferentes para {left_key} ({left_dtype}) y {right_key} ({right_dtype})"
                    )

        # Verificar columnas duplicadas
        left_cols = set(self.left_df.columns)
        right_cols = set(self.right_df.columns)
        duplicated = left_cols & right_cols - set(config.left_keys) - set(config.right_keys)
        if duplicated:
            result.warnings.append(f"Columnas duplicadas detectadas: {list(duplicated)}")
            result.suggestions.append("Considere usar sufijos personalizados")

        return result

    def get_join_preview(self, config: JoinConfig, max_rows: int = 100) -> pd.DataFrame:
        """
        Obtener preview del resultado del join

        Args:
            config: Configuración del join
            max_rows: Número máximo de filas a devolver

        Returns:
            DataFrame con preview de resultados
        """
        try:
            # Para previews, usar una versión optimizada que limita el procesamiento
            if config.join_type == JoinType.CROSS:
                # Para cross join, tomar muestras pequeñas de ambos datasets
                left_sample = self.left_df.head(min(50, len(self.left_df)))
                right_sample = self.right_df.head(min(50, len(self.right_df)))
                temp_manager = DataJoinManager(left_sample, right_sample)
                result_df = temp_manager._perform_join(config)
                return result_df.head(max_rows)
            else:
                # Para otros joins, usar el método normal pero limitar el resultado
                result_df = self._perform_join(config)
                return result_df.head(max_rows)
        except Exception:
            return pd.DataFrame()

    def _perform_join(self, config: JoinConfig) -> pd.DataFrame:
        """
        Ejecutar la operación de join según configuración

        Args:
            config: Configuración del join

        Returns:
            DataFrame con resultado del join
        """
        # Para cross join
        if config.join_type == JoinType.CROSS:
            result = pd.merge(
                self.left_df,
                self.right_df,
                how='cross',
                suffixes=config.suffixes
            )
            return result

        # Para otros joins
        how_map = {
            JoinType.INNER: 'inner',
            JoinType.LEFT: 'left',
            JoinType.RIGHT: 'right'
        }

        # Usar indicator para calcular estadísticas
        result = pd.merge(
            self.left_df,
            self.right_df,
            left_on=config.left_keys,
            right_on=config.right_keys,
            how=how_map[config.join_type],
            suffixes=config.suffixes,
            indicator=True,
            validate='m:m' if config.validate_integrity else None
        )

        # Remover columna indicator si no se solicita
        if not config.indicator:
            result = result.drop(columns=['_merge'])

        # Ordenar si se solicita
        if config.sort_results and config.left_keys:
            result = result.sort_values(config.left_keys[0])

        # Filtrar columnas si se especifica
        if config.include_columns:
            # Verificar que las columnas existan en el resultado
            existing_columns = [col for col in config.include_columns if col in result.columns]
            if existing_columns:
                result = result[existing_columns]
            else:
                # Si ninguna columna existe, mantener todas las columnas
                pass

        return result

    def _calculate_metadata(self, config: JoinConfig, result_df: pd.DataFrame, start_time: float) -> JoinMetadata:
        """
        Calcular metadatos del join realizado

        Args:
            config: Configuración del join
            result_df: DataFrame resultado
            start_time: Tiempo de inicio

        Returns:
            JoinMetadata con estadísticas
        """
        processing_time = time.time() - start_time

        # Estadísticas básicas
        left_rows = len(self.left_df)
        right_rows = len(self.right_df)
        result_rows = len(result_df)

        # Calcular estadísticas de matching
        if config.join_type == JoinType.CROSS:
            matched_rows = result_rows
            left_only_rows = 0
            right_only_rows = 0
        else:
            # Usar merge temporal con indicator para estadísticas
            temp_result = pd.merge(
                self.left_df,
                self.right_df,
                left_on=config.left_keys,
                right_on=config.right_keys,
                how='outer',
                indicator=True
            )

            matched_rows = len(temp_result[temp_result['_merge'] == 'both'])
            left_only_rows = len(temp_result[temp_result['_merge'] == 'left_only'])
            right_only_rows = len(temp_result[temp_result['_merge'] == 'right_only'])

        # Uso de memoria
        memory_usage = result_df.memory_usage(deep=True).sum() / 1024 / 1024

        return JoinMetadata(
            left_rows=left_rows,
            right_rows=right_rows,
            result_rows=result_rows,
            join_type=config.join_type,
            join_keys=config.left_keys + config.right_keys,
            matched_rows=matched_rows,
            left_only_rows=left_only_rows,
            right_only_rows=right_only_rows,
            memory_usage_mb=memory_usage,
            processing_time_seconds=processing_time,
            timestamp=datetime.now()
        )

    def _should_use_chunking(self, config: JoinConfig, estimated_memory: float, available_memory: float) -> bool:
        """
        Determinar si se debe usar chunking basado en estimaciones de memoria

        Args:
            config: Configuración del join
            estimated_memory: Memoria estimada en MB
            available_memory: Memoria disponible en MB

        Returns:
            True si se debe usar chunking
        """
        # Usar chunking si se estima usar más del 50% de la memoria disponible
        memory_threshold = available_memory * 0.5

        # Especialmente para cross joins que pueden ser muy grandes
        if config.join_type == JoinType.CROSS:
            cross_product_size = len(self.left_df) * len(self.right_df)
            # Usar chunking para cross joins con 1M o más combinaciones
            if cross_product_size >= 1_000_000:
                return True

        return estimated_memory > memory_threshold

    def _perform_chunked_join(self, config: JoinConfig) -> pd.DataFrame:
        """
        Ejecutar join usando procesamiento por chunks para datasets grandes

        Args:
            config: Configuración del join

        Returns:
            DataFrame con resultado del join
        """
        if config.join_type == JoinType.CROSS:
            return self._perform_chunked_cross_join(config)
        else:
            return self._perform_chunked_regular_join(config)

    def _perform_chunked_cross_join(self, config: JoinConfig) -> pd.DataFrame:
        """
        Ejecutar cross join usando chunks para evitar problemas de memoria

        Args:
            config: Configuración del join

        Returns:
            DataFrame con resultado del cross join
        """
        # Para cross joins grandes, procesar por chunks del dataset más pequeño
        if len(self.left_df) <= len(self.right_df):
            smaller_df, larger_df = self.left_df, self.right_df
            swap_order = False
        else:
            smaller_df, larger_df = self.right_df, self.left_df
            swap_order = True

        chunk_size = max(1000, len(smaller_df) // 10)  # Dividir en al menos 10 chunks
        results = []

        for i in range(0, len(smaller_df), chunk_size):
            chunk = smaller_df.iloc[i:i + chunk_size]
            chunk_result = pd.merge(
                chunk if not swap_order else larger_df,
                larger_df if not swap_order else chunk,
                how='cross',
                suffixes=config.suffixes
            )
            results.append(chunk_result)

        # Combinar todos los resultados
        final_result = pd.concat(results, ignore_index=True)
        return final_result

    def _perform_chunked_regular_join(self, config: JoinConfig) -> pd.DataFrame:
        """
        Ejecutar join regular usando chunks para optimizar memoria

        Args:
            config: Configuración del join

        Returns:
            DataFrame con resultado del join
        """
        # Para joins regulares, usar el dataset más pequeño como referencia
        # y procesar el más grande por chunks si es necesario
        if len(self.left_df) <= len(self.right_df):
            reference_df, chunk_df = self.left_df, self.right_df
            left_on, right_on = config.left_keys, config.right_keys
            swap_order = False
        else:
            reference_df, chunk_df = self.right_df, self.left_df
            left_on, right_on = config.right_keys, config.left_keys
            swap_order = True

        # Si el dataset de referencia es pequeño, hacer join normal
        if len(reference_df) < 10000:
            return self._perform_join(config)

        # Para datasets grandes, dividir el chunk_df en partes
        chunk_size = max(5000, len(chunk_df) // 5)  # Dividir en 5 chunks máximo
        results = []

        how_map = {
            JoinType.INNER: 'inner',
            JoinType.LEFT: 'left',
            JoinType.RIGHT: 'right'
        }

        for i in range(0, len(chunk_df), chunk_size):
            chunk = chunk_df.iloc[i:i + chunk_size]

            if swap_order:
                chunk_result = pd.merge(
                    chunk, reference_df,
                    left_on=right_on, right_on=left_on,
                    how=how_map[config.join_type],
                    suffixes=config.suffixes,
                    indicator=True,
                    validate='m:m' if config.validate_integrity else None
                )
            else:
                chunk_result = pd.merge(
                    reference_df, chunk,
                    left_on=left_on, right_on=right_on,
                    how=how_map[config.join_type],
                    suffixes=config.suffixes,
                    indicator=True,
                    validate='m:m' if config.validate_integrity else None
                )
            results.append(chunk_result)

        # Combinar resultados
        final_result = pd.concat(results, ignore_index=True)

        # Remover duplicados si es inner join (pueden aparecer en chunks)
        if config.join_type == JoinType.INNER:
            final_result = final_result.drop_duplicates()

        # Remover columna indicator si no se solicita
        if not config.indicator:
            final_result = final_result.drop(columns=['_merge'])

        # Ordenar si se solicita
        if config.sort_results and config.left_keys:
            sort_key = config.left_keys[0] if not swap_order else config.right_keys[0]
            if sort_key in final_result.columns:
                final_result = final_result.sort_values(sort_key)

        return final_result

    def _estimate_memory_usage(self, config: JoinConfig) -> float:
        """
        Estimar uso de memoria para la operación de join

        Args:
            config: Configuración del join

        Returns:
            Memoria estimada en MB
        """
        left_memory = self.left_df.memory_usage(deep=True).sum() / 1024 / 1024
        right_memory = self.right_df.memory_usage(deep=True).sum() / 1024 / 1024

        # Estimación básica: resultado tendrá al menos el tamaño de los datasets combinados
        if config.join_type == JoinType.CROSS:
            # Cross join: producto cartesiano
            estimated_rows = len(self.left_df) * len(self.right_df)
            estimated_cols = len(self.left_df.columns) + len(self.right_df.columns)
        else:
            # Otros joins: estimación conservadora
            estimated_rows = max(len(self.left_df), len(self.right_df))
            estimated_cols = len(self.left_df.columns) + len(self.right_df.columns)

        # Estimación por celda (8 bytes promedio por valor)
        estimated_memory = (estimated_rows * estimated_cols * 8) / 1024 / 1024

        # Factor de overhead (índices, etc.)
        return estimated_memory * 1.5