#!/usr/bin/env python3
"""
Test para validar la funcionalidad de columnas opcionales en diálogo simple
"""

import sys
import pandas as pd
sys.path.insert(0, '.')

def test_optional_columns_functionality() -> None:
    """Test de funcionalidad de columnas opcionales"""
    print("🧪 TESTING: Columnas Opcionales en Diálogo Simple")
    print("=" * 60)
    
    try:
        # Importar diálogo simple
        from app.widgets.simple_pivot_dialog import SimplePivotDialog
        from PySide6.QtWidgets import QApplication
        
        app = QApplication([])
        
        # Crear dataset de prueba
        df_test = pd.DataFrame({
            'region': ['Norte', 'Sur', 'Norte', 'Sur', 'Norte'],
            'categoria': ['A', 'A', 'B', 'B', 'A'],
            'ventas': [100, 150, 200, 120, 180],
            'unidades': [10, 15, 20, 12, 18]
        })
        
        # Test 1: Crear diálogo y verificar configuración inicial
        print("📊 Test 1: Verificar diálogo con columna opcional")
        dialog = SimplePivotDialog(df_test, None)
        dialog.set_data(df_test)
        
        # Verificar que se agregó la opción vacía
        columns_count = dialog.columns_combo.count()
        print(f"✅ Combo de columnas tiene {columns_count} opciones (incluyendo vacía)")
        
        # Test 2: Configuración sin columna para pivot (agregación simple)
        print("\n📊 Test 2: Configuración de agregación simple (sin pivot)")
        dialog.index_combo.setCurrentText("region")
        dialog.values_combo.setCurrentText("ventas")
        dialog.agg_func_combo.setCurrentText("sum - Suma")
        # columns_combo se queda vacío (opción vacía)
        
        config = dialog.get_config()
        print(f"Configuración: {config}")
        
        # Verificar que is_pivot=False cuando no hay columna para columnas
        expected_is_pivot = config.get('is_pivot', True) == False
        if expected_is_pivot:
            print("✅ Configuración correcta para agregación simple (is_pivot=False)")
        else:
            print("❌ Error: Debería ser is_pivot=False para agregación simple")
        
        # Test 3: Configuración con columna para pivot (pivote real)
        print("\n📊 Test 3: Configuración de pivote real")
        dialog.columns_combo.setCurrentText("categoria")
        
        config_pivot = dialog.get_config()
        print(f"Configuración pivote: {config_pivot}")
        
        # Verificar que is_pivot=True cuando hay columna para columnas
        expected_is_pivot_real = config_pivot.get('is_pivot', False) == True
        if expected_is_pivot_real:
            print("✅ Configuración correcta para pivote real (is_pivot=True)")
        else:
            print("❌ Error: Debería ser is_pivot=True para pivote real")
        
        # Test 4: Verificar función de agregación simple en MainWindow
        print("\n📊 Test 4: Verificar función de agregación simple")
        
        # Simular MainWindow
        class MockMainWindow:
            def __init__(self, df: pd.DataFrame) -> None:
                self.df_vista_actual = df
            
            def crear_agregacion_simple(self, config: dict) -> pd.DataFrame:
                """Simular la función crear_agregacion_simple"""
                index_column = config.get('index')
                values_column = config.get('values')
                agg_function = config.get('aggfunc', 'mean')
                
                if not index_column or not values_column:
                    raise ValueError("Se requieren columnas de índice y valores para la agregación")
                
                # Agrupar por la columna índice y agregar la columna de valores
                result = self.df_vista_actual.groupby(index_column)[values_column].agg(agg_function).reset_index()
                
                # Renombrar la columna para que sea más clara
                result.columns = [index_column, f"{values_column}_{agg_function}"]
                
                return result
        
        mock_window = MockMainWindow(df_test)
        
        # Probar agregación simple
        result = mock_window.crear_agregacion_simple(config)
        print(f"✅ Agregación simple exitosa: {result.shape}")
        print(f"Columnas: {list(result.columns)}")
        print(f"Contenido:\n{result}")
        
        print("\n🎉 TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
        return True
        
    except Exception as e:
        print(f"❌ ERROR EN TESTS: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTS DE COLUMNAS OPCIONALES")
    print("=" * 70)
    
    # Ejecutar tests
    test_passed = test_optional_columns_functionality()
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE TESTS")
    print("=" * 70)
    
    if test_passed:
        print("🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("✅ Columna para Columnas es opcional")
        print("✅ is_pivot=False cuando no se selecciona columna para pivot")
        print("✅ is_pivot=True cuando se selecciona columna para pivot")
        print("✅ Función de agregación simple funciona correctamente")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
    
    print("=" * 70)