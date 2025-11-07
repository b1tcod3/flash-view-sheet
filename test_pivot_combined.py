#!/usr/bin/env python3
"""
Test específico para Combined Pivot Table
Valida las funcionalidades de la Fase 3: selección múltiple y filtros avanzados
"""

import pandas as pd
import numpy as np
import unittest
import logging
import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar módulos pivot
from core.pivot import CombinedPivotTable, PivotFilterManager, PivotAggregationManager
from core.pivot.pivot_filters import PivotFilter
from core.pivot.pivot_aggregations import PivotAggregation

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_data() -> pd.DataFrame:
    """Crear datos de prueba para testing de combined pivot"""
    np.random.seed(42)
    
    # Crear dataset de ejemplo
    data = {
        'region': ['Norte', 'Sur', 'Este', 'Oeste', 'Norte', 'Sur', 'Este', 'Oeste'] * 12,
        'categoria': ['A', 'B', 'C'] * 32,
        'producto': ['Producto1', 'Producto2', 'Producto3', 'Producto4'] * 24,
        'vendedor': [f'Vendedor{i%8+1}' for i in range(96)],
        'ventas': np.random.normal(1000, 200, 96).round(2),
        'unidades': np.random.randint(10, 100, 96),
        'fecha': pd.date_range('2023-01-01', periods=96, freq='3D'),
        'descuento': np.random.uniform(0, 0.3, 96).round(2)
    }
    
    return pd.DataFrame(data)

class TestCombinedPivotTable(unittest.TestCase):
    """Test para Combined Pivot Table"""
    
    def setUp(self):
        """Configurar test"""
        self.df = create_test_data()
        self.pivot_table = CombinedPivotTable()
        logger.info(f"Dataset creado: {self.df.shape}")
        
    def test_basic_combined_pivot(self):
        """Test de pivoteo combinado básico"""
        logger.info("Test: Pivoteo combinado básico")
        
        parameters = {
            'index': ['region', 'categoria'],
            'columns': ['producto'],
            'values': ['ventas', 'unidades'],
            'aggfuncs': ['sum', 'mean']
        }
        
        try:
            result = self.pivot_table.execute(self.df, parameters)
            logger.info(f"Resultado shape: {result.shape}")
            logger.info(f"Columnas: {list(result.columns)}")
            
            # Validaciones básicas
            self.assertFalse(result.empty, "El resultado no debe estar vacío")
            self.assertGreater(result.shape[0], 0, "Debe tener al menos una fila")
            
            # Verificar que se crearon columnas para múltiples valores/funciones
            expected_patterns = ['ventas', 'unidades']
            for pattern in expected_patterns:
                matching_cols = [col for col in result.columns if pattern in str(col)]
                self.assertGreater(len(matching_cols), 0, f"Debe haber columnas con {pattern}")
                
        except Exception as e:
            logger.error(f"Error en test básico: {str(e)}")
            self.fail(f"Fallo en pivoteo básico: {str(e)}")
            
    def test_multiple_index_columns(self):
        """Test con múltiples índices y columnas"""
        logger.info("Test: Múltiples índices y columnas")
        
        parameters = {
            'index': ['region', 'categoria', 'vendedor'],
            'columns': ['producto'],
            'values': ['ventas'],
            'aggfuncs': ['sum', 'mean', 'count']
        }
        
        try:
            result = self.pivot_table.execute(self.df, parameters)
            logger.info(f"Resultado multi-índice shape: {result.shape}")
            
            self.assertFalse(result.empty)
            self.assertGreater(result.shape[0], 0)
            
            # Verificar que hay múltiples funciones de agregación
            agg_patterns = ['sum', 'mean', 'count']
            for pattern in agg_patterns:
                matching_cols = [col for col in result.columns if pattern in str(col)]
                self.assertGreater(len(matching_cols), 0, f"Debe haber columnas con función {pattern}")
                
        except Exception as e:
            logger.error(f"Error en test múltiples índices: {str(e)}")
            self.fail(f"Fallo en múltiples índices: {str(e)}")
            
    def test_advanced_filters(self):
        """Test con filtros avanzados"""
        logger.info("Test: Filtros avanzados")
        
        filters = {
            'ventas': {
                'type': 'greater_than',
                'value': 800,
                'operator': 'and'
            },
            'categoria': {
                'type': 'in_list',
                'value': ['A', 'B'],
                'operator': 'and'
            },
            'region': {
                'type': 'not_equals',
                'value': 'Oeste',
                'operator': 'and'
            }
        }
        
        parameters = {
            'index': ['region'],
            'columns': ['categoria'],
            'values': ['ventas'],
            'aggfuncs': ['sum'],
            'filters': filters
        }
        
        try:
            # Aplicar filtros directamente para verificar
            filter_manager = PivotFilterManager()
            filter_manager.add_filters_from_dict(filters)
            filtered_df = filter_manager.apply_filters(self.df)
            
            logger.info(f"DataFrame original: {self.df.shape}")
            logger.info(f"DataFrame filtrado: {filtered_df.shape}")
            
            result = self.pivot_table.execute(self.df, parameters)
            logger.info(f"Resultado con filtros shape: {result.shape}")
            
            self.assertFalse(result.empty)
            self.assertLessEqual(result.shape[0], self.df.shape[0], 
                               "El resultado filtrado debe tener menos o igual filas que el original")
            
        except Exception as e:
            logger.error(f"Error en test filtros: {str(e)}")
            self.fail(f"Fallo en filtros avanzados: {str(e)}")
            
    def test_complex_parameters(self):
        """Test con parámetros complejos"""
        logger.info("Test: Parámetros complejos")
        
        parameters = {
            'index': ['region', 'categoria'],
            'columns': ['producto', 'vendedor'],
            'values': ['ventas', 'unidades', 'descuento'],
            'aggfuncs': ['sum', 'mean', 'std'],
            'fill_value': 0,
            'dropna': False,
            'margins': True,
            'margins_name': 'Total'
        }
        
        try:
            result = self.pivot_table.execute(self.df, parameters)
            logger.info(f"Resultado complejo shape: {result.shape}")
            
            self.assertFalse(result.empty)
            
            # Verificar que se aplicaron parámetros
            self.assertIn('margins', self.pivot_table.pivot_params)
            self.assertTrue(self.pivot_table.pivot_params['margins'])
            
        except Exception as e:
            logger.error(f"Error en test complejo: {str(e)}")
            self.fail(f"Fallo en parámetros complejos: {str(e)}")
            
    def test_pivot_filter_manager_integration(self):
        """Test de integración con PivotFilterManager"""
        logger.info("Test: Integración PivotFilterManager")
        
        # Crear filtros usando el manager
        filter_manager = PivotFilterManager()
        filter_manager.add_filter('ventas', 'greater_than', 900)
        filter_manager.add_filter('categoria', 'equals', 'A', 'and')
        filter_manager.set_logic_operator('and')
        
        # Aplicar filtros
        filtered_df = filter_manager.apply_filters(self.df)
        
        logger.info(f"Filtros aplicados: {filter_manager.get_filter_summary()}")
        logger.info(f"Filas originales: {len(self.df)}, filtradas: {len(filtered_df)}")
        
        # Verificar que se aplicaron los filtros
        self.assertLessEqual(len(filtered_df), len(self.df))
        
        # Verificar que la columna de ventas cumple el filtro
        if not filtered_df.empty:
            self.assertTrue((filtered_df['ventas'] > 900).all())
            self.assertTrue((filtered_df['categoria'] == 'A').all())
            
    def test_pivot_aggregation_manager_integration(self):
        """Test de integración con PivotAggregationManager"""
        logger.info("Test: Integración PivotAggregationManager")
        
        # Crear agregaciones usando el manager
        agg_manager = PivotAggregationManager()
        agg_manager.add_aggregation('sum', 'ventas', 'total_ventas')
        agg_manager.add_aggregation('mean', 'ventas', 'promedio_ventas')
        agg_manager.add_aggregation('count', 'unidades', 'conteo_unidades')
        
        # Aplicar agregaciones a un grupo de datos
        sample_data = self.df.groupby(['region', 'categoria'])['ventas'].apply(list)
        
        for name, group_data in sample_data.items():
            result = agg_manager.apply_aggregations(pd.DataFrame({'ventas': group_data, 'unidades': group_data}))
            logger.info(f"Agrregaciones para {name}: {list(result.columns)}")
            
        summary = agg_manager.get_aggregation_summary()
        logger.info(f"Resumen agregaciones: {summary}")
        
        self.assertEqual(summary['total_aggregations'], 3)
        
    def test_error_handling(self):
        """Test de manejo de errores"""
        logger.info("Test: Manejo de errores")
        
        # Test con parámetros inválidos
        with self.assertRaises(ValueError):
            self.pivot_table.execute(self.df, {
                'index': [],
                'columns': [],
                'values': [],
                'aggfuncs': []
            })
            
        # Test con columna inexistente
        with self.assertRaises(ValueError):
            self.pivot_table.execute(self.df, {
                'index': ['columna_inexistente'],
                'columns': ['region'],
                'values': ['ventas'],
                'aggfuncs': ['sum']
            })
            
        # Test con función de agregación inválida
        with self.assertRaises(ValueError):
            self.pivot_table.execute(self.df, {
                'index': ['region'],
                'columns': ['categoria'],
                'values': ['ventas'],
                'aggfuncs': ['funcion_invalida']
            })
            
    def test_performance_with_large_data(self):
        """Test de rendimiento con datos grandes"""
        logger.info("Test: Rendimiento con datos grandes")
        
        # Crear dataset más grande
        large_data = {
            'region': np.random.choice(['Norte', 'Sur', 'Este', 'Oeste'], 1000),
            'categoria': np.random.choice(['A', 'B', 'C', 'D'], 1000),
            'producto': np.random.choice([f'Producto{i}' for i in range(20)], 1000),
            'ventas': np.random.normal(1000, 300, 1000)
        }
        large_df = pd.DataFrame(large_data)
        
        parameters = {
            'index': ['region', 'categoria'],
            'columns': ['producto'],
            'values': ['ventas'],
            'aggfuncs': ['sum', 'mean']
        }
        
        import time
        start_time = time.time()
        
        try:
            result = self.pivot_table.execute(large_df, parameters)
            end_time = time.time()
            
            execution_time = end_time - start_time
            logger.info(f"Tiempo de ejecución: {execution_time:.3f}s")
            logger.info(f"Resultado shape: {result.shape}")
            
            # El tiempo de ejecución debe ser razonable (menos de 10 segundos)
            self.assertLess(execution_time, 10.0, "La ejecución tomó demasiado tiempo")
            
        except Exception as e:
            logger.error(f"Error en test de rendimiento: {str(e)}")
            self.fail(f"Fallo en test de rendimiento: {str(e)}")

def run_comprehensive_tests():
    """Ejecutar todos los tests de manera comprehensiva"""
    logger.info("=== INICIANDO TESTS DE COMBINED PIVOT TABLE ===")
    
    # Ejecutar tests unitarios
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCombinedPivotTable)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen final
    logger.info("=== RESUMEN DE TESTS ===")
    logger.info(f"Tests ejecutados: {result.testsRun}")
    logger.info(f"Errores: {len(result.errors)}")
    logger.info(f"Fallos: {len(result.failures)}")
    
    if result.errors:
        logger.error("ERRORES:")
        for test, error in result.errors:
            logger.error(f"  {test}: {error}")
            
    if result.failures:
        logger.error("FALLOS:")
        for test, failure in result.failures:
            logger.error(f"  {test}: {failure}")
    
    success = len(result.errors) == 0 and len(result.failures) == 0
    logger.info(f"RESULTADO: {'ÉXITO' if success else 'FALLO'}")
    
    return success

if __name__ == '__main__':
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)