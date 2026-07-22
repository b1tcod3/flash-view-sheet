#!/usr/bin/env python3
"""
Test específico para el bug en VirtualizedPandasModel
"""

import pandas as pd
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from app.widgets.data_view import DataView
from app.models.pandas_model import VirtualizedPandasModel

def create_test_data() -> pd.DataFrame:
    """Crear datos de prueba con más de 10 filas"""
    data = {
        'ID': list(range(1, 36)),  # 35 filas
        'Nombre': [f'Usuario_{i}' for i in range(1, 36)],
        'Edad': [20 + i for i in range(35)]
    }
    return pd.DataFrame(data)

class VirtualizedModelTest(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Test VirtualizedPandasModel Bug")
        self.setGeometry(100, 100, 800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Crear DataFrame completo
        full_df = create_test_data()
        print(f"🔍 DEBUG: DataFrame completo: {len(full_df)} filas")
        
        # Simular obtener datos de página 1 (filas 1-10)
        page1_data = full_df.iloc[0:10].copy()
        print(f"🔍 DEBUG: Página 1: {len(page1_data)} filas")
        print(f"   IDs: {page1_data['ID'].tolist()}")
        
        # Crear modelo para página 1
        self.model1 = VirtualizedPandasModel(page1_data)
        print(f"🔍 DEBUG: Modelo 1 creado:")
        print(f"   - Virtualización: {self.model1.enable_virtualization}")
        print(f"   - Total filas: {self.model1.rowCount()}")
        print(f"   - Total columnas: {self.model1.columnCount()}")
        
        # Simular obtener datos de página 2 (filas 11-20)
        page2_data = full_df.iloc[10:20].copy()
        print(f"\n🔍 DEBUG: Página 2: {len(page2_data)} filas")
        print(f"   IDs: {page2_data['ID'].tolist()}")
        
        # Crear modelo para página 2
        self.model2 = VirtualizedPandasModel(page2_data)
        print(f"🔍 DEBUG: Modelo 2 creado:")
        print(f"   - Virtualización: {self.model2.enable_virtualization}")
        print(f"   - Total filas: {self.model2.rowCount()}")
        print(f"   - Total columnas: {self.model2.columnCount()}")
        
        # Probar acceso a datos en ambos modelos
        self.test_data_access(self.model1, "Modelo 1")
        self.test_data_access(self.model2, "Modelo 2")
        
        # Crear tabla para visualizar
        from PySide6.QtWidgets import QTableView
        self.table = QTableView()
        layout.addWidget(self.table)
        
        # Establecer primer modelo
        self.table.setModel(self.model1)
        
        # Agregar botones para cambiar entre modelos
        from PySide6.QtWidgets import QHBoxLayout, QPushButton
        button_layout = QHBoxLayout()
        
        self.btn_model1 = QPushButton("Ver Modelo 1 (Página 1)")
        self.btn_model2 = QPushButton("Ver Modelo 2 (Página 2)")
        self.btn_model1.clicked.connect(lambda: self.show_model(self.model1))
        self.btn_model2.clicked.connect(lambda: self.show_model(self.model2))
        
        button_layout.addWidget(self.btn_model1)
        button_layout.addWidget(self.btn_model2)
        layout.addLayout(button_layout)
        
        # Mostrar ventana
        self.show()
        
    def test_data_access(self, model: Any, model_name: str) -> None:
        """Probar acceso a datos en el modelo"""
        print(f"\n🔍 TEST DE ACCESO - {model_name}:")
        
        for row in range(min(3, model.rowCount())):  # Solo primeras 3 filas
            data_list = []
            for col in range(model.columnCount()):
                index = model.index(row, col)
                value = model.data(index, Qt.DisplayRole)
                data_list.append(value)
            
            print(f"   Fila {row}: {data_list}")
            
            # Verificar si los datos son correctos
            expected_first_col = str(row + 1) if model_name == "Modelo 1" else str(row + 11)
            if data_list[0] != expected_first_col:
                print(f"   ❌ ERROR: Esperado {expected_first_col}, obtenido {data_list[0]}")
            else:
                print(f"   ✅ Correcto")
    
    def show_model(self, model: Any) -> None:
        """Cambiar modelo en la tabla"""
        print(f"\n🔄 Cambiando a modelo con {model.rowCount()} filas")
        self.table.setModel(model)

def main() -> None:
    """Función principal"""
    app = QApplication(sys.argv)
    
    print("📋 TEST VIRTUALIZED MODEL:")
    print("1. Crear dos modelos con datos de diferentes páginas")
    print("2. Verificar que ambos modelos muestren datos correctamente")
    print("3. Si un modelo muestra datos en blanco, ese es el bug")
    
    window = VirtualizedModelTest()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()