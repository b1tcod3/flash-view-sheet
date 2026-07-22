#!/usr/bin/env python3
"""
DEBUG ESPECÍFICO: Bug de página 2 vacía
Reproduce el problema exacto reportado por el usuario
"""

import pandas as pd
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import QTimer
from app.widgets.data_view import DataView

def create_test_data():
    """Crear datos de prueba como en la aplicación real"""
    data = {
        'ID': list(range(1, 51)),  # 50 filas para 5 páginas de 10
        'Nombre': [f'Usuario_{i}' for i in range(1, 51)],
        'Edad': [20 + i for i in range(50)],
        'Departamento': ['Ventas' if i % 2 == 0 else 'IT' for i in range(50)],
        'Salario': [30000 + i * 1000 for i in range(50)]
    }
    return pd.DataFrame(data)

class BugReproductionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BUG DEBUG: Página 2 vacía - Reproducir problema")
        self.setGeometry(200, 200, 1200, 800)
        
        # Crear DataView
        self.data_view = DataView()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Debug info
        debug_layout = QVBoxLayout()
        
        self.status_label = QLabel("Estado: Listo para reproducir bug")
        self.status_label.setStyleSheet("background-color: #ffebee; padding: 10px; border: 1px solid #f44336; border-radius: 5px;")
        debug_layout.addWidget(self.status_label)
        
        # Botones para reproducir el bug
        buttons_layout = QVBoxLayout()
        
        # Paso 1: Cargar datos
        btn_load = QPushButton("1️⃣ CARGAR DATOS (50 filas)")
        btn_load.setStyleSheet("background-color: #2196f3; color: white; padding: 10px; font-weight: bold;")
        btn_load.clicked.connect(self.step1_load_data)
        buttons_layout.addWidget(btn_load)
        
        # Paso 2: Ir a página 2
        btn_page2 = QPushButton("2️⃣ IR A PÁGINA 2 (aquí debería aparecer el bug)")
        btn_page2.setStyleSheet("background-color: #f44336; color: white; padding: 10px; font-weight: bold;")
        btn_page2.clicked.connect(self.step2_go_to_page2)
        buttons_layout.addWidget(btn_page2)
        
        # Paso 3: Verificar estado
        btn_verify = QPushButton("3️⃣ VERIFICAR ESTADO DETALLADO")
        btn_verify.setStyleSheet("background-color: #ff9800; color: white; padding: 10px;")
        btn_verify.clicked.connect(self.step3_verify_state)
        buttons_layout.addWidget(btn_verify)
        
        # Botón para ir manualmente a otras páginas
        manual_buttons_layout = QVBoxLayout()
        manual_buttons_layout.addWidget(QLabel("Prueba manual de páginas:"))
        
        for page_num in range(1, 6):
            btn = QPushButton(f"Ir a página {page_num}")
            btn.setStyleSheet("background-color: #4caf50; color: white; padding: 5px; margin: 2px;")
            btn.clicked.connect(lambda checked, p=page_num: self.manual_go_to_page(p))
            manual_buttons_layout.addWidget(btn)
        
        debug_layout.addLayout(buttons_layout)
        debug_layout.addLayout(manual_buttons_layout)
        layout.addLayout(debug_layout)
        
        # Añadir DataView
        layout.addWidget(self.data_view, 1)
        
    def step1_load_data(self):
        """Paso 1: Cargar datos"""
        print("\n🔍 BUG DEBUG: PASO 1 - Cargando datos...")
        self.status_label.setText("🔍 PASO 1: Cargando datos...")
        
        df = create_test_data()
        print(f"   - DataFrame creado: {len(df)} filas")
        
        self.data_view.set_data(df)
        print("   - Datos establecidos en DataView")
        
        # Verificar estado después de cargar
        self.verify_current_state("Después de cargar datos")
        
    def step2_go_to_page2(self):
        """Paso 2: Ir a página 2 (aquí ocurre el bug)"""
        print("\n🔍 BUG DEBUG: PASO 2 - Navegando a página 2...")
        self.status_label.setText("🔍 PASO 2: Navegando a página 2...")
        
        if self.data_view.pagination_manager:
            current = self.data_view.pagination_manager.get_current_page()
            print(f"   - Página actual antes de navegar: {current}")
            
            self.data_view.pagination_manager.next_page()
            
            new_current = self.data_view.pagination_manager.get_current_page()
            print(f"   - Página actual después de navegar: {new_current}")
            
            # Verificar datos de página 2
            page_data = self.data_view.pagination_manager.get_page_data()
            print(f"   - Datos en página 2: {len(page_data)} filas")
            
            if len(page_data) > 0:
                print(f"   - IDs en página 2: {page_data['ID'].min()}-{page_data['ID'].max()}")
                print("   ✅ PÁGINA 2 TIENE DATOS")
            else:
                print("   ❌ BUG CONFIRMADO: PÁGINA 2 ESTÁ VACÍA")
                self.status_label.setText("❌ BUG CONFIRMADO: Página 2 vacía")
        else:
            print("   ❌ No hay PaginationManager")
            self.status_label.setText("❌ Error: No hay PaginationManager")
            
    def step3_verify_state(self):
        """Paso 3: Verificar estado detallado"""
        print("\n🔍 BUG DEBUG: PASO 3 - Verificando estado detallado...")
        self.status_label.setText("🔍 PASO 3: Verificando estado...")
        
        self.verify_current_state("Verificación manual")
        
    def manual_go_to_page(self, page_num):
        """Navegación manual a página específica"""
        print(f"\n🔍 BUG DEBUG: Navegación manual a página {page_num}")
        self.status_label.setText(f"🔄 Navegando a página {page_num}...")
        
        if self.data_view.pagination_manager:
            pm = self.data_view.pagination_manager
            total_pages = pm.get_total_pages()
            current = pm.get_current_page()
            
            print(f"   - Estado actual: página {current}/{total_pages}")
            
            # Navegar usando next_page() repetidamente
            while pm.get_current_page() < page_num:
                pm.next_page()
                if pm.get_current_page() > total_pages:
                    break
                    
            new_current = pm.get_current_page()
            print(f"   - Estado después: página {new_current}")
            
            # Verificar datos
            page_data = pm.get_page_data()
            print(f"   - Datos en página {new_current}: {len(page_data)} filas")
            
            if len(page_data) > 0:
                print(f"   - IDs: {page_data['ID'].min()}-{page_data['ID'].max()}")
                print(f"   ✅ PÁGINA {new_current} TIENE DATOS")
                self.status_label.setText(f"✅ Página {new_current}: {len(page_data)} filas")
            else:
                print(f"   ❌ BUG: PÁGINA {new_current} ESTÁ VACÍA")
                self.status_label.setText(f"❌ Bug en página {new_current}: vacía")
        else:
            print("   ❌ No hay PaginationManager")
            
    def verify_current_state(self, context):
        """Verificar estado actual del sistema"""
        print(f"\n--- VERIFICACIÓN: {context} ---")
        
        if self.data_view is None:
            print("❌ DataView: None")
            return
            
        print(f"✅ DataView: existe")
        
        # Verificar DataFrame original
        if self.data_view.original_df is not None:
            print(f"✅ DataFrame original: {len(self.data_view.original_df)} filas")
        else:
            print("❌ DataFrame original: None")
            
        # Verificar PaginationManager
        if self.data_view.pagination_manager is not None:
            pm = self.data_view.pagination_manager
            print(f"✅ PaginationManager: existe")
            
            current_page = pm.get_current_page()
            total_pages = pm.get_total_pages()
            page_size = pm.get_page_size()
            
            print(f"   - Página actual: {current_page}")
            print(f"   - Total páginas: {total_pages}")
            print(f"   - Tamaño página: {page_size}")
            
            # Verificar datos filtrados
            if hasattr(pm, 'filtered_df') and pm.filtered_df is not None:
                print(f"   - DataFrame filtrado: {len(pm.filtered_df)} filas")
            else:
                print("   ❌ DataFrame filtrado: None o no existe")
                
            # Verificar datos de página actual
            page_data = pm.get_page_data()
            print(f"   - Datos en página actual: {len(page_data)} filas")
            
            if len(page_data) > 0:
                print(f"   - IDs en página: {page_data['ID'].min()}-{page_data['ID'].max()}")
            else:
                print(f"   ❌ PÁGINA {current_page} ESTÁ VACÍA")
                
        else:
            print("❌ PaginationManager: None")
            
        # Verificar modelo de tabla
        if self.data_view.table_view is not None:
            model = self.data_view.table_view.model()
            if model is not None:
                print(f"✅ Modelo tabla: {model.rowCount()} filas")
            else:
                print("❌ Modelo tabla: None")
        else:
            print("❌ TableView: None")
            
        print("--- FIN VERIFICACIÓN ---\n")

def main():
    """Función principal para debug del bug"""
    print("=" * 70)
    print("🐛 DEBUG ESPECÍFICO: Bug de página 2 vacía")
    print("=" * 70)
    print("Este test reproduce exactamente el problema reportado:")
    print("1. Cargar datos (50 filas = 5 páginas)")
    print("2. Ir a página 2")
    print("3. Verificar que aparece vacía")
    print("=" * 70)
    
    app = QApplication(sys.argv)
    
    window = BugReproductionWindow()
    window.show()
    
    print("\n🚀 Aplicación de debug iniciada.")
    print("Siga los pasos en orden para reproducir el bug.")
    
    return app.exec()

if __name__ == "__main__":
    try:
        result = main()
        print(f"\n✅ Debug finalizado (código: {result})")
    except Exception as e:
        print(f"\n❌ Error en debug: {str(e)}")
        import traceback
        traceback.print_exc()