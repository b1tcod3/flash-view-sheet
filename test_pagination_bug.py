#!/usr/bin/env python3
"""
Test específico para verificar la corrección del bug de página en blanco
"""

import sys
import os
import pandas as pd

# Añadir el directorio actual al path para importar módulos
sys.path.insert(0, '/var/www/html/proyectos/flash-sheet')

from paginacion.pagination_manager import PaginationManager

def test_pagination_bug():
    """Test específico para verificar que todas las páginas muestren datos correctamente"""
    print("\n=== Test de Bug de Paginación ===")
    
    # Crear datos de prueba con tamaño mayor al default de 10
    n_filas = 35  # Esto creará 4 páginas de 10 filas cada una
    data = {
        'ID': range(1, n_filas + 1),
        'Nombre': [f'Fila_{i}' for i in range(1, n_filas + 1)],
        'Valor': [i * 10 for i in range(1, n_filas + 1)]
    }
    
    df = pd.DataFrame(data)
    print(f"DataFrame creado con {len(df)} filas")
    
    # Crear PaginationManager con tamaño por defecto (10)
    pm = PaginationManager(df, page_size=10)
    
    print(f"Total de páginas esperadas: {len(df) // 10 + (1 if len(df) % 10 > 0 else 0)}")
    print(f"Total de páginas calculadas: {pm.get_total_pages()}")
    
    # Verificar que cada página tenga datos
    for page_num in range(1, pm.get_total_pages() + 1):
        print(f"\n--- Verificando Página {page_num} ---")
        
        # Ir a la página
        pm.set_current_page(page_num)
        
        # Obtener datos de la página
        page_data = pm.get_page_data()
        
        # Verificar que hay datos
        if len(page_data) == 0:
            print(f"❌ ERROR: Página {page_num} está VACÍA!")
            return False
        
        print(f"✅ Página {page_num}: {len(page_data)} filas")
        print(f"   Primer ID: {page_data.iloc[0]['ID']}")
        print(f"   Último ID: {page_data.iloc[-1]['ID']}")
        
        # Verificar que los IDs son correctos para la página
        expected_start = (page_num - 1) * 10 + 1
        expected_end = min(page_num * 10, len(df))
        
        actual_first_id = page_data.iloc[0]['ID']
        actual_last_id = page_data.iloc[-1]['ID']
        
        if actual_first_id != expected_start:
            print(f"❌ ERROR: Primer ID esperado {expected_start}, obtenido {actual_first_id}")
            return False
        
        if actual_last_id != expected_end:
            print(f"❌ ERROR: Último ID esperado {expected_end}, obtenido {actual_last_id}")
            return False
    
    # Verificar información de página para cada página
    print(f"\n--- Verificando información de página ---")
    for page_num in range(1, pm.get_total_pages() + 1):
        pm.set_current_page(page_num)
        page_info = pm.get_page_info()
        
        expected_start_row = (page_num - 1) * 10 + 1
        expected_end_row = min(page_num * 10, len(df))
        
        if page_info['start_row'] != expected_start_row:
            print(f"❌ ERROR: Página {page_num} - start_row esperado {expected_start_row}, obtenido {page_info['start_row']}")
            return False
            
        if page_info['end_row'] != expected_end_row:
            print(f"❌ ERROR: Página {page_num} - end_row esperado {expected_end_row}, obtenido {page_info['end_row']}")
            return False
        
        print(f"✅ Página {page_num}: filas {page_info['start_row']}-{page_info['end_row']}")
    
    return True

def main():
    """Función principal de test"""
    print("Iniciando test de corrección del bug de paginación...")
    
    success = test_pagination_bug()
    
    if success:
        print("\n✅ ¡Bug de página en blanco SOLUCIONADO!")
        print("Todas las páginas muestran datos correctamente.")
    else:
        print("\n❌ El bug de página en blanco persiste.")
    
    return success

if __name__ == "__main__":
    main()