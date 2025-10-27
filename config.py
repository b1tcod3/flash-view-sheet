"""
Configuración de optimización para Flash View Sheet
"""

import os

# Configuración de límites de memoria y rendimiento
class OptimizationConfig:
    """Configuración para optimización de rendimiento"""

    # Límites para activar optimizaciones
    VIRTUALIZATION_THRESHOLD = 5000  # Número de filas para activar paginación virtual
    CHUNK_LOADING_THRESHOLD = 100 * 1024 * 1024  # 100MB para activar carga por chunks

    # Configuración de paginación virtual
    DEFAULT_CHUNK_SIZE = 1000  # Filas por chunk en el modelo virtual
    MAX_CACHE_CHUNKS = 10  # Número máximo de chunks en cache

    # Configuración de carga de archivos
    CSV_CHUNK_SIZE_SMALL = 50000   # Chunk size para archivos pequeños
    CSV_CHUNK_SIZE_MEDIUM = 25000  # Chunk size para archivos medianos
    CSV_CHUNK_SIZE_LARGE = 10000   # Chunk size para archivos grandes

    # Configuración de estadísticas
    STATS_SAMPLE_THRESHOLD = 100000  # Usar sample para datasets > 100k filas
    STATS_SAMPLE_SIZE = 50000        # Tamaño de muestra para estadísticas

    # Configuración de filtrado
    FILTER_OPTIMIZATION_THRESHOLD = 50000  # Usar optimización para datasets > 50k filas

    # Configuración de exportación
    PDF_MAX_ROWS = 10000  # Máximo de filas para exportación a PDF
    IMAGE_MAX_SIZE = 50 * 1024 * 1024  # 50MB máximo para exportación a imagen

    @classmethod
    def get_csv_chunk_size(cls, file_size_bytes: int) -> int:
        """
        Obtener el tamaño de chunk apropiado basado en el tamaño del archivo

        Args:
            file_size_bytes: Tamaño del archivo en bytes

        Returns:
            Tamaño de chunk en filas
        """
        if file_size_bytes > 500 * 1024 * 1024:  # > 500MB
            return cls.CSV_CHUNK_SIZE_LARGE
        elif file_size_bytes > 100 * 1024 * 1024:  # > 100MB
            return cls.CSV_CHUNK_SIZE_MEDIUM
        else:
            return cls.CSV_CHUNK_SIZE_SMALL

    @classmethod
    def should_use_virtualization(cls, row_count: int) -> bool:
        """
        Determinar si se debe usar paginación virtual

        Args:
            row_count: Número de filas en el dataset

        Returns:
            True si se debe usar virtualización
        """
        return row_count > cls.VIRTUALIZATION_THRESHOLD

    @classmethod
    def should_optimize_filtering(cls, row_count: int) -> bool:
        """
        Determinar si se debe optimizar el filtrado

        Args:
            row_count: Número de filas en el dataset

        Returns:
            True si se debe optimizar el filtrado
        """
        return row_count > cls.FILTER_OPTIMIZATION_THRESHOLD

    @classmethod
    def should_sample_stats(cls, row_count: int) -> bool:
        """
        Determinar si se deben usar muestras para estadísticas

        Args:
            row_count: Número de filas en el dataset

        Returns:
            True si se deben usar muestras
        """
        return row_count > cls.STATS_SAMPLE_THRESHOLD


# Variables de entorno para configuración
def get_config_from_env():
    """Obtener configuración desde variables de entorno"""
    config = OptimizationConfig()

    # Permitir configuración desde variables de entorno
    if 'FLASH_CHUNK_SIZE' in os.environ:
        config.DEFAULT_CHUNK_SIZE = int(os.environ['FLASH_CHUNK_SIZE'])

    if 'FLASH_CACHE_CHUNKS' in os.environ:
        config.MAX_CACHE_CHUNKS = int(os.environ['FLASH_CACHE_CHUNKS'])

    if 'FLASH_VIRT_THRESHOLD' in os.environ:
        config.VIRTUALIZATION_THRESHOLD = int(os.environ['FLASH_VIRT_THRESHOLD'])

    return config


# Configuración global
optimization_config = get_config_from_env()