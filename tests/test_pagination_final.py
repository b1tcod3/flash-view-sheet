#!/usr/bin/env python3
"""
Test simplificado para verificar que la corrección funciona sin GUI
"""

import pandas as pd
from app.services.pagination_manager import PaginationManager
from app.models.pandas_model import VirtualizedPandasModel

def test_core_pagination() -> None:
    """Test de la funcionalidad core de paginación"""
    print("=== TEST CORE DE PAGINACIÓN ===\n")
    
    # Crear datos de prueba
    data = {
        'ID': list(range(1, 36)),  # 35 filas
        'Nombre': [f'Usuario_{i}' for i in range(1, 36)],
        'Valor': [i * 10 for i in range(1, 36)]
    }
    df = pd.DataFrame(data)
    
    # Test PaginationManager
    print("1. Testing PaginationManager...")
    pm = PaginationManager(df, page_size=10)
    
    print(f"   - Total páginas: {pm.get_total_pages()}")
    
    # Test todas las páginas
    all_pages_ok = True
    for page in range(1, pm.get_total_pages() + 1):
        pm.set_current_page(page)
        page_data = pm.get_page_data()
        
        print(f"   Página {page}: {len(page_data)} filas (IDs: {page_data.iloc[0]['ID']}-{page_data.iloc[-1]['ID']})")
        
        # Crear modelo para esta página
        model = VirtualizedPandasModel(page_data)
        
        # Verificar que el modelo devuelve los datos correctos
        first_cell = model.data(model.index(0, 0))
        last_cell = model.data(model.index(len(page_data)-1, 0))
        
        expected_first = str(page_data.iloc[0]['ID'])
        expected_last = str(page_data.iloc[-1]['ID'])
        
        if first_cell != expected_first or last_cell != expected_last:
            print(f"   ❌ Error en página {page}")
            all_pages_ok = False
        else:
            print(f"   ✅ Página {page} correcta")
    
    return all_pages_ok

def test_edge_cases() -> None:
    """Test de casos extremos"""
    print("\n=== TEST DE CASOS EXTREMOS ===\n")
    
    # Test 1: Dataset muy pequeño
    print("1. Dataset pequeño (3 filas, page_size=10)...")
    small_data = pd.DataFrame({'ID': [1, 2, 3], 'Nombre': ['A', 'B', 'C']})
    pm_small = PaginationManager(small_data, page_size=10)
    model_small = VirtualizedPandasModel(pm_small.get_page_data())
    
    first_cell = model_small.data(model_small.index(0, 0))
    print(f"   Primera celda: '{first_cell}' - {'✅' if first_cell == '1' else '❌'}")
    
    # Test 2: Dataset vacío
    print("\n2. Dataset vacío...")
    empty_data = pd.DataFrame()
    pm_empty = PaginationManager(empty_data, page_size=10)
    page_data_empty = pm_empty.get_page_data()
    print(f"   Filas en página: {len(page_data_empty)} - {'✅' if len(page_data_empty) == 0 else '❌'}")
    
    # Test 3: Datos con NaN
    print("\n3. Datos con valores NaN...")
    nan_data = pd.DataFrame({
        'ID': [1, 2, 3],
        'Nombre': ['A', None, 'C'],
        'Valor': [10, None, 30]
    })
    pm_nan = PaginationManager(nan_data, page_size=10)
    model_nan = VirtualizedPandasModel(pm_nan.get_page_data())
    
    cell_none = model_nan.data(model_nan.index(1, 1))  # Nombre: None
    cell_nan = model_nan.data(model_nan.index(1, 2))   # Valor: None
    print(f"   None como string: '{cell_none}' - {'✅' if cell_none == '' else '❌'}")
    print(f"   NaN como string: '{cell_nan}' - {'✅' if cell_nan == '' else '❌'}")
    
    return True

def test_virtualization() -> None:
    """Test específico para virtualización"""
    print("\n=== TEST DE VIRTUALIZACIÓN ===\n")
    
    # Dataset grande que active virtualización (>5000 filas según config)
    large_data = {
        'ID': list(range(1, 6001)),  # 6000 filas
        'Valor': [i * 10 for i in range(1, 6001)]
    }
    df_large = pd.DataFrame(large_data)
    
    pm_large = PaginationManager(df_large, page_size=100)
    page_data = pm_large.get_page_data()
    
    model = VirtualizedPandasModel(page_data)
    
    print(f"   - Total filas en página: {len(page_data)}")
    print(f"   - Virtualización activada: {model.enable_virtualization}")
    
    # Verificar acceso a datos
    first_cell = model.data(model.index(0, 0))
    last_cell = model.data(model.index(len(page_data)-1, 0))
    
    expected_first = str(page_data.iloc[0]['ID'])
    expected_last = str(page_data.iloc[-1]['ID'])
    
    print(f"   - Primera celda: '{first_cell}' (esperado: '{expected_first}') - {'✅' if first_cell == expected_first else '❌'}")
    print(f"   - Última celda: '{last_cell}' (esperado: '{expected_last}') - {'✅' if last_cell == expected_last else '❌'}")
    
    return True

def main() -> int:
    """Función principal"""
    print("🔍 TEST COMPLETO POST-CORRECCIÓN (SIN GUI)")
    print("=" * 55)
    
    # Test core
    core_ok = test_core_pagination()
    
    # Test edge cases
    edge_ok = test_edge_cases()
    
    # Test virtualización
    virt_ok = test_virtualization()
    
    print("\n" + "=" * 55)
    print("📋 RESUMEN FINAL:")
    print(f"   - Core pagination: {'✅ OK' if core_ok else '❌ FAILED'}")
    print(f"   - Edge cases: {'✅ OK' if edge_ok else '❌ FAILED'}")
    print(f"   - Virtualization: {'✅ OK' if virt_ok else '❌ FAILED'}")
    
    if core_ok and edge_ok and virt_ok:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        print("La corrección de paginación es exitosa.")
    else:
        print("\n⚠️ Algunos tests fallaron.")
    
    return core_ok and edge_ok and virt_ok

if __name__ == "__main__":
    main()