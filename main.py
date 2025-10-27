#!/usr/bin/env python3
"""
Flash View Sheet - Visor de Datos Tabulares
Punto de entrada principal de la aplicación
"""

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableView,
                             QFileDialog, QMessageBox, QProgressDialog, QDockWidget,
                             QComboBox, QLineEdit, QPushButton, QHBoxLayout, QWidget, QInputDialog)
from PySide6.QtCore import Qt, QThread, Signal
from app.widgets.info_panel import InfoPanel
from app.widgets.visualization_panel import VisualizationPanel


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
        self.visualization_panel = None
        self.filter_combo = None
        self.filter_input = None
        self.apply_filter_btn = None
        self.clear_filter_btn = None

        self.setup_ui()
        self.setup_connections()
        self.create_visualization_panel()

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
        if self.apply_filter_btn:
            self.apply_filter_btn.clicked.connect(self.aplicar_filtro)
        if self.clear_filter_btn:
            self.clear_filter_btn.clicked.connect(self.limpiar_filtro)
        if self.filter_input:
            self.filter_input.returnPressed.connect(self.aplicar_filtro)

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

        # Acción Exportar a PDF
        pdf_action = exportar_menu.addAction("&PDF...")
        pdf_action.setShortcut("Ctrl+P")
        pdf_action.triggered.connect(self.exportar_a_pdf)

        # Acción Exportar a Imagen
        imagen_action = exportar_menu.addAction("&Imagen...")
        imagen_action.setShortcut("Ctrl+I")
        imagen_action.triggered.connect(self.exportar_a_imagen)

        # Acción Exportar a SQL
        sql_action = exportar_menu.addAction("&SQL...")
        sql_action.setShortcut("Ctrl+S")
        sql_action.triggered.connect(self.exportar_a_sql)

        # Acción Salir
        salir_action = archivo_menu.addAction("&Salir")
        salir_action.setShortcut("Ctrl+Q")
        salir_action.triggered.connect(self.close)

    def create_tool_bar(self):
        """Crear la barra de herramientas"""
        tool_bar = self.addToolBar("Herramientas")
        self.create_filtering_ui(tool_bar)

    def create_filtering_ui(self, tool_bar):
        """Crear la interfaz de filtrado en la barra de herramientas"""
        # Widget contenedor para los elementos de filtrado
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)

        # ComboBox para selección de columna
        self.filter_combo = QComboBox()
        self.filter_combo.setFixedWidth(150)
        self.filter_combo.setPlaceholderText("Seleccionar columna")
        filter_layout.addWidget(self.filter_combo)

        # LineEdit para término de búsqueda
        self.filter_input = QLineEdit()
        self.filter_input.setFixedWidth(200)
        self.filter_input.setPlaceholderText("Término de búsqueda")
        filter_layout.addWidget(self.filter_input)

        # Botón Aplicar Filtro
        self.apply_filter_btn = QPushButton("Aplicar Filtro")
        filter_layout.addWidget(self.apply_filter_btn)

        # Botón Limpiar Filtro
        self.clear_filter_btn = QPushButton("Limpiar Filtro")
        filter_layout.addWidget(self.clear_filter_btn)

        # Añadir el widget a la barra de herramientas
        tool_bar.addWidget(filter_widget)

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

    def create_visualization_panel(self):
        """Crear el panel de visualizaciones"""
        self.visualization_panel = VisualizationPanel()
        dock_widget = QDockWidget("Visualizaciones")
        dock_widget.setWidget(self.visualization_panel)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock_widget)

    def abrir_archivo(self):
        """Slot para abrir un archivo"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir archivo de datos",
            "",
            "Archivos de Excel (*.xlsx *.xls);;Archivos CSV (*.csv);;Archivos JSON (*.json);;Archivos XML (*.xml)")

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

        # Actualizar panel de visualizaciones
        if self.visualization_panel:
            self.visualization_panel.update_data(df)

        # Poblar el ComboBox con nombres de columnas
        self.filter_combo.clear()
        self.filter_combo.addItems(df.columns.tolist())

        # Limpiar filtros previos
        self.filter_input.clear()
        self.filter_combo.setCurrentIndex(-1)

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

            # Actualizar panel de información
            if self.info_panel:
                self.info_panel.update_info(self.df_original)

            # Actualizar panel de visualizaciones
            if self.visualization_panel:
                self.visualization_panel.update_data(self.df_original)

            # Limpiar filtros previos
            if self.filter_input:
                self.filter_input.clear()
            if self.filter_combo:
                self.filter_combo.setCurrentIndex(-1)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo: {str(e)}")

    def actualizar_vista(self):
        """Actualizar la vista con los datos actuales"""
        from app.models.pandas_model import VirtualizedPandasModel

        if self.df_vista_actual is not None:
            # Usar el modelo virtualizado para mejor rendimiento
            self.pandas_model = VirtualizedPandasModel(self.df_vista_actual)
        self.tabla_datos.setModel(self.pandas_model)

    def aplicar_filtro(self):
        """Aplicar filtro a los datos"""
        if self.df_original is None:
            QMessageBox.warning(self, "Advertencia", "No hay datos cargados para filtrar.")
            return

        columna = self.filter_combo.currentText()
        termino = self.filter_input.text().strip()

        if not columna:
            QMessageBox.warning(self, "Advertencia", "Selecciona una columna para filtrar.")
            return

        if not termino:
            QMessageBox.warning(self, "Advertencia", "Ingresa un término de búsqueda.")
            return

        try:
            from core.data_handler import aplicar_filtro
            self.df_vista_actual = aplicar_filtro(self.df_original, columna, termino)
            self.actualizar_vista()
            self.statusBar().showMessage(f"Filtro aplicado: {len(self.df_vista_actual)} filas mostradas")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al aplicar filtro: {str(e)}")

    def limpiar_filtro(self):
        """Limpiar el filtro y mostrar todos los datos"""
        if self.df_original is None:
            return

        self.df_vista_actual = self.df_original.copy()
        self.actualizar_vista()
        self.filter_input.clear()
        self.filter_combo.setCurrentIndex(-1)  # Deseleccionar columna
        self.statusBar().showMessage(f"Datos restaurados: {len(self.df_vista_actual)} filas mostradas")

    def exportar_a_pdf(self):
        """Exportar datos actuales a PDF"""
        if self.df_vista_actual is None:
            QMessageBox.warning(self, "Advertencia", "No hay datos para exportar.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar como PDF",
            "",
            "Archivos PDF (*.pdf)"
        )

        if filepath:
            from core.data_handler import exportar_a_pdf
            success = exportar_a_pdf(self.df_vista_actual, filepath)
            if success:
                QMessageBox.information(self, "Éxito", f"Datos exportados a {filepath}")
                self.statusBar().showMessage(f"Exportado a PDF: {filepath}")
            else:
                QMessageBox.critical(self, "Error", "No se pudo exportar a PDF.")

    def exportar_a_imagen(self):
        """Exportar vista de tabla a imagen"""
        if self.df_vista_actual is None:
            QMessageBox.warning(self, "Advertencia", "No hay datos para exportar.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar como Imagen",
            "",
            "Archivos de Imagen (*.png *.jpg *.jpeg)"
        )

        if filepath:
            from core.data_handler import exportar_a_imagen
            success = exportar_a_imagen(self.tabla_datos, filepath)
            if success:
                QMessageBox.information(self, "Éxito", f"Imagen exportada a {filepath}")
                self.statusBar().showMessage(f"Exportado a imagen: {filepath}")
            else:
                QMessageBox.critical(self, "Error", "No se pudo exportar a imagen.")

    def exportar_a_sql(self):
        """Exportar datos a base de datos SQL"""
        if self.df_vista_actual is None:
            QMessageBox.warning(self, "Advertencia", "No hay datos para exportar.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar como Base de Datos SQL",
            "",
            "Bases de Datos SQLite (*.db)"
        )

        if filepath:
            nombre_tabla, ok = self.get_text_input("Nombre de la Tabla", "Ingresa el nombre de la tabla:")
            if ok and nombre_tabla:
                from core.data_handler import exportar_a_sql
                success = exportar_a_sql(self.df_vista_actual, filepath, nombre_tabla)
                if success:
                    QMessageBox.information(self, "Éxito", f"Datos exportados a {filepath} en tabla '{nombre_tabla}'")
                    self.statusBar().showMessage(f"Exportado a SQL: {filepath}")
                else:
                    QMessageBox.critical(self, "Error", "No se pudo exportar a SQL.")
            else:
                QMessageBox.warning(self, "Advertencia", "Nombre de tabla requerido.")

    def get_text_input(self, title, label):
        """Obtener entrada de texto del usuario"""
        from PySide6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, title, label)
        return text, ok

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