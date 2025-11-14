"""
Pruebas para funcionalidad de cruce de datos (join)
"""

import pytest
import pandas as pd
import numpy as np
from core.join.models import JoinConfig, JoinType
from core.join.data_join_manager import DataJoinManager
from core.join.exceptions import JoinValidationError, UnsupportedJoinError


class TestDataJoinManager:
    """Pruebas para DataJoinManager"""

    @pytest.fixture
    def sample_dataframes(self):
        """Crear DataFrames de prueba"""
        left_df = pd.DataFrame({
            'id': [1, 2, 3, 4],
            'name': ['Alice', 'Bob', 'Charlie', 'David'],
            'value': [100, 200, 300, 400]
        })

        right_df = pd.DataFrame({
            'id': [1, 2, 3, 5],
            'department': ['HR', 'IT', 'Sales', 'Marketing'],
            'salary': [50000, 60000, 55000, 65000]
        })

        return left_df, right_df

    def test_inner_join(self, sample_dataframes):
        """Probar join interno"""
        left_df, right_df = sample_dataframes

        config = JoinConfig(
            left_keys=['id'],
            right_keys=['id'],
            join_type=JoinType.INNER
        )

        manager = DataJoinManager(left_df, right_df)
        result = manager.execute_join(config)

        assert result.success
        assert len(result.data) == 3  # ids 1, 2, 3 coinciden
        assert 'name' in result.data.columns
        assert 'department' in result.data.columns

    def test_left_join(self, sample_dataframes):
        """Probar left join"""
        left_df, right_df = sample_dataframes

        config = JoinConfig(
            left_keys=['id'],
            right_keys=['id'],
            join_type=JoinType.LEFT
        )

        manager = DataJoinManager(left_df, right_df)
        result = manager.execute_join(config)

        assert result.success
        assert len(result.data) == 4  # todos los del izquierdo
        assert result.data['department'].isnull().sum() == 1  # id 4 no tiene match

    def test_cross_join(self, sample_dataframes):
        """Probar cross join"""
        left_df, right_df = sample_dataframes

        config = JoinConfig(
            join_type=JoinType.CROSS
        )

        manager = DataJoinManager(left_df, right_df)
        result = manager.execute_join(config)

        assert result.success
        assert len(result.data) == 16  # 4 * 4
        assert len(result.data.columns) == 6  # id, name, value, id, department, salary

    def test_validation_missing_columns(self, sample_dataframes):
        """Probar validación de columnas faltantes"""
        left_df, right_df = sample_dataframes

        config = JoinConfig(
            left_keys=['nonexistent'],
            right_keys=['id'],
            join_type=JoinType.INNER
        )

        manager = DataJoinManager(left_df, right_df)
        validation = manager.validate_join(config)

        assert not validation.is_valid
        assert "nonexistent" in str(validation.errors)

    def test_validation_different_key_counts(self, sample_dataframes):
        """Probar validación de número diferente de keys"""
        left_df, right_df = sample_dataframes

        config = JoinConfig(
            left_keys=['id', 'name'],
            right_keys=['id'],
            join_type=JoinType.INNER
        )

        manager = DataJoinManager(left_df, right_df)
        validation = manager.validate_join(config)

        assert not validation.is_valid
        assert "igual" in str(validation.errors).lower()

    def test_unsupported_join_type(self, sample_dataframes):
        """Probar tipo de join no soportado"""
        left_df, right_df = sample_dataframes

        # Crear config con tipo no soportado
        config = JoinConfig(
            left_keys=['id'],
            right_keys=['id'],
            join_type="unsupported"  # Esto debería fallar
        )

        manager = DataJoinManager(left_df, right_df)

        with pytest.raises(UnsupportedJoinError):
            manager.validate_join(config)

    def test_preview_functionality(self, sample_dataframes):
        """Probar funcionalidad de preview"""
        left_df, right_df = sample_dataframes

        config = JoinConfig(
            left_keys=['id'],
            right_keys=['id'],
            join_type=JoinType.INNER
        )

        manager = DataJoinManager(left_df, right_df)
        preview = manager.get_join_preview(config, max_rows=2)

        assert len(preview) <= 2
        assert not preview.empty

    def test_chunking_large_cross_join(self):
        """Probar chunking para cross joins grandes"""
        # Crear datasets más grandes para forzar chunking
        left_df = pd.DataFrame({
            'id': range(100),  # 100 filas
            'value': [f'left_{i}' for i in range(100)]
        })

        right_df = pd.DataFrame({
            'id': range(50),  # 50 filas
            'data': [f'right_{i}' for i in range(50)]
        })

        config = JoinConfig(join_type=JoinType.CROSS)

        manager = DataJoinManager(left_df, right_df)
        result = manager.execute_join(config)

        assert result.success
        assert len(result.data) == 5000  # 100 * 50
        assert len(result.data.columns) == 4  # id_left, value, id_right, data

    def test_chunking_detection(self):
        """Probar que el sistema detecta cuando usar chunking"""
        # Crear datasets que deberían activar chunking
        left_df = pd.DataFrame({
            'id': range(1000),
            'value': [f'val_{i}' for i in range(1000)]
        })

        right_df = pd.DataFrame({
            'id': range(1000),
            'data': [f'data_{i}' for i in range(1000)]
        })

        manager = DataJoinManager(left_df, right_df)

        # Cross join con 1M de combinaciones debería usar chunking
        config_cross = JoinConfig(join_type=JoinType.CROSS)
        should_chunk_cross = manager._should_use_chunking(
            config_cross,
            manager._estimate_memory_usage(config_cross),
            1000  # Memoria disponible alta para probar lógica
        )
        assert should_chunk_cross

        # Inner join normal no debería usar chunking con datasets pequeños
        config_inner = JoinConfig(
            left_keys=['id'],
            right_keys=['id'],
            join_type=JoinType.INNER
        )
        should_chunk_inner = manager._should_use_chunking(
            config_inner,
            manager._estimate_memory_usage(config_inner),
            100  # Memoria baja
        )
        assert not should_chunk_inner  # Datasets pequeños no activan chunking

    def test_column_suppression(self, sample_dataframes):
        """Probar supresión de columnas en resultados"""
        left_df, right_df = sample_dataframes

        # Configurar join sin supresión de columnas
        config_full = JoinConfig(
            left_keys=['id'],
            right_keys=['id'],
            join_type=JoinType.INNER
        )

        manager = DataJoinManager(left_df, right_df)
        result_full = manager.execute_join(config_full)

        # Verificar que todas las columnas están presentes
        expected_columns = {'id', 'name', 'value', 'department', 'salary'}
        assert set(result_full.data.columns) == expected_columns

        # Configurar join con supresión de columnas (solo algunas)
        config_filtered = JoinConfig(
            left_keys=['id'],
            right_keys=['id'],
            join_type=JoinType.INNER,
            include_columns=['name', 'department', 'salary']  # Solo estas columnas
        )

        result_filtered = manager.execute_join(config_filtered)

        # Verificar que solo las columnas especificadas están presentes
        assert set(result_filtered.data.columns) == {'name', 'department', 'salary'}
        assert len(result_filtered.data) == 3  # Mismos registros

    def test_column_suppression_empty_list(self, sample_dataframes):
        """Probar que lista vacía de columnas incluye todas"""
        left_df, right_df = sample_dataframes

        config = JoinConfig(
            left_keys=['id'],
            right_keys=['id'],
            join_type=JoinType.INNER,
            include_columns=[]  # Lista vacía = incluir todas
        )

        manager = DataJoinManager(left_df, right_df)
        result = manager.execute_join(config)

        # Debería incluir todas las columnas
        expected_columns = {'id', 'name', 'value', 'department', 'salary'}
        assert set(result.data.columns) == expected_columns

    def test_column_suppression_invalid_columns(self, sample_dataframes):
        """Probar manejo de columnas inexistentes en include_columns"""
        left_df, right_df = sample_dataframes

        config = JoinConfig(
            left_keys=['id'],
            right_keys=['id'],
            join_type=JoinType.INNER,
            include_columns=['name', 'nonexistent_column', 'department']
        )

        manager = DataJoinManager(left_df, right_df)
        result = manager.execute_join(config)

        # Debería incluir solo las columnas válidas
        assert set(result.data.columns) == {'name', 'department'}
        assert len(result.data) == 3


class TestJoinConfig:
    """Pruebas para JoinConfig"""

    def test_config_creation(self):
        """Probar creación de configuración"""
        config = JoinConfig(
            left_keys=['id'],
            right_keys=['customer_id'],
            join_type=JoinType.LEFT,
            suffixes=('_left', '_right'),
            validate_integrity=True,
            sort_results=True,
            indicator=True
        )

        assert config.left_keys == ['id']
        assert config.right_keys == ['customer_id']
        assert config.join_type == JoinType.LEFT
        assert config.suffixes == ('_left', '_right')
        assert config.validate_integrity is True
        assert config.sort_results is True
        assert config.indicator is True