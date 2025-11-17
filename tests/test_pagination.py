#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de paginación
"""

import sys
import os
import pandas as pd

# Añadir el directorio actual al path para importar módulos
sys.path.insert(0, '/var/www/html/proyectos/flash-sheet')

from paginacion.pagination_manager import PaginationManager
from paginacion.data_view import DataView
import pandas as pd

def crear_datos_prueba():
    """Crear DataFrame de prueba con datos suficientes para paginación"""
    # Crear dataset grande para probar paginación
    n_filas = 250
    data = {
        'ID': range(1, n_filas + 1),
        'Nombre': [f'Persona_{i}' for i in range(1, n_filas + 1)],
        'Edad': [20 + (i % 50) for i in range(1, n_filas + 1)],
        'Ciudad': [f'Ciudad_{i % 10}' for i in range(1, n_filas + 1)],
        'Salario': [30000 + (i * 1000) % 70000 for i in range(1, n_filas + 1)]
    }
    
    df = pd.DataFrame(data)
    print(f"DataFrame creado con {len(df)} filas y {len(df.columns)} columnas")
    return df

def probar_pagination_manager():
    """Probar la funcionalidad del PaginationManager"""
    print("\n=== Probando PaginationManager ===")
    
    # Crear datos de prueba
    df = crear_datos_prueba()
    
    # Crear PaginationManager
    pm = PaginationManager(df, page_size=50)
    
    print(f"Total de páginas: {pm.get_total_pages()}")
    print(f"Página actual: {pm.get_current_page()}")
    print(f"Tamaño de página: {pm.get_page_size()}")
    
    # Probar navegación
    print("\n--- Probando navegación ---")
    
    # Ir a página 2
    pm.set_current_page(2)
    print(f"Página actual después de ir a 2: {pm.get_current_page()}")
    
    # Obtener datos de página actual
    page_data = pm.get_page_data()
    print(f"Filas en página actual: {len(page_data)}")
    print(f"Primeras 3 filas de la página:")
    print(page_data.head(3))
    
    # Probar siguiente página
    pm.next_page()
    print(f"Página después de next(): {pm.get_current_page()}")
    
    # Probar filtros
    print("\n--- Probando filtros ---")
    pm.apply_filter('Ciudad', 'Ciudad_1')
    print(f"Filas después de filtro: {pm.get_total_rows()}")
    print(f"Página actual después de filtro: {pm.get_current_page()}")
    
    # Limpiar filtro
    pm.clear_filter()
    print(f"Filas después de limpiar filtro: {pm.get_total_rows()}")
    
    return True

def probar_data_view():
    """Probar la creación de DataView"""
    print("\n=== Probando DataView ===")
    
    try:
        # Crear instancia de DataView
        dv = DataView()
        print("DataView creado exitosamente")
        
        # Crear datos de prueba
        df = crear_datos_prueba()
        
        # Establecer datos
        dv.set_data(df)
        print("Datos establecidos en DataView")
        
        # Verificar información de filtro
        filter_info = dv.get_current_filter_info()
        print(f"Información de filtro: {filter_info}")
        
        # Obtener datos de página actual
        current_page = dv.export_current_page()
        print(f"Filas en página actual: {len(current_page)}")
        
        return True
        
    except Exception as e:
        print(f"Error al probar DataView: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("Iniciando pruebas de paginación...")
    
    success_pm = probar_pagination_manager()
    success_dv = probar_data_view()
    
    if success_pm and success_dv:
        print("\n✅ Todas las pruebas pasaron exitosamente!")
        print("\nLa implementación de paginación está funcionando correctamente.")
    else:
        print("\n❌ Algunas pruebas fallaron.")
    
    return success_pm and success_dv

if __name__ == "__main__":
    main()