#!/usr/bin/env python3
"""
Test simple para verificar el problema de páginas en blanco
"""

import pandas as pd
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Qt
from app.widgets.data_view import DataView
from app.services.pagination_manager import PaginationManager

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

class SimpleTestWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Test Simple - Sin Virtualización")
        self.setGeometry(100, 100, 1000, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Tabla simple (sin modelo virtualizado)
        self.simple_table = QTableWidget()
        layout.addWidget(self.simple_table)
        
        # Botones para navegación
        layout.addWidget(self.create_navigation_buttons())
        
        # Información de debug
        self.info_label = QWidget()
        self.info_label.setMaximumHeight(100)
        layout.addWidget(self.info_label)
        
        # Crear PaginationManager directamente
        self.pagination_manager = None
        self.setup_pagination()
        
    def create_navigation_buttons(self) -> pd.DataFrame:
        """Crear botones de navegación simples"""
        from PySide6.QtWidgets import QHBoxLayout, QPushButton
        
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Botones
        self.first_btn = QPushButton("⏮️ Primera")
        self.prev_btn = QPushButton("◀️ Anterior")
        self.next_btn = QPushButton("▶️ Siguiente")
        self.last_btn = QPushButton("⏭️ Última")
        
        # Conectar señales
        self.first_btn.clicked.connect(self.first_page)
        self.prev_btn.clicked.connect(self.previous_page)
        self.next_btn.clicked.connect(self.next_page)
        self.last_btn.clicked.connect(self.last_page)
        
        layout.addWidget(self.first_btn)
        layout.addWidget(self.prev_btn)
        layout.addWidget(self.next_btn)
        layout.addWidget(self.last_btn)
        
        return widget
    
    def setup_pagination(self) -> None:
        """Configurar paginación"""
        df = create_test_data()
        self.pagination_manager = PaginationManager(df, page_size=10)
        
        # Conectar señal
        self.pagination_manager.page_changed.connect(self.on_page_changed)
        
        # Mostrar primera página
        self.show_current_page()
        
    def show_current_page(self) -> None:
        """Mostrar página actual en tabla simple"""
        page_data = self.pagination_manager.get_page_data()
        
        print(f"🔍 Debug - Mostrando página {self.pagination_manager.get_current_page()}")
        print(f"   Filas en página: {len(page_data)}")
        print(f"   Primer ID: {page_data.iloc[0]['ID'] if len(page_data) > 0 else 'N/A'}")
        print(f"   Último ID: {page_data.iloc[-1]['ID'] if len(page_data) > 0 else 'N/A'}")
        
        # Configurar tabla
        self.simple_table.setRowCount(len(page_data))
        self.simple_table.setColumnCount(len(page_data.columns))
        self.simple_table.setHorizontalHeaderLabels(page_data.columns.tolist())
        
        # Llenar tabla
        for i, row in page_data.iterrows():
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.simple_table.setItem(i - page_data.index[0], j, item)
        
        # Actualizar información
        self.update_info()
    
    def update_info(self) -> None:
        """Actualizar información de página"""
        page_info = self.pagination_manager.get_page_info()
        from PySide6.QtWidgets import QLabel
        
        # Crear o actualizar etiqueta
        if not hasattr(self, 'info_text') or self.info_text is None:
            layout = self.info_label.layout() if self.info_label.layout() else QVBoxLayout(self.info_label)
            self.info_text = QLabel()
            layout.addWidget(self.info_text)
        
        text = (f"Página {page_info['current_page']} de {page_info['total_pages']} "
               f"({page_info['start_row']}-{page_info['end_row']} de {page_info['total_rows']} filas)")
        self.info_text.setText(text)
        
        # Actualizar estado de botones
        self.update_button_states()
    
    def update_button_states(self) -> None:
        """Actualizar estado de botones"""
        can_prev = self.pagination_manager.can_go_previous()
        can_next = self.pagination_manager.can_go_next()
        
        self.first_btn.setEnabled(can_prev and self.pagination_manager.get_current_page() > 1)
        self.prev_btn.setEnabled(can_prev)
        self.next_btn.setEnabled(can_next)
        self.last_btn.setEnabled(can_next and self.pagination_manager.get_current_page() < self.pagination_manager.get_total_pages())
    
    # Métodos de navegación
    def first_page(self) -> None:
        self.pagination_manager.first_page()
    
    def previous_page(self) -> None:
        self.pagination_manager.previous_page()
    
    def next_page(self) -> None:
        self.pagination_manager.next_page()
    
    def last_page(self) -> None:
        self.pagination_manager.last_page()
    
    def on_page_changed(self, page: int) -> None:
        """Manejar cambio de página"""
        print(f"\n🔄 CAMBIO A PÁGINA {page}")
        self.show_current_page()

def main() -> None:
    """Función principal"""
    app = QApplication(sys.argv)
    
    print("📋 TEST SIMPLE:")
    print("- Este test usa una tabla simple sin virtualización")
    print("- Si funciona correctamente, el problema está en VirtualizedPandasModel")
    print("- Si sigue fallando, el problema está en PaginationManager")
    
    window = SimpleTestWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()