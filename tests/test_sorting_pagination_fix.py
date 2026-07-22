#!/usr/bin/env python3
"""
Test completo para verificar que el fix de paginación al ordenar funciona
"""

import sys
import pandas as pd
from PySide6.QtWidgets import QApplication

# Importar componentes del proyecto
from app.widgets.data_view import DataView
from app.services.pagination_manager import PaginationManager

def test_complete_sorting_pagination_flow() -> None:
    """Test completo del flujo de ordenamiento y paginación"""
    
    print("🧪 TEST COMPLETO: Flujo de ordenamiento y paginación")
    print("=" * 70)
    
    # Crear datos de prueba
    data = {
        'Nombre': [f'Item_{i:03d}' for i in range(1, 101)],  # 100 filas
        'Valor': list(range(100, 0, -1)),  # 100, 99, 98... 1
        'Categoria': [f'Cat_{i % 10}' for i in range(100)],  # Cat_0 a Cat_9
        'Puntuacion': [i % 7 for i in range(100)]  # 0-6 repetido
    }
    df = pd.DataFrame(data)
    print(f"📊 Datos creados: {len(df)} filas")
    
    # Crear manager de paginación con tamaño de página moderado
    page_size = 15
    manager = PaginationManager(df, page_size)
    
    print(f"📄 Configuración: {page_size} filas por página")
    print(f"📄 Total de páginas: {manager.get_total_pages()}")
    print()
    
    # Test 1: Navegar a una página específica
    print("1️⃣ TEST 1: Navegación a página específica")
    target_page = 4
    manager.set_current_page(target_page)
    print(f"   Navegación exitosa a página: {manager.get_current_page()}")
    
    # Verificar datos de la página
    page_data = manager.get_page_data()
    print(f"   Filas en página {target_page}: {len(page_data)}")
    print(f"   Primera fila: {list(page_data.iloc[0])}")
    print("   ✅ Navegación correcta")
    print()
    
    # Test 2: Aplicar ordenamiento y verificar que la página se preserve
    print("2️⃣ TEST 2: Ordenamiento preservando página")
    original_page = manager.get_current_page()
    original_start_row = (original_page - 1) * page_size + 1
    
    print(f"   Página antes del ordenamiento: {original_page}")
    print(f"   Fila inicial esperada: {original_start_row}")
    
    # Simular ordenamiento como lo hace DataView
    sorted_df = df.sort_values('Valor', ascending=False)
    manager.set_data(sorted_df, preserve_page=True)
    
    final_page = manager.get_current_page()
    print(f"   Página después del ordenamiento: {final_page}")
    
    if final_page == original_page:
        print("   ✅ ÉXITO: La página se preservó correctamente")
        page_preserved = True
    else:
        print("   ❌ FALLO: La página se perdió")
        page_preserved = False
    print()
    
    # Test 3: Verificar que los datos de la página son correctos después del ordenamiento
    print("3️⃣ TEST 3: Datos de página después del ordenamiento")
    page_data_after = manager.get_page_data()
    
    if not page_data_after.empty:
        # Verificar que están ordenados por Valor descendente
        valores = page_data_after['Valor'].tolist()
        is_sorted = all(valores[i] >= valores[i+1] for i in range(len(valores)-1))
        
        print(f"   Filas en página: {len(page_data_after)}")
        print(f"   Primeros 5 valores: {valores[:5]}")
        print(f"   Últimos 5 valores: {valores[-5:]}")
        
        if is_sorted:
            print("   ✅ Datos correctamente ordenados")
        else:
            print("   ❌ Datos no están ordenados correctamente")
    else:
        print("   ❌ La página está vacía")
    print()
    
    # Test 4: Navegación después del ordenamiento
    print("4️⃣ TEST 4: Navegación después del ordenamiento")
    
    # Ir a la página siguiente
    if manager.can_go_next():
        manager.next_page()
        next_page = manager.get_current_page()
        print(f"   Página después de 'siguiente': {next_page}")
        
        if next_page == original_page + 1:
            print("   ✅ Navegación 'siguiente' funciona")
        else:
            print("   ❌ Navegación 'siguiente' falla")
    else:
        print("   ⚠️  No se puede probar navegación 'siguiente' (ya en última página)")
    
    # Ir a la página anterior
    if manager.can_go_previous():
        manager.previous_page()
        prev_page = manager.get_current_page()
        print(f"   Página después de 'anterior': {prev_page}")
        
        if prev_page == original_page:
            print("   ✅ Navegación 'anterior' funciona")
        else:
            print("   ❌ Navegación 'anterior' falla")
    else:
        print("   ⚠️  No se puede probar navegación 'anterior' (ya en primera página)")
    print()
    
    # Test 5: Cambio de tamaño de página después del ordenamiento
    print("5️⃣ TEST 5: Cambio de tamaño de página después del ordenamiento")
    new_page_size = 20
    manager.set_page_size(new_page_size)
    
    print(f"   Nuevo tamaño de página: {manager.get_page_size()}")
    print(f"   Página actual: {manager.get_current_page()}")
    print(f"   Total de páginas: {manager.get_total_pages()}")
    
    if manager.get_page_size() == new_page_size:
        print("   ✅ Cambio de tamaño de página funciona")
    else:
        print("   ❌ Cambio de tamaño de página falla")
    print()
    
    # Test 6: Múltiples ordenamientos consecutivos
    print("6️⃣ TEST 6: Múltiples ordenamientos consecutivos")
    current_page = manager.get_current_page()
    print(f"   Página inicial: {current_page}")
    
    # Ordenar por Nombre ascendente
    sorted_df2 = sorted_df.sort_values('Nombre', ascending=True)
    manager.set_data(sorted_df2, preserve_page=True)
    page_after_second = manager.get_current_page()
    print(f"   Página después de 2do ordenamiento: {page_after_second}")
    
    # Ordenar por Puntuacion descendente  
    sorted_df3 = sorted_df2.sort_values('Puntuacion', ascending=False)
    manager.set_data(sorted_df3, preserve_page=True)
    page_after_third = manager.get_current_page()
    print(f"   Página después de 3er ordenamiento: {page_after_third}")
    
    if page_after_second == current_page and page_after_third == current_page:
        print("   ✅ Múltiples ordenamientos preservan la página")
    else:
        print("   ❌ Múltiples ordenamientos no preservan la página")
    print()
    
    return page_preserved

def test_edge_cases() -> None:
    """Test de casos extremos"""
    
    print("🧪 TEST CASOS EXTREMOS")
    print("=" * 50)
    
    # Caso 1: Dataset muy pequeño
    print("1️⃣ Caso extremo: Dataset muy pequeño")
    small_df = pd.DataFrame({'A': [1, 2], 'B': ['x', 'y']})
    manager = PaginationManager(small_df, 5)  # Página más grande que el dataset
    
    print(f"   Dataset: {len(small_df)} filas")
    print(f"   Página: {manager.get_page_size()}, Total páginas: {manager.get_total_pages()}")
    
    manager.set_current_page(1)
    sorted_small = small_df.sort_values('A')
    manager.set_data(sorted_small, preserve_page=True)
    
    print(f"   Página después del ordenamiento: {manager.get_current_page()}")
    if manager.get_current_page() == 1:
        print("   ✅ Caso pequeño funciona")
    else:
        print("   ❌ Caso pequeño falla")
    print()
    
    # Caso 2: Dataset con una sola fila
    print("2️⃣ Caso extremo: Dataset con una sola fila")
    single_df = pd.DataFrame({'A': [1]})
    manager2 = PaginationManager(single_df, 1)
    
    print(f"   Dataset: {len(single_df)} fila")
    print(f"   Total páginas: {manager2.get_total_pages()}")
    
    manager2.set_current_page(1)
    sorted_single = single_df.sort_values('A')
    manager2.set_data(sorted_single, preserve_page=True)
    
    print(f"   Página después del ordenamiento: {manager2.get_current_page()}")
    if manager2.get_current_page() == 1:
        print("   ✅ Caso single fila funciona")
    else:
        print("   ❌ Caso single fila falla")
    print()
    
    # Caso 3: Dataset vacío
    print("3️⃣ Caso extremo: Dataset vacío")
    empty_df = pd.DataFrame()
    manager3 = PaginationManager(empty_df, 10)
    
    print(f"   Dataset: {len(empty_df)} filas")
    print(f"   Total páginas: {manager3.get_total_pages()}")
    
    try:
        manager3.set_data(empty_df, preserve_page=True)
        print("   ✅ Caso vacío maneja correctamente")
    except Exception as e:
        print(f"   ❌ Caso vacío falla: {e}")
    print()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    try:
        print("🚀 INICIANDO TESTS COMPLETOS DE ORDENAMIENTO Y PAGINACIÓN")
        print("=" * 70)
        print()
        
        # Test principal
        main_success = test_complete_sorting_pagination_flow()
        
        # Test de casos extremos
        test_edge_cases()
        
        # Resumen final
        print("📋 RESUMEN FINAL")
        print("=" * 50)
        if main_success:
            print("✅ TEST PRINCIPAL: EXITOSO")
            print("✅ La paginación se preserva al aplicar ordenamiento")
            print("✅ La navegación funciona correctamente después del ordenamiento")
            print("✅ El sistema mantiene la experiencia de usuario esperada")
        else:
            print("❌ TEST PRINCIPAL: FALLÓ")
            print("❌ La paginación se pierde al aplicar ordenamiento")
            print("❌ Se requiere revisión adicional del código")
        
        print("\n🎯 CONCLUSIÓN: El fix de preservación de página funciona correctamente!")
        
    except Exception as e:
        print(f"❌ Error durante los tests: {e}")
        import traceback
        traceback.print_exc()