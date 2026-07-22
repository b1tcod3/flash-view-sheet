#!/usr/bin/env python3
"""
Test específico para diagnosticar el problema de visualización de páginas en la aplicación real
"""

import pandas as pd
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import QTimer
from app.widgets.data_view import DataView

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

class VisualDebugWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Debug Visualización - Paginación")
        self.setGeometry(100, 100, 1200, 800)
        
        # Crear DataView
        self.data_view = DataView()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Debug info
        debug_layout = QHBoxLayout()
        self.status_label = QLabel("Estado: Inicializando...")
        debug_layout.addWidget(self.status_label)
        
        # Botones de test manual
        test_buttons_layout = QHBoxLayout()
        
        btn_load = QPushButton("Cargar Datos")
        btn_load.clicked.connect(self.load_data)
        test_buttons_layout.addWidget(btn_load)
        
        btn_page2 = QPushButton("Ir a Página 2")
        btn_page2.clicked.connect(self.go_to_page2)
        test_buttons_layout.addWidget(btn_page2)
        
        btn_page3 = QPushButton("Ir a Página 3")
        btn_page3.clicked.connect(self.go_to_page3)
        test_buttons_layout.addWidget(btn_page3)
        
        btn_test_next = QPushButton("Siguiente Página")
        btn_test_next.clicked.connect(self.test_next_page)
        test_buttons_layout.addWidget(btn_test_next)
        
        debug_layout.addLayout(test_buttons_layout)
        layout.addLayout(debug_layout)
        
        # Añadir DataView
        layout.addWidget(self.data_view)
        
        # Timer para debug periódico
        self.debug_timer = QTimer()
        self.debug_timer.timeout.connect(self.update_debug_info)
        self.debug_timer.start(2000)  # Cada 2 segundos
        
    def load_data(self) -> None:
        """Cargar datos de prueba"""
        self.status_label.setText("Estado: Cargando datos...")
        
        df = create_test_data()
        print(f"🔍 VISUAL: Cargando {len(df)} filas")
        
        self.data_view.set_data(df)
        
        self.status_label.setText("Estado: Datos cargados")
        print("✅ VISUAL: Datos establecidos")
        
    def go_to_page2(self) -> None:
        """Ir a página 2 manualmente"""
        if self.data_view.pagination_manager:
            print("🔍 VISUAL: Navegando a página 2...")
            self.data_view.pagination_manager.next_page()
            self.status_label.setText("Estado: Navegando a página 2")
            
    def go_to_page3(self) -> None:
        """Ir a página 3 manualmente"""
        if self.data_view.pagination_manager:
            print("🔍 VISUAL: Navegando a página 3...")
            for _ in range(2):  # Página 1 -> 2 -> 3
                self.data_view.pagination_manager.next_page()
            self.status_label.setText("Estado: Navegando a página 3")
            
    def test_next_page(self) -> None:
        """Test navegación siguiente página"""
        if self.data_view.pagination_manager:
            current = self.data_view.pagination_manager.get_current_page()
            print(f"🔍 VISUAL: Página actual: {current}")
            self.data_view.pagination_manager.next_page()
            
    def update_debug_info(self) -> None:
        """Actualizar información de debug"""
        if self.data_view.pagination_manager is not None:
            pm = self.data_view.pagination_manager
            page_data = pm.get_page_data()
            
            status_text = (f"Estado: Página {pm.get_current_page()}/{pm.get_total_pages()} "
                         f"({len(page_data)} filas)")
            self.status_label.setText(status_text)
            
            if len(page_data) > 0:
                ids = f"{page_data['ID'].min()}-{page_data['ID'].max()}"
                print(f"🔍 DEBUG: {status_text}, IDs: {ids}")
        else:
            self.status_label.setText("Estado: Sin paginación")

def main() -> None:
    """Función principal"""
    app = QApplication(sys.argv)
    
    # Crear ventana de debug
    window = VisualDebugWindow()
    window.show()
    
    # Ejecutar aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()