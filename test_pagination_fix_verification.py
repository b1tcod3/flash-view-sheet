#!/usr/bin/env python3
"""
Test específico para verificar que la corrección de paginación al ordenar funciona
"""

import sys
import pandas as pd
import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Importar componentes del proyecto
from paginacion.data_view import DataView

def test_sorting_preserves_pagination():
    """Test que verifica específicamente la preservación de paginación al ordenar"""
    
    print("🧪 TEST: Preservación de paginación al ordenar")
    print("=" * 60)
    
    # Crear datos de prueba con una columna que tenga valores únicos para verificar ordenamiento
    np.random.seed(42)
    data = {
        'Nombre': [f'Item_{i:03d}' for i in range(1, 101)],  # 100 filas
        'Valor': list(range(100, 0, -1)),  # 100, 99, 98... 1
        'Categoria': [f'Cat_{i % 10}' for i in range(100)]
    }
    df = pd.DataFrame(data)
    print(f"📊 Datos creados: {len(df)} filas")
    
    # Crear DataView y configurar datos
    data_view = DataView()
    data_view.set_data(df)
    
    print(f"📄 Configuración: {data_view.pagination_manager.get_page_size()} filas por página")
    print(f"📄 Total de páginas: {data_view.pagination_manager.get_total_pages()}")
    print()
    
    # Test 1: Navegar a una página específica
    print("1️⃣ Navegación a página específica")
    target_page = 4
    data_view.pagination_manager.set_current_page(target_page)
    current_page = data_view.pagination_manager.get_current_page()
    print(f"   Página actual: {current_page}")
    
    if current_page != target_page:
        print("   ❌ FALLO: No se pudo navegar a la página objetivo")
        return False
    
    print("   ✅ Navegación exitosa")
    print()
    
    # Test 2: Simular ordenamiento por columna 'Valor'
    print("2️⃣ Simular ordenamiento (como lo hace Qt internamente)")
    
    # Obtener el modelo actual
    model = data_view.pandas_model
    if model is None:
        print("   ❌ FALLO: No hay modelo disponible")
        return False
    
    # Verificar datos antes del ordenamiento
    page_data_before = data_view.pagination_manager.get_page_data()
    print(f"   Filas en página antes del ordenamiento: {len(page_data_before)}")
    print(f"   Primeros 3 valores: {page_data_before['Valor'].head(3).tolist()}")
    
    # Simular ordenamiento llamando al método sort() del modelo
    # Column 1 = 'Valor' (0='Nombre', 1='Valor', 2='Categoria')
    ascending = False  # Ordenamiento descendente
    
    try:
        # Llamar al método sort() del modelo
        model.sort(1, Qt.AscendingOrder if ascending else Qt.DescendingOrder)
        
        # El ordenamiento debería haber emitido layoutChanged
        # Esto debería haber activado on_model_sorted() en DataView
        
        # Verificar la página después del ordenamiento
        page_after_sorting = data_view.pagination_manager.get_current_page()
        print(f"   Página después del ordenamiento: {page_after_sorting}")
        
        # Verificar datos ordenados
        page_data_after = data_view.pagination_manager.get_page_data()
        print(f"   Filas en página después del ordenamiento: {len(page_data_after)}")
        print(f"   Primeros 3 valores después: {page_data_after['Valor'].head(3).tolist()}")
        
        # Verificar si la página se preservó
        if page_after_sorting == target_page:
            print("   ✅ ÉXITO: La página se preservó durante el ordenamiento")
            page_preserved = True
        else:
            print(f"   ❌ FALLO: La página cambió de {target_page} a {page_after_sorting}")
            page_preserved = False
            
        # Verificar que los datos están ordenados
        valores_despues = page_data_after['Valor'].tolist()
        if len(valores_despues) > 1:
            # Para ordenamiento descendente, deben estar en orden decreciente
            is_descending_sorted = all(valores_despues[i] >= valores_despues[i+1] 
                                     for i in range(len(valores_despues)-1))
            if is_descending_sorted:
                print("   ✅ Los datos están correctamente ordenados")
            else:
                print("   ❌ Los datos NO están ordenados correctamente")
        else:
            print("   ⚠️  No hay suficientes datos para verificar ordenamiento")
            
    except Exception as e:
        print(f"   ❌ FALLO: Error durante el ordenamiento: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Test 3: Navegación después del ordenamiento
    print("3️⃣ Navegación después del ordenamiento")
    
    try:
        # Intentar navegar a la página siguiente
        if data_view.pagination_manager.can_go_next():
            original_page = data_view.pagination_manager.get_current_page()
            data_view.pagination_manager.next_page()
            new_page = data_view.pagination_manager.get_current_page()
            
            print(f"   Navegación 'siguiente': {original_page} → {new_page}")
            
            if new_page == original_page + 1:
                print("   ✅ La navegación funciona después del ordenamiento")
                navigation_ok = True
            else:
                print("   ❌ La navegación falla después del ordenamiento")
                navigation_ok = False
        else:
            print("   ⚠️  Ya estamos en la última página")
            navigation_ok = True
            
    except Exception as e:
        print(f"   ❌ Error durante navegación: {e}")
        navigation_ok = False
    
    print()
    
    # Test 4: Ordenamiento en otra dirección
    print("4️⃣ Ordenamiento en dirección opuesta")
    
    try:
        current_page_before = data_view.pagination_manager.get_current_page()
        
        # Ordenar por la misma columna en orden ascendente
        model.sort(1, Qt.AscendingOrder)
        
        current_page_after = data_view.pagination_manager.get_current_page()
        
        print(f"   Página antes del segundo ordenamiento: {current_page_before}")
        print(f"   Página después del segundo ordenamiento: {current_page_after}")
        
        if current_page_before == current_page_after:
            print("   ✅ La página se mantiene en múltiples ordenamientos")
            multiple_sorting_ok = True
        else:
            print("   ❌ La página se pierde en múltiples ordenamientos")
            multiple_sorting_ok = False
            
    except Exception as e:
        print(f"   ❌ Error en segundo ordenamiento: {e}")
        multiple_sorting_ok = False
    
    print()
    
    return page_preserved and navigation_ok and multiple_sorting_ok

def test_different_column_types():
    """Test ordenamiento en diferentes tipos de columnas"""
    
    print("🧪 TEST: Diferentes tipos de columnas")
    print("=" * 50)
    
    # Crear datos con diferentes tipos
    np.random.seed(42)
    data = {
        'Texto': ['A', 'B', 'C'] * 15,
        'Numeros': list(range(45, 0, -1)),
        'Decimal': [i / 3.14 for i in range(45)],
        'Fecha': pd.date_range('2023-01-01', periods=45),
        'Boolean': [True, False] * 22 + [True]
    }
    df = pd.DataFrame(data)
    print(f"📊 Datos de prueba: {len(df)} filas")
    
    data_view = DataView()
    data_view.set_data(df)
    
    # Test cada tipo de columna
    columns_to_test = [
        (0, 'Texto'),
        (1, 'Numeros'), 
        (2, 'Decimal'),
        (3, 'Fecha'),
        (4, 'Boolean')
    ]
    
    success_count = 0
    total_tests = len(columns_to_test)
    
    for col_idx, col_name in columns_to_test:
        try:
            # Ir a una página específica
            data_view.pagination_manager.set_current_page(2)
            page_before = data_view.pagination_manager.get_current_page()
            
            # Ordenar por esta columna
            data_view.pandas_model.sort(col_idx, Qt.DescendingOrder)
            
            # Verificar que la página se mantuvo
            page_after = data_view.pagination_manager.get_current_page()
            
            if page_before == page_after:
                print(f"   {col_name:10}: ✅ Preserva página")
                success_count += 1
            else:
                print(f"   {col_name:10}: ❌ Pierde página ({page_before} → {page_after})")
                
        except Exception as e:
            print(f"   {col_name:10}: ❌ Error - {e}")
    
    print(f"\n   Resultado: {success_count}/{total_tests} columnas preservan la página")
    return success_count == total_tests

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    try:
        print("🚀 TEST ESPECÍFICO DE CORRECCIÓN DE PAGINACIÓN")
        print("=" * 70)
        print()
        
        # Test principal
        main_test_passed = test_sorting_preserves_pagination()
        
        # Test de diferentes tipos de columnas
        column_types_passed = test_different_column_types()
        
        # Resumen final
        print("📋 RESUMEN FINAL")
        print("=" * 50)
        
        if main_test_passed and column_types_passed:
            print("🎉 TODOS LOS TESTS PASARON!")
            print("✅ La corrección de paginación al ordenar funciona perfectamente")
            print("✅ La página se preserva independientemente del tipo de columna")
            print("✅ La navegación funciona correctamente después del ordenamiento")
        else:
            print("❌ ALGUNOS TESTS FALLARON:")
            print(f"   Test principal: {'✅' if main_test_passed else '❌'}")
            print(f"   Tipos de columnas: {'✅' if column_types_passed else '❌'}")
            
            if not main_test_passed:
                print("\n⚠️  La corrección principal necesita revisión")
            if not column_types_passed:
                print("\n⚠️  Algunos tipos de columna no funcionan correctamente")
        
        print(f"\n🎯 CONCLUSIÓN FINAL:")
        if main_test_passed and column_types_passed:
            print("✅ LA CORRECCIÓN DE PAGINACIÓN ESTÁ FUNCIONANDO")
        else:
            print("❌ SE REQUIEREN AJUSTES EN LA CORRECCIÓN")
        
    except Exception as e:
        print(f"❌ Error durante los tests: {e}")
        import traceback
        traceback.print_exc()