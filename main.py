#!/usr/bin/env python3
"""
Flash View Sheet - Visor de Datos Tabulares
Punto de entrada principal de la aplicación
"""

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableView,
                          QFileDialog, QMessageBox, QProgressDialog, QDockWidget)
from PySide6.QtCore import Qt, QThread, Signal
from app.widgets.info_panel import InfoPanel


class DataLoaderThread(QThread):
    """Hilo para cargar datos en segundo plano"""

    data_loaded = Signal(object)
    error_occurred = Signal(str)

    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath

    def run(self):
        """Ejecutar la carga de datos"""
        try:
            from core.data_handler import cargar_datos
            df = cargar_datos(self.filepath)
            self.data_loaded.emit(df)
        except Exception as e:
            self.error_occurred.emit(str(e))


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flash View Sheet - Visor de Datos Tabulares")
        self.setGeometry(100, 100, 1200, 800)

        # Inicializar componentes
        self.df_original = None
        self.df_vista_actual = None
        self.pandas_model = None
        self.loading_thread = None
        self.info_panel = None

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
        self.create_info_panel()

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

    def create_info_panel(self):
        """Crear el panel de información"""
        self.info_panel = InfoPanel()
        dock_widget = QDockWidget("Información")
        dock_widget.setWidget(self.info_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_widget)

    def abrir_archivo(self):
        """Slot para abrir un archivo"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir archivo de datos",
            "",
            "Archivos de Excel (*.xlsx *.xls);;Archivos CSV (*.csv)")

        if filepath:
            self.mostrar_loading_indicator(filepath)

    def mostrar_loading_indicator(self, filepath):
        """Mostrar indicador de carga mientras se procesa el archivo"""

        # Crear y configurar el diálogo de progreso
        self.progress_dialog = QProgressDialog("Cargando archivo...", "Cancelar", 0, 100)
        self.progress_dialog.setWindowTitle("Cargando datos")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()

        # Crear y ejecutar el hilo de carga
        self.loading_thread = DataLoaderThread(filepath)
        self.loading_thread.data_loaded.connect(self.on_datos_cargados)
        self.loading_thread.error_occurred.connect(self.on_error_carga)
        self.loading_thread.start()

    def on_datos_cargados(self, df):
        """Slot para manejar datos cargados exitosamente"""
        self.df_original = df
        self.df_vista_actual = df

        # Cerrar el diálogo de progreso
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

        # Actualizar interfaz
        self.actualizar_vista()
        self.statusBar().showMessage(f"Datos cargados: {self.loading_thread.filepath}")

        # Actualizar panel de información
        self.info_panel.update_info(df)

    def on_error_carga(self, error_message):
        """Slot para manejar errores de carga"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

        QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo: {error_message}")

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