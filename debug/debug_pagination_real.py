#!/usr/bin/env python3
"""
Debug del problema de paginación en la aplicación real
"""

import pandas as pd
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from app.widgets.data_view import DataView
from app.services.pagination_manager import PaginationManager
from app.models.pandas_model import VirtualizedPandasModel

def create_test_data():
    """Crear datos de prueba con más de 10 filas"""
    data = {
        'ID': list(range(1, 36)),  # 35 filas
        'Nombre': [f'Usuario_{i}' for i in range(1, 36)],
        'Edad': [20 + i for i in range(35)],
        'Departamento': ['Ventas' if i % 2 == 0 else 'IT' for i in range(35)],
        'Salario': [30000 + i * 1000 for i in range(35)]
    }
    return pd.DataFrame(data)

class DebugWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Debug Paginación - Prueba Real")
        self.setGeometry(200, 200, 1000, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Crear DataView
        self.data_view = DataView()
        layout.addWidget(self.data_view)
        
        # Crear y cargar datos
        df = create_test_data()
        print(f"🔍 DEBUG: Creando DataFrame con {len(df)} filas")
        print(f"Columnas: {list(df.columns)}")
        
        # Cargar datos en DataView
        self.data_view.set_data(df)
        print("✅ DEBUG: Datos cargados en DataView")
        
        # Verificar estado interno
        self.verify_internal_state()
        
        # Mostrar ventana
        self.show()
        
    def verify_internal_state(self):
        """Verificar estado interno del DataView"""
        print("\n=== VERIFICACIÓN DE ESTADO INTERNO ===")
        
        # Verificar DataFrame original
        if self.data_view.original_df is not None:
            print(f"✅ DataFrame original: {len(self.data_view.original_df)} filas")
        else:
            print("❌ DataFrame original: None")
            
        # Verificar PaginationManager
        if self.data_view.pagination_manager is not None:
            pm = self.data_view.pagination_manager
            print(f"✅ PaginationManager creado:")
            print(f"   - Página actual: {pm.get_current_page()}")
            print(f"   - Total páginas: {pm.get_total_pages()}")
            print(f"   - Tamaño página: {pm.get_page_size()}")
            print(f"   - Total filas: {len(pm.filtered_df)}")
            
            # Verificar datos de página actual
            page_data = pm.get_page_data()
            print(f"   - Filas en página actual: {len(page_data)}")
            if len(page_data) > 0:
                print(f"   - Primer ID en página: {page_data.iloc[0]['ID']}")
                print(f"   - Último ID en página: {page_data.iloc[-1]['ID']}")
                
        else:
            print("❌ PaginationManager: None")
            
        # Verificar modelo
        if self.data_view.pandas_model is not None:
            print(f"✅ PandasModel creado:")
            print(f"   - Filas en modelo: {self.data_view.pandas_model.rowCount()}")
        else:
            print("❌ PandasModel: None")
            
        # Verificar tabla
        if self.data_view.table_view is not None:
            print(f"✅ TableView configurado:")
            print(f"   - Modelo establecido: {self.data_view.table_view.model() is not None}")
        else:
            print("❌ TableView: None")
            
        print("=== FIN VERIFICACIÓN ===\n")

def main():
    """Función principal"""
    app = QApplication(sys.argv)
    
    # Crear ventana de debug
    window = DebugWindow()
    
    # Ejecutar aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()