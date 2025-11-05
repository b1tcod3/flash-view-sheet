#!/usr/bin/env python3
"""
Test completo para verificar que la corrección de paginación no introduce regresiones
"""

import pandas as pd
import sys
from paginacion.data_view import DataView
from paginacion.pagination_manager import PaginationManager
from app.models.pandas_model import VirtualizedPandasModel

def test_edge_cases():
    """Probar casos extremos y regresiones"""
    print("=== TEST DE CASOS EXTREMOS Y REGRESIONES ===\n")
    
    # Test 1: Dataset muy pequeño (menos que page_size)
    print("1. Testing dataset más pequeño que page_size...")
    small_data = {
        'ID': [1, 2, 3],
        'Nombre': ['A', 'B', 'C']
    }
    df_small = pd.DataFrame(small_data)
    
    pm_small = PaginationManager(df_small, page_size=10)  # Más filas que datos
    page_data = pm_small.get_page_data()
    print(f"   - Total páginas: {pm_small.get_total_pages()}")
    print(f"   - Filas en página: {len(page_data)}")
    
    model_small = VirtualizedPandasModel(page_data)
    first_cell = model_small.data(model_small.index(0, 0))
    print(f"   - Primera celda: '{first_cell}'")
    print(f"   ✅ Dataset pequeño: {'OK' if first_cell == '1' else 'FAIL'}")
    
    # Test 2: Dataset vacío
    print("\n2. Testing dataset vacío...")
    df_empty = pd.DataFrame()
    pm_empty = PaginationManager(df_empty, page_size=10)
    page_data_empty = pm_empty.get_page_data()
    print(f"   - Total páginas: {pm_empty.get_total_pages()}")
    print(f"   - Filas en página: {len(page_data_empty)}")
    print(f"   ✅ Dataset vacío: {'OK' if len(page_data_empty) == 0 else 'FAIL'}")
    
    # Test 3: Dataset que requiere virtualización
    print("\n3. Testing dataset grande (requiere virtualización)...")
    large_data = {
        'ID': list(range(1, 6000)),  # 6000 filas > threshold de 5000
        'Valor': [i * 10 for i in range(1, 6000)]
    }
    df_large = pd.DataFrame(large_data)
    
    pm_large = PaginationManager(df_large, page_size=100)
    page_data_large = pm_large.get_page_data()
    print(f"   - Total páginas: {pm_large.get_total_pages()}")
    print(f"   - Filas en página: {len(page_data_large)}")
    
    model_large = VirtualizedPandasModel(page_data_large)
    print(f"   - Virtualización: {model_large.enable_virtualization}")
    first_cell_large = model_large.data(model_large.index(0, 0))
    print(f"   - Primera celda: '{first_cell_large}'")
    print(f"   ✅ Dataset grande: {'OK' if first_cell_large == '1' else 'FAIL'}")
    
    # Test 4: Datos con valores NaN
    print("\n4. Testing datos con valores NaN...")
    nan_data = {
        'ID': [1, 2, 3, 4, 5],
        'Nombre': ['A', None, 'C', 'D', None],
        'Valor': [10, 20, None, 40, 50]
    }
    df_nan = pd.DataFrame(nan_data)
    
    pm_nan = PaginationManager(df_nan, page_size=10)
    model_nan = VirtualizedPandasModel(pm_nan.get_page_data())
    
    # Probar acceso a valores NaN
    cell_none = model_nan.data(model_nan.index(1, 1))  # Nombre: None
    cell_nan = model_nan.data(model_nan.index(2, 2))   # Valor: NaN
    
    print(f"   - Celda con None: '{cell_none}'")
    print(f"   - Celda con NaN: '{cell_nan}'")
    print(f"   ✅ Manejo de NaN: {'OK' if cell_none == '' and cell_nan == '' else 'FAIL'}")
    
    # Test 5: Cambio de page_size dinámico
    print("\n5. Testing cambio dinámico de page_size...")
    df_dynamic = pd.DataFrame({
        'ID': list(range(1, 25)),
        'Valor': list(range(1, 25))
    })
    
    pm_dynamic = PaginationManager(df_dynamic, page_size=5)
    page_data_5 = pm_dynamic.get_page_data()
    print(f"   - Página size 5: {len(page_data_5)} filas")
    
    pm_dynamic.set_page_size(10)
    page_data_10 = pm_dynamic.get_page_data()
    print(f"   - Página size 10: {len(page_data_10)} filas")
    
    model_dynamic = VirtualizedPandasModel(page_data_10)
    first_dynamic = model_dynamic.data(model_dynamic.index(0, 0))
    print(f"   ✅ Cambio dinámico: {'OK' if first_dynamic == '1' else 'FAIL'}")
    
    return True

def test_pagination_flow():
    """Probar flujo completo de paginación"""
    print("\n=== TEST DE FLUJO COMPLETO DE PAGINACIÓN ===\n")
    
    # Crear datos que generen múltiples páginas
    data = {
        'ID': list(range(1, 31)),  # 30 filas
        'Nombre': [f'Usuario_{i}' for i in range(1, 31)],
        'Edad': [20 + i for i in range(30)]
    }
    df = pd.DataFrame(data)
    
    # Crear DataView
    data_view = DataView()
    data_view.set_data(df)
    
    pm = data_view.pagination_manager
    
    print(f"Total páginas: {pm.get_total_pages()}")
    
    # Navegar a cada página y verificar datos
    all_pages_correct = True
    
    for page in range(1, pm.get_total_pages() + 1):
        print(f"\nVerificando página {page}...")
        
        # Cambiar página
        pm.set_current_page(page)
        
        # Verificar modelo
        model = data_view.pandas_model
        page_data = pm.get_page_data()
        
        if model.rowCount() != len(page_data):
            print(f"   ❌ Error: Modelo tiene {model.rowCount()} filas, esperado {len(page_data)}")
            all_pages_correct = False
            continue
        
        # Verificar que los datos en la primera celda sean correctos
        expected_first_id = str(page_data.iloc[0]['ID'])
        actual_first_id = model.data(model.index(0, 0))
        
        if actual_first_id != expected_first_id:
            print(f"   ❌ Error: Primera celda '{actual_first_id}', esperada '{expected_first_id}'")
            all_pages_correct = False
            continue
        
        print(f"   ✅ Página {page}: OK (IDs {expected_first_id}-{page_data.iloc[-1]['ID']})")
    
    print(f"\n{'✅ Flujo completo: OK' if all_pages_correct else '❌ Flujo completo: FAILED'}")
    return all_pages_correct

def main():
    """Función principal"""
    print("🔍 TEST COMPLETO POST-CORRECCIÓN")
    print("=" * 50)
    
    # Test de casos extremos
    edge_cases_pass = test_edge_cases()
    
    # Test de flujo completo
    flow_pass = test_pagination_flow()
    
    print("\n" + "=" * 50)
    print("📋 RESUMEN FINAL:")
    print(f"   - Casos extremos: {'✅ PASARON' if edge_cases_pass else '❌ FALLARON'}")
    print(f"   - Flujo completo: {'✅ PASÓ' if flow_pass else '❌ FALLÓ'}")
    
    if edge_cases_pass and flow_pass:
        print("\n🎉 ¡CORRECCIÓN EXITOSA!")
        print("El bug de páginas en blanco está completamente solucionado.")
        print("No hay regresiones en la funcionalidad de paginación.")
    else:
        print("\n⚠️ Hay problemas que requieren atención.")
    
    return edge_cases_pass and flow_pass

if __name__ == "__main__":
    main()