#!/usr/bin/env python3
"""
Debug detallado para entender el flujo exacto de señales durante el ordenamiento
"""

import sys
import pandas as pd
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from paginacion.data_view import DataView

def debug_signal_flow():
    """Debug del flujo de señales durante ordenamiento"""
    
    print("🔍 DEBUG: Flujo de señales durante ordenamiento")
    print("=" * 60)
    
    # Crear datos
    data = {'A': list(range(10, 0, -1)), 'B': [f'Item_{i}' for i in range(10)]}
    df = pd.DataFrame(data)
    
    data_view = DataView()
    data_view.set_data(df)
    
    # Monitorear señales
    original_set_data = data_view.pagination_manager.set_data
    original_update_view = data_view.update_view
    original_on_page_changed = data_view.on_page_changed
    
    call_log = []
    
    def logged_set_data(df, preserve_page=True):
        print(f"📞 set_data() llamado con preserve_page={preserve_page}, página antes: {data_view.pagination_manager.current_page}")
        result = original_set_data(df, preserve_page)
        print(f"📞 set_data() terminado, página después: {data_view.pagination_manager.current_page}")
        call_log.append(f"set_data({preserve_page})")
        return result
    
    def logged_update_view():
        print(f"📞 update_view() llamado, página actual: {data_view.pagination_manager.current_page}")
        call_log.append("update_view()")
        return original_update_view()
    
    def logged_on_page_changed(page):
        print(f"📞 on_page_changed({page}) llamado")
        call_log.append(f"on_page_changed({page})")
        return original_on_page_changed(page)
    
    # Aplicar monkey patches
    data_view.pagination_manager.set_data = logged_set_data
    data_view.update_view = logged_update_view
    data_view.on_page_changed = logged_on_page_changed
    
    print("1️⃣ Navegar a página 3...")
    data_view.pagination_manager.set_current_page(3)
    print(f"   Página actual: {data_view.pagination_manager.get_current_page()}")
    print()
    
    print("2️⃣ Simular ordenamiento...")
    print("   Estado de llamadas hasta ahora:", call_log)
    call_log.clear()
    
    # Ordenar
    model = data_view.pandas_model
    model.sort(0, Qt.DescendingOrder)
    
    print("   Estado de llamadas durante ordenamiento:", call_log)
    print(f"   Página final: {data_view.pagination_manager.get_current_page()}")
    print()
    
    print("3️⃣ Análisis del flujo:")
    for i, call in enumerate(call_log):
        print(f"   {i+1}. {call}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    debug_signal_flow()