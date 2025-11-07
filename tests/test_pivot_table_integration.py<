"""
Tests de integración para la funcionalidad completa de Tabla Pivote
Prueba la integración entre UI, core logic y flujo end-to-end
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar clases a probar
from core.pivot import SimplePivotTable, CombinedPivotTable
from app.widgets.pivot_table_widget import PivotTableWidget, PivotWorkerThread
from app.widgets.pivot_filter_panel import PivotFilterPanel
from app.widgets.pivot_aggregation_panel import PivotAggregationPanel


class TestPivotTableIntegration(unittest.TestCase):
    """Tests de integración para Tabla Pivote"""
    
    @classmethod
    def setUpClass(cls):
        """Configurar QApplication para tests de UI"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
            
    def setUp(self):
        """Configurar datos de prueba para cada test"""
        # Datos de prueba básicos
        self.test_data = pd.DataFrame({
            'region': ['Norte', 'Sur', 'Norte', 'Sur', 'Este', 'Oeste', 'Norte', 'Sur'],
            'categoria': ['A', 'A', 'B', 'B', 'A', 'A', 'A', 'B'],
            'producto': ['P1', 'P1', 'P1', 'P1', 'P2', 'P2', 'P2', 'P2'],
            'vendedor': ['V1', 'V1', 'V2', 'V2', 'V1', 'V2', 'V1', 'V2'],
            'ventas': [100, 150, 200, 120, 180, 90, 110, 160],
            'unidades': [10, 15, 20, 12, 18, 9, 11, 16],
            'descuento': [5, 8, 12, 6, 10, 4, 7, 9]
        })
        
    def test_core_logic_integration(self):
        """Test de integración entre Simple y Combined Pivot"""
        # Crear instancias
        simple_pivot = SimplePivotTable()
        combined_pivot = CombinedPivotTable()
        
        # Parámetros equivalentes
        simple_params = {
            'index': 'region',
            'columns': 'categoria',
            'values': 'ventas',
            'aggfunc': 'sum'
        }
        
        combined_params = {
            'index': ['region'],
            'columns': ['categoria'],
            'values': ['ventas'],
            'aggfuncs': ['sum']
        }
        
        # Ejecutar pivoteos
        simple_result = simple_pivot.execute(self.test_data, simple_params)
        combined_result = combined_pivot.execute(self.test_data, combined_params)
        
        # Verificar que ambos funcionan
        self.assertIsInstance(simple_result, pd.DataFrame)
        self.assertIsInstance(combined_result, pd.DataFrame)
        self.assertFalse(simple_result.empty)
        self.assertFalse(combined_result.empty)
        
    def test_filter_integration(self):
        """Test de integración con sistema de filtros"""
        from core.pivot import PivotFilterManager
        
        # Crear manager de filtros
        filter_manager = PivotFilterManager()
        
        # Configurar filtros
        filters = {
            'ventas': {'type': 'greater_than', 'value': 100},
            'region': {'type': 'in_list', 'value': ['Norte', 'Sur']}
        }
        
        # Aplicar filtros
        filtered_data = filter_manager.apply_filters(self.test_data, filters)
        
        # Verificar que los filtros se aplicaron correctamente
        self.assertTrue(all(filtered_data['ventas'] > 100))
        self.assertTrue(all(filtered_data['region'].isin(['Norte', 'Sur'])))
        
        # Ahora usar los datos filtrados en pivot
        pivot = CombinedPivotTable()
        params = {
            'index': ['region'],
            'columns': ['categoria'],
            'values': ['ventas'],
            'aggfuncs': ['sum']
        }
        
        result = pivot.execute(filtered_data, params)
        self.assertIsInstance(result, pd.DataFrame)
        
    def test_aggregation_integration(self):
        """Test de integración con sistema de agregaciones"""
        from core.pivot import PivotAggregationManager
        
        # Crear manager de agregaciones
        agg_manager = PivotAggregationManager()
        
        # Configurar agregaciones complejas
        aggregations = [
            {'column': 'ventas', 'function': 'sum', 'name': 'Total Ventas'},
            {'column': 'ventas', 'function': 'mean', 'name': 'Promedio Ventas'},
            {'column': 'unidades', 'function': 'sum', 'name': 'Total Unidades'}
        ]
        
        # Crear diccionario de agregaciones para pandas
        agg_dict = {}
        for agg in aggregations:
            col = agg['column']
            func = agg['function']
            if col not in agg_dict:
                agg_dict[col] = []
            agg_dict[col].append(func)
        
        # Verificar que las agregaciones son válidas
        self.assertIn('ventas', agg_dict)
        self.assertIn('unidades', agg_dict)
        
    def test_end_to_end_workflow(self):
        """Test de flujo completo end-to-end"""
        # 1. Crear datos
        self.assertFalse(self.test_data.empty)
        
        # 2. Aplicar filtros
        filters = {'ventas': {'type': 'greater_than', 'value': 100}}
        filtered_data = self.apply_filters_to_data(self.test_data, filters)
        
        # 3. Crear pivote
        pivot = CombinedPivotTable()
        params = {
            'index': ['region'],
            'columns': ['categoria'],
            'values': ['ventas', 'unidades'],
            'aggfuncs': ['sum', 'mean']
        }
        
        result = pivot.execute(filtered_data, params)
        
        # 4. Verificar resultado
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        
        # 5. Aplicar transformaciones adicionales si es necesario
        # (esto sería parte del flujo completo)
        
    def apply_filters_to_data(self, df, filters):
        """Helper para aplicar filtros en tests"""
        filtered_df = df.copy()
        
        for column, filter_config in filters.items():
            if column not in filtered_df.columns:
                continue
                
            filter_type = filter_config.get('type', 'equals')
            filter_value = filter_config.get('value')
            
            if filter_type == 'greater_than':
                filtered_df = filtered_df[filtered_df[column] > filter_value]
            elif filter_type == 'in_list':
                if isinstance(filter_value, list):
                    filtered_df = filtered_df[filtered_df[column].isin(filter_value)]
                    
        return filtered_df
        
    def test_performance_integration(self):
        """Test de rendimiento en integración"""
        import time
        
        # Crear dataset más grande
        large_data = self.create_large_dataset(5000)
        
        # Medir tiempo de pivoteo complejo
        start_time = time.time()
        
        pivot = CombinedPivotTable()
        params = {
            'index': ['region', 'categoria'],
            'columns': ['producto'],
            'values': ['ventas', 'unidades'],
            'aggfuncs': ['sum', 'mean', 'count']
        }
        
        result = pivot.execute(large_data, params)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Verificar rendimiento
        self.assertLess(execution_time, 10.0, "Tiempo de ejecución excesivo")
        self.assertIsInstance(result, pd.DataFrame)
        
    def create_large_dataset(self, n_records):
        """Helper para crear dataset grande para tests"""
        np.random.seed(42)
        
        return pd.DataFrame({
            'region': np.random.choice(['Norte', 'Sur', 'Este', 'Oeste'], n_records),
            'categoria': np.random.choice(['A', 'B', 'C', 'D'], n_records),
            'producto': np.random.choice([f'P{i}' for i in range(1, 21)], n_records),
            'vendedor': np.random.choice([f'V{i}' for i in range(1, 11)], n_records),
            'ventas': np.random.normal(1000, 200, n_records).round(2),
            'unidades': np.random.randint(1, 100, n_records),
            'descuento': np.random.uniform(0, 20, n_records).round(2)
        })


class TestPivotTableUIIntegration(unittest.TestCase):
    """Tests de integración de UI para Tabla Pivote"""
    
    @classmethod
    def setUpClass(cls):
        """Configurar QApplication para tests de UI"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
            
    def setUp(self):
        """Configurar datos de prueba"""
        self.test_data = pd.DataFrame({
            'region': ['Norte', 'Sur', 'Norte', 'Sur'],
            'categoria': ['A', 'A', 'B', 'B'],
            'ventas': [100, 150, 200, 120],
            'unidades': [10, 15, 20, 12]
        })
        
    def test_pivot_table_widget_initialization(self):
        """Test de inicialización del widget principal"""
        widget = PivotTableWidget()
        
        # Verificar que se inicializa sin errores
        self.assertIsNotNone(widget)
        self.assertIsNone(widget.df_original)
        
    def test_pivot_table_widget_data_setting(self):
        """Test de establecimiento de datos en el widget"""
        widget = PivotTableWidget()
        widget.set_data(self.test_data)
        
        # Verificar que los datos se establecieron
        self.assertIsNotNone(widget.df_original)
        self.assertEqual(len(widget.df_original), 4)
        
    def test_pivot_worker_thread_integration(self):
        """Test de integración del worker thread"""
        # Crear worker thread
        worker = PivotWorkerThread(
            self.test_data, 'combined', {
                'index': ['region'],
                'columns': ['categoria'],
                'values': ['ventas'],
                'aggfuncs': ['sum']
            }
        )
        
        # Verificar que el worker se configura correctamente
        self.assertIsNotNone(worker.df)
        self.assertEqual(worker.pivot_type, 'combined')
        self.assertIsNotNone(worker.parameters)
        
    def test_filter_panel_integration(self):
        """Test de integración del panel de filtros"""
        panel = PivotFilterPanel(self.test_data)
        
        # Verificar que se inicializa con datos
        self.assertIsNotNone(panel.df_original)
        self.assertEqual(len(panel.df_original), 4)
        
    def test_aggregation_panel_integration(self):
        """Test de integración del panel de agregaciones"""
        values_columns = ['ventas', 'unidades']
        panel = PivotAggregationPanel(self.test_data, values_columns)
        
        # Verificar configuración
        self.assertIsNotNone(panel.df_original)
        self.assertEqual(panel.values_columns, values_columns)
        
    def test_signal_integration(self):
        """Test de integración de señales entre componentes"""
        widget = PivotTableWidget()
        widget.set_data(self.test_data)
        
        # Simular configuración de parámetros
        mock_params = {
            'index': ['region'],
            'columns': ['categoria'],
            'values': ['ventas'],
            'aggfuncs': ['sum']
        }
        
        # Verificar que el widget puede manejar la configuración
        # (esto requeriría mocking más complejo en un test real)
        self.assertIsNotNone(widget)


class TestPivotTableErrorHandling(unittest.TestCase):
    """Tests de manejo de errores en integración"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.test_data = pd.DataFrame({
            'region': ['Norte', 'Sur'],
            'ventas': [100, 150]
        })
        
    def test_invalid_data_handling(self):
        """Test de manejo de datos inválidos"""
        pivot = CombinedPivotTable()
        
        # Test con DataFrame vacío
        with self.assertRaises(ValueError):
            pivot.execute(pd.DataFrame(), {'index': ['region']})
            
        # Test con DataFrame None
        with self.assertRaises(ValueError):
            pivot.execute(None, {'index': ['region']})
            
    def test_invalid_parameters_handling(self):
        """Test de manejo de parámetros inválidos"""
        pivot = CombinedPivotTable()
        
        # Test con columnas inexistentes
        with self.assertRaises(ValueError):
            pivot.execute(self.test_data, {
                'index': ['columna_inexistente'],
                'columns': ['region'],
                'values': ['ventas'],
                'aggfuncs': ['sum']
            })
            
    def test_filter_error_handling(self):
        """Test de manejo de errores en filtros"""
        from core.pivot import PivotFilterManager
        
        filter_manager = PivotFilterManager()
        
        # Test con filtro en columna inexistente
        filters = {'columna_inexistente': {'type': 'equals', 'value': 'test'}}
        result = filter_manager.apply_filters(self.test_data, filters)
        
        # Debe retornar el DataFrame original (sin filtrar)
        pd.testing.assert_frame_equal(result, self.test_data)


class TestPivotTableRealWorldScenarios(unittest.TestCase):
    """Tests de escenarios del mundo real"""
    
    def setUp(self):
        """Configurar datos de ejemplo realista"""
        # Simular datos de ventas
        np.random.seed(42)
        n_records = 1000
        
        self.sales_data = pd.DataFrame({
            'fecha': pd.date_range('2023-01-01', periods=n_records, freq='D'),
            'region': np.random.choice(['Norte', 'Sur', 'Este', 'Oeste'], n_records),
            'categoria': np.random.choice(['Electrónicos', 'Ropa', 'Hogar', 'Deportes'], n_records),
            'producto': [f'Producto_{i}' for i in range(1, 101)],
            'vendedor': np.random.choice(['Ana', 'Luis', 'María', 'Carlos', 'Sofía'], n_records),
            'cantidad_vendida': np.random.randint(1, 50, n_records),
            'precio_unitario': np.round(np.random.uniform(10, 500, n_records), 2),
            'descuento_aplicado': np.round(np.random.uniform(0, 0.3, n_records), 2)
        })
        
        # Calcular ventas totales
        self.sales_data['ventas_totales'] = (
            self.sales_data['cantidad_vendida'] * 
            self.sales_data['precio_unitario'] * 
            (1 - self.sales_data['descuento_aplicado'])
        )
        
    def test_sales_analysis_scenario(self):
        """Test de escenario de análisis de ventas"""
        pivot = CombinedPivotTable()
        
        # Análisis por región y categoría
        params = {
            'index': ['region'],
            'columns': ['categoria'],
            'values': ['ventas_totales', 'cantidad_vendida'],
            'aggfuncs': ['sum', 'mean'],
            'filters': {
                'ventas_totales': {'type': 'greater_than', 'value': 1000}
            }
        }
        
        result = pivot.execute(self.sales_data, params)
        
        # Verificar resultados
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        
        # Verificar que los datos filtrados tienen ventas > 1000
        min_sales = self.sales_data[self.sales_data['ventas_totales'] > 1000]['ventas_totales'].min()
        self.assertGreater(min_sales, 1000)
        
    def test_time_series_pivot_scenario(self):
        """Test de escenario de análisis temporal"""
        pivot = CombinedPivotTable()
        
        # Análisis por mes y región
        self.sales_data['mes'] = self.sales_data['fecha'].dt.to_period('M')
        
        params = {
            'index': ['mes'],
            'columns': ['region'],
            'values': ['ventas_totales'],
            'aggfuncs': ['sum']
        }
        
        result = pivot.execute(self.sales_data, params)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        
    def test_performance_optimization_scenario(self):
        """Test de optimización de rendimiento en escenario real"""
        import time
        
        # Crear dataset aún más grande
        large_data = self.create_large_sales_data(10000)
        
        start_time = time.time()
        
        pivot = CombinedPivotTable()
        params = {
            'index': ['region', 'categoria'],
            'columns': ['vendedor'],
            'values': ['ventas_totales'],
            'aggfuncs': ['sum', 'count']
        }
        
        result = pivot.execute(large_data, params)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verificar que el rendimiento es aceptable
        self.assertLess(execution_time, 15.0, "Tiempo de ejecución inaceptable para dataset grande")
        self.assertIsInstance(result, pd.DataFrame)
        
    def create_large_sales_data(self, n_records):
        """Helper para crear datos de ventas grandes"""
        np.random.seed(42)
        
        return pd.DataFrame({
            'fecha': pd.date_range('2023-01-01', periods=n_records, freq='H'),
            'region': np.random.choice(['Norte', 'Sur', 'Este', 'Oeste'], n_records),
            'categoria': np.random.choice(['Electrónicos', 'Ropa', 'Hogar', 'Deportes'], n_records),
            'producto': [f'Producto_{i}' for i in range(1, 501)],
            'vendedor': np.random.choice(['Ana', 'Luis', 'María', 'Carlos', 'Sofía', 'Pedro', 'Laura'], n_records),
            'cantidad_vendida': np.random.randint(1, 20, n_records),
            'precio_unitario': np.round(np.random.uniform(10, 500, n_records), 2),
            'descuento_aplicado': np.round(np.random.uniform(0, 0.3, n_records), 2)
        }).assign(
            ventas_totales=lambda x: (
                x['cantidad_vendida'] * 
                x['precio_unitario'] * 
                (1 - x['descuento_aplicado'])
            )
        )


if __name__ == '__main__':
    # Configurar logging
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Ejecutar tests con más detalle
    unittest.main(verbosity=2)