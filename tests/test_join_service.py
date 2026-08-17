"""
Pruebas para JoinService — servicio de orquestación de joins
"""

import pytest
import pandas as pd
from core.join.models import JoinConfig, JoinType
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

    @staticmethod
    def test_valid_inner_join(service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id']
        )
        result = service.validate_config(left_df, right_df, config)
        assert result.is_valid is True
        assert len(result.errors) == 0

    @staticmethod
    def test_valid_left_join(service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.LEFT,
            left_keys=['id'],
            right_keys=['id']
        )
        result = service.validate_config(left_df, right_df, config)
        assert result.is_valid is True

    @staticmethod
    def test_missing_left_keys(service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=[],
            right_keys=['id']
        )
        result = service.validate_config(left_df, right_df, config)
        assert result.is_valid is False
        assert any('izquierdo' in e for e in result.errors)

    @staticmethod
    def test_missing_right_keys(service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=[]
        )
        result = service.validate_config(left_df, right_df, config)
        assert result.is_valid is False
        assert any('derecho' in e for e in result.errors)

    @staticmethod
    def test_mismatched_key_counts(service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id', 'dept'],
            right_keys=['id']
        )
        result = service.validate_config(left_df, right_df, config)
        assert result.is_valid is False
        assert any('igual' in e for e in result.errors)

    @staticmethod
    def test_missing_column_in_left(service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['no_existe'],
            right_keys=['id']
        )
        result = service.validate_config(left_df, right_df, config)
        assert result.is_valid is False
        assert any('no encontrada' in e.lower() or 'izquierdo' in e for e in result.errors)

    @staticmethod
    def test_missing_column_in_right(service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['no_existe']
        )
        result = service.validate_config(left_df, right_df, config)
        assert result.is_valid is False

    @staticmethod
    def test_cross_join_no_keys_needed(service, left_df, right_df):
        config = JoinConfig(join_type=JoinType.CROSS)
        result = service.validate_config(left_df, right_df, config)
        assert result.is_valid is True

    @staticmethod
    def test_cross_join_keys_produces_warning(service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.CROSS,
            left_keys=['id'],
            right_keys=['id']
        )
        result = service.validate_config(left_df, right_df, config)
        assert result.is_valid is True
        assert len(result.warnings) > 0

    @staticmethod
    def test_type_mismatch_warning(service, left_df, right_df):
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

    @staticmethod
    def test_inner_join(service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id']
        )
        result = service.execute_join(left_df, right_df, config)
        assert result.success is True
        assert len(result.data) == 2
        assert set(result.data.columns) >= {'id', 'nombre', 'salario'}

    @staticmethod
    def test_left_join(service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.LEFT,
            left_keys=['id'],
            right_keys=['id']
        )
        result = service.execute_join(left_df, right_df, config)
        assert result.success is True
        assert len(result.data) == 4
        assert result.metadata.left_rows == 4

    @staticmethod
    def test_outer_join(service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.OUTER,
            left_keys=['id'],
            right_keys=['id']
        )
        result = service.execute_join(left_df, right_df, config)
        assert result.success is True
        assert len(result.data) == 5

    @staticmethod
    def test_cross_join(service, left_df, right_df):
        config = JoinConfig(join_type=JoinType.CROSS)
        result = service.execute_join(left_df, right_df, config)
        assert result.success is True
        assert len(result.data) == len(left_df) * len(right_df)

    @staticmethod
    def test_invalid_config_returns_failed_result(service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=[],
            right_keys=[]
        )
        result = service.execute_join(left_df, right_df, config)
        assert result.success is False
        assert result.error_message
        assert result.data.empty

    @staticmethod
    def test_metadata_has_join_keys(service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.LEFT,
            left_keys=['id'],
            right_keys=['id']
        )
        result = service.execute_join(left_df, right_df, config)
        assert 'id' in result.metadata.join_keys

    @staticmethod
    def test_metadata_has_processing_time(service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id']
        )
        result = service.execute_join(left_df, right_df, config)
        assert result.metadata.processing_time_seconds >= 0

    @staticmethod
    def test_result_stores_config(service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id']
        )
        result = service.execute_join(left_df, right_df, config)
        assert result.config is config

    @staticmethod
    def test_indicator_true_keeps_merge_column(service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id'],
            indicator=True
        )
        result = service.execute_join(left_df, right_df, config)
        assert '_merge' in result.data.columns

    @staticmethod
    def test_include_columns_filters_result(service, left_df, right_df):
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

    @staticmethod
    def test_preview_returns_dataframe(service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.LEFT,
            left_keys=['id'],
            right_keys=['id']
        )
        preview = service.get_preview(left_df, right_df, config)
        assert isinstance(preview, pd.DataFrame)

    @staticmethod
    def test_preview_respects_max_rows(service, left_df, right_df):
        config = JoinConfig(join_type=JoinType.CROSS)
        preview = service.get_preview(left_df, right_df, config, max_rows=5)
        assert len(preview) <= 5

    @staticmethod
    def test_preview_cross_join(service, left_df, right_df):
        config = JoinConfig(join_type=JoinType.CROSS)
        preview = service.get_preview(left_df, right_df, config, max_rows=10)
        assert isinstance(preview, pd.DataFrame)

    @staticmethod
    def test_preview_inner_join(service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id']
        )
        preview = service.get_preview(left_df, right_df, config, max_rows=100)
        assert len(preview) == 2


# ==================== estimate_operation_time ====================

class TestEstimateOperationTime:

    @staticmethod
    def test_inner_join_fast(service, left_df, right_df):
        config = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id']
        )
        time_est = service.estimate_operation_time(left_df, right_df, config)
        assert 0.0 <= time_est <= 30.0

    @staticmethod
    def test_cross_join_slower(service, left_df, right_df):
        config_cross = JoinConfig(join_type=JoinType.CROSS)
        config_inner = JoinConfig(
            join_type=JoinType.INNER,
            left_keys=['id'],
            right_keys=['id']
        )
        time_cross = service.estimate_operation_time(left_df, right_df, config_cross)
        time_inner = service.estimate_operation_time(left_df, right_df, config_inner)
        assert time_cross >= time_inner

    @staticmethod
    def test_validation_adds_time(service, left_df, right_df):
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

    @staticmethod
    def test_minimum_time_floor(service):
        tiny_left = pd.DataFrame({'a': [1]})
        tiny_right = pd.DataFrame({'b': [1]})
        config = JoinConfig(join_type=JoinType.INNER, left_keys=['a'], right_keys=['b'])
        time_est = service.estimate_operation_time(tiny_left, tiny_right, config)
        assert time_est >= 0.5

    @staticmethod
    def test_large_dataset_estimation(service):
        big_left = pd.DataFrame({'id': range(100_000)})
        big_right = pd.DataFrame({'id': range(100_000)})
        config = JoinConfig(join_type=JoinType.INNER, left_keys=['id'], right_keys=['id'])
        time_est = service.estimate_operation_time(big_left, big_right, config)
        assert time_est > 1.0


# ==================== stateless verification ====================

class TestStateless:

    @staticmethod
    def test_multiple_calls_independent(service, left_df, right_df):
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

    @staticmethod
    def test_inner_join_no_overlap():
        cols = compute_result_columns(
            ['id', 'name'], ['dept', 'salary'],
            ['id'], ['dept'],
        )
        assert cols == ['id', 'name', 'dept', 'salary']

    @staticmethod
    def test_inner_join_same_key_name():
        cols = compute_result_columns(
            ['id', 'name'], ['id', 'salary'],
            ['id'], ['id'],
        )
        assert cols == ['id', 'name', 'salary']

    @staticmethod
    def test_overlapping_non_key_columns():
        cols = compute_result_columns(
            ['id', 'city'], ['id', 'city'],
            ['id'], ['id'],
        )
        assert 'city_left' in cols
        assert 'city_right' in cols

    @staticmethod
    def test_custom_suffixes():
        cols = compute_result_columns(
            ['id', 'city'], ['id', 'city'],
            ['id'], ['id'],
            suffixes=('_l', '_r'),
        )
        assert 'city_l' in cols
        assert 'city_r' in cols

    @staticmethod
    def test_multiple_keys():
        cols = compute_result_columns(
            ['a', 'b', 'val'], ['a', 'b', 'info'],
            ['a', 'b'], ['a', 'b'],
        )
        assert cols == ['a', 'b', 'val', 'info']

    @staticmethod
    def test_cross_join_fallback():
        left = ['a', 'b']
        right = ['c', 'd']
        cols = compute_result_columns(left, right, [], [])
        assert cols == ['a', 'b', 'c', 'd']

    @staticmethod
    def test_matches_real_merge():
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
