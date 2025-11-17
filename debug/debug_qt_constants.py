#!/usr/bin/env python3
"""
Debug de los valores Qt para verificar qué está pasando con el ordenamiento
"""

from PySide6.QtCore import Qt
import pandas as pd

def debug_qt_constants():
    """Debug de las constantes Qt"""
    print("=== DEBUG DE CONSTANTES QT ===")
    print(f"Qt.AscendingOrder = {Qt.AscendingOrder}")
    print(f"Qt.DescendingOrder = {Qt.DescendingOrder}")
    print(f"0 = {0}")
    print(f"1 = {1}")
    
    # Test directo con pandas
    print("\n=== TEST DIRECTO CON PANDAS ===")
    data = [10, 5, 15, 3, 20, 8, 12, 1, 25, 7]
    df = pd.DataFrame({'ID': data})
    
    print("Datos originales:", data)
    
    # Ascendente
    df_asc = df.sort_values('ID', ascending=True)
    print("Ascendente (True):", df_asc['ID'].tolist())
    
    # Descendente  
    df_desc = df.sort_values('ID', ascending=False)
    print("Descendente (False):", df_desc['ID'].tolist())
    
    # Test con valores de Qt
    print(f"\n=== TEST CON VALORES QT ===")
    asc_order = Qt.AscendingOrder
    desc_order = Qt.DescendingOrder
    
    print(f"Ascending order value: {asc_order}")
    print(f"Descending order value: {desc_order}")
    
    # Verificar qué pasa cuando uso estos valores
    expected_asc = asc_order == Qt.AscendingOrder
    expected_desc = desc_order == Qt.AscendingOrder
    
    print(f"asc_order == Qt.AscendingOrder: {expected_asc}")
    print(f"desc_order == Qt.AscendingOrder: {expected_desc}")

if __name__ == "__main__":
    debug_qt_constants()