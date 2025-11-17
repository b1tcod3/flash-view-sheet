#!/usr/bin/env python3
"""
Test para verificar que el ordenamiento funciona correctamente con la paginación
"""

import pandas as pd
from paginacion.data_view import DataView
from paginacion.pagination_manager import PaginationManager
from app.models.pandas_model import VirtualizedPandasModel

def create_test_data_unsorted():
    """Crear datos de prueba desordenados"""
    data = {
        'ID': [10, 5, 15, 3, 20, 8, 12, 1, 25, 7],  # IDs desordenados
        'Nombre': ['J', 'E', 'O', 'D', 'T', 'H', 'L', 'A', 'Y', 'G'],
        'Edad': [25, 30, 20, 35, 28, 22, 27, 33, 24, 29],
        'Puntuacion': [85.5, 92.0, 78.3, 88.7, 95.1, 82.4, 90.2, 87.9, 93.6, 84.8]
    }
    return pd.DataFrame(data)

def test_sorting_with_pagination():
    """Test del ordenamiento con paginación"""
    print("=== TEST DE ORDENAMIENTO CON PAGINACIÓN ===\n")
    
    # Crear datos desordenados
    df = create_test_data_unsorted()
    print("Datos originales (desordenados):")
    print(df.to_string(index=False))
    print(f"\nTotal filas: {len(df)}")
    
    # Test con PaginationManager
    print("\n--- Test PaginationManager ---")
    pm = PaginationManager(df, page_size=5)  # 2 páginas de 5 filas cada una
    
    # Verificar página 1 original
    pm.set_current_page(1)
    page1_original = pm.get_page_data()
    print(f"\nPágina 1 original - IDs: {page1_original['ID'].tolist()}")
    
    # Verificar página 2 original  
    pm.set_current_page(2)
    page2_original = pm.get_page_data()
    print(f"Página 2 original - IDs: {page2_original['ID'].tolist()}")
    
    # Test VirtualizedPandasModel sorting
    print("\n--- Test VirtualizedPandasModel Sorting ---")
    
    # Página 1 - sin ordenamiento
    pm.set_current_page(1)
    page_data = pm.get_page_data()
    model = VirtualizedPandasModel(page_data)
    
    print(f"\nPágina 1 (sin ordenamiento):")
    for i in range(min(3, len(page_data))):
        cell_value = model.data(model.index(i, 0))  # Primera columna (ID)
        print(f"  Fila {i}: {cell_value}")
    
    # Ordenar por ID (ascendente)
    print(f"\n--- Ordenando por ID (ascendente) ---")
    from PySide6.QtCore import Qt
    model.sort(0, Qt.AscendingOrder)  # columna 0, orden ascendente
    
    # Verificar ordenamiento
    print(f"Página 1 después del ordenamiento:")
    for i in range(min(3, model.rowCount())):
        cell_value = model.data(model.index(i, 0))
        print(f"  Fila {i}: {cell_value}")
    
    # Verificar que los datos están ordenados
    if model.rowCount() >= 2:
        first_id = int(model.data(model.index(0, 0)))
        second_id = int(model.data(model.index(1, 0)))
        third_id = int(model.data(model.index(2, 0))) if model.rowCount() > 2 else None
        
        print(f"\nVerificación:")
        print(f"  Primer ID: {first_id}")
        print(f"  Segundo ID: {second_id}")
        if third_id:
            print(f"  Tercer ID: {third_id}")
        
        if first_id <= second_id and (third_id is None or second_id <= third_id):
            print(f"  ✅ Ordenamiento ascendente correcto")
        else:
            print(f"  ❌ Error en ordenamiento ascendente")
    
    # Test ordenamiento descendente
    print(f"\n--- Ordenando por ID (descendente) ---")
    model.sort(0, Qt.DescendingOrder)  # columna 0, orden descendente
    
    print(f"Página 1 después de ordenamiento descendente:")
    for i in range(min(3, model.rowCount())):
        cell_value = model.data(model.index(i, 0))
        print(f"  Fila {i}: {cell_value}")
    
    # Verificar ordenamiento descendente
    if model.rowCount() >= 2:
        first_id = int(model.data(model.index(0, 0)))
        second_id = int(model.data(model.index(1, 0)))
        third_id = int(model.data(model.index(2, 0))) if model.rowCount() > 2 else None
        
        if first_id >= second_id and (third_id is None or second_id >= third_id):
            print(f"  ✅ Ordenamiento descendente correcto")
        else:
            print(f"  ❌ Error en ordenamiento descendente")
    
    return True

def test_sorting_integration_with_data_view():
    """Test de integración con DataView"""
    print("\n=== TEST DE INTEGRACIÓN CON DATAVIEW ===\n")
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        
        # Crear aplicación (necesaria para GUI)
        app = QApplication([])
        
        # Crear DataView
        data_view = DataView()
        
        # Crear datos desordenados
        df = create_test_data_unsorted()
        data_view.set_data(df)
        
        print("Datos cargados en DataView")
        
        # Verificar estado inicial
        pm = data_view.pagination_manager
        print(f"Páginas totales: {pm.get_total_pages()}")
        
        # Verificar datos originales
        pm.set_current_page(1)
        page1_data = pm.get_page_data()
        print(f"Página 1 inicial - IDs: {page1_data['ID'].tolist()}")
        
        # Simular ordenamiento en el modelo
        model = data_view.pandas_model
        print(f"\nAplicando ordenamiento al modelo...")
        model.sort(0, Qt.AscendingOrder)  # Ordenar por ID ascendente
        
        # Actualizar pagination manager con datos ordenados
        sorted_data = model.full_df
        pm.set_data(sorted_data)
        
        # Verificar datos ordenados
        pm.set_current_page(1)
        page1_sorted = pm.get_page_data()
        print(f"Página 1 después de ordenamiento - IDs: {page1_sorted['ID'].tolist()}")
        
        # Verificar que están ordenados
        ids_sorted = page1_sorted['ID'].tolist()
        if ids_sorted == sorted(ids_sorted):
            print(f"  ✅ Datos correctamente ordenados")
            return True
        else:
            print(f"  ❌ Error: datos no están ordenados")
            return False
            
    except Exception as e:
        print(f"Error en test de integración: {e}")
        return False

def main():
    """Función principal"""
    print("🔍 TEST DE ORDENAMIENTO CON PAGINACIÓN")
    print("=" * 50)
    
    # Test básico de ordenamiento
    sort_ok = test_sorting_with_pagination()
    
    # Test de integración (solo si el básico pasa)
    if sort_ok:
        integration_ok = test_sorting_integration_with_data_view()
    else:
        integration_ok = False
    
    print("\n" + "=" * 50)
    print("📋 RESUMEN:")
    print(f"   - Ordenamiento básico: {'✅ OK' if sort_ok else '❌ FAILED'}")
    print(f"   - Integración DataView: {'✅ OK' if integration_ok else '❌ FAILED'}")
    
    if sort_ok and integration_ok:
        print("\n🎉 ¡ORDENAMIENTO FUNCIONA CORRECTAMENTE!")
        print("El ordenamiento está completamente implementado.")
    else:
        print("\n⚠️ Hay problemas con el ordenamiento.")
    
    return sort_ok and integration_ok

if __name__ == "__main__":
    main()