"""
Pruebas para ProfilerService — motor de perfilado de datos.
"""

import pytest
import pandas as pd
import numpy as np

from app.services.profiler_service import (
    ProfilerService,
    ProfilerWorkerThread,
    _safe_percent,
    _to_native,
)


@pytest.fixture
def service():
    return ProfilerService()


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'nombre': ['Ana', 'Bob', 'Carlos', 'Ana', None],
        'dept': ['IT', 'Ventas', 'IT', 'RRHH', 'IT'],
        'salario': [50000.0, 60000.0, 70000.0, 80000.0, 90000.0],
        'fecha': pd.to_datetime(['2024-01-01', '2024-02-01', '2024-03-01',
                                 '2024-04-01', '2024-05-01']),
        'nulos_total': [None, None, None, None, None],
    })


# ==================== Métricas generales ====================

class TestGeneralMetrics:

    def test_estructura_del_perfil(self, service, sample_df):
        profile = service.generate_profile(sample_df)
        assert profile['total_rows'] == 5
        assert profile['total_columns'] == 6
        assert 'columns' in profile
        assert set(profile['columns'].keys()) == set(sample_df.columns)

    def test_memoria_y_duplicados(self, service, sample_df):
        profile = service.generate_profile(sample_df)
        assert profile['memory_usage_mb'] > 0
        assert profile['duplicated_rows'] == 0

    def test_df_vacio(self, service):
        profile = service.generate_profile(pd.DataFrame())
        assert profile['total_rows'] == 0
        assert profile['columns'] == {}

    def test_df_con_duplicados(self, service):
        df = pd.DataFrame({'a': [1, 1, 2], 'b': ['x', 'x', 'y']})
        profile = service.generate_profile(df)
        assert profile['duplicated_rows'] == 2


# ==================== Progreso ====================

class TestProgress:

    def test_progress_monotono_hasta_100(self, service, sample_df):
        steps: list[int] = []
        profile = service.generate_profile(sample_df, progress_callback=steps.append)
        assert steps == sorted(steps)
        assert steps[-1] == 100
        assert steps[0] == 5

    def test_progress_df_vacio_100(self, service):
        steps: list[int] = []
        service.generate_profile(pd.DataFrame(), progress_callback=steps.append)
        assert steps == [100]


# ==================== Tolerancia a fallos ====================

class TestFaultTolerance:

    def test_error_por_columna_no_aborta(self, service, sample_df, monkeypatch):
        original = service._profile_column

        def broken(df, col, total_rows):
            if str(col) == 'nombre':
                raise ValueError("boom")
            return original(df, col, total_rows)

        monkeypatch.setattr(service, '_profile_column', broken)
        profile = service.generate_profile(sample_df)
        nombre = profile['columns']['nombre']
        assert nombre['error'] is True
        assert 'boom' in nombre['error_msg']
        assert profile['columns']['id'].get('error') is not True
        assert profile['columns']['id']['null_count'] == 0


# ==================== Resumen de calidad ====================

class TestQualitySummary:

    def test_resumen_de_calidad_presente(self, service, sample_df):
        profile = service.generate_profile(sample_df)
        quality = profile['data_quality_summary']
        assert 'null_percent' in quality
        assert 'duplicate_percent' in quality
        assert 'high_cardinality_columns' in quality
        assert 'high_null_columns' in quality
        assert 'overall_quality_score' in quality

    def test_resumen_de_calidad_coherente(self, service, sample_df):
        profile = service.generate_profile(sample_df)
        quality = profile['data_quality_summary']
        assert quality['null_percent'] == pytest.approx(6 / 30 * 100, abs=0.01)
        assert quality['duplicate_percent'] == 0.0
        assert quality['high_null_columns'] == 1
        assert 0.0 <= quality['overall_quality_score'] <= 100.0

    def test_resumen_de_calidad_sin_datos(self, service):
        profile = service.generate_profile(pd.DataFrame())
        assert profile['data_quality_summary'] == {}


# ==================== Métricas por columna ====================

class TestColumnMetrics:

    def test_columna_numerica(self, service, sample_df):
        col = service._profile_column(sample_df, 'salario', 5)
        assert col['dtype'] == 'float'
        assert col['null_count'] == 0
        assert col['null_percent'] == 0.0
        assert col['unique_count'] == 5
        assert col['unique_percent'] == 100.0
        assert col['numeric_stats'] is not None
        stats = col['numeric_stats']
        assert stats['min'] == 50000.0
        assert stats['max'] == 90000.0
        assert stats['mean'] == 70000.0
        assert stats['median'] == 70000.0

    def test_dtype_detallado(self, service, sample_df):
        assert service._profile_column(sample_df, 'id', 5)['dtype'] == 'integer'
        assert service._profile_column(sample_df, 'salario', 5)['dtype'] == 'float'
        assert service._profile_column(sample_df, 'nombre', 5)['dtype'] == 'string'
        assert service._profile_column(sample_df, 'fecha', 5)['dtype'] == 'datetime'

    def test_columna_categorica(self, service, sample_df):
        col = service._profile_column(sample_df, 'nombre', 5)
        assert col['numeric_stats'] is None
        assert col['null_count'] == 1
        assert col['null_percent'] == 20.0
        assert col['unique_count'] == 3
        assert col['top_values'] is not None
        top = dict(col['top_values'])
        assert top['Ana'] == 2

    def test_columna_100_porciento_nula(self, service, sample_df):
        col = service._profile_column(sample_df, 'nulos_total', 5)
        assert col['null_count'] == 5
        assert col['null_percent'] == 100.0
        assert col['unique_count'] == 0
        assert col['numeric_stats'] is None
        assert col['top_values'] == []

    def test_columna_fecha(self, service, sample_df):
        col = service._profile_column(sample_df, 'fecha', 5)
        assert col['date_range'] is not None
        assert col['date_range']['days_span'] == 121

    def test_cardinalidad_alta_numerica_con_distribucion(self, service):
        df = pd.DataFrame({'id': range(0, 2000)})
        col = service._profile_column(df, 'id', 2000)
        assert col['unique_count'] == 2000
        assert col['top_values'] is None
        assert col['value_distribution'] is not None
        assert len(col['value_distribution']) > 0
        for value, count in col['value_distribution']:
            assert isinstance(value, str)
            assert isinstance(count, int)

    def test_cardinalidad_alta_datetime_con_distribucion(self, service):
        df = pd.DataFrame({'fecha': pd.date_range('2020-01-01', periods=2000, freq='D')})
        col = service._profile_column(df, 'fecha', 2000)
        assert col['value_distribution'] is not None
        assert len(col['value_distribution']) > 0
        assert len(col['value_distribution']) <= 5

    def test_columna_todo_nan_numerica(self, service):
        df = pd.DataFrame({'a': [np.nan, np.nan]})
        col = service._profile_column(df, 'a', 2)
        assert col['numeric_stats'] is None


# ==================== Helpers ====================

class TestHelpers:

    def test_safe_percent(self):
        assert _safe_percent(5, 10) == 50.0
        assert _safe_percent(0, 0) == 0.0
        assert _safe_percent(1, 3) == 33.33

    def test_to_native_numpy_scalars(self):
        assert _to_native(np.int64(5)) == 5
        assert _to_native(np.float64(5.5)) == 5.5
        assert _to_native('texto') == 'texto'
        assert _to_native(pd.Timestamp('2024-01-01')) == '2024-01-01T00:00:00'

    def test_to_native_convierte_nulos(self):
        assert _to_native(None) is None
        assert _to_native(np.nan) is None
        assert _to_native(pd.NaT) is None
        assert _to_native(np.float64(np.nan)) is None

    def test_valores_nativos_en_perfil(self, service, sample_df):
        profile = service.generate_profile(sample_df)
        salario = profile['columns']['salario']['numeric_stats']
        assert isinstance(salario['min'], float)
        assert isinstance(sample_df['salario'].iloc[0], float)


# ==================== ProfilerWorkerThread ====================

class TestProfilerWorkerThread:

    def test_run_emite_perfil(self):
        df = pd.DataFrame({'a': [1, 2, 3], 'b': ['x', 'y', 'x']})
        thread = ProfilerWorkerThread(df)
        results = []
        thread.finished.connect(results.append)
        thread.run()
        assert len(results) == 1
        assert results[0]['total_rows'] == 3

    def test_run_emite_error_en_df_invalido(self):
        thread = ProfilerWorkerThread("no-es-un-dataframe")  # type: ignore[arg-type]
        errors = []
        thread.error.connect(errors.append)
        thread.run()
        assert len(errors) == 1
        assert isinstance(errors[0], str)
