"""
Testing de Integración - Tabla Pivote
Prueba la integración completa del sistema de Tabla Pivote con la aplicación principal
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch
import pandas as pd

# Agregar ruta del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Imports del sistema
try:
    from core.pivot import SimplePivotTable, CombinedPivotTable, PivotFilterManager
    from app.widgets.pivot_table_widget import PivotTableWidget, PivotWorkerThread
    from app.widgets.pivot_filter_panel import PivotFilterPanel
    from app.widgets.pivot_aggregation_panel import PivotAggregationPanel
    from app.widgets.pivot_config_dialog import PivotConfigDialog
    from main import MainWindow
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"Error de importación: {e}")
    IMPORTS_SUCCESSFUL = False


class TestPivotIntegration(unittest.TestCase):
    """Clase principal de testing de integración"""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para todos los tests"""
        if not IMPORTS_SUCCESSFUL:
            cls.skipTest(cls, "Imports fallidos")
        
        # Crear datos de prueba
        cls.test_data = pd.DataFrame({
            'region': ['Norte', 'Sur', 'Norte', 'Sur', 'Este', 'Oeste'] * 5,
            'categoria': ['A', 'B', 'A', 'B', 'A', 'B'] * 5,
            'producto': ['X', 'Y', 'Z', 'X', 'Y', 'Z'] * 5,
            'ventas': [100, 200, 150, 300, 250, 180] * 5,
            'unidades': [10, 20, 15, 30, 25, 18] * 5,
            'vendedor': ['Juan', 'Maria', 'Carlos', 'Ana', 'Luis', 'Carmen'] * 5
        })
    
    def test_01_core_pivot_functionality(self):
        """Test 1: Verificar funcionalidad core de pivoteo"""
        print("🧪 Test 1: Funcionalidad Core de Pivoteo")
        
        # Test Simple Pivot
        simple_pivot = SimplePivotTable()
        result = simple_pivot.execute(self.test_data, {
            'index': 'region',
            'columns': 'categoria',
            'values': 'ventas',
            'aggfunc': 'sum'
        })
        
        self.assertIsNotNone(result)
        self.assertFalse(result.empty)
        self.assertGreater(len(result), 0)
        print("   ✅ Simple Pivot - OK")
        
        # Test Combined Pivot
        combined_pivot = CombinedPivotTable()
        result = combined_pivot.execute(self.test_data, {
            'index': ['region', 'categoria'],
            'columns': 'producto',
            'values': ['ventas', 'unidades'],
            'aggfuncs': ['sum', 'mean']
        })
        
        self.assertIsNotNone(result)
        self.assertFalse(result.empty)
        print("   ✅ Combined Pivot - OK")
    
    def test_02_filter_manager_functionality(self):
        """Test 2: Verificar funcionalidad del gestor de filtros"""
        print("🧪 Test 2: Gestor de Filtros")
        
        filter_manager = PivotFilterManager()
        
        # Test filtros simples
        filters = {
            'region': {'type': 'equals', 'value': 'Norte'},
            'ventas': {'type': 'greater_than', 'value': 150}
        }
        
        filtered_df = filter_manager.apply_filters(self.test_data, filters)
        
        self.assertIsNotNone(filtered_df)
        # La región debe ser solo Norte y ventas > 150
        self.assertTrue(all(filtered_df['region'] == 'Norte'))
        self.assertTrue(all(filtered_df['ventas'] > 150))
        print("   ✅ Filtros - OK")
    
    def test_03_widget_creation(self):
        """Test 3: Verificar creación de widgets"""
        print("🧪 Test 3: Creación de Widgets")
        
        try:
            # Test PivotTableWidget
            pivot_widget = PivotTableWidget()
            self.assertIsNotNone(pivot_widget)
            print("   ✅ PivotTableWidget - OK")
            
            # Test FilterPanel
            filter_panel = PivotFilterPanel(self.test_data)
            self.assertIsNotNone(filter_panel)
            filter_panel.set_data(self.test_data)
            print("   ✅ PivotFilterPanel - OK")
            
            # Test AggregationPanel
            agg_panel = PivotAggregationPanel(self.test_data, ['ventas', 'unidades'])
            self.assertIsNotNone(agg_panel)
            agg_panel.set_data(self.test_data, ['ventas', 'unidades'])
            print("   ✅ PivotAggregationPanel - OK")
            
            # Test ConfigDialog
            config_dialog = PivotConfigDialog(self.test_data)
            self.assertIsNotNone(config_dialog)
            config_dialog.set_data(self.test_data)
            print("   ✅ PivotConfigDialog - OK")
            
        except Exception as e:
            self.fail(f"Error creando widgets: {e}")
    
    def test_04_widget_integration(self):
        """Test 4: Verificar integración entre widgets"""
        print("🧪 Test 4: Integración de Widgets")
        
        try:
            # Crear widgets
            pivot_widget = PivotTableWidget()
            pivot_widget.set_data(self.test_data)
            
            # Verificar que los datos se establecen correctamente
            self.assertIsNotNone(pivot_widget.df_original)
            self.assertEqual(len(pivot_widget.df_original), len(self.test_data))
            
            # Simular configuración
            params = {
                'index': ['region'],
                'columns': ['categoria'],
                'values': ['ventas'],
                'aggfuncs': ['sum']
            }
            
            # Verificar que la validación funciona
            errors = pivot_widget.validate_parameters(params)
            self.assertEqual(len(errors), 0, f"Errores de validación: {errors}")
            
            print("   ✅ Integración de Widgets - OK")
            
        except Exception as e:
            self.fail(f"Error en integración de widgets: {e}")
    
    def test_05_worker_thread_functionality(self):
        """Test 5: Verificar funcionalidad del worker thread"""
        print("🧪 Test 5: Worker Thread")
        
        try:
            # Crear worker thread
            worker = PivotWorkerThread(
                self.test_data, 
                'simple', 
                {
                    'index': ['region'],
                    'columns': ['categoria'],
                    'values': ['ventas'],
                    'aggfunc': 'sum'
                }
            )
            
            # Verificar configuración inicial
            self.assertIsNotNone(worker.df)
            self.assertEqual(worker.pivot_type, 'simple')
            self.assertIsNotNone(worker.parameters)
            
            print("   ✅ Worker Thread - OK")
            
        except Exception as e:
            self.fail(f"Error en worker thread: {e}")
    
    def test_06_main_window_integration(self):
        """Test 6: Verificar integración con MainWindow"""
        print("🧪 Test 6: Integración con MainWindow")
        
        try:
            # Test creación de MainWindow (sin GUI)
            with patch('PySide6.QtWidgets.QApplication'):
                main_window = MainWindow()
                
                # Verificar que se crearon los componentes
                self.assertIsNotNone(main_window.pivot_table_view)
                self.assertIsNotNone(main_window.view_pivot_table_btn)
                
                # Simular carga de datos
                main_window.on_datos_cargados(self.test_data)
                
                # Verificar que los datos se establecieron
                self.assertIsNotNone(main_window.df_original)
                self.assertEqual(len(main_window.df_original), len(self.test_data))
                
                print("   ✅ MainWindow Integration - OK")
                
        except Exception as e:
            self.fail(f"Error en integración con MainWindow: {e}")
    
    def test_07_complete_workflow(self):
        """Test 7: Verificar flujo completo de trabajo"""
        print("🧪 Test 7: Flujo Completo de Trabajo")
        
        try:
            # 1. Crear widget principal
            pivot_widget = PivotTableWidget()
            pivot_widget.set_data(self.test_data)
            
            # 2. Configurar filtros
            if hasattr(pivot_widget, 'filter_panel'):
                pivot_widget.filter_panel.set_data(self.test_data)
                pivot_widget.filter_panel.add_filter('region', 'equals', 'Norte')
            
            # 3. Configurar agregaciones
            if hasattr(pivot_widget, 'aggregation_panel'):
                pivot_widget.aggregation_panel.set_data(self.test_data, ['ventas'])
                # Agregar una función de agregación
                pivot_widget.aggregation_panel.add_aggregation_function()
            
            # 4. Obtener parámetros
            params = pivot_widget.get_current_parameters()
            self.assertIsNotNone(params)
            self.assertIn('index', params)
            self.assertIn('columns', params)
            self.assertIn('values', params)
            
            # 5. Validar parámetros
            errors = pivot_widget.validate_parameters(params)
            if errors:
                print(f"   ⚠️  Advertencias de validación: {errors}")
            
            print("   ✅ Flujo Completo - OK")
            
        except Exception as e:
            self.fail(f"Error en flujo completo: {e}")
    
    def test_08_error_handling(self):
        """Test 8: Verificar manejo de errores"""
        print("🧪 Test 8: Manejo de Errores")
        
        try:
            # Test con DataFrame vacío
            empty_df = pd.DataFrame()
            simple_pivot = SimplePivotTable()
            
            with self.assertRaises(ValueError):
                simple_pivot.execute(empty_df, {
                    'index': 'region',
                    'columns': 'categoria',
                    'values': 'ventas'
                })
            
            # Test con parámetros inválidos
            pivot_widget = PivotTableWidget()
            invalid_params = {
                'index': [],  # Vacío - debe dar error
                'columns': ['categoria'],
                'values': ['ventas']
            }
            
            errors = pivot_widget.validate_parameters(invalid_params)
            self.assertGreater(len(errors), 0)
            
            print("   ✅ Manejo de Errores - OK")
            
        except Exception as e:
            self.fail(f"Error en manejo de errores: {e}")


def run_integration_tests():
    """Ejecutar todos los tests de integración"""
    print("=" * 60)
    print("🧪 INICIANDO TESTS DE INTEGRACIÓN - TABLA PIVOTE")
    print("=" * 60)
    
    if not IMPORTS_SUCCESSFUL:
        print("❌ Error: No se pudieron importar las dependencias necesarias")
        return False
    
    # Crear suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPivotIntegration)
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
    
    # Ejecutar tests
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS DE INTEGRACIÓN")
    print("=" * 60)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Fallos: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FALLOS:")
        for test, traceback in result.failures:
            error_line = traceback.split('AssertionError: ')[-1].split('\n')[0]
            print(f"  - {test}: {error_line}")
    
    if result.errors:
        print("\n❌ ERRORES:")
        for test, traceback in result.errors:
            error_line = traceback.split('\n')[-2]
            print(f"  - {test}: {error_line}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print("\n✅ TODOS LOS TESTS DE INTEGRACIÓN PASARON")
    else:
        print("\n❌ ALGUNOS TESTS FALLARON")
    
    print("=" * 60)
    return success


if __name__ == "__main__":
    # Ejecutar tests
    success = run_integration_tests()
    
    # Salir con código de estado
    sys.exit(0 if success else 1)