"""
JoinService: Servicio stateless de orquestación para operaciones de cruce

Envuelve DataJoinManager exponiendo una API limpia para la UI y el
coordinator. Cada método recibe los DataFrames como parámetro; el
servicio no mantiene estado entre llamadas.
"""

import logging
import traceback

import pandas as pd
from PySide6.QtCore import QThread, Signal

from core.join.data_join_manager import DataJoinManager
from core.join.models import JoinConfig, JoinResult, JoinType, ValidationResult

logger = logging.getLogger(__name__)


class JoinService:
    """Servicio de orquestación para joins entre datasets.

    Proporciona validación, ejecución, preview y estimación de tiempo
    sin mantener estado interno. Cada operación crea un DataJoinManager
    temporal con los DataFrames recibidos.
    """

    def validate_config(
        self,
        left_df: pd.DataFrame,
        right_df: pd.DataFrame,
        config: JoinConfig,
    ) -> ValidationResult:
        """Validar configuración de join contra los datasets.

        Args:
            left_df: DataFrame izquierdo
            right_df: DataFrame derecho
            config: Configuración a validar

        Returns:
            ValidationResult con errores, advertencias y sugerencias
        """
        manager = DataJoinManager(left_df, right_df)
        return manager.validate_join(config)

    def execute_join(
        self,
        left_df: pd.DataFrame,
        right_df: pd.DataFrame,
        config: JoinConfig,
    ) -> JoinResult:
        """Ejecutar operación de join y devolver resultado con metadatos.

        Args:
            left_df: DataFrame izquierdo
            right_df: DataFrame derecho
            config: Configuración del join

        Returns:
            JoinResult con DataFrame resultante, metadatos y estado
        """
        manager = DataJoinManager(left_df, right_df)
        return manager.execute_join(config)

    def get_preview(
        self,
        left_df: pd.DataFrame,
        right_df: pd.DataFrame,
        config: JoinConfig,
        max_rows: int = 10,
    ) -> pd.DataFrame:
        """Obtener preview del resultado del join.

        Args:
            left_df: DataFrame izquierdo
            right_df: DataFrame derecho
            config: Configuración del join
            max_rows: Número máximo de filas en el preview

        Returns:
            DataFrame con hasta max_rows filas del resultado
        """
        manager = DataJoinManager(left_df, right_df)
        return manager.get_join_preview(config, max_rows)

    def estimate_operation_time(
        self,
        left_df: pd.DataFrame,
        right_df: pd.DataFrame,
        config: JoinConfig,
    ) -> float:
        """Estimar tiempo de ejecución de la operación en segundos.

        Usa heurísticas basadas en el tamaño de los datasets y el tipo
        de join para predecir si la operación será lenta.

        Args:
            left_df: DataFrame izquierdo
            right_df: DataFrame derecho
            config: Configuración del join

        Returns:
            Tiempo estimado en segundos
        """
        left_rows = len(left_df)
        right_rows = len(right_df)

        if config.join_type == JoinType.CROSS:
            base_time = (left_rows * right_rows) / 1_000_000
        elif config.join_type == JoinType.INNER:
            base_time = min(left_rows, right_rows) / 50_000
        else:
            base_time = left_rows / 30_000

        if config.validate_integrity:
            base_time *= 1.2

        if config.sort_results:
            base_time *= 1.1

        return max(0.5, min(base_time, 30.0))


class JoinWorkerThread(QThread):
    """Hilo para ejecutar un join sin bloquear la interfaz.

    Señales:
        progress_updated(int): Porcentaje de progreso (0-100).
        finished(object): JoinResult cuando la operación completa.
        error_occurred(str): Mensaje de error si falla.
    """

    progress_updated = Signal(int)
    finished = Signal(object)
    error_occurred = Signal(str)

    def __init__(
        self,
        join_service: JoinService,
        left_df: pd.DataFrame,
        right_df: pd.DataFrame,
        config: JoinConfig,
    ) -> None:
        super().__init__()
        self._join_service = join_service
        self._left_df = left_df
        self._right_df = right_df
        self._config = config

    def run(self) -> None:
        try:
            if self.isInterruptionRequested():
                return

            self.progress_updated.emit(10)

            if self.isInterruptionRequested():
                return

            self.progress_updated.emit(30)
            result = self._join_service.execute_join(
                self._left_df, self._right_df, self._config
            )

            if self.isInterruptionRequested():
                return

            self.progress_updated.emit(100)
            self.finished.emit(result)

        except Exception as e:
            logger.error("JoinWorkerThread error: %s\n%s", e, traceback.format_exc())
            if not self.isInterruptionRequested():
                self.error_occurred.emit(str(e))


def compute_result_columns(
    left_columns: list[str],
    right_columns: list[str],
    left_keys: list[str],
    right_keys: list[str],
    suffixes: tuple[str, str] = ('_left', '_right'),
) -> list[str]:
    """Calcular los nombres de columna resultantes sin ejecutar el merge.

    Replica la lógica de nombres de columna de ``pd.merge`` para
    jointypes con claves (inner, left, right, outer).

    Args:
        left_columns: Columnas del DataFrame izquierdo.
        right_columns: Columnas del DataFrame derecho.
        left_keys: Columnas clave del lado izquierdo.
        right_keys: Columnas clave del lado derecho.
        suffixes: Tupla de sufijos ``(left_suffix, right_suffix)``.

    Returns:
        Lista de nombres de columna del resultado.
    """
    left_suffix, right_suffix = suffixes

    left_key_set = set(left_keys)
    right_key_set = set(right_keys)
    paired_keys = list(zip(left_keys, right_keys))

    right_non_key = [c for c in right_columns if c not in right_key_set]

    conflicting = {
        c for c in left_columns
        if c not in left_key_set and c in right_non_key
    }

    result_cols: list[str] = []

    for col in left_columns:
        if col in conflicting:
            result_cols.append(f"{col}{left_suffix}")
        else:
            result_cols.append(col)

    for col in right_columns:
        if col in right_key_set:
            paired_left = next(
                (lk for lk, rk in paired_keys if rk == col), None
            )
            if paired_left and paired_left in left_key_set and col == paired_left:
                continue
            elif paired_left and paired_left in left_key_set:
                result_cols.append(col)
            else:
                result_cols.append(col)
        else:
            if col in conflicting:
                result_cols.append(f"{col}{right_suffix}")
            else:
                result_cols.append(col)

    return result_cols
