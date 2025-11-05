#!/usr/bin/env python3
"""
Test crítico: Simular exactamente el flujo de main.py con debug profundo
"""

import pandas as pd
import sys
import tempfile
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread, Signal, QTimer

# Importar módulos exactos de main.py
from core.data_handler import cargar_datos_con_opciones
from paginacion.data_view import DataView

class RealDataLoaderThread(QThread):
    """Hilo real de carga de datos como en main.py"""
    data_loaded = Signal(object)
    error_occurred = Signal(str)

    def __init__(self, filepath, skip_rows=0, column_names=None):
        super().__init__()
        self.filepath = filepath
        self.skip_rows = skip_rows
        self.column_names = column_names if column_names else {}

    def run(self):
        """Ejecutar la carga de datos exactamente como main.py"""
        print("🔍 REAL: Iniciando carga de datos...")
        try:
            df = cargar_datos_con_opciones(self.filepath, self.skip_rows, self.column_names)
            print(f"✅ REAL: Datos cargados exitosamente: {len(df)} filas, {len(df.columns)} columnas")
            print(f"   Columnas: {list(df.columns)}")
            self.data_loaded.emit(df)
        except Exception as e:
            print(f"❌ REAL: Error en carga: {str(e)}")
            self.error_occurred.emit(str(e))

def create_real_test_file():
    """Crear archivo CSV real para probar"""
    data = {
        'ID': list(range(1, 51)),  # 50 filas para tener múltiples páginas
        'Nombre': [f'Empleado_{i:03d}' for i in range(1, 51)],
        'Edad': [25 + (i % 40) for i in range(50)],
        'Departamento': ['Ventas', 'IT', 'RRHH', 'Marketing', 'Finanzas'] * 10,
        'Salario': [25000 + i * 500 for i in range(50)],
        'Fecha_Ingreso': pd.date_range('2020-01-01', periods=50, freq='D'),
        'Activo': [True if i % 3 == 0 else False for i in range(50)]
    }
    df = pd.DataFrame(data)
    
    # Crear archivo temporal
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='')
    df.to_csv(temp_file.name, index=False)
    temp_file.close()
    
    return temp_file.name, df

def test_main_flow():
    """Test del flujo principal como en main.py"""
    print("=== TEST CRÍTICO: Flujo Principal de main.py ===")
    
    app = QApplication(sys.argv)
    
    # Variables como en main.py
    data_view = None
    loading_thread = None
    df_original = None
    
    print("🔍 REAL: Creando DataView...")
    data_view = DataView()
    print("✅ REAL: DataView creado")
    
    # Verificar estado inicial del DataView
    print("\n--- ESTADO INICIAL DEL DATAVIEW ---")
    print(f"   - original_df: {data_view.original_df is not None}")
    print(f"   - pagination_manager: {data_view.pagination_manager is not None}")
    print(f"   - pandas_model: {data_view.pandas_model is not None}")
    print(f"   - table_view modelo: {data_view.table_view.model() is not None if data_view.table_view else False}")
    
    print("\n🔍 REAL: Creando archivo de prueba...")
    filepath, expected_df = create_real_test_file()
    print(f"✅ REAL: Archivo creado: {filepath}")
    print(f"   - Filas esperadas: {len(expected_df)}")
    
    print("\n🔍 REAL: Iniciando carga asíncrona...")
    
    def on_data_loaded(df):
        nonlocal data_view, df_original
        print(f"\n✅ REAL: Slot on_datos_cargados ejecutado")
        print(f"   - DataFrame recibido: {len(df)} filas")
        print(f"   - Columnas: {list(df.columns)}")
        
        # Variables como en main.py
        df_original = df
        
        print(f"   - Estableciendo datos en DataView...")
        data_view.set_data(df)
        print("✅ REAL: Datos establecidos en DataView")
        
        # Verificar estado después de set_data
        print(f"\n--- ESTADO DESPUÉS DE SET_DATA ---")
        print(f"   - original_df: {len(data_view.original_df)} filas" if data_view.original_df is not None else "   - original_df: None")
        print(f"   - pagination_manager: {data_view.pagination_manager is not None}")
        
        if data_view.pagination_manager is not None:
            pm = data_view.pagination_manager
            page_data = pm.get_page_data()
            print(f"   - Página actual: {pm.get_current_page()}/{pm.get_total_pages()}")
            print(f"   - Filas en página: {len(page_data)}")
            if len(page_data) > 0:
                print(f"   - IDs en página: {page_data['ID'].min()}-{page_data['ID'].max()}")
        
        print(f"   - table_view modelo: {data_view.table_view.model() is not None if data_view.table_view else False}")
        if data_view.table_view and data_view.table_view.model():
            model = data_view.table_view.model()
            print(f"   - Filas en modelo: {model.rowCount()}")
        
        # Test de navegación manual
        print(f"\n🔍 REAL: Probando navegación manual...")
        if data_view.pagination_manager and data_view.pagination_manager.get_total_pages() > 1:
            print("   - Navegando a página 2...")
            data_view.pagination_manager.next_page()
            
            if data_view.pagination_manager:
                page_data = data_view.pagination_manager.get_page_data()
                print(f"   - Después de navegar: {len(page_data)} filas")
                if len(page_data) > 0:
                    print(f"   - IDs después de navegar: {page_data['ID'].min()}-{page_data['ID'].max()}")
        
        # Timer para verificar estado después de un tiempo
        QTimer.singleShot(1000, lambda: verify_final_state(data_view, expected_df))
        
    def on_error(error_message):
        print(f"❌ REAL: Error de carga: {error_message}")
        
    # Crear y ejecutar hilo de carga (como main.py)
    loading_thread = RealDataLoaderThread(filepath)
    loading_thread.data_loaded.connect(on_data_loaded)
    loading_thread.error_occurred.connect(on_error)
    loading_thread.start()
    
    print("🔍 REAL: Hilo de carga iniciado, esperando...")
    
    # Ejecutar aplicación por un tiempo y luego salir
    def quit_app():
        print("\n🔍 REAL: Finalizando test...")
        
        # Limpiar archivo temporal
        if os.path.exists(filepath):
            os.unlink(filepath)
            
        app.quit()
        
    # Timer para salir después de 5 segundos
    QTimer.singleShot(5000, quit_app)
    
    return app.exec()

def verify_final_state(data_view, expected_df):
    """Verificar estado final después de la carga"""
    print(f"\n--- VERIFICACIÓN FINAL ---")
    
    if data_view.original_df is not None:
        print(f"✅ DataFrame original: {len(data_view.original_df)} filas")
    else:
        print("❌ DataFrame original: None")
        
    if data_view.pagination_manager is not None:
        pm = data_view.pagination_manager
        page_data = pm.get_page_data()
        print(f"✅ PaginationManager: Página {pm.get_current_page()}/{pm.get_total_pages()}")
        print(f"   - Filas en página actual: {len(page_data)}")
        if len(page_data) > 0:
            print(f"   - Rango de IDs: {page_data['ID'].min()}-{page_data['ID'].max()}")
    else:
        print("❌ PaginationManager: None")
        
    if data_view.table_view and data_view.table_view.model():
        model = data_view.table_view.model()
        print(f"✅ TableView modelo: {model.rowCount()} filas")
    else:
        print("❌ TableView o modelo: None")

if __name__ == "__main__":
    print("Iniciando test crítico del flujo de main.py...")
    try:
        result = test_main_flow()
        print(f"Test finalizado con código: {result}")
    except Exception as e:
        print(f"❌ Error en test: {str(e)}")
        import traceback
        traceback.print_exc()