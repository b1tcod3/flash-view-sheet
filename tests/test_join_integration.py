"""
Pruebas de integración para funcionalidad de cruce de datos (join)
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication

from core.join.models import JoinConfig, JoinType
from core.join.data_join_manager import DataJoinManager
from app.widgets.join.join_dialog import JoinDialog
from app.widgets.join.joined_data_view import JoinedDataView


@pytest.fixture(scope="session")
def qapp():
    """Fixture para QApplication"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestJoinIntegration:
    """Pruebas de integración end-to-end para joins"""

    @pytest.fixture
    def sample_dataframes(self):
        """Crear DataFrames de prueba más realistas"""
        # Dataset de ventas
        ventas_df = pd.DataFrame({
            'cliente_id': [1, 2, 3, 4, 5, 1, 2, 3],
            'producto': ['Laptop', 'Mouse', 'Teclado', 'Monitor', 'Impresora', 'Mouse', 'Teclado', 'Laptop'],
            'cantidad': [1, 2, 1, 1, 1, 1, 1, 1],
            'precio': [1000, 50, 100, 300, 200, 50, 100, 1000]
        })

        # Dataset de clientes
        clientes_df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5, 6],
            'nombre': ['Juan Pérez', 'María García', 'Carlos Ruiz', 'Ana López', 'Pedro Martínez', 'Laura Sánchez'],
            'ciudad': ['Madrid', 'Barcelona', 'Madrid', 'Valencia', 'Barcelona', 'Madrid'],
            'edad': [35, 28, 42, 31, 39, 26]
        })

        return ventas_df, clientes_df

    def test_full_join_workflow(self, sample_dataframes, qapp):
        """Probar flujo completo de join desde configuración hasta resultado"""
        ventas_df, clientes_df = sample_dataframes

        # Configurar join
        config = JoinConfig(
            left_keys=['cliente_id'],
            right_keys=['id'],
            join_type=JoinType.LEFT,
            suffixes=('_venta', '_cliente'),
            validate_integrity=True,
            sort_results=True,
            indicator=False
        )

        # Ejecutar join
        manager = DataJoinManager(ventas_df, clientes_df)
        result = manager.execute_join(config)

        # Verificar resultado
        assert result.success
        assert len(result.data) == 8  # Todas las ventas (left join)
        assert 'cliente_id' in result.data.columns
        assert 'producto' in result.data.columns
        assert 'nombre' in result.data.columns  # No hay conflicto de nombres, sufijos no aplican
        assert 'ciudad' in result.data.columns

        # Verificar metadatos
        assert result.metadata.result_rows == 8
        assert result.metadata.matched_rows == 8  # Todas las ventas tienen cliente
        assert result.metadata.left_only_rows == 0
        assert result.metadata.right_only_rows == 1  # Cliente 6 sin ventas

    def test_join_dialog_integration(self, sample_dataframes, qapp):
        """Probar integración del JoinDialog"""
        ventas_df, clientes_df = sample_dataframes

        # Crear diálogo
        dialog = JoinDialog(ventas_df)

        # Simular carga manual de dataset derecho (sin UI)
        dialog.right_df = clientes_df
        dialog.right_file_path = 'clientes.csv'
        dialog.enable_join_config(True)
        dialog.update_column_combos()

        # Verificar que se cargó correctamente
        assert dialog.right_df is not None
        assert dialog.right_file_path == 'clientes.csv'

        # Verificar que se habilitaron los controles
        assert dialog.left_key_combo.isEnabled()
        assert dialog.right_key_combo.isEnabled()

        # Configurar join programáticamente
        dialog.left_key_combo.setCurrentText('cliente_id')
        dialog.right_key_combo.setCurrentText('id')
        dialog.join_type_group.buttons()[1].setChecked(True)  # Left join

        # Obtener configuración
        config = dialog.get_config()
        assert config is not None
        assert config.join_type == JoinType.LEFT
        assert config.left_keys == ['cliente_id']
        assert config.right_keys == ['id']

    def test_joined_data_view_integration(self, sample_dataframes, qapp):
        """Probar integración de JoinedDataView"""
        ventas_df, clientes_df = sample_dataframes

        # Crear resultado de join
        config = JoinConfig(
            left_keys=['cliente_id'],
            right_keys=['id'],
            join_type=JoinType.INNER
        )

        manager = DataJoinManager(ventas_df, clientes_df)
        result = manager.execute_join(config)

        # Crear vista
        view = JoinedDataView()

        # Establecer resultado
        view.set_join_result(result, 'ventas.csv', 'clientes.csv')

        # Verificar que se estableció correctamente
        assert view.join_metadata is not None
        assert view.left_dataset_name == 'ventas.csv'
        assert view.right_dataset_name == 'clientes.csv'
        assert view.original_df is not None
        assert len(view.original_df) == result.metadata.result_rows

        # Verificar metadatos mostrados
        metadata_text = view.metadata_text.toPlainText()
        assert 'Inner Join' in metadata_text
        assert 'ventas.csv + clientes.csv' in metadata_text
        assert str(result.metadata.result_rows) in metadata_text

    def test_export_integration(self, sample_dataframes, qapp, tmp_path):
        """Probar integración de exportación de resultados"""
        ventas_df, clientes_df = sample_dataframes

        # Crear resultado de join
        config = JoinConfig(
            left_keys=['cliente_id'],
            right_keys=['id'],
            join_type=JoinType.INNER
        )

        manager = DataJoinManager(ventas_df, clientes_df)
        result = manager.execute_join(config)

        # Crear vista y establecer resultado
        view = JoinedDataView()
        view.set_join_result(result, 'ventas.csv', 'clientes.csv')

        # Verificar que la vista tiene datos para exportar
        assert view.original_df is not None
        assert not view.original_df.empty

        # Verificar que el botón de exportar está habilitado
        assert view.export_btn.isEnabled()

    def test_join_history_integration(self, sample_dataframes):
        """Probar integración del sistema de historial"""
        from core.join.join_history import JoinHistory

        ventas_df, clientes_df = sample_dataframes

        # Crear configuración y resultado
        config = JoinConfig(
            left_keys=['cliente_id'],
            right_keys=['id'],
            join_type=JoinType.LEFT
        )

        manager = DataJoinManager(ventas_df, clientes_df)
        result = manager.execute_join(config)

        # Crear historial y añadir entrada
        history = JoinHistory(max_entries=10)
        initial_count = len(history.get_entries())
        history.add_entry('ventas.csv', 'clientes.csv', config, result)

        # Verificar que se guardó
        entries = history.get_entries()
        assert len(entries) == initial_count + 1
        # Verificar la entrada más reciente
        latest_entry = entries[0]  # Las entradas se añaden al inicio
        assert latest_entry.left_dataset_name == 'ventas.csv'
        assert latest_entry.right_dataset_name == 'clientes.csv'
        assert latest_entry.config.join_type == JoinType.LEFT
        assert latest_entry.success == True

    def test_memory_limit_handling(self):
        """Probar estimación de memoria"""
        # Crear datasets que generen un resultado muy grande
        large_left = pd.DataFrame({
            'id': range(1000),
            'value': [f'val_{i}' for i in range(1000)]
        })
        large_right = pd.DataFrame({
            'id': range(1000),
            'data': [f'data_{i}' for i in range(1000)]
        })

        config = JoinConfig(
            join_type=JoinType.CROSS  # Cross join de 1000x1000 = 1M filas
        )

        manager = DataJoinManager(large_left, large_right)

        # Verificar que la estimación de memoria funciona
        estimated_memory = manager._estimate_memory_usage(config)
        assert estimated_memory > 0

        # Verificar que se detecta cuando usar chunking
        should_chunk = manager._should_use_chunking(config, estimated_memory, 200 * 1024 * 1024)  # 200 MB
        assert should_chunk  # Debería usar chunking para cross joins grandes

    def test_error_recovery_integration(self, sample_dataframes):
        """Probar recuperación de errores en integración completa"""
        ventas_df, clientes_df = sample_dataframes

        # Configuración inválida (columnas faltantes)
        config = JoinConfig(
            left_keys=['columna_inexistente'],
            right_keys=['id'],
            join_type=JoinType.INNER
        )

        manager = DataJoinManager(ventas_df, clientes_df)
        result = manager.execute_join(config)

        # Debería fallar con error descriptivo
        assert not result.success
        assert "columna_inexistente" in result.error_message
        assert result.data.empty

    def test_large_dataset_performance(self):
        """Probar rendimiento con datasets más grandes"""
        # Crear datasets de tamaño mediano
        left_df = pd.DataFrame({
            'id': range(5000),
            'value': [f'val_{i}' for i in range(5000)]
        })

        right_df = pd.DataFrame({
            'id': range(3000),
            'data': [f'data_{i}' for i in range(3000)]
        })

        config = JoinConfig(
            left_keys=['id'],
            right_keys=['id'],
            join_type=JoinType.LEFT
        )

        manager = DataJoinManager(left_df, right_df)

        import time
        start_time = time.time()
        result = manager.execute_join(config)
        execution_time = time.time() - start_time

        # Verificar que completó exitosamente
        assert result.success
        assert len(result.data) == 5000  # Left join mantiene todas las filas del izquierdo

        # Verificar que no tomó demasiado tiempo (menos de 10 segundos)
        assert execution_time < 10.0

        # Verificar metadatos de rendimiento
        assert result.metadata.processing_time_seconds < 10.0
        assert result.metadata.memory_usage_mb > 0