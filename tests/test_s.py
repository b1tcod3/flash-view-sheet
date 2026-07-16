#!/usr/bin/env python3
"""
Test específico para el bug de página 2 vacía
"""

import pandas as pd
from paginacion.pagination_manager import PaginationManager

def test_page2_bug() -> None:
    """Test específico para reproducir el bug de página 2 vacía"""
    print("=" * 60)
    print("🔍 TEST ESPECÍFICO: Bug página 2 vacía")
    print("=" * 60)
    
    # Crear datos de prueba (50 filas, 5 páginas de 10)
    data = {
        'ID': list(range(1, 51)),
        'Nombre': [f'Usuario_{i}' for i in range(1, 51)],
        'Valor': [i * 100 for i in range(1, 51)]
    }
    df = pd.DataFrame(data)
    
    print(f"📊 DataFrame creado: {len(df)} filas")
    print(f"📋 IDs: {df['ID'].min()} a {df['ID'].max()}")
    
    # Crear PaginationManager
    pm = PaginationManager(df, page_size=10)
    
    print(f"\n📖 ESTADO INICIAL:")
    print(f"   - Página actual: {pm.get_current_page()}")
    print(f"   - Total páginas: {pm.get_total_pages()}")
    print(f"   - Tamaño página: {pm.get_page_size()}")
    
    # Verificar página 1
    print(f"\n📄 PÁGINA 1:")
    page1_data = pm.get_page_data()
    print(f"   - Filas en página: {len(page1_data)}")
    if len(page1_data) > 0:
        print(f"   - IDs en página: {page1_data['ID'].min()} a {page1_data['ID'].max()}")
        print(f"   - Datos: {list(page1_data['ID'])}")
    
    # Navegar a página 2
    print(f"\n➡️ NAVEGANDO A PÁGINA 2:")
    pm.next_page()
    
    print(f"   - Página actual después de next_page(): {pm.get_current_page()}")
    print(f"   - Total páginas: {pm.get_total_pages()}")
    
    # Verificar página 2
    print(f"\n📄 PÁGINA 2:")
    page2_data = pm.get_page_data()
    print(f"   - Filas en página: {len(page2_data)}")
    
    if len(page2_data) > 0:
        print(f"   - IDs en página: {page2_data['ID'].min()} a {page2_data['ID'].max()}")
        print(f"   - Datos: {list(page2_data['ID'])}")
        print("   ✅ PÁGINA 2 TIENE DATOS")
    else:
        print("   ❌ BUG CONFIRMADO: PÁGINA 2 ESTÁ VACÍA")
        
        # Debug detallado
        print(f"\n🔍 DEBUG DETALLADO:")
        print(f"   - current_page: {pm.current_page}")
        print(f"   - page_size: {pm.page_size}")
        print(f"   - filtered_df length: {len(pm.filtered_df)}")
        
        start_idx = (pm.current_page - 1) * pm.page_size
        end_idx = min(start_idx + pm.page_size, len(pm.filtered_df))
        
        print(f"   - start_idx calculado: {start_idx}")
        print(f"   - end_idx calculado: {end_idx}")
        print(f"   - Rango iloc: [{start_idx}:{end_idx}]")
        
        if start_idx < len(pm.filtered_df):
            print(f"   - Datos en rango calculado:")
            sample_data = pm.filtered_df.iloc[start_idx:end_idx]
            print(f"     {len(sample_data)} filas")
            if len(sample_data) > 0:
                print(f"     IDs: {list(sample_data['ID'])}")
        else:
            print(f"   - start_idx ({start_idx}) >= length ({len(pm.filtered_df)})")
    
    # Probar navegación manual
    print(f"\n🔧 NAVEGACIÓN MANUAL:")
    pm.set_current_page(2)
    print(f"   - Página después de set_current_page(2): {pm.get_current_page()}")
    
    page2_manual = pm.get_page_data()
    print(f"   - Filas después de navegación manual: {len(page2_manual)}")
    
    if len(page2_manual) > 0:
        print(f"   - IDs: {page2_manual['ID'].min()} a {page2_manual['ID'].max()}")
        print("   ✅ NAVEGACIÓN MANUAL FUNCIONA")
    else:
        print("   ❌ NAVEGACIÓN MANUAL TAMBIÉN FALLA")
    
    # Test de todas las páginas
    print(f"\n📋 TEST COMPLETO DE TODAS LAS PÁGINAS:")
    for page in range(1, pm.get_total_pages() + 1):
        pm.set_current_page(page)
        page_data = pm.get_page_data()
        status = "✅" if len(page_data) > 0 else "❌"
        if len(page_data) > 0:
            print(f"   {status} Página {page}: {len(page_data)} filas (IDs {page_data['ID'].min()}-{page_data['ID'].max()})")
        else:
            print(f"   {status} Página {page}: VACÍA")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_page2_bug()