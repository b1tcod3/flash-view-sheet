#!/usr/bin/env python3
"""
Flash View Sheet - Visor de Datos Tabulares
Punto de entrada principal de la aplicación
"""

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableView,
                               QFileDialog, QMessageBox, QProgressDialog, QDockWidget,
                               QComboBox, QLineEdit, QPushButton, QHBoxLayout, QWidget, QInputDialog,
                               QStackedWidget, QDialog)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon, QPixmap
from app.widgets.main_view import MainView
from app.widgets.info_modal import InfoModal
from app.widgets.graphics_view import GraphicsView
from app.widgets.pivot_table_widget import PivotTableWidget
from paginacion.data_view import DataView
from app.widgets.join.joined_data_view import JoinedDataView
from core.data_handler import ExcelTemplateSplitter
from core.join.join_history import JoinHistory
import pandas as pd

class DataLoaderThread(QThread):
    """Hilo para cargar datos en segundo plano"""

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
            from core.data_handler import cargar_datos_con_opciones
            df = cargar_datos_con_opciones(self.filepath, self.skip_rows, self.column_names)
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
        # Removed old panels as they are now in separate views
        self.main_view = None
        self.data_view = None
        self.info_modal = None
        self.graphics_view = None
        self.stacked_widget = None
        self.filter_combo = None
        self.filter_input = None
        self.apply_filter_btn = None
        self.clear_filter_btn = None
        self.view_main_btn = None
        self.view_data_btn = None
        self.view_info_btn = None
        self.view_graphics_btn = None
        self.view_joined_data_btn = None
        # self.view_pivot_table_btn = None  # Ya no se usa
        # self.pivot_table_view = None      # Ya no se usa como vista separada
        self.joined_data_view = None

        # Referencias para funcionalidad de separación
        self.separar_menu = None
        self.exportar_separado_action = None

        # Referencias para funcionalidad de datos
        self.datos_menu = None
        self.cruzar_datos_action = None

        # Sistema de historial de joins
        self.join_history = JoinHistory()

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
        self.create_views()

    def setup_connections(self):
        """Configurar conexiones de señales y slots"""
        # Conectar señal de recarga con opciones desde la vista principal
        if self.main_view:
            self.main_view.reload_with_options.connect(self.on_reload_with_options)
            
            
        # Conectar señales de DataView
        if self.data_view:
            self.data_view.filter_applied.connect(self.on_filter_applied)
            self.data_view.filter_cleared.connect(self.on_filter_cleared)
            self.data_view.data_updated.connect(self.on_data_updated)

    def create_menu_bar(self):
        """Crear la barra de menú"""
        menu_bar = self.menuBar()

        # Menú Archivo
        archivo_menu = menu_bar.addMenu("&Archivo")

        # Acción Abrir
        abrir_action = archivo_menu.addAction("&Abrir...")
        abrir_action.setShortcut("Ctrl+O")
        abrir_action.triggered.connect(self.abrir_archivo)

        # Acción Cargar Carpeta
        cargar_carpeta_action = archivo_menu.addAction("&Cargar Carpeta...")
        cargar_carpeta_action.setShortcut("Ctrl+Shift+O")
        cargar_carpeta_action.triggered.connect(self.cargar_carpeta)

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

        # Acción Exportar a XLSX
        xlsx_action = exportar_menu.addAction("&XLSX...")
        xlsx_action.setShortcut("Ctrl+X")
        xlsx_action.triggered.connect(self.exportar_a_xlsx)

        # Acción Exportar a CSV
        csv_action = exportar_menu.addAction("&CSV...")
        csv_action.setShortcut("Ctrl+C")
        csv_action.triggered.connect(self.exportar_a_csv)

        # Acción Exportar a SQL
        sql_action = exportar_menu.addAction("&SQL...")
        sql_action.setShortcut("Ctrl+S")
        sql_action.triggered.connect(self.exportar_a_sql)

        # Acción Salir
        salir_action = archivo_menu.addAction("&Salir")
        salir_action.setShortcut("Ctrl+Q")
        salir_action.triggered.connect(self.close)

        # Nuevo Menú Separar
        separar_menu = menu_bar.addMenu("&Separar")

        # Acción Exportar Datos Separados
        exportar_separado_action = separar_menu.addAction("&Exportar Datos Separados...")
        exportar_separado_action.setShortcut("Ctrl+Shift+S")
        exportar_separado_action.triggered.connect(self.exportar_datos_separados)
        exportar_separado_action.setEnabled(False)  # Se habilita solo con datos cargados

        # Nuevo Menú Datos
        datos_menu = menu_bar.addMenu("&Datos")

        # Acción Cruzar Datos
        cruzar_datos_action = datos_menu.addAction("&Cruzar Datos...")
        cruzar_datos_action.setShortcut("Ctrl+Shift+J")
        cruzar_datos_action.triggered.connect(self.abrir_cruzar_datos)
        cruzar_datos_action.setEnabled(False)  # Se habilita solo con datos cargados

        # Nuevo Menú Tabla Pivote
        tabla_pivote_menu = menu_bar.addMenu("&Tabla Pivote")

        # Acción Pivot Simple
        pivot_simple_action = tabla_pivote_menu.addAction("&Simple...")
        pivot_simple_action.setShortcut("Ctrl+Alt+S")
        pivot_simple_action.triggered.connect(self.abrir_pivot_simple)
        pivot_simple_action.setEnabled(False)  # Se habilita solo con datos cargados

        # Acción Pivot Combinada
        pivot_combinada_action = tabla_pivote_menu.addAction("&Combinada...")
        pivot_combinada_action.setShortcut("Ctrl+Alt+C")
        pivot_combinada_action.triggered.connect(self.abrir_pivot_combinada)
        pivot_combinada_action.setEnabled(False)  # Se habilita solo con datos cargados

        # Separador
        tabla_pivote_menu.addSeparator()

        # Acción Exportar Resultado de Pivote
        export_pivot_action = tabla_pivote_menu.addAction("&Exportar Datos Actuales...")
        export_pivot_action.setShortcut("Ctrl+Alt+E")
        export_pivot_action.triggered.connect(self.exportar_resultado_pivote)
        export_pivot_action.setEnabled(False)  # Se habilita solo con datos cargados

        # Menú Ayuda
        ayuda_menu = menu_bar.addMenu("&Ayuda")

        # Acción Acerca de
        acerca_de_action = ayuda_menu.addAction("&Acerca de...")
        acerca_de_action.setShortcut("F1")
        acerca_de_action.triggered.connect(self.mostrar_acerca_de)

        # Guardar referencias a los menús para habilitar/deshabilitar
        self.separar_menu = separar_menu
        self.exportar_separado_action = exportar_separado_action
        self.datos_menu = datos_menu
        self.cruzar_datos_action = cruzar_datos_action
        self.tabla_pivote_menu = tabla_pivote_menu
        self.pivot_simple_action = pivot_simple_action
        self.pivot_combinada_action = pivot_combinada_action
        self.export_pivot_action = export_pivot_action

    def create_tool_bar(self):
        """Crear la barra de herramientas"""
        tool_bar = self.addToolBar("Herramientas")
        self.create_view_switcher_ui(tool_bar)
        # Nota: Los filtros ahora están integrados en DataView

    def create_view_switcher_ui(self, tool_bar):
        """Crear la interfaz para cambiar vistas en la barra de herramientas"""
        # Widget contenedor para los botones de vista
        view_widget = QWidget()
        view_layout = QHBoxLayout(view_widget)

        # Botón Vista Principal
        self.view_main_btn = QPushButton("Vista Principal")
        self.view_main_btn.clicked.connect(lambda: self.switch_view(0))
        view_layout.addWidget(self.view_main_btn)

        # Botón Vista de Datos
        self.view_data_btn = QPushButton("Vista de Datos")
        self.view_data_btn.clicked.connect(lambda: self.switch_view(1))
        view_layout.addWidget(self.view_data_btn)

        # Botón Vista Información
        self.view_info_btn = QPushButton("Vista Información")
        self.view_info_btn.clicked.connect(self.show_info_modal)
        view_layout.addWidget(self.view_info_btn)


        # Botón Vista Gráficos
        self.view_graphics_btn = QPushButton("Vista Gráficos")
        self.view_graphics_btn.clicked.connect(lambda: self.switch_view(2))
        view_layout.addWidget(self.view_graphics_btn)

        # Botón Vista Datos Cruzados
        self.view_joined_data_btn = QPushButton("Cruzar Datos")
        self.view_joined_data_btn.clicked.connect(lambda: self.switch_view(3))
        self.view_joined_data_btn.setEnabled(False)  # Se habilita cuando hay resultados de join
        view_layout.addWidget(self.view_joined_data_btn)

        # Añadir el widget a la barra de herramientas
        tool_bar.addWidget(view_widget)

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
        """Crear el widget central con stacked views"""
        # Crear stacked widget para las vistas
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

    def create_status_bar(self):
        """Crear la barra de estado"""
        self.statusBar().showMessage("Listo para cargar datos")


    def create_views(self):
        """Crear las vistas y añadirlas al stacked widget"""
        # Vista Principal (índice 0)
        self.main_view = MainView()
        self.main_view.file_loaded.connect(self.on_file_loaded_from_main_view)
        self.stacked_widget.addWidget(self.main_view)

        # Vista de Tabla (índice 1) - DataView con paginación
        self.data_view = DataView()
        self.stacked_widget.addWidget(self.data_view)

        # Vista de Información (índice 2) - modal
        # Se muestra mediante show_info_modal()

        # Vista de Gráficos (índice 3)
        self.graphics_view = GraphicsView()
        self.stacked_widget.addWidget(self.graphics_view)

        # Vista de Datos Cruzados (índice 4)
        self.joined_data_view = JoinedDataView()
        self.joined_data_view.new_join_requested.connect(self.abrir_cruzar_datos)
        self.stacked_widget.addWidget(self.joined_data_view)

        # Vista de Tabla Pivote eliminada - ahora se usa a través de diálogos

        # Establecer vista inicial
        self.stacked_widget.setCurrentIndex(0)

    def switch_view(self, index):
        """Cambiar a la vista especificada"""
        self.stacked_widget.setCurrentIndex(index)

    def show_info_modal(self):
        """Mostrar el modal de información"""
        if self.df_original is not None:
            if self.info_modal is None:
                self.info_modal = InfoModal(self)
            filename = os.path.basename(self.loading_thread.filepath) if self.loading_thread else "Archivo cargado"
            self.info_modal.update_info(self.df_original, filename)
            self.info_modal.exec()
        else:
            QMessageBox.warning(self, "Advertencia", "No hay datos cargados para mostrar información.")

    def abrir_archivo(self):
        """Slot para abrir un archivo"""
        from core.data_handler import get_supported_file_formats
        
        # Obtener formatos soportados dinámicamente
        supported_formats = get_supported_file_formats()
        
        # Crear filtro de archivos dinámico
        format_filters = []
        format_descriptions = {
            '.xlsx': 'Archivos de Excel',
            '.xls': 'Archivos de Excel Legacy',
            '.csv': 'Archivos CSV',
            '.tsv': 'Archivos TSV',
            '.json': 'Archivos JSON',
            '.xml': 'Archivos XML',
            '.parquet': 'Archivos Parquet',
            '.feather': 'Archivos Feather',
            '.hdf5': 'Archivos HDF5',
            '.h5': 'Archivos HDF5',
            '.pkl': 'Archivos Pickle',
            '.pickle': 'Archivos Pickle',
            '.db': 'Bases de Datos SQLite',
            '.sqlite': 'Bases de Datos SQLite',
            '.sqlite3': 'Bases de Datos SQLite',
            '.yaml': 'Archivos YAML',
            '.yml': 'Archivos YAML',
        }
        
        for ext in supported_formats:
            if ext in format_descriptions:
                format_filters.append(f"{format_descriptions[ext]} (*{ext})")
        
        # Añadir filtro de "Todos los soportados"
        all_extensions = " ".join([f"*{ext}" for ext in supported_formats])
        all_formats = f"Todos los archivos soportados ({all_extensions})"
        format_filters.insert(0, all_formats)
        
        # Crear el filtro final
        file_filter = ";;".join(format_filters)
        
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir archivo de datos",
            "",
            file_filter)

        if filepath:
            self.mostrar_loading_indicator(filepath)

    def mostrar_loading_indicator(self, filepath, skip_rows=0, column_names=None):
        """Mostrar indicador de carga mientras se procesa el archivo"""

        # Crear y configurar el diálogo de progreso
        self.progress_dialog = QProgressDialog("Cargando archivo...", "Cancelar", 0, 100)
        self.progress_dialog.setWindowTitle("Cargando datos")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()

        # Crear y ejecutar el hilo de carga
        self.loading_thread = DataLoaderThread(filepath, skip_rows, column_names)
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

        # Establecer datos en DataView
        if self.data_view:
            self.data_view.set_data(df)

        # Actualizar interfaz
        self.actualizar_vista()
        self.statusBar().showMessage(f"Datos cargados: {self.loading_thread.filepath}")

        # Actualizar vista de gráficos
        if self.graphics_view:
            self.graphics_view.update_data(df)

        # Vista de Tabla Pivote ahora se maneja a través de diálogos

        # Actualizar vista principal
        if self.main_view:
            self.main_view.set_file_info(self.loading_thread.filepath)
            # Mostrar el botón de opciones después de cargar
            self.main_view.show_options_button()

        # Poblar el ComboBox con nombres de columnas
        if self.filter_combo:
            self.filter_combo.clear()
            self.filter_combo.addItems(df.columns.tolist())

        # Limpiar filtros previos
        if self.filter_input:
            self.filter_input.clear()
        if self.filter_combo:
            self.filter_combo.setCurrentIndex(-1)

        # Actualizar menús
        self.actualizar_menu_separar()
        self.actualizar_menu_pivote()
        self.actualizar_menu_datos()

        # Cambiar a vista de tabla por defecto
        self.switch_view(1)

    def on_error_carga(self, error_message):
        """Slot para manejar errores de carga"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

        QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo: {error_message}")

    def on_file_loaded_from_main_view(self, filepath, skip_rows=0, column_names=None):
        """Slot para manejar carga de archivo desde la vista principal"""
        if column_names is None:
            column_names = {}
        self.mostrar_loading_indicator(filepath, skip_rows, column_names)

    def cargar_carpeta(self):
        """Abrir diálogo para cargar carpeta con archivos Excel"""
        try:
            from app.widgets.folder_load_dialog import FolderLoadDialog
            dialog = FolderLoadDialog(self)

            if dialog.exec() == QDialog.Accepted:
                config = dialog.get_config()
                if config and config.folder_path:
                    self.procesar_carga_carpeta(config)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error abriendo diálogo de carga de carpeta: {str(e)}")

    def procesar_carga_carpeta(self, config):
        """Procesar la carga de carpeta según configuración"""
        try:
            from core.loaders.folder_loader import FolderLoader
            from core.consolidation.excel_consolidator import ExcelConsolidator
            from PySide6.QtWidgets import QProgressDialog
            from PySide6.QtCore import Qt

            # Crear diálogo de progreso
            progress = QProgressDialog("Cargando archivos de carpeta...", "Cancelar", 0, 100, self)
            progress.setWindowTitle("Carga de Carpeta")
            progress.setWindowModality(Qt.WindowModal)
            progress.show()

            # Escanear carpeta
            progress.setLabelText("Escaneando carpeta...")
            folder_loader = FolderLoader(config.folder_path)

            # Filtrar archivos según configuración
            selected_files = []
            all_metadata = folder_loader.get_all_metadata()

            for meta in all_metadata:
                if config.should_include_file(meta['filename']):
                    selected_files.append(meta['filepath'])

            if not selected_files:
                QMessageBox.warning(self, "Advertencia", "No se encontraron archivos Excel válidos en la carpeta seleccionada.")
                return

            # Cargar y consolidar archivos usando procesamiento por lotes
            consolidator = ExcelConsolidator()

            # Aplicar renombrado de columnas si configurado
            if config.column_rename_mapping:
                consolidator.set_column_mappings(config.column_rename_mapping)

            # Usar consolidación por lotes para mejor rendimiento
            progress_callback = lambda p: (
                progress.setValue(int(50 + (p * 0.4))),  # 50-90% para consolidación
                progress.setLabelText(f"Procesando archivos... {int(p)}% completado")
            )

            consolidated_df = consolidator.consolidate_chunked(
                selected_files,
                alignment_method='position',
                chunk_size=10,  # Procesar de 10 en 10 archivos
                progress_callback=progress_callback
            )

            progress.setValue(100)
            progress.close()

            # Establecer datos consolidados
            self.df_original = consolidated_df
            self.df_vista_actual = consolidated_df

            # Actualizar vistas
            if self.data_view:
                self.data_view.set_data(consolidated_df)

            # Actualizar interfaz
            self.actualizar_vista()
            self.statusBar().showMessage(f"Carpeta cargada: {len(selected_files)} archivos consolidados")

            # Actualizar vista de gráficos
            if self.graphics_view:
                self.graphics_view.update_data(consolidated_df)

            # Poblar filtros
            if self.filter_combo:
                self.filter_combo.clear()
                self.filter_combo.addItems(consolidated_df.columns.tolist())

            # Actualizar menús
            self.actualizar_menu_separar()
            self.actualizar_menu_pivote()
            self.actualizar_menu_datos()

            # Cambiar a vista de tabla
            self.switch_view(1)

            QMessageBox.information(self, "Éxito",
                                  f"Carpeta cargada exitosamente.\n\n"
                                  f"Archivos procesados: {len(selected_files)}\n"
                                  f"Filas totales: {len(consolidated_df)}\n"
                                  f"Columnas: {len(consolidated_df.columns)}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error procesando carga de carpeta: {str(e)}")
            if 'progress' in locals():
                progress.close()

    def on_reload_with_options(self, filepath, skip_rows, column_names):
        """Slot para manejar recarga de archivo con nuevas opciones"""
        self.mostrar_loading_indicator(filepath, skip_rows, column_names)

    def on_filter_applied(self, column, term):
        """Slot para manejar filtro aplicado desde DataView"""
        self.statusBar().showMessage(f"Filtro aplicado en columna '{column}': '{term}'")
        
    def on_filter_cleared(self):
        """Slot para manejar filtro limpiado desde DataView"""
        self.statusBar().showMessage("Filtro limpiado")
        
    def on_data_updated(self):
        """Slot para manejar datos actualizados desde DataView"""
        # Actualizar otras vistas con los datos actuales
        if self.graphics_view and self.data_view:
            current_page_data = self.data_view.export_current_page()
            if not current_page_data.empty:
                self.graphics_view.update_data(current_page_data)
        

    def abrir_cruzar_datos(self):
        """Abrir diálogo para cruzar datos"""
        if self.df_vista_actual is None or self.df_vista_actual.empty:
            QMessageBox.warning(self, "Advertencia", "No hay datos cargados para cruzar.")
            return

        try:
            # Importar diálogo de join
            from app.widgets.join.join_dialog import JoinDialog

            # Crear diálogo
            dialog = JoinDialog(self.df_vista_actual, self)
            dialog.join_completed.connect(self.on_join_completed)

            if dialog.exec() == QDialog.Accepted:
                # El diálogo ya maneja la configuración, pero si se acepta sin configurar,
                # no debería pasar nada
                pass

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error abriendo diálogo de cruce de datos: {str(e)}")

    def on_join_completed(self, result, right_file_path):
        """Manejar resultado de join completado"""
        try:
            # Establecer resultado en vista de datos cruzados
            left_name = os.path.basename(self.loading_thread.filepath) if self.loading_thread else "Dataset Izquierdo"
            right_name = os.path.basename(right_file_path) if right_file_path else "Dataset Derecho"

            self.joined_data_view.set_join_result(result, left_name, right_name)

            # Añadir al historial
            if result.success and result.config:
                self.join_history.add_entry(left_name, right_name, result.config, result)

            # Habilitar botón de vista
            self.view_joined_data_btn.setEnabled(True)

            # Cambiar a vista de datos cruzados
            self.switch_view(3)

            self.statusBar().showMessage(f"Cruce completado: {result.metadata.result_rows} filas resultantes")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error procesando resultado del join: {str(e)}")

    def abrir_pivot_simple(self):
        """Abrir diálogo de tabla pivote simple"""
        if self.df_vista_actual is None or self.df_vista_actual.empty:
            QMessageBox.warning(self, "Advertencia", "No hay datos cargados para crear tabla pivote.")
            return
        
        try:
            # Importar diálogo de pivote simple
            from app.widgets.simple_pivot_dialog import SimplePivotDialog
            
            # Crear diálogo simplificado
            dialog = SimplePivotDialog(self.df_vista_actual, self)
            dialog.set_data(self.df_vista_actual)
            
            if dialog.exec() == QDialog.Accepted:
                pivot_config = dialog.get_config()
                if pivot_config:
                    self.procesar_pivot_simple(pivot_config)
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error abriendo diálogo de pivote simple: {str(e)}")

    def abrir_pivot_combinada(self):
        """Abrir diálogo de tabla pivote combinada"""
        if self.df_vista_actual is None or self.df_vista_actual.empty:
            QMessageBox.warning(self, "Advertencia", "No hay datos cargados para crear tabla pivote.")
            return
        
        try:
            # Importar diálogo de configuración de pivote combinada
            from app.widgets.pivot_config_dialog import PivotConfigDialog
            
            # Crear diálogo completo
            dialog = PivotConfigDialog(self.df_vista_actual, self)
            dialog.set_data(self.df_vista_actual)
            
            if dialog.exec() == QDialog.Accepted:
                pivot_config = dialog.get_config()
                if pivot_config:
                    self.procesar_pivot_combinada(pivot_config)
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error abriendo diálogo de pivote combinada: {str(e)}")

    def procesar_pivot_simple(self, config):
        """Procesar creación de tabla pivote simple con fallback a agregación"""
        try:
            from core.pivot import SimplePivotTable
            
            # Verificar si es pivote o agregación simple
            is_pivot = config.get('is_pivot', True)
            
            if is_pivot:
                # Es un pivote real - intentar ejecutar pivote
                pivot = SimplePivotTable()
                result = pivot.execute(self.df_vista_actual, config)
                
                if result is not None and not result.empty:
                    # Actualizar datos actuales y mostrar resultado en vista de datos
                    self.df_vista_actual = result
                    self.data_view.set_data(result)
                    self.switch_view(1)  # Cambiar a vista de datos
                    self.statusBar().showMessage(f"Tabla pivote simple creada: {len(result)} filas, {len(result.columns)} columnas")
                    QMessageBox.information(self, "Éxito", f"Tabla pivote simple creada exitosamente.\n\nDimensiones: {len(result)} filas x {len(result.columns)} columnas")
                else:
                    QMessageBox.warning(self, "Advertencia", "No se pudo crear la tabla pivote simple.")
                    self.statusBar().showMessage("Error creando tabla pivote simple")
            else:
                # Es agregación simple por filas
                result = self.crear_agregacion_simple(config)
                
                if result is not None and not result.empty:
                    # Actualizar datos actuales y mostrar resultado en vista de datos
                    self.df_vista_actual = result
                    self.data_view.set_data(result)
                    self.switch_view(1)  # Cambiar a vista de datos
                    self.statusBar().showMessage(f"Agregación por filas creada: {len(result)} filas, {len(result.columns)} columnas")
                    QMessageBox.information(self, "Éxito", f"Agregación por filas creada exitosamente.\n\nDimensiones: {len(result)} filas x {len(result.columns)} columnas\n\nNota: Se creó un resumen por filas sin pivoteo de columnas.")
                else:
                    QMessageBox.warning(self, "Advertencia", "No se pudo crear la agregación por filas.")
                    self.statusBar().showMessage("Error creando agregación por filas")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error procesando tabla pivote simple:\n{str(e)}")
            self.statusBar().showMessage("Error en tabla pivote simple")

    def procesar_pivot_combinada(self, config):
        """Procesar creación de tabla pivote combinada con fallback a agregación"""
        try:
            from core.pivot import CombinedPivotTable

            # Crear instancia de tabla pivote combinada
            pivot = CombinedPivotTable()

            # Intentar ejecutar pivote primero
            result = None
            pivot_exitoso = False

            try:
                result = pivot.execute(self.df_vista_actual, config)
                if result is not None and not result.empty:
                    pivot_exitoso = True
            except Exception as pivot_error:
                self.statusBar().showMessage(f"Pivote combinado falló, usando agregación como fallback: {str(pivot_error)}")

            # Si el pivote no fue exitoso, usar agregación como fallback
            if not pivot_exitoso:
                result = self.crear_agregacion_fallback(config, tipo_pivote="combinada")

            if result is not None and not result.empty:
                # Actualizar datos actuales y mostrar resultado en vista de datos
                self.df_vista_actual = result
                self.data_view.set_data(result)
                self.switch_view(1)  # Cambiar a vista de datos

                if pivot_exitoso:
                    self.statusBar().showMessage(f"Tabla pivote combinada creada: {len(result)} filas, {len(result.columns)} columnas")
                    QMessageBox.information(self, "Éxito", f"Tabla pivote combinada creada exitosamente.\n\nDimensiones: {len(result)} filas x {len(result.columns)} columnas")
                else:
                    self.statusBar().showMessage(f"Agregación de fallback creada: {len(result)} filas, {len(result.columns)} columnas")
                    QMessageBox.information(self, "Éxito", f"Tabla de agregación creada (fallback).\n\nDimensiones: {len(result)} filas x {len(result.columns)} columnas\n\nNota: Se usó agregación porque el pivote no fue posible.")
            else:
                QMessageBox.warning(self, "Advertencia", "No se pudo crear la tabla pivote combinada ni la agregación de fallback.")
                self.statusBar().showMessage("Error en tabla pivote combinada y agregación fallback")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error procesando tabla pivote combinada:\n{str(e)}")
            self.statusBar().showMessage("Error en tabla pivote combinada")

    def exportar_resultado_pivote(self):
        """Exportar resultado de tabla pivote mostrándose actualmente"""
        # Usar los datos que se están mostrando actualmente (resultado de cualquier transformación)
        if self.df_vista_actual is None or self.df_vista_actual.empty:
            QMessageBox.warning(self, "Advertencia", "No hay datos para exportar. Realice una operación de tabla pivote primero.")
            return

        # Exportar los datos actuales (que pueden ser resultado de pivote u otra transformación)
        self._exportar_dataframe_directo(self.df_vista_actual, "Resultado_Pivote")

    def _procesar_pivote_para_exportacion(self, config):
        """Procesar pivote y devolver DataFrame para exportación"""
        try:
            from core.pivot import CombinedPivotTable

            # Crear instancia de tabla pivote combinada
            pivot = CombinedPivotTable()

            # Intentar ejecutar pivote primero
            result = None
            pivot_exitoso = False

            try:
                result = pivot.execute(self.df_vista_actual, config)
                if result is not None and not result.empty:
                    pivot_exitoso = True
            except Exception as pivot_error:
                print(f"Pivote combinado falló, usando agregación como fallback: {str(pivot_error)}")

            # Si el pivote no fue exitoso, usar agregación como fallback
            if not pivot_exitoso:
                result = self.crear_agregacion_fallback(config, tipo_pivote="combinada")

            return result

        except Exception as e:
            print(f"Error procesando pivote para exportación: {str(e)}")
            return None

    def _exportar_dataframe_directo(self, df, default_filename_prefix):
        """Exportar DataFrame directamente con diálogo de selección de formato"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton

        dialog = QDialog(self)
        dialog.setWindowTitle("Exportar Resultado de Pivote")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        # Selección de formato
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Formato:"))
        format_combo = QComboBox()
        format_combo.addItems(["CSV (.csv)", "Excel (.xlsx)", "PDF (.pdf)"])
        format_combo.setCurrentText("Excel (.xlsx)")
        format_layout.addWidget(format_combo)
        layout.addLayout(format_layout)

        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        export_btn = QPushButton("Exportar")
        export_btn.clicked.connect(dialog.accept)
        buttons_layout.addWidget(export_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

        if dialog.exec() != QDialog.Accepted:
            return

        # Obtener formato seleccionado
        format_text = format_combo.currentText()

        # Determinar extensión y función de exportación
        if "CSV" in format_text:
            extension = "csv"
            export_func_name = "exportar_a_csv"
            file_filter = "CSV Files (*.csv);;All Files (*)"
        elif "Excel" in format_text:
            extension = "xlsx"
            export_func_name = "exportar_a_xlsx"
            file_filter = "Excel Files (*.xlsx);;All Files (*)"
        elif "PDF" in format_text:
            extension = "pdf"
            export_func_name = "exportar_a_pdf"
            file_filter = "PDF Files (*.pdf);;All Files (*)"
        else:
            QMessageBox.warning(self, "Error", "Formato no soportado.")
            return

        # Diálogo para guardar archivo
        import pandas as pd
        default_filename = f"{default_filename_prefix}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Resultado de Pivote",
            default_filename,
            file_filter
        )

        if not filepath:
            return

        # Ejecutar exportación
        try:
            from core.data_handler import exportar_a_csv, exportar_a_xlsx, exportar_a_pdf

            # Obtener la función correcta
            if extension == "csv":
                success = exportar_a_csv(df, filepath, delimiter=',', encoding='utf-8')
            elif extension == "xlsx":
                success = exportar_a_xlsx(df, filepath)
            elif extension == "pdf":
                success = exportar_a_pdf(df, filepath)
            else:
                success = False

            if success:
                QMessageBox.information(
                    self,
                    "Exportación Exitosa",
                    f"Resultado exportado exitosamente a:\n{filepath}"
                )
                self.statusBar().showMessage(f"Exportado resultado de pivote: {filepath}")
            else:
                QMessageBox.warning(
                    self,
                    "Error de Exportación",
                    "Error al exportar el archivo. Verifique los permisos y el formato."
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error durante la exportación:\n{str(e)}"
            )

    def crear_agregacion_simple(self, config):
        """Crear agregación simple por filas cuando no se selecciona columna para pivot"""
        try:
            # Esta es para el caso simple donde no hay columna para pivot
            # Hace un resumen por una sola columna (índice)
            index_column = config.get('index')
            values_column = config.get('values')
            agg_function = config.get('aggfunc', 'mean')
            
            if not index_column or not values_column:
                raise ValueError("Se requieren columnas de índice y valores para la agregación")
            
            # Agrupar por la columna índice y agregar la columna de valores
            result = self.df_vista_actual.groupby(index_column)[values_column].agg(agg_function).reset_index()
            
            # Renombrar la columna para que sea más clara
            result.columns = [index_column, f"{values_column}_{agg_function}"]
            
            return result
            
        except Exception as e:
            self.statusBar().showMessage(f"Error en agregación simple: {str(e)}")
            raise e

    def crear_agregacion_fallback(self, config, tipo_pivote="simple"):
        """Crear agregación de fallback cuando el pivote no es posible"""
        try:
            # Determinar columnas de grouping (equivalente al índice del pivote)
            groupby_columns = []
            if tipo_pivote == "simple":
                index = config.get('index')
                if index:
                    if isinstance(index, str):
                        groupby_columns = [index]
                    elif isinstance(index, list):
                        groupby_columns = index[:1]  # Solo la primera columna
            else:  # combinada
                index = config.get('index')
                if index:
                    groupby_columns = index if isinstance(index, list) else [index]
                else:
                    groupby_columns = []  # Sin grouping = agregación global

            # Determinar columnas a agregar y funciones
            values = config.get('values', [])
            aggfunc = config.get('aggfunc') or config.get('aggfuncs', ['mean'])

            # Normalizar values a lista
            if isinstance(values, str):
                values_columns = [values]
            elif isinstance(values, list):
                values_columns = values
            else:
                values_columns = []

            if not values_columns:
                # Si no hay valores específicos, usar todas las columnas numéricas
                values_columns = [col for col in self.df_vista_actual.columns
                                if self.df_vista_actual[col].dtype in ['int64', 'float64']]
                if not values_columns:
                    # Si no hay columnas numéricas, usar todas las columnas
                    values_columns = self.df_vista_actual.columns.tolist()

            # Filtrar solo columnas que realmente existen
            values_columns = [col for col in values_columns if col in self.df_vista_actual.columns]

            if not values_columns:
                raise ValueError("No se encontraron columnas válidas para agregar")

            # Normalizar función de agregación
            if isinstance(aggfunc, list):
                agg_function = aggfunc[0] if aggfunc else 'mean'
            else:
                agg_function = aggfunc if aggfunc else 'mean'

            # Crear agregación usando pandas directamente
            if groupby_columns:
                # Agregación por grupos
                result = self.df_vista_actual.groupby(groupby_columns)[values_columns].agg(agg_function).reset_index()
            else:
                # Agregación global
                result = self.df_vista_actual[values_columns].agg(agg_function).to_frame().T.reset_index(drop=True)

            return result

        except Exception as e:
            self.statusBar().showMessage(f"Error en agregación de fallback: {str(e)}")
            raise e

    def cargar_datos(self, filepath):
        """Cargar datos desde un archivo"""
        try:
            from core.data_handler import cargar_datos
            self.df_original = cargar_datos(filepath)
            self.df_vista_actual = self.df_original

            # Actualizar interfaz
            self.actualizar_vista()
            self.actualizar_menu_separar()
            self.statusBar().showMessage(f"Datos cargados: {filepath}")
    
            # Limpiar filtros previos
            if self.filter_input:
                self.filter_input.clear()
            if self.filter_combo:
                self.filter_combo.setCurrentIndex(-1)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo: {str(e)}")

    def actualizar_vista(self):
        """Actualizar la vista con los datos actuales"""
        # Nota: Esta función mantiene compatibilidad con el sistema anterior
        # La DataView se actualiza automáticamente cuando se establecen los datos
        pass

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
            # Actualizar vista de gráficos con datos filtrados
            if self.graphics_view:
                self.graphics_view.update_data(self.df_vista_actual)
            self.statusBar().showMessage(f"Filtro aplicado: {len(self.df_vista_actual)} filas mostradas")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al aplicar filtro: {str(e)}")

    def limpiar_filtro(self):
        """Limpiar el filtro y mostrar todos los datos"""
        if self.df_original is None:
            return

        self.df_vista_actual = self.df_original.copy()
        self.actualizar_vista()
        # Actualizar vista de gráficos con datos originales
        if self.graphics_view:
            self.graphics_view.update_data(self.df_vista_actual)
        if self.filter_input:
            self.filter_input.clear()
        if self.filter_combo:
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
            # Asegurar que tenga extensión .pdf
            if not filepath.lower().endswith('.pdf'):
                filepath += '.pdf'

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
            # Asegurar que tenga extensión de imagen
            image_extensions = ['.png', '.jpg', '.jpeg']
            has_extension = any(filepath.lower().endswith(ext) for ext in image_extensions)
            if not has_extension:
                filepath += '.png'  # Extensión por defecto

            from core.data_handler import exportar_a_imagen
            success = exportar_a_imagen(self.tabla_datos, filepath)
            if success:
                QMessageBox.information(self, "Éxito", f"Imagen exportada a {filepath}")
                self.statusBar().showMessage(f"Exportado a imagen: {filepath}")
            else:
                QMessageBox.critical(self, "Error", "No se pudo exportar a imagen.")

    def exportar_a_xlsx(self):
        """Exportar datos a archivo Excel (.xlsx)"""
        if self.df_vista_actual is None:
            QMessageBox.warning(self, "Advertencia", "No hay datos para exportar.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar como Excel",
            "",
            "Archivos Excel (*.xlsx)"
        )

        if filepath:
            # Asegurar que tenga extensión .xlsx
            if not filepath.lower().endswith('.xlsx'):
                filepath += '.xlsx'

            from core.data_handler import exportar_a_xlsx
            success = exportar_a_xlsx(self.df_vista_actual, filepath)
            if success:
                QMessageBox.information(self, "Éxito", f"Datos exportados a {filepath}")
                self.statusBar().showMessage(f"Exportado a XLSX: {filepath}")
            else:
                QMessageBox.critical(self, "Error", "No se pudo exportar a XLSX.")

    def exportar_a_csv(self):
        """Exportar datos a archivo CSV"""
        if self.df_vista_actual is None:
            QMessageBox.warning(self, "Advertencia", "No hay datos para exportar.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar como CSV",
            "",
            "Archivos CSV (*.csv)"
        )

        if filepath:
            # Asegurar que tenga extensión .csv
            if not filepath.lower().endswith('.csv'):
                filepath += '.csv'

            from core.data_handler import exportar_a_csv
            success = exportar_a_csv(self.df_vista_actual, filepath)
            if success:
                QMessageBox.information(self, "Éxito", f"Datos exportados a {filepath}")
                self.statusBar().showMessage(f"Exportado a CSV: {filepath}")
            else:
                QMessageBox.critical(self, "Error", "No se pudo exportar a CSV.")

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
            # Asegurar que tenga extensión .db
            if not filepath.lower().endswith('.db'):
                filepath += '.db'

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

    def exportar_datos_separados(self):
        """Slot para exportar datos separados usando plantillas Excel"""
        if self.df_vista_actual is None:
            QMessageBox.warning(self, "Advertencia", "No hay datos para exportar.")
            return
            
        if self.df_vista_actual.empty:
            QMessageBox.warning(self, "Advertencia", "Los datos están vacíos.")
            return
        
        try:
            # Importar diálogo de exportación separada
            from app.widgets.export_separated_dialog import ExportSeparatedDialog
            
            # Crear y mostrar diálogo
            dialog = ExportSeparatedDialog(self.df_vista_actual, self)
            
            if dialog.exec():
                config = dialog.config
                if config:
                    self.procesar_exportacion_separada(config)
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error abriendo diálogo de exportación: {str(e)}")

    def procesar_exportacion_separada(self, config):
        """Procesar la exportación separada con progreso"""
        try:
            from core.data_handler import exportar_datos_separados
            from core.data_handler import ExcelTemplateSplitter
            from core.join.join_history import JoinHistory
            from PySide6.QtWidgets import QProgressDialog
            from PySide6.QtCore import Qt, QTimer
            from PySide6.QtTest import QTest
            
            # Estimar tiempo de procesamiento para barra de progreso
            try:
                splitter = ExcelTemplateSplitter(self.df_vista_actual, config)
                validation = splitter.validate_configuration()
                if validation.is_valid:
                    analisis = splitter.analyze_data()
                    grupos_estimados = getattr(analisis, 'estimated_groups', len(self.df_vista_actual.groupby(config.separator_column)) if hasattr(config, 'separator_column') else 1)
                    grupos_estimados = max(grupos_estimados, 1)
                else:
                    grupos_estimados = 1
            except:
                grupos_estimados = 1
            
            # Crear diálogo de progreso
            self.progress_dialog = QProgressDialog("Iniciando exportación...", "Cancelar", 0, grupos_estimados)
            self.progress_dialog.setWindowTitle("Exportación Separada")
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.setMinimumDuration(0)  # Mostrar inmediatamente
            
            # Actualizar etiqueta de progreso
            self.progress_dialog.setLabelText("Analizando datos y configurando...")
            self.progress_dialog.show()
            
            # Procesar exportación con callback de progreso
            def callback_progreso(grupo_actual, total_grupos):
                if self.progress_dialog and self.progress_dialog.isVisible():
                    self.progress_dialog.setValue(grupo_actual)
                    self.progress_dialog.setLabelText(f"Procesando grupo {grupo_actual}/{total_grupos}...")
                    
            resultado = exportar_datos_separados(self.df_vista_actual, config.__dict__)
            
            # Cerrar diálogo de progreso
            if hasattr(self, 'progress_dialog') and self.progress_dialog:
                self.progress_dialog.close()
            
            # Mostrar resultado
            if resultado.get('success', False):
                archivos_generados = resultado.get('files_created', [])
                grupos_procesados = resultado.get('groups_processed', 0)
                tiempo_procesamiento = resultado.get('processing_time', 0)
                
                mensaje = f"Exportación completada exitosamente:\n\n"
                mensaje += f"• {grupos_procesados} grupos procesados\n"
                mensaje += f"• {len(archivos_generados)} archivos generados\n"
                mensaje += f"• Tiempo: {tiempo_procesamiento:.1f} segundos\n"
                mensaje += f"• Carpeta: {config.output_folder}"
                
                # Mostrar archivos generados si no son demasiados
                if len(archivos_generados) <= 10 and archivos_generados:
                    mensaje += f"\n\nArchivos creados:\n" + "\n".join([f"• {archivo}" for archivo in archivos_generados])
                elif len(archivos_generados) > 10:
                    mensaje += f"\n\nPrimeros 10 archivos:\n" + "\n".join([f"• {archivo}" for archivo in archivos_generados[:10]])
                    mensaje += f"\n... y {len(archivos_generados) - 10} archivos más"
                
                QMessageBox.information(self, "Éxito", mensaje)
                self.statusBar().showMessage(f"Exportación completada: {len(archivos_generados)} archivos generados en {tiempo_procesamiento:.1f}s")
                
            else:
                errores = resultado.get('errors', [])
                warning_msgs = resultado.get('warnings', [])
                
                if errores:
                    error_msg = "\n".join(errores) if errores else "Error desconocido"
                    QMessageBox.critical(self, "Error en Exportación", f"No se pudo completar la exportación:\n\n{error_msg}")
                elif warning_msgs:
                    warning_msg = "\n".join(warning_msgs)
                    QMessageBox.warning(self, "Advertencias", f"Exportación completada con advertencias:\n\n{warning_msg}")
                else:
                    QMessageBox.warning(self, "Advertencia", "No se pudo completar la exportación. Revisa los datos y configuración.")
                
        except Exception as e:
            error_str = str(e)
            
            # Manejar errores específicos de Excel
            if "Excel" in error_str or "xlsx" in error_str or "openpyxl" in error_str:
                if "corrupt" in error_str.lower() or "formato" in error_str.lower():
                    error_msg = "Error de archivo Excel:\n\n• El archivo de plantilla puede estar corrupto\n• Verifica que sea un archivo .xlsx válido\n• Asegúrate de que no esté abierto en Excel\n\nDetalles: " + error_str
                elif "permission" in error_str.lower() or "permiso" in error_str.lower():
                    error_msg = "Error de permisos:\n\n• No tienes permisos para escribir en la carpeta\n• Verifica los permisos de la carpeta de destino\n• Prueba con una carpeta diferente\n\nDetalles: " + error_str
                elif "template" in error_str.lower():
                    error_msg = "Error de plantilla:\n\n• La plantilla Excel no se puede leer\n• Verifica que el archivo existe y es accesible\n• Asegúrate de que sea un archivo Excel válido\n\nDetalles: " + error_str
                else:
                    error_msg = "Error relacionado con Excel:\n\n• Verifica que los archivos Excel no estén abiertos\n• Asegúrate de tener permisos de lectura/escritura\n• Revisa que la plantilla sea compatible\n\nDetalles: " + error_str
            elif "template" in error_str.lower():
                error_msg = "Error de plantilla:\n\n• La plantilla especificada no se puede leer\n• Verifica que el archivo existe y es válido\n\nDetalles: " + error_str
            elif "memoria" in error_str.lower() or "memory" in error_str.lower():
                error_msg = "Error de memoria:\n\n• El dataset es demasiado grande para procesarlo\n• Prueba con un dataset más pequeño\n• Considera usar la opción de chunking\n\nDetalles: " + error_str
            else:
                error_msg = f"Error procesando exportación:\n\nDetalles: {error_str}"
                
            QMessageBox.critical(self, "Error", error_msg)
            self.statusBar().showMessage("Error en exportación separada")

    def actualizar_menu_separar(self):
        """Actualizar estado del menú Separar basado en datos cargados"""
        if hasattr(self, 'exportar_separado_action') and self.exportar_separado_action:
            if self.df_vista_actual is not None and not self.df_vista_actual.empty:
                self.exportar_separado_action.setEnabled(True)
                self.exportar_separado_action.setStatusTip("Exportar datos separados por columna usando plantillas Excel")
            else:
                self.exportar_separado_action.setEnabled(False)
                self.exportar_separado_action.setStatusTip("Carga datos primero para habilitar esta opción")

    def actualizar_menu_pivote(self):
        """Actualizar estado del menú Tabla Pivote basado en datos cargados"""
        if hasattr(self, 'pivot_simple_action') and self.pivot_simple_action:
            if self.df_vista_actual is not None and not self.df_vista_actual.empty:
                self.pivot_simple_action.setEnabled(True)
                self.pivot_simple_action.setStatusTip("Crear tabla pivote simple")
                self.pivot_combinada_action.setEnabled(True)
                self.pivot_combinada_action.setStatusTip("Crear tabla pivote combinada")
                self.export_pivot_action.setEnabled(True)
                self.export_pivot_action.setStatusTip("Exportar los datos que se muestran actualmente (resultado de transformaciones)")
            else:
                self.pivot_simple_action.setEnabled(False)
                self.pivot_simple_action.setStatusTip("Carga datos primero para habilitar esta opción")
                self.pivot_combinada_action.setEnabled(False)
                self.pivot_combinada_action.setStatusTip("Carga datos primero para habilitar esta opción")
                self.export_pivot_action.setEnabled(False)
                self.export_pivot_action.setStatusTip("Carga datos primero para habilitar esta opción")

    def actualizar_menu_datos(self):
        """Actualizar estado del menú Datos basado en datos cargados"""
        if hasattr(self, 'cruzar_datos_action') and self.cruzar_datos_action:
            if self.df_vista_actual is not None and not self.df_vista_actual.empty:
                self.cruzar_datos_action.setEnabled(True)
                self.cruzar_datos_action.setStatusTip("Cruzar datos con otro dataset usando operaciones de join")
            else:
                self.cruzar_datos_action.setEnabled(False)
                self.cruzar_datos_action.setStatusTip("Carga datos primero para habilitar esta opción")

    def mostrar_acerca_de(self):
        """Mostrar diálogo Acerca de con información del software y creador"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QPixmap, QIcon
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Acerca de Flash View Sheet")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Logo y título principal
        header_layout = QHBoxLayout()
        
        # Intentar cargar logo si existe
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(logo_label)
        
        # Título y versión
        title_layout = QVBoxLayout()
        
        title_label = QLabel("Flash View Sheet")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2E86AB;")
        title_layout.addWidget(title_label)
        
        version_label = QLabel("Versión 1.1.0")
        version_label.setStyleSheet("font-size: 12px; color: #666;")
        title_layout.addWidget(version_label)
        
        header_layout.addLayout(title_layout)
        layout.addLayout(header_layout)
        
        # Descripción del software
        desc_text = """
        <p><b>Flash View Sheet</b> es una aplicación de escritorio ligera para visualizar y analizar datos de archivos Excel y CSV.</p>
        
        <p><b>Características principales:</b></p>
        <ul>
        <li>📊 Visualización interactiva de datos tabulares</li>
        <li>📈 Análisis estadístico con optimizaciones para datasets grandes</li>
        <li>🔍 Filtrado y búsqueda avanzada</li>
        <li>📤 Exportación múltiple (PDF, XLSX, CSV, Imagen, SQL)</li>
        <li>⚡ Optimizaciones de rendimiento (paginación virtual, carga por chunks)</li>
        </ul>
        
        <p><b>Desarrollado con:</b> Python 3.10+ y PySide6</p>
        """
        
        desc_label = QLabel(desc_text)
        desc_label.setWordWrap(True)
        desc_label.setTextFormat(Qt.RichText)
        layout.addWidget(desc_label)
        
        # Información del creador
        creator_text = """
        <p><b>Creador:</b> b1tcod3</p>
        <p><b>GitHub:</b> <a href="https://github.com/b1tcod3">github.com/b1tcod3</a></p>
        """
        
        creator_label = QLabel(creator_text)
        creator_label.setWordWrap(True)
        creator_label.setTextFormat(Qt.RichText)
        creator_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        layout.addWidget(creator_label)
        
        # Botón OK
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("Aceptar")
        ok_button.clicked.connect(dialog.accept)
        ok_button.setDefault(True)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        
        dialog.exec()

    def closeEvent(self, event):
        """Manejar el cierre de la aplicación"""
        event.accept()
def main():
    """Función principal de la aplicación"""
    app = QApplication(sys.argv)

    # Configurar icono de la aplicación
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    if os.path.exists(logo_path):
        app_icon = QIcon(logo_path)
        app.setWindowIcon(app_icon)

    # Crear ventana principal
    window = MainWindow()
    window.show()

    # Ejecutar aplicación
    sys.exit(app.exec())


if __name__ == "__main__":
    main()