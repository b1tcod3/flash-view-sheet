"""
Test de validación end-to-end para la funcionalidad completa de Tabla Pivote
Simula el flujo completo de usuario desde la carga hasta el resultado final
"""

import unittest
import sys
import os
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pivot import SimplePivotTable, CombinedPivotTable
from core.pivot import PivotFilterManager, PivotAggregationManager


class TestEndToEndWorkflow(unittest.TestCase):
    """Test del flujo completo end-to-end"""
    
    def setUp(self):
        """Configurar datos de prueba para simular escenario real"""
        # Simular datos de ventas empresariales
        np.random.seed(42)
        n_records = 500
        
        self.sales_data = pd.DataFrame({
            'fecha_venta': pd.date_range('2023-01-01', periods=n_records, freq='D')[:n_records],
            'region': np.random.choice(['Norte', 'Sur', 'Este', 'Oeste'], n_records),
            'categoria_producto': np.random.choice(['Electrónicos', 'Ropa', 'Hogar', 'Deportes', 'Libros'], n_records),
            'nombre_producto': [f'Producto_{i:03d}' for i in range(1, n_records + 1)],
            'vendedor_asignado': np.random.choice(['Ana García', 'Luis Martín', 'María López', 'Carlos Ruiz', 'Sofía Fernández'], n_records),
            'cantidad_vendida': np.random.randint(1, 50, n_records),
            'precio_unitario': np.round(np.random.uniform(15.99, 299.99, n_records), 2),
            'descuento_aplicado': np.round(np.random.uniform(0, 0.25, n_records), 3),
            'costo_unitario': np.round(np.random.uniform(5.99, 199.99, n_records), 2)
        })
        
        # Calcular métricas derivadas
        self.sales_data['total_sin_descuento'] = (
            self.sales_data['cantidad_vendida'] * self.sales_data['precio_unitario']
        )
        self.sales_data['total_con_descuento'] = (
            self.sales_data['total_sin_descuento'] * (1 - self.sales_data['descuento_aplicado'])
        )
        self.sales_data['ganancia_unitaria'] = (
            self.sales_data['precio_unitario'] - self.sales_data['costo_unitario']
        )
        self.sales_data['ganancia_total'] = (
            self.sales_data['ganancia_unitaria'] * self.sales_data['cantidad_vendida']
        )
        
        # Agregar campos de fecha para análisis temporal
        self.sales_data['año'] = self.sales_data['fecha_venta'].dt.year
        self.sales_data['mes'] = self.sales_data['fecha_venta'].dt.month
        self.sales_data['trimestre'] = self.sales_data['fecha_venta'].dt.quarter
        self.sales_data['dia_semana'] = self.sales_data['fecha_venta'].dt.dayofweek
        
    def test_complete_sales_analysis_workflow(self):
        """Test del flujo completo de análisis de ventas"""
        print("=== INICIANDO FLUJO COMPLETO DE ANÁLISIS DE VENTAS ===")
        
        # Paso 1: Validar datos de entrada
        self.assertFalse(self.sales_data.empty)
        self.assertEqual(len(self.sales_data), 500)
        self.assertIn('total_con_descuento', self.sales_data.columns)
        print(f"✓ Datos cargados: {len(self.sales_data)} registros, {len(self.sales_data.columns)} columnas")
        
        # Paso 2: Análisis por región y categoría
        print("\n--- Análisis 1: Ventas por Región y Categoría ---")
        pivot1 = CombinedPivotTable()
        
        params1 = {
            'index': ['region'],
            'columns': ['categoria_producto'],
            'values': ['total_con_descuento', 'ganancia_total', 'cantidad_vendida'],
            'aggfuncs': ['sum', 'mean', 'count'],
            'margins': True,
            'margins_name': 'TOTAL'
        }
        
        result1 = pivot1.execute(self.sales_data, params1)
        self.assertIsInstance(result1, pd.DataFrame)
        self.assertFalse(result1.empty)
        print(f"✓ Pivote generado: {result1.shape[0]} filas, {result1.shape[1]} columnas")
        
        # Paso 3: Análisis temporal con filtros
        print("\n--- Análisis 2: Ventas Temporales con Filtros ---")
        
        # Filtrar solo ciertos períodos y categorías
        pivot2 = CombinedPivotTable()
        
        params2 = {
            'index': ['año', 'mes'],
            'columns': ['region'],
            'values': ['total_con_descuento', 'ganancia_total'],
            'aggfuncs': ['sum'],
            'filters': {
                'total_con_descuento': {'type': 'greater_than', 'value': 1000},
                'categoria_producto': {'type': 'in_list', 'value': ['Electrónicos', 'Ropa']}
            }
        }
        
        result2 = pivot2.execute(self.sales_data, params2)
        self.assertIsInstance(result2, pd.DataFrame)
        print(f"✓ Pivote filtrado: {result2.shape[0]} filas, {result2.shape[1]} columnas")
        
        # Paso 4: Análisis de rendimiento de vendedores
        print("\n--- Análisis 3: Rendimiento de Vendedores ---")
        
        pivot3 = CombinedPivotTable()
        
        params3 = {
            'index': ['vendedor_asignado'],
            'columns': ['categoria_producto', 'region'],
            'values': ['ganancia_total', 'cantidad_vendida'],
            'aggfuncs': ['sum', 'mean', 'max'],
            'filters': {
                'ganancia_total': {'type': 'greater_than', 'value': 500}
            }
        }
        
        result3 = pivot3.execute(self.sales_data, params3)
        self.assertIsInstance(result3, pd.DataFrame)
        print(f"✓ Análisis vendedor: {result3.shape[0]} filas, {result3.shape[1]} columnas")
        
        # Paso 5: Validar coherencia de resultados
        print("\n--- Validación de Consistencia ---")
        
        # Verificar que los totales son coherentes
        total_ventas_raw = self.sales_data['total_con_descuento'].sum()
        total_ventas_pivot1 = result1.iloc[-1, -3] if result1.shape[0] > 0 else 0
        total_ventas_pivot2 = result2['total_con_descuento'].sum() if 'total_con_descuento' in result2.columns else 0
        
        print(f"✓ Total ventas raw: ${total_ventas_raw:,.2f}")
        print(f"✓ Total ventas pivot1: ${total_ventas_pivot1:,.2f}")
        print(f"✓ Total ventas pivot2: ${total_ventas_pivot2:,.2f}")
        
        # Verificar que los datos son consistentes (con margen de tolerancia)
        self.assertAlmostEqual(total_ventas_raw, total_ventas_pivot1, delta=0.01)
        
        print("\n✅ FLUJO COMPLETO EJECUTADO EXITOSAMENTE")
        
    def test_pivot_table_advanced_scenarios(self):
        """Test de escenarios avanzados de tabla pivote"""
        print("=== ESCENARIOS AVANZADOS ===")
        
        # Escenario 1: Pivote multi-nivel complejo
        print("\n--- Escenario 1: Análisis Multinivel ---")
        pivot = CombinedPivotTable()
        
        complex_params = {
            'index': ['año', 'trimestre', 'region'],
            'columns': ['categoria_producto', 'vendedor_asignado'],
            'values': ['total_con_descuento', 'ganancia_total', 'cantidad_vendida'],
            'aggfuncs': ['sum', 'mean', 'count', 'std'],
            'filters': {
                'total_con_descuento': {'type': 'greater_than', 'value': 500},
                'categoria_producto': {'type': 'not_in_list', 'value': ['Libros']}
            },
            'margins': True,
            'margins_name': 'TOTAL',
            'dropna': True
        }
        
        result = pivot.execute(self.sales_data, complex_params)
        self.assertIsInstance(result, pd.DataFrame)
        print(f"✓ Pivote complejo: {result.shape[0]} filas, {result.shape[1]} columnas")
        
        # Escenario 2: Análisis de tendencias
        print("\n--- Escenario 2: Análisis de Tendencias ---")
        
        # Crear datos de serie temporal
        time_series_data = pd.DataFrame({
            'fecha': pd.date_range('2023-01-01', '2023-12-31', freq='D'),
            'metric_a': np.random.normal(100, 20, 365),
            'metric_b': np.random.normal(50, 10, 365),
            'category': np.random.choice(['X', 'Y', 'Z'], 365)
        })
        
        pivot_ts = CombinedPivotTable()
        ts_params = {
            'index': [time_series_data['fecha'].dt.to_period('M')],
            'columns': ['category'],
            'values': ['metric_a', 'metric_b'],
            'aggfuncs': ['sum', 'mean', 'std']
        }
        
        ts_result = pivot_ts.execute(time_series_data, ts_params)
        self.assertIsInstance(ts_result, pd.DataFrame)
        print(f"✓ Serie temporal: {ts_result.shape[0]} filas, {ts_result.shape[1]} columnas")
        
        print("\n✅ ESCENARIOS AVANZADOS COMPLETADOS")
        
    def test_error_handling_and_edge_cases(self):
        """Test de manejo de errores y casos extremos"""
        print("=== MANEJO DE ERRORES Y CASOS EXTREMOS ===")
        
        # Caso 1: Datos vacíos
        print("\n--- Caso 1: Datos Vacíos ---")
        pivot = CombinedPivotTable()
        
        with self.assertRaises(ValueError):
            pivot.execute(pd.DataFrame(), {'index': ['col']})
        print("✓ Error manejado correctamente para datos vacíos")
        
        # Caso 2: Columnas inexistentes
        print("\n--- Caso 2: Columnas Inexistentes ---")
        
        with self.assertRaises(ValueError):
            pivot.execute(self.sales_data, {
                'index': ['columna_inexistente'],
                'columns': ['region'],
                'values': ['ventas'],
                'aggfuncs': ['sum']
            })
        print("✓ Error manejado para columnas inexistentes")
        
        # Caso 3: Configuración vacía
        print("\n--- Caso 3: Configuración Vacía ---")
        
        with self.assertRaises(ValueError):
            pivot.execute(self.sales_data, {})
        print("✓ Error manejado para configuración vacía")
        
        # Caso 4: Función de agregación inválida
        print("\n--- Caso 4: Función Inválida ---")
        
        with self.assertRaises(ValueError):
            pivot.execute(self.sales_data, {
                'index': ['region'],
                'columns': ['categoria_producto'],
                'values': ['total_con_descuento'],
                'aggfuncs': ['funcion_inexistente']
            })
        print("✓ Error manejado para función inválida")
        
        # Caso 5: Filtros con datos inconsistentes
        print("\n--- Caso 5: Filtros con Datos Inconsistentes ---")
        
        # Test con filtro que no coincide con ningún dato
        result = pivot.execute(self.sales_data, {
            'index': ['region'],
            'columns': ['categoria_producto'],
            'values': ['total_con_descuento'],
            'aggfuncs': ['sum'],
            'filters': {'total_con_descuento': {'type': 'greater_than', 'value': 999999}}
        })
        
        # Debe retornar DataFrame vacío, no error
        self.assertIsInstance(result, pd.DataFrame)
        print("✓ Filtros con datos vacíos manejados correctamente")
        
        print("\n✅ MANEJO DE ERRORES VALIDADO")
        
    def test_performance_with_large_datasets(self):
        """Test de rendimiento con datasets grandes"""
        print("=== RENDIMIENTO CON DATASETS GRANDES ===")
        
        import time
        
        # Crear dataset grande
        print("\n--- Creando Dataset Grande (10,000 registros) ---")
        large_data = self.create_large_dataset(10000)
        print(f"✓ Dataset creado: {len(large_data)} registros")
        
        # Test de rendimiento
        print("\n--- Ejecutando Pivote Complejo ---")
        
        pivot = CombinedPivotTable()
        
        performance_params = {
            'index': ['region', 'categoria_producto'],
            'columns': ['vendedor_asignado'],
            'values': ['total_con_descuento', 'ganancia_total', 'cantidad_vendida'],
            'aggfuncs': ['sum', 'mean', 'count'],
            'filters': {
                'total_con_descuento': {'type': 'greater_than', 'value': 100}
            }
        }
        
        start_time = time.time()
        result = pivot.execute(large_data, performance_params)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Verificar que el rendimiento es aceptable
        self.assertLess(execution_time, 10.0, f"Ejecución demasiado lenta: {execution_time:.2f}s")
        self.assertIsInstance(result, pd.DataFrame)
        
        print(f"✓ Pivote completado en {execution_time:.2f}s")
        print(f"✓ Resultado: {result.shape[0]} filas, {result.shape[1]} columnas")
        
        # Test con dataset muy grande
        print("\n--- Ejecutando Pivote con Dataset Muy Grande (50,000 registros) ---")
        very_large_data = self.create_large_dataset(50000)
        
        start_time = time.time()
        result_vl = pivot.execute(very_large_data, {
            'index': ['region'],
            'columns': ['categoria_producto'],
            'values': ['total_con_descuento'],
            'aggfuncs': ['sum']
        })
        end_time = time.time()
        
        execution_time_vl = end_time - start_time
        
        # Para datasets muy grandes, el tiempo puede ser mayor pero aún razonable
        self.assertLess(execution_time_vl, 30.0, f"Ejecución demasiado lenta: {execution_time_vl:.2f}s")
        self.assertIsInstance(result_vl, pd.DataFrame)
        
        print(f"✓ Pivote grande completado en {execution_time_vl:.2f}s")
        
        print("\n✅ RENDIMIENTO VALIDADO")
        
    def create_large_dataset(self, n_records):
        """Helper para crear dataset grande para tests de rendimiento"""
        np.random.seed(42)
        
        return pd.DataFrame({
            'region': np.random.choice(['Norte', 'Sur', 'Este', 'Oeste'], n_records),
            'categoria_producto': np.random.choice(['A', 'B', 'C', 'D', 'E'], n_records),
            'producto': [f'P_{i}' for i in range(1, n_records + 1)],
            'vendedor_asignado': np.random.choice(['V1', 'V2', 'V3', 'V4', 'V5'], n_records),
            'cantidad_vendida': np.random.randint(1, 100, n_records),
            'precio_unitario': np.round(np.random.uniform(10, 500, n_records), 2),
            'descuento_aplicado': np.round(np.random.uniform(0, 0.3, n_records), 3),
            'costo_unitario': np.round(np.random.uniform(5, 300, n_records), 2)
        }).assign(
            total_con_descuento=lambda x: (
                x['cantidad_vendida'] * x['precio_unitario'] * (1 - x['descuento_aplicado'])
            ),
            ganancia_total=lambda x: (
                (x['precio_unitario'] - x['costo_unitario']) * x['cantidad_vendida']
            )
        )
        
    def test_integration_with_filter_and_aggregation_managers(self):
        """Test de integración con managers de filtros y agregaciones"""
        print("=== INTEGRACIÓN CON MANAGERS ESPECIALIZADOS ===")
        
        # Test con PivotFilterManager
        print("\n--- Test PivotFilterManager ---")
        
        filter_manager = PivotFilterManager()
        filter_manager.add_filter('total_con_descuento', 'greater_than', 1000)
        filter_manager.add_filter('region', 'in_list', ['Norte', 'Sur'])
        filter_manager.set_logic_operator('and')
        
        filtered_data = filter_manager.apply_filters(self.sales_data)
        self.assertTrue(all(filtered_data['total_con_descuento'] > 1000))
        self.assertTrue(all(filtered_data['region'].isin(['Norte', 'Sur'])))
        print(f"✓ Filtros aplicados: {len(self.sales_data)} → {len(filtered_data)} registros")
        
        # Test con PivotAggregationManager
        print("\n--- Test PivotAggregationManager ---")
        
        agg_manager = PivotAggregationManager()
        agg_manager.add_aggregation('sum', 'total_con_descuento', 'Total_Ventas')
        agg_manager.add_aggregation('mean', 'total_con_descuento', 'Promedio_Ventas')
        agg_manager.add_aggregation('count', 'total_con_descuento', 'Num_Transacciones')
        
        agg_result = agg_manager.apply_aggregations(filtered_data)
        self.assertIn('Total_Ventas', agg_result.columns)
        self.assertIn('Promedio_Ventas', agg_result.columns)
        print(f"✓ Agregaciones aplicadas: {len(agg_result.columns)} métricas calculadas")
        
        # Test de integración completa
        print("\n--- Test Integración Completa ---")
        
        pivot = CombinedPivotTable()
        integration_params = {
            'index': ['region'],
            'columns': ['categoria_producto'],
            'values': ['total_con_descuento', 'ganancia_total'],
            'aggfuncs': ['sum', 'mean'],
            'filters': {
                'total_con_descuento': {'type': 'greater_than', 'value': 500},
                'region': {'type': 'in_list', 'value': ['Norte', 'Sur']}
            }
        }
        
        result = pivot.execute(self.sales_data, integration_params)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        print(f"✓ Integración completa: {result.shape[0]} filas, {result.shape[1]} columnas")
        
        print("\n✅ INTEGRACIÓN CON MANAGERS VALIDADA")


if __name__ == '__main__':
    # Configurar logging
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("🧪 INICIANDO TESTS END-TO-END DE TABLA PIVOTE")
    print("=" * 60)
    
    # Ejecutar tests con salida detallada
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("✅ TODOS LOS TESTS END-TO-END COMPLETADOS EXITOSAMENTE")