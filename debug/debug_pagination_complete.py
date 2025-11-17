#!/usr/bin/env python3
"""
Test específico para identificar el problema exacto de paginación
"""

import pandas as pd
import sys
from paginacion.data_view import DataView
from paginacion.pagination_manager import PaginationManager
from app.models.pandas_model import VirtualizedPandasModel

def test_pagination_issue():
    """Test para identificar el problema de paginación"""
    print("=== DIAGNÓSTICO DE PROBLEMA DE PAGINACIÓN ===\n")
    
    # 1. Crear datos de prueba
    data = {
        'ID': list(range(1, 36)),  # 35 filas
        'Nombre': [f'Usuario_{i}' for i in range(1, 36)],
        'Valor': [i * 10 for i in range(1, 36)]
    }
    df = pd.DataFrame(data)
    print(f"1. DataFrame creado: {len(df)} filas")
    
    # 2. Probar PaginationManager
    print("\n2. Probando PaginationManager...")
    pm = PaginationManager(df, page_size=10)
    
    for page in range(1, pm.get_total_pages() + 1):
        pm.set_current_page(page)
        page_data = pm.get_page_data()
        print(f"   Página {page}: {len(page_data)} filas (IDs: {page_data.iloc[0]['ID']}-{page_data.iloc[-1]['ID']})")
        
        # Verificar que cada página tiene datos
        if len(page_data) == 0:
            print(f"   ❌ ERROR: Página {page} está vacía!")
            return False
    
    # 3. Probar VirtualizedPandasModel con datos de diferentes páginas
    print("\n3. Probando VirtualizedPandasModel...")
    
    for page in range(1, pm.get_total_pages() + 1):
        pm.set_current_page(page)
        page_data = pm.get_page_data()
        
        print(f"\n   Página {page} ({len(page_data)} filas):")
        
        # Crear modelo con datos de la página
        model = VirtualizedPandasModel(page_data)
        
        # Verificar configuración del modelo
        print(f"     - Virtualización: {model.enable_virtualization}")
        print(f"     - Total filas modelo: {model.rowCount()}")
        print(f"     - Total columnas modelo: {model.columnCount()}")
        
        # Probar acceso a datos
        if model.rowCount() > 0:
            first_cell = model.data(model.index(0, 0))
            last_cell = model.data(model.index(model.rowCount()-1, 0))
            print(f"     - Primera celda: '{first_cell}'")
            print(f"     - Última celda: '{last_cell}'")
            
            # Verificar datos
            expected_first = str(page_data.iloc[0]['ID'])
            expected_last = str(page_data.iloc[-1]['ID'])
            
            if first_cell != expected_first:
                print(f"     ❌ ERROR: Primera celda esperada '{expected_first}', obtenida '{first_cell}'")
                return False
            if last_cell != expected_last:
                print(f"     ❌ ERROR: Última celda esperada '{expected_last}', obtenida '{last_cell}'")
                return False
            print(f"     ✅ Datos correctos")
        else:
            print(f"     ❌ ERROR: Modelo vacío!")
            return False
    
    print("\n✅ TODAS LAS PRUEBAS PASARON - El problema está en la interfaz, no en la lógica")
    return True

def test_data_view_integration():
    """Test de integración completo con DataView"""
    print("\n=== TEST DE INTEGRACIÓN DATAVIEW ===\n")
    
    # Importar PySide6 solo si es necesario
    try:
        from PySide6.QtWidgets import QApplication
        
        # Crear aplicación
        app = QApplication([])
        
        # Crear DataView
        data_view = DataView()
        
        # Crear datos
        data = {
            'ID': list(range(1, 36)),
            'Nombre': [f'Usuario_{i}' for i in range(1, 36)],
            'Valor': [i * 100 for i in range(1, 36)]
        }
        df = pd.DataFrame(data)
        
        # Cargar datos
        data_view.set_data(df)
        print(f"1. Datos cargados en DataView: {len(df)} filas")
        
        # Verificar estado inicial
        pm = data_view.pagination_manager
        print(f"   - Página inicial: {pm.get_current_page()}")
        print(f"   - Total páginas: {pm.get_total_pages()}")
        
        # Probar navegación a cada página
        for page in range(1, pm.get_total_pages() + 1):
            print(f"\n2. Navegando a página {page}...")
            
            # Ir a la página
            pm.set_current_page(page)
            
            # Verificar que el modelo se actualiza correctamente
            model = data_view.pandas_model
            if model is not None:
                print(f"   - Modelo tiene {model.rowCount()} filas")
                
                # Verificar datos en el modelo
                if model.rowCount() > 0:
                    first_cell = model.data(model.index(0, 0))
                    print(f"   - Primera celda: '{first_cell}'")
                    
                    # Verificar que los datos son correctos
                    expected_data = pm.get_page_data()
                    expected_first_id = str(expected_data.iloc[0]['ID'])
                    
                    if first_cell == expected_first_id:
                        print(f"   ✅ Página {page} correcta")
                    else:
                        print(f"   ❌ ERROR: Página {page} incorrecta. Esperado '{expected_first_id}', obtenido '{first_cell}'")
                        return False
                else:
                    print(f"   ❌ ERROR: Modelo vacío en página {page}")
                    return False
            else:
                print(f"   ❌ ERROR: Modelo es None en página {page}")
                return False
        
        print("\n✅ INTEGRACIÓN COMPLETA - El problema podría estar en el hilo de ejecución o las señales")
        return True
        
    except Exception as e:
        print(f"Error en test de integración: {e}")
        return False

def main():
    """Función principal de diagnóstico"""
    print("🔍 DIAGNÓSTICO COMPLETO DEL PROBLEMA DE PAGINACIÓN")
    print("=" * 60)
    
    # Test básico de lógica
    basic_success = test_pagination_issue()
    
    # Test de integración (solo si el básico pasa)
    if basic_success:
        integration_success = test_data_view_integration()
        
        if integration_success:
            print("\n🎯 CONCLUSIÓN:")
            print("La lógica de paginación funciona correctamente.")
            print("El problema está en:")
            print("1. La forma en que DataView maneja las señales de cambio de página")
            print("2. Un posible problema de thread/concurrencia")
            print("3. Un problema en la actualización del modelo en la tabla")
        else:
            print("\n🎯 CONCLUSIÓN:")
            print("Hay un problema en la integración de DataView.")
    else:
        print("\n🎯 CONCLUSIÓN:")
        print("Hay un problema fundamental en la lógica de paginación.")

if __name__ == "__main__":
    main()