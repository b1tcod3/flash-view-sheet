#!/usr/bin/env python3
"""
Flash View Sheet - Visor de Datos Tabulares
Punto de entrada principal de la aplicación
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QTableView, QFileDialog, QMessageBox
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flash View Sheet - Visor de Datos")
        self.setGeometry(100, 100, 1200, 800)
        
        # Inicializar componentes
        self.df_original = None
        self.df_vista_actual = None
        self.pandas_model = None
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Aquí se cargará la interfaz desde el archivo .ui
        # Por ahora, creamos una interfaz básica
        self.create_menu_bar()
        self.create_tool_bar()
        self.create_central_widget()
        self.create_status_bar()
        
    def setup_connections(self):
        """Configurar conexiones de señales y slots"""
        pass
        
    def create_menu_bar(self):
        """Crear la barra de menú"""
        menu_bar = self.menuBar()
        
        # Menú Archivo
        archivo_menu = menu_bar.addMenu("&Archivo")
        
        # Acción Abrir
        abrir_action = archivo_menu.addAction("&Abrir...")
        abrir_action.setShortcut("Ctrl+O")
        abrir_action.triggered.connect(self.abrir_archivo)
        
        # Menú Exportar
        exportar_menu = archivo_menu.addMenu("&Exportar como...")
        
        # Acción Salir
        salir_action = archivo_menu.addAction("&Salir")
        salir_action.setShortcut("Ctrl+Q")
        salir_action.triggered.connect(self.close)
        
    def create_tool_bar(self):
        """Crear la barra de herramientas"""
        tool_bar = self.addToolBar("Herramientas")
        
    def create_central_widget(self):
        """Crear el widget central (tabla de datos)"""
        # Crear tabla de datos
        self.tabla_datos = QTableView()
        self.setCentralWidget(self.tabla_datos)
        
    def create_status_bar(self):
        """Crear la barra de estado"""
        self.statusBar().showMessage("Listo para cargar datos")
        
    def abrir_archivo(self):
        """Slot para abrir un archivo"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir archivo de datos",
            "",
            "Archivos de Excel (*.xlsx *.xls);;Archivos CSV (*.csv)")
        
        if filepath:
            self.cargar_datos(filepath)
            
    def cargar_datos(self, filepath):
        """Cargar datos desde un archivo"""
        try:
            from core.data_handler import cargar_datos
            self.df_original = cargar_datos(filepath)
            self.df_vista_actual = self.df_original
            
            # Actualizar interfaz
            self.actualizar_vista()
            self.statusBar().showMessage(f"Datos cargados: {filepath}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo: {str(e)}")
            
    def actualizar_vista(self):
        """Actualizar la vista con los datos actuales"""
        from app.models.pandas_model import PandasTableModel
        
        if self.df_vista_actual is not None:
            self.pandas_model = PandasTableModel(self.df_vista_actual)
            self.tabla_datos.setModel(self.pandas_model)
        
    def closeEvent(self, event):
        """Manejar el cierre de la aplicación"""
        event.accept()

def main():
    """Función principal de la aplicación"""
    app = QApplication(sys.argv)
    
    # Crear ventana principal
    window = MainWindow()
    window.show()
    
    # Ejecutar aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()