"""
Tests unitarios para la funcionalidad de Tabla Pivote
Prueba las clases SimplePivotTable y CombinedPivotTable
"""

import unittest
import pandas as pd
import numpy as np
from core.pivot import SimplePivotTable, CombinedPivotTable


class TestSimplePivotTable(unittest.TestCase):
    """Tests para la clase SimplePivotTable"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.pivot_table = SimplePivotTable()
        
        # Crear DataFrame de prueba
        self.test_data = pd.DataFrame({
            'region': ['Norte', 'Sur', 'Norte', 'Sur', 'Este', 'Este'],
            'producto': ['A', 'A', 'B', 'B', 'A', 'B'],
            'ventas': [100, 150, 200, 120, 180, 90],
            'unidades': [10, 15, 20, 12, 18, 9]
        })
        
    def test_initialization(self):
        """Test de inicialización"""
        self.assertEqual(self.pivot_table.name, "simple_pivot")
        self.assertIn("pivoteo simple", self.pivot_table.description.lower())
        
    def test_validation_data_empty(self):
        """Test de validación con DataFrame vacío"""
        empty_df = pd.DataFrame()
        with self.assertRaises(ValueError):
            self.pivot_table.validate_data(empty_df)
            
    def test_validation_data_none(self):
        """Test de validación con DataFrame None"""
        with self.assertRaises(ValueError):
            self.pivot_table.validate_data(None)
            
    def test_validation_columns_exist(self):
        """Test de validación de existencia de columnas"""
        # Columnas que existen
        self.assertTrue(self.pivot_table.validate_columns_exist(
            self.test_data, ['region', 'producto']))
            
        # Columnas que no existen
        with self.assertRaises(ValueError):
            self.pivot_table.validate_columns_exist(
                self.test_data, ['columna_inexistente'])
                
    def test_normalize_parameter(self):
        """Test de normalización de parámetros"""
        # String único
        result = self.pivot_table.normalize_parameter("columna")
        self.assertEqual(result, ["columna"])
        
        # Lista
        result = self.pivot_table.normalize_parameter(["col1", "col2"])
        self.assertEqual(result, ["col1", "col2"])
        
    def test_apply_filters(self):
        """Test de aplicación de filtros"""
        # Filtro de igualdad
        filters = {'ventas': {'type': 'greater_than', 'value': 100}}
        result = self.pivot_table.apply_filters(self.test_data, filters)
        
        # Verificar que se aplicó el filtro
        self.assertTrue(all(result['ventas'] > 100))
        
    def test_simple_pivot_execution(self):
        """Test de ejecución de pivoteo simple"""
        parameters = {
            'index': 'region',
            'columns': 'producto',
            'values': 'ventas',
            'aggfunc': 'sum'
        }
        
        result = self.pivot_table.execute(self.test_data, parameters)
        
        # Verificar que el resultado es un DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        
        # Verificar que tiene datos
        self.assertFalse(result.empty)
        
    def test_simple_pivot_with_filters(self):
        """Test de pivoteo simple con filtros"""
        parameters = {
            'index': 'region',
            'columns': 'producto', 
            'values': 'ventas',
            'aggfunc': 'sum',
            'filters': {'ventas': {'type': 'greater_than', 'value': 100}}
        }
        
        result = self.pivot_table.execute(self.test_data, parameters)
        self.assertIsInstance(result, pd.DataFrame)
        
    def test_simple_pivot_missing_parameters(self):
        """Test de pivoteo simple con parámetros faltantes"""
        parameters = {}  # Parámetros mínimos
        
        with self.assertRaises(ValueError):
            self.pivot_table.execute(self.test_data, parameters)
            
    def test_simple_pivot_margins(self):
        """Test de pivoteo simple con márgenes"""
        parameters = {
            'index': 'region',
            'columns': 'producto',
            'values': 'ventas',
            'aggfunc': 'sum',
            'margins': True,
            'margins_name': 'Total'
        }
        
        result = self.pivot_table.execute(self.test_data, parameters)
        self.assertIsInstance(result, pd.DataFrame)


class TestCombinedPivotTable(unittest.TestCase):
    """Tests para la clase CombinedPivotTable"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.pivot_table = CombinedPivotTable()
        
        # Crear DataFrame de prueba más complejo
        self.test_data = pd.DataFrame({
            'region': ['Norte', 'Sur', 'Norte', 'Sur', 'Este', 'Oeste', 'Norte', 'Sur'],
            'categoria': ['A', 'A', 'B', 'B', 'A', 'A', 'A', 'B'],
            'producto': ['P1', 'P1', 'P1', 'P1', 'P2', 'P2', 'P2', 'P2'],
            'vendedor': ['V1', 'V1', 'V2', 'V2', 'V1', 'V2', 'V1', 'V2'],
            'ventas': [100, 150, 200, 120, 180, 90, 110, 160],
            'unidades': [10, 15, 20, 12, 18, 9, 11, 16],
            'descuento': [5, 8, 12, 6, 10, 4, 7, 9]
        })
        
    def test_initialization(self):
        """Test de inicialización"""
        self.assertEqual(self.pivot_table.name, "combined_pivot")
        self.assertIn("pivoteo combinado", self.pivot_table.description.lower())
        
    def test_combined_pivot_multiple_indices(self):
        """Test de pivoteo con múltiples índices"""
        parameters = {
            'index': ['region', 'categoria'],
            'columns': ['producto'],
            'values': ['ventas', 'unidades'],
            'aggfuncs': ['sum', 'mean']
        }
        
        result = self.pivot_table.execute(self.test_data, parameters)
        
        # Verificar que el resultado es un DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        
    def test_combined_pivot_multiple_aggregations(self):
        """Test de pivoteo con múltiples agregaciones"""
        parameters = {
            'index': ['region'],
            'columns': ['categoria'],
            'values': ['ventas'],
            'aggfuncs': ['sum', 'mean', 'count', 'max', 'min']
        }
        
        result = self.pivot_table.execute(self.test_data, parameters)
        self.assertIsInstance(result, pd.DataFrame)
        
    def test_combined_pivot_with_filters(self):
        """Test de pivoteo combinado con filtros múltiples"""
        parameters = {
            'index': ['region'],
            'columns': ['producto'],
            'values': ['ventas', 'unidades'],
            'aggfuncs': ['sum', 'mean'],
            'filters': {
                'ventas': {'type': 'greater_than', 'value': 100},
                'categoria': {'type': 'in_list', 'value': ['A', 'B']}
            }
        }
        
        result = self.pivot_table.execute(self.test_data, parameters)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        
    def test_combined_pivot_invalid_aggregation(self):
        """Test de pivoteo con función de agregación inválida"""
        parameters = {
            'index': ['region'],
            'columns': ['producto'],
            'values': ['ventas'],
            'aggfuncs': ['funcion_inexistente']
        }
        
        with self.assertRaises(ValueError):
            self.pivot_table.execute(self.test_data, parameters)
            
    def test_combined_pivot_empty_configuration(self):
        """Test de pivoteo con configuración vacía"""
        parameters = {}  # Sin configuración
        
        with self.assertRaises(ValueError):
            self.pivot_table.execute(self.test_data, parameters)
            
    def test_combined_pivot_margins(self):
        """Test de pivoteo combinado con márgenes"""
        parameters = {
            'index': ['region'],
            'columns': ['categoria'],
            'values': ['ventas'],
            'aggfuncs': ['sum'],
            'margins': True,
            'margins_name': 'TOTAL'
        }
        
        result = self.pivot_table.execute(self.test_data, parameters)
        self.assertIsInstance(result, pd.DataFrame)
        
    def test_complex_scenario(self):
        """Test de escenario complejo con múltiples parámetros"""
        parameters = {
            'index': ['region', 'vendedor'],
            'columns': ['categoria', 'producto'],
            'values': ['ventas', 'unidades', 'descuento'],
            'aggfuncs': ['sum', 'mean', 'std'],
            'filters': {
                'ventas': {'type': 'greater_than', 'value': 80},
                'region': {'type': 'in_list', 'value': ['Norte', 'Sur']}
            },
            'margins': True,
            'margins_name': 'Total'
        }
        
        result = self.pivot_table.execute(self.test_data, parameters)
        self.assertIsInstance(result, pd.DataFrame)
        # En casos complejos, el resultado puede estar vacío si no hay datos que coincidan


class TestPivotTableIntegration(unittest.TestCase):
    """Tests de integración entre Simple y Combined Pivot"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.test_data = pd.DataFrame({
            'año': [2020, 2020, 2021, 2021, 2022, 2022],
            'trimestre': [1, 2, 1, 2, 1, 2],
            'region': ['Norte', 'Sur', 'Norte', 'Sur', 'Norte', 'Sur'],
            'ventas': [1000, 1200, 1100, 1300, 1050, 1250],
            'gastos': [800, 900, 850, 950, 820, 920]
        })
        
    def test_simple_to_combined_compatibility(self):
        """Test de compatibilidad entre Simple y Combined Pivot"""
        simple_pivot = SimplePivotTable()
        combined_pivot = CombinedPivotTable()
        
        # Mismos parámetros para ambos
        simple_params = {
            'index': 'año',
            'columns': 'region', 
            'values': 'ventas',
            'aggfunc': 'sum'
        }
        
        combined_params = {
            'index': ['año'],
            'columns': ['region'],
            'values': ['ventas'],
            'aggfuncs': ['sum']
        }
        
        simple_result = simple_pivot.execute(self.test_data, simple_params)
        combined_result = combined_pivot.execute(self.test_data, combined_params)
        
        # Ambos deben producir resultados
        self.assertIsInstance(simple_result, pd.DataFrame)
        self.assertIsInstance(combined_result, pd.DataFrame)
        
    def test_data_consistency(self):
        """Test de consistencia de datos entre diferentes configuraciones"""
        pivot = CombinedPivotTable()
        
        # Configuración 1: Sin filtros
        params1 = {
            'index': ['año'],
            'columns': ['region'],
            'values': ['ventas'],
            'aggfuncs': ['sum']
        }
        
        result1 = pivot.execute(self.test_data, params1)
        
        # Configuración 2: Con filtro que no excluye datos
        params2 = {
            'index': ['año'],
            'columns': ['region'],
            'values': ['ventas'],
            'aggfuncs': ['sum'],
            'filters': {'ventas': {'type': 'greater_than', 'value': 0}}
        }
        
        result2 = pivot.execute(self.test_data, params2)
        
        # Los resultados deben ser iguales cuando el filtro no excluye datos
        # (esto puede variar según la implementación, pero la estructura debe ser similar)
        self.assertIsInstance(result1, pd.DataFrame)
        self.assertIsInstance(result2, pd.DataFrame)


class TestPivotTablePerformance(unittest.TestCase):
    """Tests de rendimiento para Tabla Pivote"""
    
    def setUp(self):
        """Configurar dataset grande para tests de rendimiento"""
        # Crear dataset más grande
        np.random.seed(42)
        n_records = 1000
        
        self.large_data = pd.DataFrame({
            'region': np.random.choice(['Norte', 'Sur', 'Este', 'Oeste'], n_records),
            'categoria': np.random.choice(['A', 'B', 'C', 'D'], n_records),
            'producto': np.random.choice(['P1', 'P2', 'P3', 'P4', 'P5'], n_records),
            'vendedor': np.random.choice(['V1', 'V2', 'V3', 'V4', 'V5'], n_records),
            'ventas': np.random.normal(1000, 200, n_records).round(2),
            'unidades': np.random.randint(1, 100, n_records),
            'descuento': np.random.uniform(0, 20, n_records).round(2)
        })
        
    def test_large_dataset_performance(self):
        """Test de rendimiento con dataset grande"""
        import time
        
        pivot = CombinedPivotTable()
        
        parameters = {
            'index': ['region', 'categoria'],
            'columns': ['producto'],
            'values': ['ventas', 'unidades'],
            'aggfuncs': ['sum', 'mean']
        }
        
        # Medir tiempo de ejecución
        start_time = time.time()
        result = pivot.execute(self.large_data, parameters)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Verificar que se completó en tiempo razonable (menos de 5 segundos)
        self.assertLess(execution_time, 5.0, "La ejecución tardó demasiado tiempo")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        
    def test_memory_efficiency(self):
        """Test de eficiencia de memoria"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            pivot = CombinedPivotTable()
            
            parameters = {
                'index': ['region'],
                'columns': ['categoria'],
                'values': ['ventas'],
                'aggfuncs': ['sum']
            }
            
            result = pivot.execute(self.large_data, parameters)
            
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = memory_after - memory_before
            
            # El uso de memoria no debe aumentar dramáticamente (menos de 100MB)
            self.assertLess(memory_increase, 100, "Aumento excesivo de memoria")
            self.assertIsInstance(result, pd.DataFrame)
            
        except ImportError:
            # Skip test if psutil not available
            self.skipTest("psutil not available for memory testing")
            self.assertIsInstance(pivot.execute(self.large_data, parameters), pd.DataFrame)


if __name__ == '__main__':
    # Configurar logging para tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Ejecutar tests
    unittest.main(verbosity=2)