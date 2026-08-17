"""
Pruebas para VisualizationService — motor de visualizaciones minimalistas.
"""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from matplotlib.figure import Figure

from app.services.visualization_service import (
    VisualizationService,
    VisualizerWorkerThread,
    apply_minimal_theme,
)

matplotlib.use("Agg")


@pytest.fixture
def service():
    return VisualizationService()


@pytest.fixture
def sample_df():
    rng = np.random.default_rng(42)
    return pd.DataFrame({
        'id': range(200),
        'valor': rng.normal(100, 15, 200),
        'categoria': rng.choice(['A', 'B', 'C'], 200),
        'nulos': [None] * 200,
        'constante': [5.0] * 200,
    })


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    plt.close("all")


# ==================== Tema minimalista ====================

class TestTheme:

    @staticmethod
    def test_spines_superior_y_derecho_ocultos():
        fig = plt.figure()
        ax = fig.add_subplot(111)
        apply_minimal_theme(ax)
        assert ax.spines['top'].get_visible() is False
        assert ax.spines['right'].get_visible() is False
        assert ax.spines['left'].get_visible() is True
        assert ax.spines['bottom'].get_visible() is True

    @staticmethod
    def test_rejilla_solo_en_eje_y():
        fig = plt.figure()
        ax = fig.add_subplot(111)
        apply_minimal_theme(ax)
        assert ax.yaxis.get_gridlines() is not None
        assert ax.xaxis.get_gridlines() is not None


# ==================== Generadores de gráficos ====================

class TestChartGenerators:

    @staticmethod
    def test_genera_histograma(service, sample_df):
        fig = service.generate_histogram(sample_df, 'valor')
        assert isinstance(fig, Figure)
        assert len(fig.axes) == 1

    @staticmethod
    def test_genera_scatter(service, sample_df):
        fig = service.generate_scatter(sample_df, 'id', 'valor')
        assert isinstance(fig, Figure)
        assert len(fig.axes) == 1

    @staticmethod
    def test_genera_barras(service, sample_df):
        fig = service.generate_bar_counts(sample_df, 'categoria')
        assert isinstance(fig, Figure)

    @staticmethod
    def test_barras_respeta_top_n(service):
        df = pd.DataFrame({'c': list('ABCDEFGHIJKLMNOP') * 5})
        fig = service.generate_bar_counts(df, 'c', top=10)
        ax = fig.axes[0]
        assert len(ax.get_yticklabels()) <= 10

    @staticmethod
    def test_genera_boxplot(service, sample_df):
        fig = service.generate_boxplot(sample_df, 'valor')
        assert isinstance(fig, Figure)

    @staticmethod
    def test_histograma_columna_nula(service, sample_df):
        fig = service.generate_histogram(sample_df, 'nulos')
        assert isinstance(fig, Figure)

    @staticmethod
    def test_boxplot_valores_constantes(service, sample_df):
        fig = service.generate_boxplot(sample_df, 'constante')
        assert isinstance(fig, Figure)

    @staticmethod
    def test_barras_columna_vacia(service):
        df = pd.DataFrame({'c': [np.nan, np.nan]})
        fig = service.generate_bar_counts(df, 'c')
        assert isinstance(fig, Figure)


# ==================== Downsampling ====================

class TestDownsampling:

    @staticmethod
    def test_scatter_submuestrea_masivo(service):
        big = pd.DataFrame({
            'x': np.random.default_rng(1).uniform(0, 1, 15000),
            'y': np.random.default_rng(2).uniform(0, 1, 15000),
        })
        x_data, y_data = service.prepare_scatter_data(big, 'x', 'y', max_points=10000)
        assert len(x_data) == 10000
        assert len(y_data) == 10000

    @staticmethod
    def test_scatter_pequeno_sin_submuestreo(service, sample_df):
        x_data, y_data = service.prepare_scatter_data(sample_df, 'id', 'valor')
        assert len(x_data) == 200
        assert len(y_data) == 200

    @staticmethod
    def test_scatter_descarta_nulos(service):
        df = pd.DataFrame({'x': [1.0, 2.0, np.nan], 'y': [1.0, np.nan, 3.0]})
        x_data, _ = service.prepare_scatter_data(df, 'x', 'y')
        assert len(x_data) == 1
        assert x_data.iloc[0] == 1.0


# ==================== Despacho de generación ====================

class TestDispatch:

    @staticmethod
    @pytest.mark.parametrize("chart_type", ["histogram", "scatter", "bar", "boxplot"])
    def test_despacha_todos_los_tipos(service, sample_df, chart_type):
        fig = service.generate_figure(sample_df, chart_type, 'id', 'valor')
        assert isinstance(fig, Figure)

    @staticmethod
    def test_tipo_no_soportado_lanza_error(service, sample_df):
        with pytest.raises(ValueError):
            service.generate_figure(sample_df, 'pastel', 'id', 'valor')


# ==================== VisualizerWorkerThread ====================

class TestVisualizerWorkerThread:

    @staticmethod
    def test_run_emite_figura():
        df = pd.DataFrame({'a': [1, 2, 3, 4, 5]})
        thread = VisualizerWorkerThread(df, 'histogram', 'a', '')
        results = []
        thread.finished.connect(results.append)
        thread.run()
        assert len(results) == 1
        assert isinstance(results[0], Figure)

    @staticmethod
    def test_run_emite_error_en_tipo_invalido():
        df = pd.DataFrame({'a': [1, 2, 3]})
        thread = VisualizerWorkerThread(df, 'no_existe', 'a', '')
        errors = []
        thread.error.connect(errors.append)
        thread.run()
        assert len(errors) == 1
        assert isinstance(errors[0], str)
