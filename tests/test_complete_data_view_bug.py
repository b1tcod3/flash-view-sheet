#!/usr/bin/env python3
"""
Test completo para verificar el bug de páginas en blanco en DataView
"""

import pandas as pd
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from paginacion.data_view import DataView
from paginacion.pagination_manager import PaginationManager

def create_test_data() -> pd.DataFrame:
    """Crear datos de prueba con más de 10 filas"""
    data = {
        'ID': list(range(1, 36)),  # 35 filas
        'Nombre': [f'Usuario_{i}' for i in range(1, 36)],
        'Edad': [20 + i for i in range(35)],
        'Departamento': ['Ventas' if i % 2 == 0 else 'IT' for i in range(35)],
        'Salario': [30000 + i * 1000 for i in range(35)]
    }
    return pd.DataFrame(data)

class TestWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Test Bug Páginas en Blanco - DataView")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Información de debug
        self.debug_label = QLabel("Instrucciones: Ir a página 2 y verificar si hay datos")
        layout.addWidget(self.debug_label)
        
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
        
        # Conectar señales para debug
        self.data_view.pagination_manager.page_changed.connect(self.on_page_changed)
        
        # Mostrar ventana
        self.show()
        
    def on_page_changed(self, page: int) -> None:
        """Debug cuando cambia la página"""
        print(f"\n🔄 CAMBIO DE PÁGINA A: {page}")
        
        # Verificar estado del PaginationManager
        pm = self.data_view.pagination_manager
        page_data = pm.get_page_data()
        page_info = pm.get_page_info()
        
        print(f"   📊 PaginationManager:")
        print(f"      - Página actual: {pm.get_current_page()}")
        print(f"      - Total páginas: {pm.get_total_pages()}")
        print(f"      - Filas en página: {len(page_data)}")
        print(f"      - Rango: {page_info['start_row']}-{page_info['end_row']}")
        
        if len(page_data) > 0:
            print(f"      - Primer ID: {page_data.iloc[0]['ID']}")
            print(f"      - Último ID: {page_data.iloc[-1]['ID']}")
        else:
            print(f"      ❌ ¡PÁGINA VACÍA!")
        
        # Verificar estado del modelo
        if self.data_view.pandas_model is not None:
            model = self.data_view.pandas_model
            print(f"   🗃️ PandasModel:")
            print(f"      - Total filas en modelo: {model.rowCount()}")
            print(f"      - Modelo correcto: {'✅' if model.rowCount() == len(page_data) else '❌'}")
        else:
            print(f"   ❌ PandasModel: None")

def main() -> None:
    """Función principal"""
    app = QApplication(sys.argv)
    
    # Crear ventana de test
    window = TestWindow()
    
    print("📝 INSTRUCCIONES:")
    print("1. Observar que página 1 muestra datos correctamente")
    print("2. Hacer clic en '▶️' para ir a página 2")
    print("3. Verificar si la tabla aparece en blanco")
    print("4. Revisar los logs de debug en la consola")
    
    # Ejecutar aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()