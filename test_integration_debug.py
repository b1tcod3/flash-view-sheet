#!/usr/bin/env python3
"""
Test de integración para reproducir exactamente el escenario de main.py
"""

import pandas as pd
import sys
import tempfile
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QStackedWidget
from PySide6.QtCore import QThread, Signal

# Simular las importaciones de main.py
from paginacion.data_view import DataView
from core.data_handler import cargar_datos_con_opciones

class DataLoaderThread(QThread):
    """Hilo para cargar datos en segundo plano - idéntico a main.py"""
    data_loaded = Signal(object)
    error_occurred = Signal(str)

    def __init__(self, filepath, skip_rows=0, column_names=None):
        super().__init__()
        self.filepath = filepath
        self.skip_rows = skip_rows
        self.column_names = column_names if column_names else {}

    def run(self):
        """Ejecutar la carga de datos"""
        try:
            df = cargar_datos_con_opciones(self.filepath, self.skip_rows, self.column_names)
            self.data_loaded.emit(df)
        except Exception as e:
            self.error_occurred.emit(str(e))

def create_test_csv():
    """Crear archivo CSV de prueba"""
    data = {
        'ID': list(range(1, 36)),  # 35 filas
        'Nombre': [f'Usuario_{i}' for i in range(1, 36)],
        'Edad': [20 + i for i in range(35)],
        'Departamento': ['Ventas' if i % 2 == 0 else 'IT' for i in range(35)],
        'Salario': [30000 + i * 1000 for i in range(35)]
    }
    df = pd.DataFrame(data)
    
    # Crear archivo temporal
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='')
    df.to_csv(temp_file.name, index=False)
    temp_file.close()
    
    return temp_file.name

class IntegrationTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test de Integración - main.py simulation")
        self.setGeometry(200, 200, 1000, 700)
        
        # Variables idénticas a main.py
        self.df_original = None
        self.df_vista_actual = None
        self.pandas_model = None
        self.loading_thread = None
        self.data_view = None
        self.stacked_widget = None
        
        self.setup_ui()
        self.setup_connections()
        
        # Crear archivo CSV y cargarlo
        self.filepath = create_test_csv()
        self.load_data_async()
        
    def setup_ui(self):
        """Configurar la interfaz idéntica a main.py"""
        # Widget central con stacked widget (igual que main.py)
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Crear vista principal (índice 0)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(QLabel("Cargando..."))
        self.stacked_widget.addWidget(main_widget)
        
        # Vista de Tabla (índice 1) - DataView con paginación (igual que main.py)
        self.data_view = DataView()
        self.stacked_widget.addWidget(self.data_view)
        
        # Establecer vista inicial (igual que main.py)
        self.stacked_widget.setCurrentIndex(0)
        
    def setup_connections(self):
        """Configurar conexiones de señales idénticas a main.py"""
        if self.data_view:
            self.data_view.filter_applied.connect(self.on_filter_applied)
            self.data_view.filter_cleared.connect(self.on_filter_cleared)
            self.data_view.data_updated.connect(self.on_data_updated)
            
    def load_data_async(self):
        """Cargar datos asincrónicamente - idéntico a main.py"""
        print("🔍 TEST: Iniciando carga asíncrona de datos...")
        
        # Crear y ejecutar el hilo de carga (igual que main.py)
        self.loading_thread = DataLoaderThread(self.filepath)
        self.loading_thread.data_loaded.connect(self.on_datos_cargados)
        self.loading_thread.error_occurred.connect(self.on_error_carga)
        self.loading_thread.start()
        
    def on_datos_cargados(self, df):
        """Slot para manejar datos cargados exitosamente - idéntico a main.py"""
        print(f"✅ TEST: Datos cargados: {len(df)} filas")
        self.df_original = df
        self.df_vista_actual = df

        # Establecer datos en DataView (igual que main.py)
        if self.data_view:
            print("🔍 TEST: Estableciendo datos en DataView...")
            self.data_view.set_data(df)
            print("✅ TEST: Datos establecidos en DataView")

        # Cambiar a vista de tabla por defecto (igual que main.py)
        self.switch_view(1)
        
        # Verificar estado después de cargar
        self.verify_integration_state()
        
    def on_error_carga(self, error_message):
        """Slot para manejar errores de carga"""
        print(f"❌ ERROR: {error_message}")
        
    def switch_view(self, index):
        """Cambiar a la vista especificada - idéntico a main.py"""
        print(f"🔍 TEST: Cambiando a vista {index}")
        self.stacked_widget.setCurrentIndex(index)
        
    def on_filter_applied(self, column, term):
        """Slot para manejar filtro aplicado"""
        print(f"🔍 TEST: Filtro aplicado: {column} = {term}")
        
    def on_filter_cleared(self):
        """Slot para manejar filtro limpiado"""
        print("🔍 TEST: Filtro limpiado")
        
    def on_data_updated(self):
        """Slot para manejar datos actualizados"""
        print("🔍 TEST: Datos actualizados")
        # Verificar estado después de actualizar
        self.verify_current_page_data()
        
    def verify_integration_state(self):
        """Verificar estado después de la integración"""
        print("\n=== VERIFICACIÓN DESPUÉS DE INTEGRACIÓN ===")
        
        # Verificar DataFrame original
        if self.df_original is not None:
            print(f"✅ df_original: {len(self.df_original)} filas")
        else:
            print("❌ df_original: None")
            
        # Verificar DataView
        if self.data_view is not None:
            print(f"✅ data_view inicializado")
            
            # Verificar estado interno del DataView
            if hasattr(self.data_view, 'pagination_manager') and self.data_view.pagination_manager is not None:
                pm = self.data_view.pagination_manager
                print(f"✅ PaginationManager inicializado:")
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
                
            # Verificar tabla
            if hasattr(self.data_view, 'table_view') and self.data_view.table_view is not None:
                model = self.data_view.table_view.model()
                print(f"✅ TableView modelo: {model is not None}")
                if model is not None:
                    print(f"   - Filas en modelo: {model.rowCount()}")
            else:
                print("❌ TableView: None")
        else:
            print("❌ data_view: None")
            
        print("=== FIN VERIFICACIÓN ===\n")
        
    def verify_current_page_data(self):
        """Verificar datos de página actual después de actualización"""
        if self.data_view and hasattr(self.data_view, 'pagination_manager'):
            pm = self.data_view.pagination_manager
            page_data = pm.get_page_data()
            print(f"🔍 TEST: Página actual tiene {len(page_data)} filas")
            if len(page_data) > 0:
                print(f"   - IDs: {page_data['ID'].min()} a {page_data['ID'].max()}")
        else:
            print("❌ No se puede verificar página actual")
            
    def closeEvent(self, event):
        """Limpiar archivo temporal al cerrar"""
        if hasattr(self, 'filepath') and os.path.exists(self.filepath):
            os.unlink(self.filepath)
        event.accept()

def main():
    """Función principal"""
    app = QApplication(sys.argv)
    
    # Crear ventana de test
    window = IntegrationTestWindow()
    window.show()
    
    # Ejecutar aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()