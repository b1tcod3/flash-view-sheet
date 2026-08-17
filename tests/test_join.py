"""
Pruebas para funcionalidad de cruce de datos (join)
"""

import pytest
import pandas as pd
import re
from pathlib import Path
from core.join.models import JoinConfig, JoinType
from core.join.data_join_manager import DataJoinManager
from core.join.exceptions import UnsupportedJoinError
from core.join.join_history import JoinHistory


class TestDataJoinManager:
    """Pruebas para DataJoinManager"""

    @staticmethod
    @pytest.fixture
    def sample_dataframes() -> tuple:
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

    @staticmethod
    def test_inner_join(sample_dataframes) -> None:
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

    @staticmethod
    def test_left_join(sample_dataframes) -> None:
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

    @staticmethod
    def test_cross_join(sample_dataframes) -> None:
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

    @staticmethod
    def test_validation_missing_columns(sample_dataframes) -> None:
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

    @staticmethod
    def test_validation_different_key_counts(sample_dataframes) -> None:
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

    @staticmethod
    def test_unsupported_join_type(sample_dataframes) -> None:
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

    @staticmethod
    def test_preview_functionality(sample_dataframes) -> None:
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

    @staticmethod
    def test_chunking_large_cross_join() -> None:
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

    @staticmethod
    def test_chunking_detection() -> None:
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

    @staticmethod
    def test_column_suppression(sample_dataframes) -> None:
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

    @staticmethod
    def test_column_suppression_empty_list(sample_dataframes) -> None:
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

    @staticmethod
    def test_column_suppression_invalid_columns(sample_dataframes) -> None:
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

    @staticmethod
    def test_config_creation() -> None:
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

    @staticmethod
    def test_config_integrity_mode_default() -> None:
        """Verificar que integrity_mode tiene valor por defecto"""
        config = JoinConfig(
            left_keys=['id'],
            right_keys=['id'],
            join_type=JoinType.INNER
        )
        assert config.integrity_mode == 'm:m'

    @staticmethod
    def test_config_integrity_mode_none() -> None:
        """Verificar que integrity_mode puede desactivarse"""
        config = JoinConfig(
            left_keys=['id'],
            right_keys=['id'],
            join_type=JoinType.INNER,
            integrity_mode=None
        )
        assert config.integrity_mode is None


class TestOuterJoin:
    """Pruebas para OUTER join"""

    @staticmethod
    @pytest.fixture
    def sample_dataframes() -> tuple:
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

    @staticmethod
    def test_outer_join(sample_dataframes) -> None:
        """Probar outer join combina todos los registros"""
        left_df, right_df = sample_dataframes
        config = JoinConfig(
            left_keys=['id'],
            right_keys=['id'],
            join_type=JoinType.OUTER
        )

        manager = DataJoinManager(left_df, right_df)
        result = manager.execute_join(config)

        assert result.success
        assert len(result.data) == 5  # ids 1,2,3 (both) + 4 (left) + 5 (right)

    @staticmethod
    def test_outer_join_metadata(sample_dataframes) -> None:
        """Verificar estadísticas de matching en outer join"""
        left_df, right_df = sample_dataframes
        config = JoinConfig(
            left_keys=['id'],
            right_keys=['id'],
            join_type=JoinType.OUTER
        )

        manager = DataJoinManager(left_df, right_df)
        result = manager.execute_join(config)

        assert result.metadata.matched_rows == 3   # ids 1, 2, 3
        assert result.metadata.left_only_rows == 1  # id 4
        assert result.metadata.right_only_rows == 1  # id 5

    @staticmethod
    def test_outer_join_no_indicator(sample_dataframes) -> None:
        """Verificar que outer join sin indicator no deja columna _merge"""
        left_df, right_df = sample_dataframes
        config = JoinConfig(
            left_keys=['id'],
            right_keys=['id'],
            join_type=JoinType.OUTER,
            indicator=False
        )

        manager = DataJoinManager(left_df, right_df)
        result = manager.execute_join(config)

        assert result.success
        assert '_merge' not in result.data.columns

    @staticmethod
    def test_outer_join_with_indicator(sample_dataframes) -> None:
        """Verificar que outer join con indicator conserva la columna _merge"""
        left_df, right_df = sample_dataframes
        config = JoinConfig(
            left_keys=['id'],
            right_keys=['id'],
            join_type=JoinType.OUTER,
            indicator=True
        )

        manager = DataJoinManager(left_df, right_df)
        result = manager.execute_join(config)

        assert '_merge' in result.data.columns
        both = len(result.data[result.data['_merge'] == 'both'])
        left_only = len(result.data[result.data['_merge'] == 'left_only'])
        right_only = len(result.data[result.data['_merge'] == 'right_only'])
        assert both == 3
        assert left_only == 1
        assert right_only == 1


class TestIncludeColumnsChunked:
    """Pruebas para include_columns en joins chunked"""

    @staticmethod
    def test_include_columns_chunked_cross_join() -> None:
        """Verificar que include_columns funciona en cross join chunked"""
        left_df = pd.DataFrame({
            'id': range(200),
            'name': [f'left_{i}' for i in range(200)]
        })
        right_df = pd.DataFrame({
            'id': range(200),
            'data': [f'right_{i}' for i in range(200)]
        })

        config = JoinConfig(
            join_type=JoinType.CROSS,
            include_columns=['name', 'data']
        )

        manager = DataJoinManager(left_df, right_df)
        result = manager.execute_join(config)

        assert result.success
        assert set(result.data.columns) == {'name', 'data'}

    @staticmethod
    def test_include_columns_chunked_regular_join() -> None:
        """Verificar que include_columns funciona en regular join chunked"""
        left_df = pd.DataFrame({
            'id': range(5000),
            'name': [f'left_{i}' for i in range(5000)],
            'extra_left': [f'el_{i}' for i in range(5000)]
        })
        right_df = pd.DataFrame({
            'id': range(5000),
            'department': [f'dept_{i}' for i in range(5000)],
            'extra_right': [f'er_{i}' for i in range(5000)]
        })

        config = JoinConfig(
            left_keys=['id'],
            right_keys=['id'],
            join_type=JoinType.LEFT,
            include_columns=['name', 'department']
        )

        manager = DataJoinManager(left_df, right_df)
        result = manager.execute_join(config)

        assert result.success
        assert set(result.data.columns) == {'name', 'department'}


class TestCreateEmptyMetadata:
    """Pruebas para _create_empty_metadata"""

    @staticmethod
    def test_create_empty_metadata() -> None:
        """Verificar que _create_empty_metadata genera metadata válida"""
        left_df = pd.DataFrame({'id': [1, 2], 'name': ['A', 'B']})
        right_df = pd.DataFrame({'id': [3, 4], 'dept': ['X', 'Y']})

        manager = DataJoinManager(left_df, right_df)
        config = JoinConfig(
            left_keys=['id'],
            right_keys=['id'],
            join_type=JoinType.LEFT
        )

        metadata = manager._create_empty_metadata(config, 0.0)

        assert metadata.result_rows == 0
        assert metadata.left_rows == 2
        assert metadata.right_rows == 2
        assert metadata.matched_rows == 0
        assert metadata.left_only_rows == 0
        assert metadata.right_only_rows == 0
        assert metadata.join_type == JoinType.LEFT


class TestJoinHistory:
    """Pruebas para JoinHistory"""

    @staticmethod
    @pytest.fixture
    def tmp_history_dir(tmp_path):
        """Directorio temporal para historial"""
        return tmp_path

    @staticmethod
    @pytest.fixture
    def sample_result():
        """Crear un JoinResult de prueba"""
        left_df = pd.DataFrame({'id': [1, 2], 'name': ['A', 'B']})
        right_df = pd.DataFrame({'id': [1, 3], 'dept': ['X', 'Y']})
        manager = DataJoinManager(left_df, right_df)
        config = JoinConfig(
            left_keys=['id'],
            right_keys=['id'],
            join_type=JoinType.LEFT
        )
        return manager.execute_join(config)

    @staticmethod
    def test_uuid_id_generation(tmp_history_dir, sample_result):
        """Verificar que los IDs son UUIDs válidos"""
        history = JoinHistory(max_entries=10, history_dir=tmp_history_dir, use_uuid=True)
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')

        history.add_entry('left.csv', 'right.csv', JoinConfig(join_type=JoinType.LEFT, left_keys=['id'], right_keys=['id']), sample_result)

        entry = history.get_entries()[0]
        assert uuid_pattern.match(entry.entry_id), f"ID no es UUID válido: {entry.entry_id}"

    @staticmethod
    def test_timestamp_id_fallback(tmp_history_dir, sample_result):
        """Con use_uuid=False, IDs mantienen formato timestamp_secuencia"""
        history = JoinHistory(max_entries=10, history_dir=tmp_history_dir, use_uuid=False)
        ts_pattern = re.compile(r'^\d{8}_\d{6}_\d+$')

        history.add_entry('left.csv', 'right.csv', JoinConfig(join_type=JoinType.LEFT, left_keys=['id'], right_keys=['id']), sample_result)

        entry = history.get_entries()[0]
        assert ts_pattern.match(entry.entry_id), f"ID no tiene formato timestamp: {entry.entry_id}"

    @staticmethod
    def test_custom_history_dir(tmp_history_dir, sample_result):
        """El archivo se crea en el directorio especificado"""
        custom_dir = tmp_history_dir / "custom_history"
        history = JoinHistory(max_entries=10, history_dir=custom_dir, use_uuid=True)

        history.add_entry('left.csv', 'right.csv', JoinConfig(join_type=JoinType.LEFT, left_keys=['id'], right_keys=['id']), sample_result)

        assert history.history_file.exists()
        assert history.history_file.parent == custom_dir

    @staticmethod
    def test_default_history_dir():
        """Sin history_dir, usa la carpeta del módulo"""
        history = JoinHistory(max_entries=50)
        expected_dir = Path(__file__).parent.parent / "core" / "join"
        assert history.history_file.parent == expected_dir

    @staticmethod
    def test_save_and_reload(tmp_history_dir, sample_result):
        """Verificar persistencia: guardar y recargar"""
        config = JoinConfig(join_type=JoinType.LEFT, left_keys=['id'], right_keys=['id'])
        history = JoinHistory(max_entries=10, history_dir=tmp_history_dir, use_uuid=True)
        history.add_entry('ventas.csv', 'clientes.csv', config, sample_result)

        # Recargar desde el mismo archivo
        history2 = JoinHistory(max_entries=10, history_dir=tmp_history_dir, use_uuid=True)
        entries = history2.get_entries()
        assert len(entries) == 1
        assert entries[0].left_dataset_name == 'ventas.csv'
        assert entries[0].success is True

    @staticmethod
    def test_corrupt_entry_skipped(tmp_history_dir):
        """Entrada corrupta se omite sin crash"""
        corrupt_file = tmp_history_dir / "join_history.json"
        corrupt_data = {
            'entries': [
                {'id': 'valid', 'timestamp': '2026-01-01T00:00:00',
                 'left_dataset_name': 'a.csv', 'right_dataset_name': 'b.csv',
                 'config': {'join_type': 'left', 'left_keys': [], 'right_keys': [],
                            'suffixes': ['_left', '_right'], 'validate_integrity': True,
                            'sort_results': True, 'indicator': False, 'include_columns': []},
                 'result_metadata': {'result_rows': 0, 'join_type': 'left', 'join_keys': [],
                                     'matched_rows': 0, 'processing_time': 0.0, 'memory_usage': 0.0},
                 'success': True, 'error_message': ''},
                {'broken_entry': True},
            ]
        }
        corrupt_file.write_text(__import__('json').dumps(corrupt_data))

        history = JoinHistory(max_entries=10, history_dir=tmp_history_dir)
        assert len(history.get_entries()) == 1
        assert history.get_entries()[0].entry_id == 'valid'

    @staticmethod
    def test_mkdir_on_save(tmp_history_dir, sample_result):
        """El directorio se crea automáticamente si no existe"""
        nested_dir = tmp_history_dir / "a" / "b" / "c"
        history = JoinHistory(max_entries=10, history_dir=nested_dir, use_uuid=True)

        history.add_entry('left.csv', 'right.csv', JoinConfig(join_type=JoinType.LEFT, left_keys=['id'], right_keys=['id']), sample_result)

        assert nested_dir.exists()
        assert history.history_file.exists()

    @staticmethod
    def test_clear_history(tmp_history_dir, sample_result):
        """Verificar que clear_history vacía las entradas"""
        history = JoinHistory(max_entries=10, history_dir=tmp_history_dir, use_uuid=True)
        history.add_entry('left.csv', 'right.csv', JoinConfig(join_type=JoinType.LEFT, left_keys=['id'], right_keys=['id']), sample_result)
        assert len(history.get_entries()) == 1

        history.clear_history()
        assert len(history.get_entries()) == 0

    @staticmethod
    def test_max_entries_respected(tmp_history_dir):
        """Verificar que max_entries limita las entradas"""
        left_df = pd.DataFrame({'id': [1, 2], 'name': ['A', 'B']})
        right_df = pd.DataFrame({'id': [1, 3], 'dept': ['X', 'Y']})
        manager = DataJoinManager(left_df, right_df)

        history = JoinHistory(max_entries=3, history_dir=tmp_history_dir, use_uuid=True)

        for i in range(5):
            config = JoinConfig(left_keys=['id'], right_keys=['id'], join_type=JoinType.LEFT)
            result = manager.execute_join(config)
            history.add_entry(f'left_{i}.csv', 'right.csv', config, result)

        assert len(history.get_entries()) == 3