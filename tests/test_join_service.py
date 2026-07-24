"""
Pruebas para JoinService — servicio de orquestación de joins
"""

import pytest
import pandas as pd
import numpy as np
from core.join.models import JoinConfig, JoinType
from core.join.exceptions import JoinValidationError, UnsupportedJoinError
from app.services.join_service import JoinService, compute_result_columns


@pytest.fixture
def service():
    return JoinService()


@pytest.fixture
def left_df():
    return pd.DataFrame({
        'id': [1, 2, 3, 4],
        'nombre': ['Ana', 'Bob', 'Carlos', 'Diana'],
        'dept': ['IT', 'Ventas', 'IT', 'RRHH']
    })


@pytest.fixture
def right_df():
    return pd.DataFrame({
        'id': [1, 3, 5],
        'salario': [50000, 60000, 70000],
        'ciudad': ['Madrid', 'Barcelona', 'Valencia']
    })


# ==================== validate_config ====================

class TestValidateConfig:

    def test_valid_inner_join(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id']
        )
        result = service.validate_config(left_df, right_df, config)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_valid_left_join(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.LEFT,
            left_keys=['id'],
            right_keys=['id']
        )
        result = service.validate_config(left_df, right_df, config)
        assert result.is_valid is True

    def test_missing_left_keys(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=[],
            right_keys=['id']
        )
        result = service.validate_config(left_df, right_df, config)
        assert result.is_valid is False
        assert any('izquierdo' in e for e in result.errors)

    def test_missing_right_keys(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=[]
        )
        result = service.validate_config(left_df, right_df, config)
        assert result.is_valid is False
        assert any('derecho' in e for e in result.errors)

    def test_mismatched_key_counts(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id', 'dept'],
            right_keys=['id']
        )
        result = service.validate_config(left_df, right_df, config)
        assert result.is_valid is False
        assert any('igual' in e for e in result.errors)

    def test_missing_column_in_left(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['no_existe'],
            right_keys=['id']
        )
        result = service.validate_config(left_df, right_df, config)
        assert result.is_valid is False
        assert any('no encontrada' in e.lower() or 'izquierdo' in e for e in result.errors)

    def test_missing_column_in_right(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['no_existe']
        )
        result = service.validate_config(left_df, right_df, config)
        assert result.is_valid is False

    def test_cross_join_no_keys_needed(self, service, left_df, right_df):
        config = JoinConfig(join_type=JoinType.CROSS)
        result = service.validate_config(left_df, right_df, config)
        assert result.is_valid is True

    def test_cross_join_keys_produces_warning(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.CROSS,
            left_keys=['id'],
            right_keys=['id']
        )
        result = service.validate_config(left_df, right_df, config)
        assert result.is_valid is True
        assert len(result.warnings) > 0

    def test_type_mismatch_warning(self, service, left_df, right_df):
        right_df_str = right_df.copy()
        right_df_str['id'] = right_df_str['id'].astype(str)
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id'],
            validate_integrity=True
        )
        result = service.validate_config(left_df, right_df_str, config)
        assert any('diferentes' in w for w in result.warnings)


# ==================== execute_join ====================

class TestExecuteJoin:

    def test_inner_join(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id']
        )
        result = service.execute_join(left_df, right_df, config)
        assert result.success is True
        assert len(result.data) == 2
        assert set(result.data.columns) >= {'id', 'nombre', 'salario'}

    def test_left_join(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.LEFT,
            left_keys=['id'],
            right_keys=['id']
        )
        result = service.execute_join(left_df, right_df, config)
        assert result.success is True
        assert len(result.data) == 4
        assert result.metadata.left_rows == 4

    def test_outer_join(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.OUTER,
            left_keys=['id'],
            right_keys=['id']
        )
        result = service.execute_join(left_df, right_df, config)
        assert result.success is True
        assert len(result.data) == 5

    def test_cross_join(self, service, left_df, right_df):
        config = JoinConfig(join_type=JoinType.CROSS)
        result = service.execute_join(left_df, right_df, config)
        assert result.success is True
        assert len(result.data) == len(left_df) * len(right_df)

    def test_invalid_config_returns_failed_result(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=[],
            right_keys=[]
        )
        result = service.execute_join(left_df, right_df, config)
        assert result.success is False
        assert result.error_message
        assert result.data.empty

    def test_metadata_has_join_keys(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.LEFT,
            left_keys=['id'],
            right_keys=['id']
        )
        result = service.execute_join(left_df, right_df, config)
        assert 'id' in result.metadata.join_keys

    def test_metadata_has_processing_time(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id']
        )
        result = service.execute_join(left_df, right_df, config)
        assert result.metadata.processing_time_seconds >= 0

    def test_result_stores_config(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id']
        )
        result = service.execute_join(left_df, right_df, config)
        assert result.config is config

    def test_indicator_true_keeps_merge_column(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id'],
            indicator=True
        )
        result = service.execute_join(left_df, right_df, config)
        assert '_merge' in result.data.columns

    def test_include_columns_filters_result(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.LEFT,
            left_keys=['id'],
            right_keys=['id'],
            include_columns=['id', 'nombre']
        )
        result = service.execute_join(left_df, right_df, config)
        assert result.success is True
        assert list(result.data.columns) == ['id', 'nombre']


# ==================== get_preview ====================

class TestGetPreview:

    def test_preview_returns_dataframe(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.LEFT,
            left_keys=['id'],
            right_keys=['id']
        )
        preview = service.get_preview(left_df, right_df, config)
        assert isinstance(preview, pd.DataFrame)

    def test_preview_respects_max_rows(self, service, left_df, right_df):
        config = JoinConfig(join_type=JoinType.CROSS)
        preview = service.get_preview(left_df, right_df, config, max_rows=5)
        assert len(preview) <= 5

    def test_preview_cross_join(self, service, left_df, right_df):
        config = JoinConfig(join_type=JoinType.CROSS)
        preview = service.get_preview(left_df, right_df, config, max_rows=10)
        assert isinstance(preview, pd.DataFrame)

    def test_preview_inner_join(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id']
        )
        preview = service.get_preview(left_df, right_df, config, max_rows=100)
        assert len(preview) == 2


# ==================== estimate_operation_time ====================

class TestEstimateOperationTime:

    def test_inner_join_fast(self, service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id']
        )
        time_est = service.estimate_operation_time(left_df, right_df, config)
        assert 0.0 <= time_est <= 30.0

    def test_cross_join_slower(self, service, left_df, right_df):
        config_cross = JoinConfig(join_type=JoinType.CROSS)
        config_inner = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id']
        )
        time_cross = service.estimate_operation_time(left_df, right_df, config_cross)
        time_inner = service.estimate_operation_time(left_df, right_df, config_inner)
        assert time_cross >= time_inner

    def test_validation_adds_time(self, service, left_df, right_df):
        config_no_val = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id'],
            validate_integrity=False,
            sort_results=False
        )
        config_val = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id'],
            validate_integrity=True,
            sort_results=True
        )
        time_no_val = service.estimate_operation_time(left_df, right_df, config_no_val)
        time_val = service.estimate_operation_time(left_df, right_df, config_val)
        assert time_val >= time_no_val

    def test_minimum_time_floor(self, service):
        tiny_left = pd.DataFrame({'a': [1]})
        tiny_right = pd.DataFrame({'b': [1]})
        config = JoinConfig(join_type=JoinType.INNER, left_keys=['a'], right_keys=['b'])
        time_est = service.estimate_operation_time(tiny_left, tiny_right, config)
        assert time_est >= 0.5

    def test_large_dataset_estimation(self, service):
        big_left = pd.DataFrame({'id': range(100_000)})
        big_right = pd.DataFrame({'id': range(100_000)})
        config = JoinConfig(join_type=JoinType.INNER, left_keys=['id'], right_keys=['id'])
        time_est = service.estimate_operation_time(big_left, big_right, config)
        assert time_est > 1.0


# ==================== stateless verification ====================

class TestStateless:

    def test_multiple_calls_independent(self, service, left_df, right_df):
        config1 = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id']
        )
        config2 = JoinConfig(
            join_type=JoinType.LEFT,
            left_keys=['id'],
            right_keys=['id']
        )
        r1 = service.execute_join(left_df, right_df, config1)
        r2 = service.execute_join(left_df, right_df, config2)
        assert len(r1.data) == 2
        assert len(r2.data) == 4
        assert r1 is not r2


# ==================== compute_result_columns ====================

class TestComputeResultColumns:

    def test_inner_join_no_overlap(self):
        cols = compute_result_columns(
            ['id', 'name'], ['dept', 'salary'],
            ['id'], ['dept'],
        )
        assert cols == ['id', 'name', 'dept', 'salary']

    def test_inner_join_same_key_name(self):
        cols = compute_result_columns(
            ['id', 'name'], ['id', 'salary'],
            ['id'], ['id'],
        )
        assert cols == ['id', 'name', 'salary']

    def test_overlapping_non_key_columns(self):
        cols = compute_result_columns(
            ['id', 'city'], ['id', 'city'],
            ['id'], ['id'],
        )
        assert 'city_left' in cols
        assert 'city_right' in cols

    def test_custom_suffixes(self):
        cols = compute_result_columns(
            ['id', 'city'], ['id', 'city'],
            ['id'], ['id'],
            suffixes=('_l', '_r'),
        )
        assert 'city_l' in cols
        assert 'city_r' in cols

    def test_multiple_keys(self):
        cols = compute_result_columns(
            ['a', 'b', 'val'], ['a', 'b', 'info'],
            ['a', 'b'], ['a', 'b'],
        )
        assert cols == ['a', 'b', 'val', 'info']

    def test_cross_join_fallback(self):
        left = ['a', 'b']
        right = ['c', 'd']
        cols = compute_result_columns(left, right, [], [])
        assert cols == ['a', 'b', 'c', 'd']

    def test_matches_real_merge(self):
        left_df = pd.DataFrame({'id': [1], 'name': ['X'], 'city': ['M']})
        right_df = pd.DataFrame({'id': [1], 'salary': [50000], 'city': ['B']})
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id'],
        )
        result_cols = compute_result_columns(
            left_df.columns.tolist(),
            right_df.columns.tolist(),
            config.left_keys,
            config.right_keys,
            config.suffixes,
        )
        real = pd.merge(left_df, right_df, left_on=['id'], right_on=['id'],
                        how='inner', suffixes=('_left', '_right'))
        assert result_cols == real.columns.tolist()
