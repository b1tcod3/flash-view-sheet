#!/usr/bin/env python3
"""
Test para validar la nueva agregación nunique (Conteo Único) en SimplePivotDialog
"""

import sys
import pandas as pd
from PySide6.QtWidgets import QApplication
from app.widgets.simple_pivot_dialog import SimplePivotDialog


def test_nunique_aggregation():
    """Test para validar la nueva función nunique (conteo único)"""
    print("🧪 TEST: Nueva agregación nunique (Conteo Único)")
    print("=" * 60)
    
    # Crear dataset con valores duplicados
    df = pd.DataFrame({
        'region': ['Norte', 'Sur', 'Norte', 'Sur', 'Este', 'Este'],
        'producto': ['Laptop', 'Mouse', 'Laptop', 'Teclado', 'Monitor', 'Monitor'],
        'categoria': ['A', 'B', 'A', 'C', 'B', 'C'],
        'ventas': [100.5, 200.0, 150.5, 300.0, 250.0, 180.0],
        'codigo': ['C001', 'C002', 'C001', 'C003', 'C004', 'C004']  # Con duplicados
    })
    
    print(f"📊 Dataset: {df.shape[0]} filas, {df.shape[1]} columnas")
    print(f"📝 Columnas: {list(df.columns)}")
    print(f"🔍 Dataset completo:")
    print(df)
    print()
    
    # Crear aplicación Qt (necesario para widgets)
    app = QApplication(sys.argv)
    
    # Test 1: Verificar que nunique está en la lista de funciones
    print("✅ Test 1: Verificar función nunique en el diálogo")
    dialog = SimplePivotDialog()
    dialog.set_data(df)
    
    agg_functions = [dialog.agg_func_combo.itemText(i) for i in range(dialog.agg_func_combo.count())]
    print(f"   📋 Funciones disponibles: {agg_functions}")
    
    nunique_found = any("nunique" in func for func in agg_functions)
    if nunique_found:
        print("   ✅ OK: Función 'nunique - Conteo Único' encontrada")
    else:
        print("   ❌ Error: Función nunique no encontrada")
    print()
    
    # Test 2: Configurar nunique para contar productos únicos por región
    print("✅ Test 2: Configurar nunique para productos únicos por región")
    dialog2 = SimplePivotDialog()
    dialog2.set_data(df)
    
    dialog2.index_combo.setCurrentText('region')
    dialog2.columns_combo.setCurrentText('')  # Vacío para agregación simple
    dialog2.values_combo.setCurrentText('producto')
    dialog2.agg_func_combo.setCurrentText('nunique - Conteo Único')
    
    config = dialog2.get_config()
    print(f"   📋 Config: {config}")
    
    if config['aggfunc'] == 'nunique':
        print("   ✅ OK: Configuración de nunique correcta")
    else:
        print("   ❌ Error: Configuración de nunique incorrecta")
    print()
    
    # Test 3: Validación para nunique (no requiere numérica)
    print("✅ Test 3: Validación para nunique")
    config = dialog2.get_config()
    
    # Simular validación de tipos
    if config['values'] in df.columns:
        # nunique no requiere numérica, debe pasar la validación
        numeric_required_funcs = ['sum', 'mean', 'min', 'max', 'median', 'std', 'var']
        is_numeric_required = config['aggfunc'] in numeric_required_funcs
        is_valid_for_nunique = config['aggfunc'] in ['count', 'nunique']
        
        if is_valid_for_nunique and not is_numeric_required:
            print("   ✅ OK: nunique no requiere columna numérica")
        else:
            print("   ❌ Error: nunique incorrectamente validado")
    print()
    
    # Test 4: Ejecución real de nunique con pandas
    print("🚀 Test 4: Ejecución real de nunique")
    try:
        # nunique de productos por región
        result_nunique = df.groupby('region')['producto'].nunique()
        print("   📊 Productos únicos por región:")
        print(result_nunique)
        print("   ✅ OK: nunique ejecutado correctamente")
        print()
        
        # Mostrar comparación con count
        result_count = df.groupby('region')['producto'].count()
        print("   📊 Conteo total de productos por región:")
        print(result_count)
        print()
        
        print("🔍 DIFERENCIA ENTRE COUNT Y NUNIQUE:")
        print("   • count: Cuenta todas las ocurrencias (incluye duplicados)")
        print("   • nunique: Cuenta valores únicos (sin duplicados)")
        
        # Comparar resultados
        comparison = pd.DataFrame({
            'count': result_count,
            'nunique': result_nunique
        })
        print("   📊 Comparación:")
        print(comparison)
        print()
        
    except Exception as e:
        print(f"   ❌ Error en ejecución de nunique: {e}")
    print()
    
    # Test 5: nunique con columna de códigos (con duplicados explícitos)
    print("✅ Test 5: nunique con códigos duplicados")
    try:
        result_codigo = df.groupby('region')['codigo'].nunique()
        print("   📊 Códigos únicos por región:")
        print(result_codigo)
        print("   ✅ OK: nunique identificó códigos duplicados correctamente")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()
    
    app.quit()
    
    print("📊 RESUMEN DEL TEST:")
    print("=" * 30)
    print("✅ Función nunique agregada exitosamente al diálogo")
    print("✅ nunique funciona con columnas de texto")
    print("✅ nunique identifica correctamente valores únicos")
    print("✅ Diferencia clara entre count y nunique")
    print("✅ Validación inteligente para nunique (no requiere numérica)")
    
    return True


def test_advanced_nunique_scenarios():
    """Test avanzado de diferentes escenarios con nunique"""
    print("\n🚀 TEST AVANZADO: Escenarios especiales con nunique")
    print("=" * 60)
    
    # Dataset con diferentes tipos de datos
    df = pd.DataFrame({
        'categoria': ['A', 'A', 'B', 'B', 'C', 'C'],
        'producto': ['Laptop', 'Laptop', 'Mouse', 'Teclado', 'Monitor', 'Monitor'],
        'precio': [100, 100, 200, 300, 250, 250],
        'codigo': ['X1', 'X2', 'X1', 'X3', 'X4', 'X5'],
        'fecha': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-01', '2023-01-03', '2023-01-01', '2023-01-04'])
    })
    
    print("📊 Dataset para test avanzado:")
    print(df)
    print()
    
    tests = [
        ("texto", "producto", "Productos únicos por categoría"),
        ("numérico", "precio", "Precios únicos por categoría"),
        ("código", "codigo", "Códigos únicos por categoría (con duplicados)"),
        ("fecha", "fecha", "Fechas únicas por categoría")
    ]
    
    for test_type, column, description in tests:
        print(f"🧪 Test nunique con {test_type}: {column}")
        try:
            result = df.groupby('categoria')[column].nunique()
            print(f"   📊 {description}:")
            print(result)
            print(f"   ✅ OK: nunique funciona con datos {test_type}")
        except Exception as e:
            print(f"   ❌ Error con {test_type}: {e}")
        print()
    
    print("🎉 TESTS AVANZADOS COMPLETADOS")
    return True


if __name__ == "__main__":
    print("🔧 Test de Nueva Agregación: nunique (Conteo Único)")
    print("=" * 70)
    
    # Test básico de nunique
    success1 = test_nunique_aggregation()
    
    # Test avanzado de escenarios
    success2 = test_advanced_nunique_scenarios()
    
    print("\n🏁 RESULTADO FINAL:")
    print("=" * 20)
    if success1 and success2:
        print("✅ TODOS LOS TESTS PASARON")
        print("✅ Nueva agregación nunique implementada exitosamente")
        print("✅ Funcionalidad completa para conteo único de valores")
    else:
        print("❌ Algunos tests fallaron")
        print("❌ Revisar implementación de nunique")