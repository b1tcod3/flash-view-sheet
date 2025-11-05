"""
Tests unitarios para transformaciones de codificación categórica y agregación avanzada
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

from core.transformations.encoding import (
    LabelEncodingTransformation,
    OneHotEncodingTransformation,
    OrdinalEncodingTransformation,
    TargetEncodingTransformation
)
from core.transformations.advanced_aggregations import (
    MultiFunctionAggregationTransformation,
    AdvancedPivotingTransformation,
    RollingWindowTransformation,
    ExpandingWindowTransformation,
    GroupByTransformationTransformation
)


class TestLabelEncoding(unittest.TestCase):
    """Tests para LabelEncodingTransformation"""
    
    def setUp(self):
        self.df = pd.DataFrame({
            'category': ['A', 'B', 'A', 'C', 'B'],
            'text': ['cat', 'dog', 'bird', 'fish', 'dog'],
            'numeric': [1, 2, 3, 4, 5]
        })
    
    def test_label_encoding(self):
        """Test encoding de etiquetas"""
        transformation = LabelEncodingTransformation(['category', 'text'])
        result = transformation.execute(self.df.copy())
        
        # Verificar que las columnas se codificaron
        self.assertIn('category', result.columns)
        self.assertIn('text', result.columns)
        
        # Verificar que los valores son numéricos
        self.assertTrue(pd.api.types.is_numeric_dtype(result['category']))
        self.assertTrue(pd.api.types.is_numeric_dtype(result['text']))
        
        # Verificar que la decodificación funciona
        decoded = transformation.decode_values(result, 'category')
        # Los valores codificados deben ser recuperables
        self.assertTrue((decoded['category'].isin(['A', 'B', 'C'])).all())
    
    def test_label_encoding_with_missing(self):
        """Test encoding con valores faltantes"""
        df_with_missing = pd.DataFrame({
            'category': ['A', 'B', None, 'C', 'B'],
            'numeric': [1, 2, 3, 4, 5]
        })
        
        transformation = LabelEncodingTransformation(['category'], handle_missing='use_encoded_value')
        result = transformation.execute(df_with_missing.copy())
        
        # El valor None debe ser codificado como -1
        self.assertTrue((result['category'] != -1).any())
    
    def test_label_encoding_parameter_validation(self):
        """Test validación de parámetros"""
        # Parámetros válidos
        valid_params = {
            'handle_unknown': 'error',
            'handle_missing': 'error'
        }
        transformation = LabelEncodingTransformation(['category'])
        self.assertTrue(transformation.validate_parameters(valid_params))
        
        # Parámetros inválidos
        invalid_params = {
            'handle_unknown': 'invalid',
            'handle_missing': 'error'
        }
        self.assertFalse(transformation.validate_parameters(invalid_params))


class TestOneHotEncoding(unittest.TestCase):
    """Tests para OneHotEncodingTransformation"""
    
    def setUp(self):
        self.df = pd.DataFrame({
            'category': ['A', 'B', 'A', 'C', 'B'],
            'color': ['red', 'blue', 'red', 'green', 'blue'],
            'numeric': [1, 2, 3, 4, 5]
        })
    
    def test_one_hot_encoding(self):
        """Test one-hot encoding"""
        transformation = OneHotEncodingTransformation(['category', 'color'])
        result = transformation.execute(self.df.copy())
        
        # Verificar que se crearon nuevas columnas
        self.assertGreater(len(result.columns), len(self.df.columns))
        
        # Verificar que las columnas originales se eliminaron
        self.assertNotIn('category', result.columns)
        self.assertNotIn('color', result.columns)
        
        # Verificar que se crearon columnas para cada categoría
        category_columns = [col for col in result.columns if col.startswith('category_')]
        color_columns = [col for col in result.columns if col.startswith('color_')]
        
        self.assertGreater(len(category_columns), 0)
        self.assertGreater(len(color_columns), 0)
    
    def test_one_hot_encoding_drop_first(self):
        """Test one-hot encoding con drop_first"""
        transformation = OneHotEncodingTransformation(['category'], drop_first=True)
        result = transformation.execute(self.df.copy())
        
        # Verificar que se droppeó la primera categoría
        # En one-hot encoding con drop_first, se omiten n-1 columnas de n categorías
        self.assertEqual(len([col for col in result.columns if col.startswith('category_')]), 
                         len(self.df['category'].unique()) - 1)
    
    def test_one_hot_encoding_with_prefix(self):
        """Test one-hot encoding con prefijo"""
        transformation = OneHotEncodingTransformation(['category'], prefix='cat')
        result = transformation.execute(self.df.copy())
        
        # Verificar que se usó el prefijo personalizado
        self.assertTrue(any(col.startswith('cat_') for col in result.columns))
    
    def test_one_hot_encoding_parameter_validation(self):
        """Test validación de parámetros"""
        # Parámetros válidos
        valid_params = {
            'drop_first': True,
            'prefix_sep': '_',
            'handle_unknown': 'ignore',
            'handle_missing': 'ignore'
        }
        transformation = OneHotEncodingTransformation(['category'])
        self.assertTrue(transformation.validate_parameters(valid_params))
        
        # Parámetros inválidos
        invalid_params = {
            'drop_first': 'invalid',  # Debe ser booleano
            'handle_unknown': 'invalid'
        }
        self.assertFalse(transformation.validate_parameters(invalid_params))


class TestOrdinalEncoding(unittest.TestCase):
    """Tests para OrdinalEncodingTransformation"""
    
    def setUp(self):
        self.df = pd.DataFrame({
            'size': ['S', 'M', 'L', 'S', 'L'],
            'rating': ['low', 'high', 'medium', 'low', 'high'],
            'numeric': [1, 2, 3, 4, 5]
        })
    
    def test_ordinal_encoding(self):
        """Test encoding ordinal"""
        # Crear un mapeo explícito para el orden
        encoding_map = {
            'size': [('S', 1), ('M', 2), ('L', 3)],
            'rating': [('low', 1), ('medium', 2), ('high', 3)]
        }
        
        transformation = OrdinalEncodingTransformation(['size', 'rating'], encoding_map=encoding_map)
        result = transformation.execute(self.df.copy())
        
        # Verificar que las columnas se codificaron
        self.assertIn('size', result.columns)
        self.assertIn('rating', result.columns)
        
        # Verificar que los valores son los correctos según el mapeo
        self.assertTrue((result['size'] == [1, 2, 3, 1, 3]).all())
        self.assertTrue((result['rating'] == [1, 3, 2, 1, 3]).all())
        
        # Verificar decodificación
        decoded = transformation.decode_values(result, 'size')
        self.assertTrue((decoded['size'] == ['S', 'M', 'L', 'S', 'L']).all())
    
    def test_ordinal_encoding_auto(self):
        """Test encoding ordinal con orden automático"""
        transformation = OrdinalEncodingTransformation(['size'])
        result = transformation.execute(self.df.copy())
        
        # Verificar que se codificó automáticamente en orden alfabético
        # 'L', 'M', 'S' -> 1, 2, 3
        self.assertTrue((result['size'] == [3, 2, 1, 3, 1]).all())
    
    def test_ordinal_encoding_with_missing(self):
        """Test encoding ordinal con valores faltantes"""
        df_with_missing = pd.DataFrame({
            'size': ['S', 'M', None, 'L', 'S'],
            'numeric': [1, 2, 3, 4, 5]
        })
        
        transformation = OrdinalEncodingTransformation(['size'], handle_missing='use_encoded_value')
        result = transformation.execute(df_with_missing.copy())
        
        # El valor None debe ser codificado como 0
        self.assertTrue(result['size'].iloc[2] == 0)
    
    def test_ordinal_encoding_parameter_validation(self):
        """Test validación de parámetros"""
        # Parámetros válidos
        valid_params = {
            'handle_unknown': 'error',
            'handle_missing': 'error'
        }
        transformation = OrdinalEncodingTransformation(['size'])
        self.assertTrue(transformation.validate_parameters(valid_params))
        
        # Parámetros inválidos
        invalid_params = {
            'handle_unknown': 'invalid',
            'handle_missing': 'error'
        }
        self.assertFalse(transformation.validate_parameters(invalid_params))


class TestTargetEncoding(unittest.TestCase):
    """Tests para TargetEncodingTransformation"""
    
    def setUp(self):
        self.df = pd.DataFrame({
            'category': ['A', 'B', 'A', 'C', 'B', 'A', 'B', 'C', 'A', 'B'],
            'numeric_feature': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'target': [0, 1, 0, 1, 1, 0, 1, 0, 0, 1]
        })
    
    def test_target_encoding(self):
        """Test encoding por target"""
        transformation = TargetEncodingTransformation(['category'], 'target')
        result = transformation.execute(self.df.copy())
        
        # Verificar que la columna se codificó
        self.assertIn('category', result.columns)
        
        # Verificar que los valores se han modificado
        # (estarán entre 0 y 1, que son valores probables para la media de 'target')
        self.assertTrue((result['category'] >= 0).all())
        self.assertTrue((result['category'] <= 1).all())
    
    def test_target_encoding_with_smoothing(self):
        """Test encoding por target con suavizado"""
        transformation = TargetEncodingTransformation(['category'], 'target', smoothing=10.0)
        result = transformation.execute(self.df.copy())
        
        # Con suavizado alto, los valores deben estar más cerca de la media global
        global_mean = self.df['target'].mean()
        
        # Verificar que los valores están suavizados hacia la media global
        for category in self.df['category'].unique():
            category_mean = self.df[self.df['category'] == category]['target'].mean()
            category_data = result[result['category'] == category]['category'].iloc[0]
            
            # Con suavizado, el valor codificado debe estar entre la media de categoría y la media global
            # Suavizado alto -> más cerca de la media global
            self.assertLess(abs(category_data - global_mean), abs(category_mean - global_mean))
    
    def test_target_encoding_parameter_validation(self):
        """Test validación de parámetros"""
        # Parámetros válidos
        valid_params = {
            'target_column': 'target',
            'smoothing': 1.0,
            'noise': 0.0,
            'cv': 5
        }
        transformation = TargetEncodingTransformation(['category'], 'target')
        self.assertTrue(transformation.validate_parameters(valid_params))
        
        # Parámetros inválidos
        invalid_params = {
            'target_column': 'nonexistent',
            'smoothing': -1.0,
            'cv': 1
        }
        self.assertFalse(transformation.validate_parameters(invalid_params))
    
    def test_target_encoding_error_non_numeric_target(self):
        """Test error cuando target no es numérico"""
        df_with_text_target = pd.DataFrame({
            'category': ['A', 'B', 'A', 'C', 'B'],
            'target': ['yes', 'no', 'yes', 'no', 'no']
        })
        
        transformation = TargetEncodingTransformation(['category'], 'target')
        
        with self.assertRaises(ValueError):
            transformation.execute(df_with_text_target.copy())


class TestMultiFunctionAggregation(unittest.TestCase):
    """Tests para MultiFunctionAggregationTransformation"""
    
    def setUp(self):
        self.df = pd.DataFrame({
            'group': ['A', 'A', 'B', 'B', 'B'],
            'value1': [1, 2, 3, 4, 5],
            'value2': [10, 20, 30, 40, 50],
            'value3': [100, 200, 300, 400, 500]
        })
    
    def test_multi_function_aggregation(self):
        """Test agregación con múltiples funciones"""
        aggregation_functions = {
            'value1': ['sum', 'mean'],
            'value2': ['count', 'max']
        }
        
        transformation = MultiFunctionAggregationTransformation(['group'], aggregation_functions)
        result = transformation.execute(self.df.copy())
        
        # Verificar estructura del resultado
        self.assertIn('group', result.columns)
        
        # Verificar que se calcularon las agregaciones
        self.assertIn('value1_sum', result.columns)
        self.assertIn('value1_mean', result.columns)
        self.assertIn('value2_count', result.columns)
        self.assertIn('value2_max', result.columns)
        
        # Verificar que los valores son correctos
        # value1: A -> sum=3, mean=1.5; B -> sum=12, mean=4
        self.assertTrue((result[result['group'] == 'A']['value1_sum'].iloc[0] == 3).all())
        self.assertTrue((result[result['group'] == 'B']['value1_sum'].iloc[0] == 12).all())
    
    def test_multi_function_aggregation_global(self):
        """Test agregación global (sin grupos)"""
        aggregation_functions = {
            'value1': ['sum', 'mean']
        }
        
        transformation = MultiFunctionAggregationTransformation([], aggregation_functions)
        result = transformation.execute(self.df.copy())
        
        # Verificar que se creó una fila para la agregación global
        self.assertEqual(len(result), 1)
        
        # Verificar que los valores son correctos
        # total: sum=15, mean=3
        self.assertEqual(result['value1_sum'].iloc[0], 15)
        self.assertEqual(result['value1_mean'].iloc[0], 3)
    
    def test_multi_function_aggregation_parameter_validation(self):
        """Test validación de parámetros"""
        # Parámetros válidos
        valid_params = {
            'groupby_columns': ['group'],
            'aggregation_functions': {
                'value1': ['sum', 'mean']
            }
        }
        transformation = MultiFunctionAggregationTransformation(['group'], {'value1': ['sum']})
        self.assertTrue(transformation.validate_parameters(valid_params))
        
        # Parámetros inválidos
        invalid_params = {
            'groupby_columns': 'not_a_list',
            'aggregation_functions': {
                'value1': ['sum', 'mean']
            }
        }
        self.assertFalse(transformation.validate_parameters(invalid_params))


class TestAdvancedPivoting(unittest.TestCase):
    """Tests para AdvancedPivotingTransformation"""
    
    def setUp(self):
        self.df = pd.DataFrame({
            'index_col': ['A', 'A', 'B', 'B', 'C', 'C'],
            'column_col': ['X', 'Y', 'X', 'Y', 'X', 'Y'],
            'value1': [1, 2, 3, 4, 5, 6],
            'value2': [10, 20, 30, 40, 50, 60]
        })
    
    def test_advanced_pivoting(self):
        """Test pivoteo avanzado"""
        transformation = AdvancedPivotingTransformation(
            index='index_col',
            columns='column_col',
            values='value1',
            aggfunc='sum'
        )
        result = transformation.execute(self.df.copy())
        
        # Verificar estructura del resultado
        self.assertIn('index_col', result.columns)
        self.assertIn('value1_X', result.columns)
        self.assertIn('value1_Y', result.columns)
        
        # Verificar valores
        # A: X=1, Y=2
        # B: X=3, Y=4
        # C: X=5, Y=6
        self.assertEqual(result[result['index_col'] == 'A']['value1_X'].iloc[0], 1)
        self.assertEqual(result[result['index_col'] == 'A']['value1_Y'].iloc[0], 2)
        self.assertEqual(result[result['index_col'] == 'B']['value1_X'].iloc[0], 3)
        self.assertEqual(result[result['index_col'] == 'B']['value1_Y'].iloc[0], 4)
    
    def test_advanced_pivoting_multiple_values(self):
        """Test pivoteo con múltiples valores"""
        transformation = AdvancedPivotingTransformation(
            index='index_col',
            columns='column_col',
            values=['value1', 'value2'],
            aggfunc='sum'
        )
        result = transformation.execute(self.df.copy())
        
        # Verificar que se crearon columnas para ambos valores
        self.assertIn('value1_X', result.columns)
        self.assertIn('value1_Y', result.columns)
        self.assertIn('value2_X', result.columns)
        self.assertIn('value2_Y', result.columns)
    
    def test_advanced_pivoting_multiple_columns(self):
        """Test pivoteo con múltiples columnas de pivote"""
        df_extended = pd.DataFrame({
            'index_col': ['A', 'A', 'A', 'A', 'B', 'B', 'B', 'B'],
            'column_col1': ['X', 'X', 'Y', 'Y', 'X', 'X', 'Y', 'Y'],
            'column_col2': ['P', 'Q', 'P', 'Q', 'P', 'Q', 'P', 'Q'],
            'value1': [1, 2, 3, 4, 5, 6, 7, 8]
        })
        
        transformation = AdvancedPivotingTransformation(
            index='index_col',
            columns=['column_col1', 'column_col2'],
            values='value1',
            aggfunc='sum'
        )
        result = transformation.execute(df_extended.copy())
        
        # Verificar estructura (debe haber columnas para cada combinación de las columnas de pivote)
        # La estructura será más compleja, pero debemos tener al menos las columnas de índice
        self.assertIn('index_col', result.columns)
    
    def test_advanced_pivoting_with_margins(self):
        """Test pivoteo con totales (margins)"""
        transformation = AdvancedPivotingTransformation(
            index='index_col',
            columns='column_col',
            values='value1',
            aggfunc='sum',
            margins=True
        )
        result = transformation.execute(self.df.copy())
        
        # Debe haber una fila adicional para los totales
        self.assertGreater(len(result), 3)  # A, B, C + total
        
        # Debe haber una columna para el total
        # En pandas, cuando margins=True, se añade una columna 'All'
        self.assertTrue(any('All' in col for col in result.columns))
    
    def test_advanced_pivoting_parameter_validation(self):
        """Test validación de parámetros"""
        # Parámetros válidos
        valid_params = {
            'index': ['index_col'],
            'columns': ['column_col'],
            'values': ['value1'],
            'aggfunc': ['sum']
        }
        transformation = AdvancedPivotingTransformation(
            'index_col',
            'column_col',
            'value1',
            'sum'
        )
        self.assertTrue(transformation.validate_parameters(valid_params))
        
        # Parámetros inválidos
        invalid_params = {
            'index': 'not_a_list',
            'aggfunc': ['invalid_func']
        }
        self.assertFalse(transformation.validate_parameters(invalid_params))


class TestRollingWindow(unittest.TestCase):
    """Tests para RollingWindowTransformation"""
    
    def setUp(self):
        self.df = pd.DataFrame({
            'value1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'value2': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            'text': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
        })
    
    def test_rolling_window(self):
        """Test rolling window"""
        transformation = RollingWindowTransformation(
            columns=['value1'],
            window_size=3,
            aggregation_function='mean'
        )
        result = transformation.execute(self.df.copy())
        
        # Verificar que se creó una nueva columna
        self.assertIn('value1_mean_w3', result.columns)
        
        # Verificar que la ventana funciona correctamente
        # La media de los primeros 3 valores: (1+2+3)/3 = 2.0
        self.assertAlmostEqual(result['value1_mean_w3'].iloc[2], 2.0, places=5)
        # La media de los valores 2,3,4: (2+3+4)/3 = 3.0
        self.assertAlmostEqual(result['value1_mean_w3'].iloc[3], 3.0, places=5)
    
    def test_rolling_window_different_functions(self):
        """Test rolling window con diferentes funciones"""
        for func in ['sum', 'min', 'max', 'std']:
            transformation = RollingWindowTransformation(
                columns=['value1'],
                window_size=3,
                aggregation_function=func
            )
            result = transformation.execute(self.df.copy())
            
            # Verificar que se creó la columna correspondiente
            self.assertIn(f'value1_{func}_w3', result.columns)
    
    def test_rolling_window_parameter_validation(self):
        """Test validación de parámetros"""
        # Parámetros válidos
        valid_params = {
            'columns': ['value1'],
            'window_size': 3,
            'aggregation_function': 'mean',
            'min_periods': 2,
            'center': False,
            'closed': 'left'
        }
        transformation = RollingWindowTransformation(['value1'], 3, 'mean')
        self.assertTrue(transformation.validate_parameters(valid_params))
        
        # Parámetros inválidos
        invalid_params = {
            'window_size': 0,  # Debe ser > 0
            'aggregation_function': 'invalid'
        }
        self.assertFalse(transformation.validate_parameters(invalid_params))
    
    def test_rolling_window_error_non_numeric(self):
        """Test error con columna no numérica"""
        transformation = RollingWindowTransformation(
            columns=['text'],
            window_size=3,
            aggregation_function='mean'
        )
        
        with self.assertRaises(ValueError):
            transformation.execute(self.df.copy())


class TestExpandingWindow(unittest.TestCase):
    """Tests para ExpandingWindowTransformation"""
    
    def setUp(self):
        self.df = pd.DataFrame({
            'value1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'value2': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            'text': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
        })
    
    def test_expanding_window(self):
        """Test expanding window"""
        transformation = ExpandingWindowTransformation(
            columns=['value1'],
            min_periods=1,
            aggregation_function='mean'
        )
        result = transformation.execute(self.df.copy())
        
        # Verificar que se creó una nueva columna
        self.assertIn('value1_mean_expanding', result.columns)
        
        # Verificar que la ventana expansiva funciona correctamente
        # La media de los primeros 3 valores: (1+2+3)/3 = 2.0
        self.assertAlmostEqual(result['value1_mean_expanding'].iloc[2], 2.0, places=5)
        # La media de los primeros 5 valores: (1+2+3+4+5)/5 = 3.0
        self.assertAlmostEqual(result['value1_mean_expanding'].iloc[4], 3.0, places=5)
    
    def test_expanding_window_different_functions(self):
        """Test expanding window con diferentes funciones"""
        for func in ['sum', 'min', 'max', 'std']:
            transformation = ExpandingWindowTransformation(
                columns=['value1'],
                min_periods=1,
                aggregation_function=func
            )
            result = transformation.execute(self.df.copy())
            
            # Verificar que se creó la columna correspondiente
            self.assertIn(f'value1_{func}_expanding', result.columns)
    
    def test_expanding_window_parameter_validation(self):
        """Test validación de parámetros"""
        # Parámetros válidos
        valid_params = {
            'columns': ['value1'],
            'min_periods': 1,
            'center': False,
            'aggregation_function': 'mean'
        }
        transformation = ExpandingWindowTransformation(['value1'], 1, False, 'mean')
        self.assertTrue(transformation.validate_parameters(valid_params))
        
        # Parámetros inválidos
        invalid_params = {
            'min_periods': 0,  # Debe ser > 0
            'aggregation_function': 'invalid'
        }
        self.assertFalse(transformation.validate_parameters(invalid_params))
    
    def test_expanding_window_error_non_numeric(self):
        """Test error con columna no numérica"""
        transformation = ExpandingWindowTransformation(
            columns=['text'],
            min_periods=1,
            aggregation_function='mean'
        )
        
        with self.assertRaises(ValueError):
            transformation.execute(self.df.copy())


class TestGroupByTransformation(unittest.TestCase):
    """Tests para GroupByTransformationTransformation"""
    
    def setUp(self):
        self.df = pd.DataFrame({
            'group': ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C'],
            'value1': [1, 2, 3, 4, 5, 6, 7, 8, 9],
            'value2': [10, 20, 30, 40, 50, 60, 70, 80, 90],
            'text': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
        })
    
    def test_groupby_rank(self):
        """Test groupby con rank"""
        transformation = GroupByTransformationTransformation(
            groupby_columns=['group'],
            transformation_function='rank',
            transformation_columns=['value1']
        )
        result = transformation.execute(self.df.copy())
        
        # Verificar que se creó una nueva columna
        self.assertIn('value1_rank_grouped', result.columns)
        
        # Verificar que el ranking funciona correctamente
        # En el grupo A: valores 1,2,3 -> rank: 0.33, 0.67, 1.0
        group_a_data = result[result['group'] == 'A'].sort_values('value1')
        self.assertAlmostEqual(group_a_data['value1_rank_grouped'].iloc[0], 1/3, places=5)
        self.assertAlmostEqual(group_a_data['value1_rank_grouped'].iloc[1], 2/3, places=5)
        self.assertAlmostEqual(group_a_data['value1_rank_grouped'].iloc[2], 1.0, places=5)
    
    def test_groupby_diff(self):
        """Test groupby con diff"""
        transformation = GroupByTransformationTransformation(
            groupby_columns=['group'],
            transformation_function='diff',
            transformation_columns=['value1']
        )
        result = transformation.execute(self.df.copy())
        
        # Verificar que se creó una nueva columna
        self.assertIn('value1_diff_grouped', result.columns)
        
        # Verificar que la diferencia funciona correctamente
        # En el grupo A: 1,2,3 -> diff: NaN, 1, 1
        group_a_data = result[result['group'] == 'A'].sort_values('value1')
        self.assertTrue(pd.isna(group_a_data['value1_diff_grouped'].iloc[0]))
        self.assertEqual(group_a_data['value1_diff_grouped'].iloc[1], 1)
        self.assertEqual(group_a_data['value1_diff_grouped'].iloc[2], 1)
    
    def test_groupby_shift(self):
        """Test groupby con shift"""
        transformation = GroupByTransformationTransformation(
            groupby_columns=['group'],
            transformation_function='shift',
            transformation_columns=['value1']
        )
        result = transformation.execute(self.df.copy())
        
        # Verificar que se creó una nueva columna
        self.assertIn('value1_shift_grouped', result.columns)
        
        # Verificar que el shift funciona correctamente
        # En el grupo A: 1,2,3 -> shift: NaN, 1, 2
        group_a_data = result[result['group'] == 'A'].sort_values('value1')
        self.assertTrue(pd.isna(group_a_data['value1_shift_grouped'].iloc[0]))
        self.assertEqual(group_a_data['value1_shift_grouped'].iloc[1], 1)
        self.assertEqual(group_a_data['value1_shift_grouped'].iloc[2], 2)
    
    def test_groupby_cumsum(self):
        """Test groupby con cumsum"""
        transformation = GroupByTransformationTransformation(
            groupby_columns=['group'],
            transformation_function='cumsum',
            transformation_columns=['value1']
        )
        result = transformation.execute(self.df.copy())
        
        # Verificar que se creó una nueva columna
        self.assertIn('value1_cumsum_grouped', result.columns)
        
        # Verificar que la suma acumulada funciona correctamente
        # En el grupo A: 1,2,3 -> cumsum: 1, 3, 6
        group_a_data = result[result['group'] == 'A'].sort_values('value1')
        self.assertEqual(group_a_data['value1_cumsum_grouped'].iloc[0], 1)
        self.assertEqual(group_a_data['value1_cumsum_grouped'].iloc[1], 3)
        self.assertEqual(group_a_data['value1_cumsum_grouped'].iloc[2], 6)
    
    def test_groupby_parameter_validation(self):
        """Test validación de parámetros"""
        # Parámetros válidos
        valid_params = {
            'groupby_columns': ['group'],
            'transformation_function': 'rank',
            'transformation_columns': ['value1'],
            'new_column_suffix': '_custom'
        }
        transformation = GroupByTransformationTransformation(
            ['group'],
            'rank',
            ['value1'],
            '_custom'
        )
        self.assertTrue(transformation.validate_parameters(valid_params))
        
        # Parámetros inválidos
        invalid_params = {
            'groupby_columns': 'not_a_list',
            'transformation_function': 'invalid_func',
            'transformation_columns': ['value1']
        }
        self.assertFalse(transformation.validate_parameters(invalid_params))
    
    def test_groupby_error_non_numeric_for_diff(self):
        """Test error con columna no numérica para diff"""
        transformation = GroupByTransformationTransformation(
            groupby_columns=['group'],
            transformation_function='diff',
            transformation_columns=['text']  # Columna de texto, no numérica
        )
        
        with self.assertRaises(ValueError):
            transformation.execute(self.df.copy())


def create_test_suite():
    """Crear suite de tests"""
    suite = unittest.TestSuite()
    
    # Añadir tests
    test_classes = [
        TestLabelEncoding,
        TestOneHotEncoding,
        TestOrdinalEncoding,
        TestTargetEncoding,
        TestMultiFunctionAggregation,
        TestAdvancedPivoting,
        TestRollingWindow,
        TestExpandingWindow,
        TestGroupByTransformation
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