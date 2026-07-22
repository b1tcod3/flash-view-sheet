"""
CleaningService - Servicio de limpieza de datos sin dependencias de UI.

Orquesta las funciones puras de core/data_cleaner.py y devuelve
resultados estructurados que el AppCoordinator traduce a UI.
"""

from typing import Any
import pandas as pd

from core.data_cleaner import (
    limpiar_nulos,
    eliminar_duplicados,
    limpiar_espacios_texto,
    limpieza_rapida,
    resumen_limpieza,
)


class CleaningService:
    """Servicio puro de limpieza. Sin imports de PySide6."""

    def ejecutar_limpieza_rapida(self, df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
        """
        Aplica limpieza estándar (nulos→eliminar, duplicados, espacios)
        y retorna (DataFrame limpio, resumen).

        Raises ValueError si df es None o está vacío.
        """
        if df is None or df.empty:
            raise ValueError("No hay datos para limpiar")

        original = df.copy()
        limpio = limpieza_rapida(original)
        resumen = resumen_limpieza(original, limpio)
        return limpio, resumen

    def ejecutar_limpieza_personalizada(
        self,
        df: pd.DataFrame,
        opciones: dict[str, Any],
    ) -> tuple[pd.DataFrame, dict[str, Any]]:
        """
        Limpieza configurable.

        opciones:
        - 'nulos': 'eliminar'/'cero'/'promedio' (None = sin cambios)
        - 'duplicados': True/False
        - 'espacios': True/False
        """
        if df is None or df.empty:
            raise ValueError("No hay datos para limpiar")

        original = df.copy()
        result = original.copy()

        nulos = opciones.get('nulos')
        if nulos:
            result = limpiar_nulos(result, estrategia=nulos)

        if opciones.get('duplicados', False):
            result = eliminar_duplicados(result)

        if opciones.get('espacios', False):
            result = limpiar_espacios_texto(result)

        resumen = resumen_limpieza(original, result)
        return result, resumen
