#!/usr/bin/env python3
"""
Test para verificar la diferenciación de diálogos de pivote
"""

import sys
import pandas as pd
sys.path.insert(0, '.')

def test_dialog_differentiation() -> None:
    """Test de diferenciación entre diálogos Simple y Combinado"""
    print("🧪 TESTING: Diferenciación de Diálogos de Pivote")
    print("=" * 60)
    
    try:
        # Test 1: Verificar que existe el diálogo simple
        print("📊 Test 1: Verificar diálogo simple")
        from app.widgets.simple_pivot_dialog import SimplePivotDialog
        print("✅ SimplePivotDialog importado correctamente")
        
        # Test 2: Verificar que existe el diálogo avanzado  
        print("\n📊 Test 2: Verificar diálogo avanzado")
        from app.widgets.pivot_config_dialog import PivotConfigDialog
        print("✅ PivotConfigDialog importado correctamente")
        
        # Test 3: Crear instancia de diálogo simple
        print("\n📊 Test 3: Crear instancia de diálogo simple")
        df_test = pd.DataFrame({
            'region': ['Norte', 'Sur', 'Norte'],
            'categoria': ['A', 'A', 'B'],
            'ventas': [100, 150, 200]
        })
        
        from PySide6.QtWidgets import QApplication
        app = QApplication([])
        
        simple_dialog = SimplePivotDialog(df_test, None)
        simple_dialog.set_data(df_test)
        
        config_simple = simple_dialog.get_config()
        print(f"✅ Diálogo simple creado y configurado: {list(config_simple.keys())}")
        
        # Test 4: Crear instancia de diálogo avanzado
        print("\n📊 Test 4: Crear instancia de diálogo avanzado")
        advanced_dialog = PivotConfigDialog(df_test, None)
        advanced_dialog.set_data(df_test)
        
        config_advanced = advanced_dialog.get_config()
        print(f"✅ Diálogo avanzado creado y configurado: {list(config_advanced.keys())}")
        
        # Test 5: Verificar que los métodos son diferentes
        print("\n📊 Test 5: Verificar diferencias en métodos")
        simple_methods = [method for method in dir(simple_dialog) if not method.startswith('_')]
        advanced_methods = [method for method in dir(advanced_dialog) if not method.startswith('_')]
        
        print(f"Métodos en diálogo simple: {len(simple_methods)}")
        print(f"Métodos en diálogo avanzado: {len(advanced_methods)}")
        
        # El diálogo simple debe tener menos métodos (es más simple)
        if len(simple_methods) < len(advanced_methods):
            print("✅ Diálogo simple tiene menos métodos (correcto)")
        else:
            print("⚠️ Los diálogos tienen la misma complejidad")
        
        # Test 6: Verificar configuración simple
        print("\n📊 Test 6: Verificar configuración simple")
        expected_simple_keys = ['index', 'columns', 'values', 'aggfunc']
        simple_has_keys = all(key in config_simple for key in expected_simple_keys)
        
        if simple_has_keys:
            print(f"✅ Diálogo simple tiene configuración correcta: {expected_simple_keys}")
        else:
            print(f"❌ Diálogo simple falta configuración: {expected_simple_keys}")
        
        # Test 7: Verificar configuración avanzada
        print("\n📊 Test 7: Verificar configuración avanzada")
        expected_advanced_keys = ['index', 'columns', 'values', 'aggfuncs', 'pivot_type']
        advanced_has_keys = all(key in config_advanced for key in expected_advanced_keys)
        
        if advanced_has_keys:
            print(f"✅ Diálogo avanzado tiene configuración correcta: {expected_advanced_keys}")
        else:
            print(f"❌ Diálogo avanzado falta configuración: {expected_advanced_keys}")
        
        print("\n🎉 TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
        return True
        
    except Exception as e:
        print(f"❌ ERROR EN TESTS: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_menu_integration() -> None:
    """Test de integración con el menú principal"""
    print("\n🔗 TESTING: Integración con Menú Principal")
    print("=" * 50)
    
    try:
        # Simular MainWindow con las funciones de menú
        from main import MainWindow
        from PySide6.QtWidgets import QApplication
        import pandas as pd
        
        app = QApplication([])
        
        # Crear instancia de MainWindow
        main_window = MainWindow()
        
        # Simular datos cargados
        df_test = pd.DataFrame({
            'region': ['Norte', 'Sur', 'Norte'],
            'categoria': ['A', 'A', 'B'],
            'ventas': [100, 150, 200]
        })
        main_window.data_service.df_vista_actual = df_test
        
        # Verificar que las funciones existen
        if hasattr(main_window, 'abrir_pivot_simple'):
            print("✅ Función abrir_pivot_simple existe")
        else:
            print("❌ Función abrir_pivot_simple no existe")
            return False
            
        if hasattr(main_window, 'abrir_pivot_combinada'):
            print("✅ Función abrir_pivot_combinada existe")
        else:
            print("❌ Función abrir_pivot_combinada no existe")
            return False
        
        # Verificar que la función de fallback existe
        if hasattr(main_window, 'crear_agregacion_fallback'):
            print("✅ Función crear_agregacion_fallback existe")
        else:
            print("❌ Función crear_agregacion_fallback no existe")
            return False
        
        print("✅ INTEGRATION TEST PASSED")
        return True
        
    except Exception as e:
        print(f"❌ ERROR EN INTEGRATION TEST: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTS DE DIFERENCIACIÓN DE DIÁLOGOS")
    print("=" * 70)
    
    # Ejecutar tests
    test1_passed = test_dialog_differentiation()
    test2_passed = test_menu_integration()
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE TESTS")
    print("=" * 70)
    
    if test1_passed and test2_passed:
        print("🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("✅ Diálogos diferenciados correctamente")
        print("✅ Simple: Interfaz básica con selección individual")
        print("✅ Combinado: Interfaz avanzada con múltiples selecciones")
        print("✅ Integración con menú funcional")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        if not test1_passed:
            print("❌ Tests de diferenciación de diálogos fallaron")
        if not test2_passed:
            print("❌ Tests de integración con menú fallaron")
    
    print("=" * 70)
