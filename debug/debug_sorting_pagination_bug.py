#!/usr/bin/env python3
"""
Test para verificar el bug de paginación al aplicar ordenamiento
"""

import sys
import pandas as pd
from PySide6.QtWidgets import QApplication

# Importar componentes del proyecto
from app.widgets.data_view import DataView
from app.services.pagination_manager import PaginationManager

def test_sorting_pagination_bug():
    """Test que reproduce el bug de paginación al ordenar"""
    
    print("🧪 TEST: Bug de paginación al aplicar ordenamiento")
    print("=" * 60)
    
    # Crear datos de prueba
    data = {
        'Columna_A': [f'Dato_{i:03d}' for i in range(1, 51)],  # 50 filas
        'Columna_B': list(range(50, 0, -1)),  # Orden descendente
        'Columna_C': [i % 5 for i in range(50)]  # Valores repetidos
    }
    df = pd.DataFrame(data)
    print(f"📊 Datos creados: {len(df)} filas")
    
    # Crear manager de paginación
    page_size = 10
    manager = PaginationManager(df, page_size)
    
    print(f"📄 Configuración: {page_size} filas por página")
    print(f"📄 Total de páginas: {manager.get_total_pages()}")
    print()
    
    # Paso 1: Ir a página 3
    print("1️⃣ Ir a página 3...")
    manager.set_current_page(3)
    print(f"   Página actual: {manager.get_current_page()}")
    print(f"   Información: {manager.get_page_info()}")
    
    # Paso 2: Obtener datos de la página 3 antes del ordenamiento
    page3_before = manager.get_page_data()
    print(f"   Datos página 3 (antes): {list(page3_before['Columna_A'])}")
    print()
    
    # Paso 3: Simular ordenamiento (como lo hace DataView)
    print("2️⃣ Simular ordenamiento (como DataView)...")
    
    # Ordenar datos
    df_sorted = df.sort_values('Columna_B', ascending=False)
    print(f"   Datos ordenados: {len(df_sorted)} filas")
    
    # ESTE ES EL PROBLEMA: set_data() resetea la página a 1
    print("3️⃣ Actualizar datos en PaginationManager...")
    manager.set_data(df_sorted)  # <-- ESTO resetea current_page a 1
    
    print(f"   Página actual después del set_data(): {manager.get_current_page()}")
    print(f"   Información: {manager.get_page_info()}")
    
    # Paso 4: Verificar que la página se perdió
    print()
    print("4️⃣ Verificación del bug:")
    if manager.get_current_page() == 1:
        print("   ❌ BUG CONFIRMADO: La página se resetó a 1")
        print("   ❌ El usuario pierde su posición en la paginación")
        return False
    else:
        print("   ✅ La página se mantuvo correctamente")
        return True

def test_proposed_solution():
    """Test de la solución propuesta"""
    
    print("\n🧪 TEST: Solución propuesta para preservar paginación")
    print("=" * 60)
    
    # Crear datos de prueba
    data = {
        'Columna_A': [f'Dato_{i:03d}' for i in range(1, 51)],
        'Columna_B': list(range(50, 0, -1))
    }
    df = pd.DataFrame(data)
    
    # Crear manager
    page_size = 10
    manager = PaginationManager(df, page_size)
    
    # Ir a página 3
    manager.set_current_page(3)
    original_page = manager.get_current_page()
    print(f"📄 Página original: {original_page}")
    
    # Crear versión corregida del método set_data
    def set_data_preserving_page(manager, df):
        """Versión corregida que preserva la página"""
        old_page = manager.current_page  # Preservar página actual
        old_total = manager.total_pages
        
        # Actualizar datos normalmente
        manager.original_df = df.copy()
        manager.filtered_df = df.copy()
        
        # NO resetear la página, recalcular si es necesario
        manager._update_total_pages()
        
        # Si la página actual sigue siendo válida, mantenerla
        if old_page <= manager.total_pages:
            manager.current_page = old_page
        else:
            # Solo si la página ya no es válida, ir a la última página
            manager.current_page = max(1, manager.total_pages)
        
        # Solo emitir señales si algo cambió realmente
        if old_total != manager.total_pages or old_page != manager.current_page:
            manager.data_changed.emit()
            if old_page != manager.current_page:
                manager.page_changed.emit(manager.current_page)
    
    # Aplicar ordenamiento
    df_sorted = df.sort_values('Columna_B', ascending=False)
    set_data_preserving_page(manager, df_sorted)
    
    print(f"📄 Página después del ordenamiento: {manager.get_current_page()}")
    
    if manager.get_current_page() == original_page:
        print("✅ ÉXITO: La página se mantuvo correctamente")
        return True
    else:
        print("❌ FALLO: La página no se mantuvo")
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    try:
        # Test del bug
        bug_confirmed = not test_sorting_pagination_bug()
        
        # Test de la solución
        solution_works = test_proposed_solution()
        
        print("\n" + "=" * 60)
        print("📋 RESUMEN FINAL:")
        print(f"   Bug confirmado: {'❌ SÍ' if bug_confirmed else '✅ NO'}")
        print(f"   Solución funciona: {'✅ SÍ' if solution_works else '❌ NO'}")
        
        if bug_confirmed and solution_works:
            print("   🎯 CONCLUSIÓN: Problema identificado y solución validada")
        elif bug_confirmed:
            print("   ⚠️  CONCLUSIÓN: Problema confirmado, solución necesita ajustes")
        else:
            print("   ✅ CONCLUSIÓN: No hay bug o ya está corregido")
            
    except Exception as e:
        print(f"❌ Error durante los tests: {e}")
        import traceback
        traceback.print_exc()