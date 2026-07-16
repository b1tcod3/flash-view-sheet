#!/usr/bin/env python3
"""
Test simple para rastrear exactamente cuándo se pierde la página
"""

import sys
import pandas as pd
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from paginacion.data_view import DataView

def test_page_preservation_debug() -> None:
    """Test que rastrea exactamente cuándo se pierde la página"""
    
    print("🔍 DEBUG: Rastreando pérdida de página")
    print("=" * 50)
    
    # Crear datos pequeños para control total
    data = {'A': list(range(1, 21))}  # 20 filas, 2 páginas de 10
    df = pd.DataFrame(data)
    
    data_view = DataView()
    data_view.set_data(df)
    
    print(f"📊 Datos: {len(df)} filas, {data_view.pagination_manager.get_total_pages()} páginas")
    
    # Paso 1: Ir a página 2
    print("1️⃣ Ir a página 2...")
    data_view.pagination_manager.set_current_page(2)
    page_after_navigation = data_view.pagination_manager.get_current_page()
    print(f"   ✅ Página después de navegación: {page_after_navigation}")
    
    if page_after_navigation != 2:
        print("   ❌ ERROR: Navegación no funcionó")
        return False
    
    # Paso 2: Verificar que el modelo actual tiene los datos correctos
    current_model = data_view.pandas_model
    current_page_data = data_view.pagination_manager.get_page_data()
    print(f"2️⃣ Datos actuales en página 2: {current_page_data['A'].tolist()}")
    
    # Paso 3: Guardar estado antes del ordenamiento
    page_before_sorting = data_view.pagination_manager.get_current_page()
    total_pages_before = data_view.pagination_manager.get_total_pages()
    print(f"3️⃣ Estado antes del ordenamiento:")
    print(f"   - Página actual: {page_before_sorting}")
    print(f"   - Total páginas: {total_pages_before}")
    
    # Paso 4: Interceptar el método set_data para ver cuándo se llama
    original_set_data = data_view.pagination_manager.set_data
    call_count = 0
    
    def debug_set_data(df: pd.DataFrame, preserve_page: bool = True) -> bool:
        nonlocal call_count
        call_count += 1
        print(f"📞 set_data() #{call_count} - preserve_page={preserve_page}, página antes: {data_view.pagination_manager.current_page}")
        result = original_set_data(df, preserve_page)
        print(f"📞 set_data() #{call_count} - página después: {data_view.pagination_manager.current_page}")
        return result
    
    data_view.pagination_manager.set_data = debug_set_data
    
    # Paso 5: Ordenar
    print("4️⃣ Ordenar por columna A...")
    try:
        current_model.sort(0, Qt.DescendingOrder)
        
        # Paso 6: Verificar estado final
        page_after_sorting = data_view.pagination_manager.get_current_page()
        print(f"5️⃣ Estado después del ordenamiento:")
        print(f"   - Página final: {page_after_sorting}")
        print(f"   - Total llamadas a set_data: {call_count}")
        
        if page_after_sorting == page_before_sorting:
            print("   ✅ ÉXITO: Página preservada")
            return True
        else:
            print(f"   ❌ FALLO: Página cambiada de {page_before_sorting} a {page_after_sorting}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR durante ordenamiento: {e}")
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    success = test_page_preservation_debug()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 El test pasó - la página se preserva")
    else:
        print("❌ El test falló - se pierde la página")