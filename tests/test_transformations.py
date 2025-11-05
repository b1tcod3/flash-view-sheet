"""
Tests unitarios para el sistema de transformaciones de datos
"""

import unittest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import tempfile
import os
import sys

# Añadir directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.transformations.base_transformation import BaseTransformation, CompositeTransformation
from core.transformations.transformation_manager import TransformationManager
from core.transformations.column_transformations import (
    RenameColumnsTransformation,
    CreateCalculatedColumnTransformation,
    ApplyFunctionTransformation,
    DropColumnsTransformation
)
from core.transformations.mathematical import (
    LogarithmicTransformation,
    ExponentialTransformation,
    ScalingTransformation,
    NormalizationTransformation
)
from core.transformations.text_processing import (
    TextCleaningTransformation,
    RegexExtractionTransformation,
    CaseConversionTransformation,
    PaddingTrimmingTransformation
)
from core.transformations.date_time import (
    DateParsingTransformation,
    ComponentExtractionTransformation,
    DateDifferenceTransformation,
    TimeZoneTransformation
)


class MockTransformation(BaseTransformation):
    """Transformación mock para testing"""
    
    def __init__(self, name="test", description="Test transformation", should_fail=False):
        super().__init__(name, description)
        self.should_fail = should_fail
        self.executed = False
        
    def execute(self, df: pd.DataFrame, parameters: dict = None):
        if self.should_fail:
            raise ValueError("Mock transformation failed")
        
        self.executed = True
        return df.copy()
    
    def validate_parameters(self, parameters: dict = None):
        return True


class TestBaseTransformation(unittest.TestCase):
    """Tests para la clase BaseTransformation"""
    
    def setUp(self):
        self.df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6],
            'C': ['x', 'y', 'z']
        })
        self.transformation = MockTransformation()
    
    def test_initialization(self):
        """Test de inicialización correcta"""
        self.assertEqual(self.transformation.name, "test")
        self.assertEqual(self.transformation.description, "Test transformation")
        self.assertTrue(self.transformation.is_reversible)
        self.assertEqual(self.transformation.execution_count, 0)
    
    def test_validate_data_valid(self):
        """Test validación de datos válidos"""
        result = self.transformation.validate_data(self.df)
        self.assertTrue(result)
    
    def test_validate_data_empty(self):
        """Test validación de DataFrame vacío"""
        empty_df = pd.DataFrame()
        with self.assertRaises(ValueError):
            self.transformation.validate_data(empty_df)
    
    def test_validate_data_none(self):
        """Test validación de DataFrame None"""
        with self.assertRaises(TypeError):
            self.transformation.validate_data(None)
    
    def test_get_metadata(self):
        """Test obtención de metadata"""
        metadata = self.transformation.get_metadata()
        self.assertEqual(metadata['name'], "test")
        self.assertEqual(metadata['description'], "Test transformation")
        self.assertTrue(metadata['is_reversible'])
    
    def test_estimate_performance(self):
        """Test estimación de rendimiento"""
        performance = self.transformation.estimate_performance(self.df)
        self.assertIn('estimated_complexity', performance)
        self.assertIn('estimated_time', performance)
        self.assertEqual(performance['row_count'], 3)
        self.assertEqual(performance['column_count'], 3)
    
    def test_undo_not_implemented(self):
        """Test undo en transformación no reversible"""
        self.transformation.is_reversible = False
        with self.assertRaises(NotImplementedError):
            self.transformation.undo(self.df)


class TestCompositeTransformation(unittest.TestCase):
    """Tests para la clase CompositeTransformation"""
    
    def setUp(self):
        self.df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        self.transformation1 = MockTransformation("trans1", "First transformation")
        self.transformation2 = MockTransformation("trans2", "Second transformation")
        self.composite = CompositeTransformation("composite", "Composite test", [self.transformation1, self.transformation2])
    
    def test_execute_sequence(self):
        """Test ejecución secuencial de transformaciones"""
        result = self.composite.execute(self.df)
        self.assertTrue(self.transformation1.executed)
        self.assertTrue(self.transformation2.executed)
        self.assertEqual(len(result), 3)
    
    def test_reversibility(self):
        """Test cálculo de reversibilidad"""
        self.assertTrue(self.composite.is_reversible)
        
        # Hacer una transformación no reversible
        self.transformation1.is_reversible = False
        # Recalcular reversibilidad después del cambio
        self.composite.is_reversible = all(t.is_reversible for t in self.composite.transformations)
        self.assertFalse(self.composite.is_reversible)
    
    def test_add_transformation(self):
        """Test añadir transformación"""
        new_transformation = MockTransformation("new", "New transformation")
        self.composite.add_transformation(new_transformation)
        self.assertEqual(len(self.composite.get_transformations()), 3)
    
    def test_remove_transformation(self):
        """Test remover transformación"""
        initial_count = len(self.composite.get_transformations())
        self.composite.remove_transformation(self.transformation1)
        self.assertEqual(len(self.composite.get_transformations()), initial_count - 1)


class TestTransformationManager(unittest.TestCase):
    """Tests para TransformationManager"""
    
    def setUp(self):
        self.manager = TransformationManager()
        self.df = pd.DataFrame({
            'numeric_col': [1, 2, 3, 4, 5],
            'text_col': ['a', 'b', 'c', 'd', 'e'],
            'mixed_col': [1, 'text', 3.5, 4, 5]
        })
    
    def test_initialization(self):
        """Test inicialización del manager"""
        self.assertTrue(self.manager._history_enabled)
        self.assertEqual(self.manager._history.maxlen, 50)
    
    def test_system_info(self):
        """Test información del sistema"""
        info = self.manager.get_system_info()
        self.assertIn('registered_transformations', info)
        self.assertIn('saved_pipelines', info)
        self.assertIn('configuration', info)
    
    def test_history_operations(self):
        """Test operaciones de historial"""
        # Ejecutar operación mock
        self.manager._save_to_history({'operation': 'test', 'data': 'test_data'})
        
        # Verificar que se guardó
        history = self.manager.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['operation'], 'test')
        
        # Test undo
        undone = self.manager.undo_last_operation()
        self.assertIsNotNone(undone)
        self.assertEqual(len(self.manager.get_history()), 0)
        
        # Test redo
        redone = self.manager.redo_last_operation()
        self.assertIsNotNone(redone)
        self.assertEqual(len(self.manager.get_history()), 1)
    
    def test_performance_metrics(self):
        """Test métricas de rendimiento"""
        # Simular ejecución de transformación
        self.manager._update_performance_metrics('test_trans', 1.5, 100)
        
        metrics = self.manager.get_performance_report()
        self.assertIn('test_trans', metrics['transformations'])
        self.assertEqual(metrics['total_operations'], 1)


class TestColumnTransformations(unittest.TestCase):
    """Tests para transformaciones de columnas"""
    
    def setUp(self):
        self.df = pd.DataFrame({
            'old_name': [1, 2, 3],
            'value1': [4, 5, 6],
            'value2': [7, 8, 9],
            'text': ['a', 'b', 'c']
        })
    
    def test_rename_columns(self):
        """Test renombrado de columnas"""
        mapping = {'old_name': 'new_name'}
        transformation = RenameColumnsTransformation(mapping)
        result = transformation.execute(self.df.copy())
        
        self.assertIn('new_name', result.columns)
        self.assertNotIn('old_name', result.columns)
        self.assertTrue((result['new_name'] == [1, 2, 3]).all())
    
    def test_create_calculated_column_formula(self):
        """Test creación de columna con fórmula"""
        transformation = CreateCalculatedColumnTransformation(
            'sum_column', 
            formula='value1 + value2'
        )
        result = transformation.execute(self.df.copy())
        
        self.assertIn('sum_column', result.columns)
        self.assertTrue((result['sum_column'] == [11, 13, 15]).all())
    
    def test_create_calculated_column_function(self):
        """Test creación de columna con función"""
        def custom_func(series1, series2):
            return series1 * series2
        
        transformation = CreateCalculatedColumnTransformation(
            'product_column',
            function=custom_func,
            source_columns=['value1', 'value2']
        )
        result = transformation.execute(self.df.copy())
        
        self.assertIn('product_column', result.columns)
        self.assertTrue((result['product_column'] == [28, 40, 54]).all())
    
    def test_apply_function(self):
        """Test aplicación de función"""
        def double(x):
            return x * 2
        
        transformation = ApplyFunctionTransformation('value1', double, new_column_name='doubled')
        result = transformation.execute(self.df.copy())
        
        self.assertIn('doubled', result.columns)
        self.assertTrue((result['doubled'] == [8, 10, 12]).all())
    
    def test_drop_columns(self):
        """Test eliminación de columnas"""
        transformation = DropColumnsTransformation(['old_name', 'text'])
        result = transformation.execute(self.df.copy())
        
        self.assertNotIn('old_name', result.columns)
        self.assertNotIn('text', result.columns)
        self.assertEqual(len(result.columns), 2)
    
    def test_drop_columns_by_pattern(self):
        """Test eliminación de columnas por patrón"""
        transformation = DropColumnsTransformation(pattern=r'value\d+')
        result = transformation.execute(self.df.copy())
        
        self.assertNotIn('value1', result.columns)
        self.assertNotIn('value2', result.columns)
        self.assertEqual(len(result.columns), 2)


class TestMathematicalTransformations(unittest.TestCase):
    """Tests para transformaciones matemáticas"""
    
    def setUp(self):
        self.df = pd.DataFrame({
            'positive': [1, 2, 3, 4, 5],
            'mixed': [-2, -1, 0, 1, 2],
            'large': [100, 200, 300, 400, 500]
        })
    
    def test_logarithmic_transformation(self):
        """Test transformación logarítmica"""
        transformation = LogarithmicTransformation(['positive'], 'log10')
        result = transformation.execute(self.df.copy())
        
        # log10(1) = 0, log10(10) = 1, etc.
        expected = np.log10(self.df['positive'])
        self.assertTrue(np.allclose(result['positive'], expected))
    
    def test_exponential_transformation(self):
        """Test transformación exponencial"""
        transformation = ExponentialTransformation(['positive'], 'square')
        result = transformation.execute(self.df.copy())
        
        expected = self.df['positive'] ** 2
        self.assertTrue((result['positive'] == expected).all())
    
    def test_scaling_minmax(self):
        """Test escalado MinMax"""
        transformation = ScalingTransformation(['positive'], 'minmax')
        result = transformation.execute(self.df.copy())
        
        # Verificar que el rango es [0, 1]
        self.assertAlmostEqual(result['positive'].min(), 0.0)
        self.assertAlmostEqual(result['positive'].max(), 1.0)
    
    def test_scaling_standard(self):
        """Test escalado estándar"""
        transformation = ScalingTransformation(['positive'], 'standard')
        result = transformation.execute(self.df.copy())
        
        # Verificar que la media es 0 y la desviación es 1
        self.assertAlmostEqual(result['positive'].mean(), 0.0, places=10)
        self.assertAlmostEqual(result['positive'].std(), 1.0, places=10)
    
    def test_normalization(self):
        """Test normalización"""
        transformation = NormalizationTransformation(['positive'], 'l2', axis=1)
        result = transformation.execute(self.df.copy())
        
        # Verificar que la norma L2 es 1 (column-wise)
        norm = np.sqrt((result['positive'] ** 2).sum())
        self.assertAlmostEqual(norm, 1.0, places=10)


class TestPipelineExecution(unittest.TestCase):
    """Tests para ejecución de pipelines"""
    
    def setUp(self):
        self.manager = TransformationManager()
        self.df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6],
            'C': [7, 8, 9]
        })
    
    def test_simple_pipeline(self):
        """Test pipeline simple con múltiples pasos"""
        # Este test se puede expandir cuando tengamos las transformaciones registradas
        pipeline_steps = []
        result = self.manager.execute_pipeline(self.df, pipeline_steps)
        
        # Sin pasos, el DataFrame debe permanecer igual
        pd.testing.assert_frame_equal(result, self.df)
    
    def test_pipeline_with_optimization(self):
        """Test pipeline con optimizaciones"""
        # Simular dataset grande
        large_df = pd.DataFrame(np.random.rand(50000, 10))
        pipeline_steps = []
        
        # Esto debería activar optimizaciones
        result = self.manager.execute_pipeline(large_df, pipeline_steps, use_optimization=True)
        self.assertEqual(len(result), 50000)


class TestErrorHandling(unittest.TestCase):
    """Tests para manejo de errores"""
    
    def setUp(self):
        self.manager = TransformationManager()
        self.df = pd.DataFrame({'A': [1, 2, 3]})
    
    def test_invalid_column_error(self):
        """Test error con columna inválida"""
        with self.assertRaises(ValueError):
            transformation = RenameColumnsTransformation({'nonexistent': 'new_name'})
            transformation.execute(self.df)
    
    def test_invalid_formula_error(self):
        """Test error con fórmula inválida"""
        transformation = CreateCalculatedColumnTransformation('bad', formula='invalid_formula++')
        with self.assertRaises(ValueError):
            transformation.execute(self.df)
    
    def test_non_numeric_error(self):
        """Test error con datos no numéricos"""
        text_df = pd.DataFrame({'text': ['a', 'b', 'c']})
        transformation = LogarithmicTransformation(['text'])
        with self.assertRaises(ValueError):
            transformation.execute(text_df)


class TestTextTransformations(unittest.TestCase):
    """Tests para transformaciones de texto"""
    
    def setUp(self):
        self.df = pd.DataFrame({
            'text_col': ['Hello World!', 'Test-Data_123', '  SPACED text  '],
            'mixed_col': ['ABC def', 'GHI jkl', 'MNO pqr']
        })
    
    def test_text_cleaning(self):
        """Test limpieza de texto"""
        transformation = TextCleaningTransformation(['text_col'], remove_special_chars=True, remove_punctuation=True)
        result = transformation.execute(self.df.copy())
        
        # Verificar que se removieron caracteres especiales
        self.assertNotIn('!', result['text_col'].iloc[0])
        self.assertNotIn('-', result['text_col'].iloc[1])
        self.assertNotIn('_', result['text_col'].iloc[1])
    
    def test_case_conversion(self):
        """Test conversión de case"""
        transformation = CaseConversionTransformation(['mixed_col'], 'upper')
        result = transformation.execute(self.df.copy())
        
        # Verificar que se convirtió a mayúsculas (mantiene espacios)
        self.assertEqual(result['mixed_col'].iloc[0], 'ABC DEF')
        self.assertEqual(result['mixed_col'].iloc[1], 'GHI JKL')
        self.assertEqual(result['mixed_col'].iloc[2], 'MNO PQR')
    
    def test_case_conversion_all_upper(self):
        """Test que todos los valores se convierten correctamente"""
        transformation = CaseConversionTransformation(['mixed_col'], 'upper')
        result = transformation.execute(self.df.copy())
        
        # Verificar que el primer valor se convirtió correctamente
        self.assertEqual(result['mixed_col'].iloc[0], 'ABC DEF')
    
    def test_regex_extraction(self):
        """Test extracción con regex"""
        # Usar patrón con grupo de captura
        transformation = RegexExtractionTransformation(['text_col'], r'(\d+)', extract_group=0)
        result = transformation.execute(self.df.copy())
        
        # Debe extraer los dígitos
        self.assertEqual(result['text_col'].iloc[1], '123')
    
    def test_padding_trimming(self):
        """Test padding y trimming"""
        transformation = PaddingTrimmingTransformation(['mixed_col'], 10, side='right')
        result = transformation.execute(self.df.copy())
        
        # Verificar que todas las strings tienen longitud 10
        self.assertTrue(all(len(str(x)) == 10 for x in result['mixed_col']))


class TestDateTimeTransformations(unittest.TestCase):
    """Tests para transformaciones de fecha y tiempo"""
    
    def setUp(self):
        self.df = pd.DataFrame({
            'date_col': ['2023-01-15', '2023-06-20', '2023-12-25'],
            'datetime_col': ['2023-01-15 10:30:00', '2023-06-20 14:45:30', '2023-12-25 23:59:59']
        })
    
    def test_date_parsing(self):
        """Test parsing de fechas"""
        transformation = DateParsingTransformation(['date_col'])
        result = transformation.execute(self.df.copy())
        
        # Verificar que se parseó correctamente
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result['date_col']))
    
    def test_component_extraction(self):
        """Test extracción de componentes"""
        transformation = ComponentExtractionTransformation(['date_col'], 'year')
        result = transformation.execute(self.df.copy())
        
        # Verificar que se extrajo el año
        self.assertTrue((result['date_col_year'] == 2023).all())
    
    def test_date_difference(self):
        """Test cálculo de diferencias de fecha"""
        transformation = DateDifferenceTransformation(['date_col'], time_unit='days')
        result = transformation.execute(self.df.copy())
        
        # Verificar que se calculó la diferencia
        self.assertIn('date_col_epoch_days_diff', result.columns)
        self.assertTrue(result['date_col_epoch_days_diff'].notna().all())


def create_test_suite():
    """Crear suite de tests"""
    suite = unittest.TestSuite()
    
    # Añadir tests
    test_classes = [
        TestBaseTransformation,
        TestCompositeTransformation,
        TestTransformationManager,
        TestColumnTransformations,
        TestMathematicalTransformations,
        TestTextTransformations,
        TestDateTimeTransformations,
        TestPipelineExecution,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    return suite


if __name__ == '__main__':
    # Crear y ejecutar suite de tests
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit con código de error si fallan tests
    exit(0 if result.wasSuccessful() else 1)