"""
Diálogo de Configuración para Exportación Separada con Plantillas Excel
Permite configurar columna de separación, plantilla Excel, mapeo de columnas y opciones de exportación
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QGroupBox, QFormLayout, 
                               QDialogButtonBox, QComboBox, QLineEdit, QSpinBox,
                               QTextEdit, QProgressBar, QMessageBox, QListWidget,
                               QListWidgetItem, QCheckBox, QTabWidget, QWidget,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QFileDialog, QStatusBar, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap
import pandas as pd
import os
import tempfile
import openpyxl
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# Importar funcionalidad core
import sys
sys.path.append('..')
from core.data_handler import (
    ExcelTemplateSplitter, ExportSeparatedConfig, ValidationResult, ExportResult,
    SeparationError, TemplateError, ConfigurationError, MemoryError
)


class ColumnMappingWidget(QWidget):
    """Widget para gestionar mapeo de columnas DataFrame ↔ Excel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.df_columns = []
        self.excel_columns = []
        self.mapping = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz de mapeo de columnas"""
        layout = QVBoxLayout(self)
        
        # Tabla de mapeo
        self.mapping_table = QTableWidget(0, 4)
        self.mapping_table.setHorizontalHeaderLabels([
            "Columna DataFrame", "→", "Columna Excel", "Vista Previa"
        ])
        
        # Configurar tabla
        header = self.mapping_table.horizontalHeader()
        header.setStretchLastSection(True)
        self.mapping_table.setAlternatingRowColors(True)
        self.mapping_table.setMaximumHeight(200)
        
        layout.addWidget(self.mapping_table)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        self.auto_map_btn = QPushButton("Auto-mapear")
        self.auto_map_btn.clicked.connect(self.auto_map_positional)
        button_layout.addWidget(self.auto_map_btn)
        
        self.add_column_btn = QPushButton("+ Añadir Columna")
        self.add_column_btn.clicked.connect(self.add_mapping_row)
        button_layout.addWidget(self.add_column_btn)
        
        self.remove_column_btn = QPushButton("- Eliminar")
        self.remove_column_btn.clicked.connect(self.remove_selected_rows)
        button_layout.addWidget(self.remove_column_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def set_dataframe_columns(self, columns: List[str]):
        """Establecer columnas del DataFrame"""
        self.df_columns = columns
        self.refresh_mapping_table()
    
    def set_excel_columns(self, columns: List[str]):
        """Establecer columnas disponibles en Excel"""
        self.excel_columns = columns
        
        # Actualizar ComboBox en tabla
        for row in range(self.mapping_table.rowCount()):
            combo = self.mapping_table.cellWidget(row, 2)
            if combo:
                combo.clear()
                combo.addItems(self.excel_columns)
    
    def refresh_mapping_table(self):
        """Actualizar tabla de mapeo con columnas del DataFrame"""
        self.mapping_table.setRowCount(len(self.df_columns))
        
        for row, col_name in enumerate(self.df_columns):
            # Columna DataFrame (readonly)
            item = QTableWidgetItem(col_name)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.mapping_table.setItem(row, 0, item)
            
            # Flecha (readonly)
            arrow_item = QTableWidgetItem("→")
            arrow_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            arrow_item.setTextAlignment(Qt.AlignCenter)
            self.mapping_table.setItem(row, 1, arrow_item)
            
            # ComboBox para columna Excel
            combo = QComboBox()
            combo.addItems(self.excel_columns)
            self.mapping_table.setCellWidget(row, 2, combo)
            
            # Vista previa
            preview_item = QTableWidgetItem("Sin datos")
            preview_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.mapping_table.setItem(row, 3, preview_item)
    
    def auto_map_positional(self):
        """Mapear automáticamente por posición"""
        for row in range(min(len(self.df_columns), len(self.excel_columns))):
            combo = self.mapping_table.cellWidget(row, 2)
            if combo:
                combo.setCurrentIndex(row)
    
    def add_mapping_row(self):
        """Añadir nueva fila de mapeo"""
        row = self.mapping_table.rowCount()
        self.mapping_table.insertRow(row)
        
        # Columna DataFrame
        item = QTableWidgetItem("")
        self.mapping_table.setItem(row, 0, item)
        
        # Flecha
        arrow_item = QTableWidgetItem("→")
        arrow_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        arrow_item.setTextAlignment(Qt.AlignCenter)
        self.mapping_table.setItem(row, 1, arrow_item)
        
        # ComboBox
        combo = QComboBox()
        combo.addItems(self.excel_columns)
        self.mapping_table.setCellWidget(row, 2, combo)
        
        # Vista previa
        preview_item = QTableWidgetItem("")
        self.mapping_table.setItem(row, 3, preview_item)
    
    def remove_selected_rows(self):
        """Eliminar filas seleccionadas"""
        selected_rows = sorted([item.row() for item in self.mapping_table.selectedIndexes()], reverse=True)
        for row in selected_rows:
            self.mapping_table.removeRow(row)
    
    def get_mapping(self) -> Dict[str, str]:
        """Obtener mapeo actual"""
        mapping = {}
        for row in range(self.mapping_table.rowCount()):
            df_col_item = self.mapping_table.item(row, 0)
            combo = self.mapping_table.cellWidget(row, 2)
            
            if df_col_item and combo:
                df_col = df_col_item.text().strip()
                excel_col = combo.currentText().strip()
                
                if df_col and excel_col:
                    mapping[df_col] = excel_col
        
        return mapping
    
    def update_preview(self, sample_data: pd.DataFrame):
        """Actualizar vista previa con datos de ejemplo"""
        mapping = self.get_mapping()
        
        for row in range(self.mapping_table.rowCount()):
            df_col_item = self.mapping_table.item(row, 0)
            preview_item = self.mapping_table.item(row, 3)
            
            if df_col_item and preview_item:
                df_col = df_col_item.text().strip()
                
                if df_col in sample_data.columns and not sample_data.empty:
                    # Mostrar primeras 3 filas de ejemplo
                    preview_data = sample_data[df_col].head(3).tolist()
                    preview_text = " | ".join([str(val) for val in preview_data])
                    preview_item.setText(preview_text)
                else:
                    preview_item.setText("Sin datos")


class ExcelTemplateDialog(QDialog):
    """Diálogo para seleccionar y validar plantilla Excel"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.template_path = ""
        self.selected_sheet = ""
        self.available_sheets = []
        self.setWindowTitle("Seleccionar Plantilla Excel")
        self.resize(700, 500)
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        layout = QVBoxLayout(self)
        
        # Selección de archivo
        file_group = QGroupBox("Archivo de Plantilla")
        file_layout = QFormLayout(file_group)
        
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        file_layout.addRow("Ruta:", self.file_path_edit)
        
        button_layout = QHBoxLayout()
        self.browse_btn = QPushButton("Explorar...")
        self.browse_btn.clicked.connect(self.browse_for_template)
        button_layout.addWidget(self.browse_btn)
        button_layout.addStretch()
        file_layout.addRow("", button_layout)
        
        layout.addWidget(file_group)
        
        # Información del archivo
        info_group = QGroupBox("Información del Archivo")
        info_layout = QFormLayout(info_group)
        
        self.info_label = QLabel("No hay archivo seleccionado")
        self.info_label.setWordWrap(True)
        info_layout.addRow("Estado:", self.info_label)
        
        self.sheet_combo = QComboBox()
        self.sheet_combo.setEnabled(False)
        self.sheet_combo.currentTextChanged.connect(self.on_sheet_changed)
        info_layout.addRow("Hoja:", self.sheet_combo)
        
        layout.addWidget(info_group)
        
        # Vista previa
        preview_group = QGroupBox("Vista Previa de la Plantilla")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_table = QTableWidget(0, 0)
        self.preview_table.setMaximumHeight(200)
        self.preview_table.setAlternatingRowColors(True)
        preview_layout.addWidget(self.preview_table)
        
        layout.addWidget(preview_group)
        
        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def browse_for_template(self):
        """Explorar archivo de plantilla"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Plantilla Excel", "", 
            "Excel Files (*.xlsx *.xlsm);;All Files (*)"
        )
        
        if file_path:
            self.load_template(file_path)
    
    def load_template(self, file_path: str):
        """Cargar y validar plantilla"""
        try:
            # Validar que es archivo Excel
            if not file_path.lower().endswith(('.xlsx', '.xlsm')):
                self.info_label.setText("Error: El archivo debe ser .xlsx o .xlsm")
                return
            
            # Intentar cargar con openpyxl
            workbook = openpyxl.load_workbook(file_path, data_only=False)
            self.available_sheets = workbook.sheetnames
            workbook.close()
            
            self.template_path = file_path
            self.file_path_edit.setText(file_path)
            
            # Actualizar información
            file_size = os.path.getsize(file_path)
            self.info_label.setText(f"✓ Archivo válido - Tamaño: {file_size/1024:.1f}KB - Hojas: {len(self.available_sheets)}")
            
            # Actualizar selector de hojas
            self.sheet_combo.clear()
            self.sheet_combo.addItems(self.available_sheets)
            self.sheet_combo.setEnabled(True)
            self.selected_sheet = self.available_sheets[0] if self.available_sheets else ""
            
            # Mostrar vista previa
            self.show_preview()
            
        except Exception as e:
            self.info_label.setText(f"Error al cargar plantilla: {str(e)}")
            self.template_path = ""
            self.file_path_edit.clear()
            self.sheet_combo.setEnabled(False)
            self.preview_table.setRowCount(0)
            self.preview_table.setColumnCount(0)
    
    def show_preview(self):
        """Mostrar vista previa de la plantilla"""
        try:
            if not self.template_path:
                return
                
            workbook = openpyxl.load_workbook(self.template_path, data_only=True)
            sheet = workbook[self.selected_sheet] if self.selected_sheet else workbook.active
            
            # Obtener datos (máximo 10 filas)
            max_rows = min(10, sheet.max_row)
            max_cols = min(10, sheet.max_column)
            
            self.preview_table.setRowCount(max_rows)
            self.preview_table.setColumnCount(max_cols)
            
            # Llenar tabla
            for row in range(max_rows):
                for col in range(max_cols):
                    cell_value = sheet.cell(row + 1, col + 1).value
                    if cell_value is not None:
                        item = QTableWidgetItem(str(cell_value))
                        self.preview_table.setItem(row, col, item)
            
            workbook.close()
            
        except Exception as e:
            print(f"Error mostrando preview: {e}")
    
    def on_sheet_changed(self, sheet_name: str):
        """Manejar cambio de hoja seleccionada"""
        self.selected_sheet = sheet_name
        if self.template_path:
            self.show_preview()
    
    def get_template_info(self) -> Tuple[str, str, List[str]]:
        """Obtener información de plantilla seleccionada"""
        return self.template_path, self.selected_sheet, self.available_sheets


class FilePreviewDialog(QDialog):
    """Diálogo para vista previa de archivos a generar"""
    
    def __init__(self, files_info: List[Dict], parent=None):
        super().__init__(parent)
        self.files_info = files_info
        self.setWindowTitle("Vista Previa de Archivos")
        self.resize(800, 400)
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interfaz del diálogo"""
        layout = QVBoxLayout(self)
        
        # Filtros
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtros:"))
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["Todos", "Listos", "Advertencias", "Errores"])
        self.status_filter.currentTextChanged.connect(self.filter_files)
        filter_layout.addWidget(self.status_filter)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Tabla de archivos
        self.files_table = QTableWidget(0, 5)
        self.files_table.setHorizontalHeaderLabels([
            "Nombre de Archivo", "Grupo", "Filas", "Tamaño", "Estado"
        ])
        
        header = self.files_table.horizontalHeader()
        header.setStretchLastSection(True)
        self.files_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.files_table)
        
        # Resumen
        self.summary_label = QLabel()
        layout.addWidget(self.summary_label)
        
        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.refresh_table()
    
    def refresh_table(self):
        """Actualizar tabla con información de archivos"""
        filtered_files = self.get_filtered_files()
        
        self.files_table.setRowCount(len(filtered_files))
        
        for row, file_info in enumerate(filtered_files):
            # Nombre de archivo
            name_item = QTableWidgetItem(file_info.get('filename', ''))
            self.files_table.setItem(row, 0, name_item)
            
            # Grupo
            group_item = QTableWidgetItem(file_info.get('group', ''))
            self.files_table.setItem(row, 1, group_item)
            
            # Filas
            rows_item = QTableWidgetItem(str(file_info.get('rows', 0)))
            self.files_table.setItem(row, 2, rows_item)
            
            # Tamaño
            size_item = QTableWidgetItem(file_info.get('size', ''))
            self.files_table.setItem(row, 3, size_item)
            
            # Estado
            status_item = QTableWidgetItem(file_info.get('status', ''))
            if file_info.get('status') == 'Listo':
                status_item.setBackground(Qt.green)
            elif file_info.get('status') == 'Advertencia':
                status_item.setBackground(Qt.yellow)
            elif file_info.get('status') == 'Error':
                status_item.setBackground(Qt.red)
            self.files_table.setItem(row, 4, status_item)
        
        self.update_summary(filtered_files)
    
    def get_filtered_files(self) -> List[Dict]:
        """Obtener archivos filtrados por estado"""
        filter_text = self.status_filter.currentText()
        
        if filter_text == "Todos":
            return self.files_info
        else:
            return [f for f in self.files_info if f.get('status') == filter_text]
    
    def update_summary(self, files: List[Dict]):
        """Actualizar resumen"""
        total_files = len(files)
        total_rows = sum(f.get('rows', 0) for f in files)
        
        self.summary_label.setText(
            f"Resumen: {total_files} archivos • {total_rows} filas totales • "
            f"Espacio disponible suficiente"
        )
    
    def filter_files(self):
        """Filtrar archivos por estado"""
        self.refresh_table()


class ExportSeparatedDialog(QDialog):
    """
    Diálogo principal para configuración de exportación separada con plantillas Excel
    """
    
    # Señales
    configuration_changed = Signal()
    validation_updated = Signal(bool, str)  # is_valid, message
    
    def __init__(self, dataframe: pd.DataFrame, parent=None):
        super().__init__(parent)
        self.df = dataframe
        self.config = None
        self.validation_result = None
        self.setup_ui()
        self.setup_connections()
        self.setup_validation()
        
        # Configurar diálogo
        self.setWindowTitle("💾 Configurar Exportación Separada con Plantillas Excel")
        self.resize(900, 700)
        
        # Inicializar datos
        self.initialize_data()
    
    def setup_ui(self):
        """Configurar interfaz completa del diálogo"""
        main_layout = QVBoxLayout(self)
        
        # Crear tabs para mejor organización
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Tab 1: Configuración Básica
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # Sección 1: Datos (Columna de Separación)
        data_group = QGroupBox("1. Datos")
        data_layout = QFormLayout(data_group)
        
        self.column_combo = QComboBox()
        self.column_combo.setPlaceholderText("Seleccionar columna para separar")
        data_layout.addRow("Columna de Separación:", self.column_combo)
        
        self.values_preview = QListWidget()
        self.values_preview.setMaximumHeight(100)
        data_layout.addRow("Preview de Valores:", self.values_preview)
        
        self.include_nulls_check = QCheckBox("Incluir valores nulos como grupo separado")
        data_layout.addRow("", self.include_nulls_check)
        
        basic_layout.addWidget(data_group)
        
        # Sección 2: Plantilla Excel
        template_group = QGroupBox("2. Plantilla Excel")
        template_layout = QFormLayout(template_group)
        
        self.template_path_label = QLabel("No hay plantilla seleccionada")
        self.template_path_label.setWordWrap(True)
        template_layout.addRow("Archivo:", self.template_path_label)
        
        template_btn_layout = QHBoxLayout()
        self.select_template_btn = QPushButton("Seleccionar Plantilla Excel")
        self.select_template_btn.clicked.connect(self.select_template)
        template_btn_layout.addWidget(self.select_template_btn)
        template_btn_layout.addStretch()
        template_layout.addRow("", template_btn_layout)
        
        self.sheet_combo = QComboBox()
        self.sheet_combo.setEnabled(False)
        template_layout.addRow("Hoja:", self.sheet_combo)
        
        # Celda inicial
        cell_layout = QHBoxLayout()
        self.start_cell_combo = QComboBox()
        self.start_cell_combo.addItems(["A1", "A2", "A5", "B1", "B2", "Personalizado"])
        cell_layout.addWidget(self.start_cell_combo)
        
        self.start_cell_edit = QLineEdit()
        self.start_cell_edit.setPlaceholderText("Ej: C10")
        self.start_cell_edit.setMaximumWidth(80)
        cell_layout.addWidget(self.start_cell_edit)
        cell_layout.addStretch()
        template_layout.addRow("Celda Inicial:", cell_layout)
        
        basic_layout.addWidget(template_group)
        
        # Sección 3: Nombres de Archivos
        naming_group = QGroupBox("3. Nombres de Archivos")
        naming_layout = QVBoxLayout(naming_group)
        
        # Campo de plantilla
        name_layout = QFormLayout()
        self.filename_template_edit = QLineEdit()
        self.filename_template_edit.setPlaceholderText("Ej: {valor}_{fecha}.xlsx")
        name_layout.addRow("Plantilla:", self.filename_template_edit)
        naming_layout.addLayout(name_layout)
        
        # Lista de placeholders
        placeholders_layout = QVBoxLayout()
        placeholders_layout.addWidget(QLabel("Placeholders disponibles:"))
        
        self.placeholders_list = QListWidget()
        self.placeholders_list.addItems([
            "{valor} - Valor de la columna de separación",
            "{fecha} - Fecha actual (YYYY-MM-DD)",
            "{hora} - Hora actual (HHMMSS)",
            "{contador} - Número secuencial (01, 02, 03...)",
            "{columna_nombre} - Nombre de columna",
            "{total_filas} - Número de filas en el grupo"
        ])
        self.placeholders_list.setMaximumHeight(80)
        placeholders_layout.addWidget(self.placeholders_list)
        naming_layout.addLayout(placeholders_layout)
        
        # Preview de nombres
        self.filenames_preview = QListWidget()
        self.filenames_preview.setMaximumHeight(60)
        naming_layout.addWidget(QLabel("Preview:"))
        naming_layout.addWidget(self.filenames_preview)
        
        basic_layout.addWidget(naming_group)
        
        self.tab_widget.addTab(basic_tab, "Configuración Básica")
        
        # Tab 2: Mapeo de Columnas
        mapping_tab = QWidget()
        mapping_layout = QVBoxLayout(mapping_tab)
        
        mapping_group = QGroupBox("Mapeo de Columnas DataFrame → Excel")
        self.mapping_widget = ColumnMappingWidget()
        mapping_layout.addWidget(self.mapping_widget)
        
        self.tab_widget.addTab(mapping_tab, "Mapeo de Columnas")
        
        # Tab 3: Destino y Opciones
        dest_tab = QWidget()
        dest_layout = QVBoxLayout(dest_tab)
        
        # Carpeta de destino
        dest_group = QGroupBox("4. Carpeta de Destino")
        dest_path_layout = QHBoxLayout()
        
        self.dest_folder_label = QLabel("No se ha seleccionado carpeta")
        dest_path_layout.addWidget(self.dest_folder_label)
        
        self.select_folder_btn = QPushButton("Cambiar...")
        self.select_folder_btn.clicked.connect(self.select_destination_folder)
        dest_path_layout.addWidget(self.select_folder_btn)
        
        dest_group.setLayout(dest_path_layout)
        dest_layout.addWidget(dest_group)
        
        # Estado de permisos
        self.permissions_label = QLabel()
        dest_layout.addWidget(self.permissions_label)
        
        # Opciones avanzadas
        advanced_group = QGroupBox("Opciones Avanzadas")
        advanced_layout = QFormLayout(advanced_group)
        
        self.handle_duplicates_combo = QComboBox()
        self.handle_duplicates_combo.addItems([
            "Sobrescribir archivos existentes",
            "Numerar automáticamente",
            "Evitar sobrescritura"
        ])
        advanced_layout.addRow("Manejo de Duplicados:", self.handle_duplicates_combo)
        
        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setMinimum(1000)
        self.chunk_size_spin.setMaximum(1000000)
        self.chunk_size_spin.setValue(10000)
        self.chunk_size_spin.setSuffix(" filas")
        advanced_layout.addRow("Tamaño de Chunk:", self.chunk_size_spin)
        
        dest_layout.addWidget(advanced_group)
        
        self.tab_widget.addTab(dest_tab, "Destino y Opciones")
        
        # Barra de estado
        self.status_bar = QStatusBar()
        main_layout.addWidget(self.status_bar)
        
        # Indicador de validación
        self.validation_label = QLabel("⚠️ Configuración incompleta")
        self.validation_label.setStyleSheet("color: red; font-weight: bold;")
        main_layout.addWidget(self.validation_label)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("Vista Previa")
        self.preview_btn.clicked.connect(self.show_file_preview)
        self.preview_btn.setEnabled(False)
        buttons_layout.addWidget(self.preview_btn)
        
        buttons_layout.addStretch()
        
        self.validate_btn = QPushButton("Validar")
        self.validate_btn.clicked.connect(self.validate_configuration)
        buttons_layout.addWidget(self.validate_btn)
        
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        self.export_btn = QPushButton("Exportar")
        self.export_btn.clicked.connect(self.accept)
        self.export_btn.setEnabled(False)
        buttons_layout.addWidget(self.export_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def setup_connections(self):
        """Configurar conexiones de señales"""
        self.column_combo.currentTextChanged.connect(self.on_column_changed)
        self.filename_template_edit.textChanged.connect(self.on_template_changed)
        self.start_cell_combo.currentTextChanged.connect(self.on_start_cell_changed)
        self.sheet_combo.currentTextChanged.connect(self.on_sheet_changed)
    
    def setup_validation(self):
        """Configurar sistema de validación"""
        self.validation_timer = QTimer()
        self.validation_timer.timeout.connect(self.validate_configuration)
        self.validation_timer.setSingleShot(True)
        self.validation_timer.setInterval(1000)  # Validar 1 segundo después del último cambio
    
    def initialize_data(self):
        """Inicializar datos del diálogo"""
        if self.df is not None and not self.df.empty:
            # Llenar combo de columnas
            self.column_combo.clear()
            self.column_combo.addItems(self.df.columns.tolist())
            
            # Configurar mapeo de columnas
            self.mapping_widget.set_dataframe_columns(self.df.columns.tolist())
            self.mapping_widget.set_excel_columns([chr(65+i) for i in range(26)])  # A-Z
            
            # Actualizar vista previa
            self.update_values_preview()
            
            # Validación inicial
            self.validate_configuration()
    
    def select_template(self):
        """Seleccionar plantilla Excel"""
        dialog = ExcelTemplateDialog(self)
        if dialog.exec():
            template_path, sheet_name, available_sheets = dialog.get_template_info()
            
            if template_path:
                # Almacenar la ruta de plantilla para uso posterior
                self._template_path = template_path
                
                self.template_path_label.setText(f"📄 {os.path.basename(template_path)}")
                self.template_path_label.setToolTip(template_path)
                
                # Actualizar selector de hojas
                self.sheet_combo.clear()
                self.sheet_combo.addItems(available_sheets)
                self.sheet_combo.setEnabled(True)
                
                if sheet_name:
                    self.sheet_combo.setCurrentText(sheet_name)
                
                self.validate_configuration()
    
    def select_destination_folder(self):
        """Seleccionar carpeta de destino"""
        folder = QFileDialog.getExistingDirectory(
            self, "Seleccionar Carpeta de Destino"
        )
        
        if folder:
            self.dest_folder_label.setText(f"📁 {folder}")
            self.dest_folder_label.setToolTip(folder)
            
            # Verificar permisos
            if os.access(folder, os.W_OK):
                self.permissions_label.setText("✅ Permisos de escritura OK")
                self.permissions_label.setStyleSheet("color: green;")
            else:
                self.permissions_label.setText("❌ Sin permisos de escritura")
                self.permissions_label.setStyleSheet("color: red;")
            
            self.validate_configuration()
    
    def on_column_changed(self, column_name: str):
        """Manejar cambio de columna de separación"""
        self.update_values_preview()
        self.update_filename_preview()
        self.validation_timer.start()
    
    def update_values_preview(self):
        """Actualizar preview de valores únicos"""
        column_name = self.column_combo.currentText()
        self.values_preview.clear()
        
        if column_name and column_name in self.df.columns:
            # Obtener valores únicos (máximo 10)
            unique_values = self.df[column_name].value_counts().head(10)
            
            for value, count in unique_values.items():
                if pd.notna(value):
                    item_text = f"• {value} ({count:,} filas)"
                    self.values_preview.addItem(item_text)
            
            # Verificar nulos
            null_count = self.df[column_name].isnull().sum()
            if null_count > 0:
                self.values_preview.addItem(f"• [VALORES NULOS] ({null_count:,} filas)")
    
    def on_template_changed(self):
        """Manejar cambio en plantilla de nombre"""
        self.update_filename_preview()
        self.validation_timer.start()
    
    def update_filename_preview(self):
        """Actualizar preview de nombres de archivos"""
        column_name = self.column_combo.currentText()
        template = self.filename_template_edit.text()
        
        self.filenames_preview.clear()
        
        if column_name and template:
            # Obtener valores únicos para preview
            unique_values = self.df[column_name].dropna().unique()[:5]  # Primeros 5
            
            for i, value in enumerate(unique_values):
                try:
                    # Simular procesamiento de plantilla
                    filename = template.replace("{valor}", str(value))
                    filename = filename.replace("{fecha}", datetime.now().strftime("%Y-%m-%d"))
                    filename = filename.replace("{contador}", f"{i+1:02d}")
                    filename = filename.replace("{columna_nombre}", column_name)
                    
                    if not filename.endswith('.xlsx'):
                        filename += '.xlsx'
                    
                    self.filenames_preview.addItem(f"• {filename}")
                    
                except Exception as e:
                    self.filenames_preview.addItem(f"• Error en plantilla: {str(e)}")
    
    def on_start_cell_changed(self):
        """Manejar cambio de celda inicial"""
        self.validation_timer.start()
    
    def on_sheet_changed(self):
        """Manejar cambio de hoja"""
        self.validation_timer.start()
    
    def validate_configuration(self):
        """Validar configuración completa"""
        try:
            # Crear configuración temporal para validación
            config = self.get_configuration(validate=False)
            
            if config:
                # Validar usando ExcelTemplateSplitter
                splitter = ExcelTemplateSplitter(self.df, config)
                validation_result = splitter.validate_configuration()
                
                self.validation_result = validation_result
                self.update_validation_display(validation_result)
                
                # Actualizar mapeo de columnas con datos de ejemplo
                if not self.df.empty:
                    sample_data = self.df.head(3)
                    self.mapping_widget.update_preview(sample_data)
                
            else:
                self.update_validation_display(None)
                
        except Exception as e:
            self.update_validation_display(None, str(e))
    
    def update_validation_display(self, validation_result: Optional[ValidationResult], error_msg: str = ""):
        """Actualizar display de validación"""
        if error_msg:
            self.validation_label.setText(f"❌ Error: {error_msg}")
            self.validation_label.setStyleSheet("color: red; font-weight: bold;")
            self.export_btn.setEnabled(False)
            self.preview_btn.setEnabled(False)
            self.status_bar.showMessage(f"Error de validación: {error_msg}", 5000)
            return
        
        if validation_result is None:
            self.validation_label.setText("⚠️ Configuración incompleta")
            self.validation_label.setStyleSheet("color: red; font-weight: bold;")
            self.export_btn.setEnabled(False)
            self.preview_btn.setEnabled(False)
            return
        
        # Contar errores y warnings
        error_count = len(validation_result.errors)
        warning_count = len(validation_result.warnings)
        
        if error_count > 0:
            self.validation_label.setText(f"❌ {error_count} error(es) encontrado(s)")
            self.validation_label.setStyleSheet("color: red; font-weight: bold;")
            self.export_btn.setEnabled(False)
            self.preview_btn.setEnabled(False)
            
            # Mostrar primer error en status bar
            self.status_bar.showMessage(f"Error: {validation_result.errors[0]}", 5000)
            
        elif warning_count > 0:
            self.validation_label.setText(f"⚠️ {warning_count} advertencias")
            self.validation_label.setStyleSheet("color: orange; font-weight: bold;")
            self.export_btn.setEnabled(True)  # Permitir exportar con advertencias
            self.preview_btn.setEnabled(True)
            
        else:
            self.validation_label.setText("✅ Configuración válida")
            self.validation_label.setStyleSheet("color: green; font-weight: bold;")
            self.export_btn.setEnabled(True)
            self.preview_btn.setEnabled(True)
            self.status_bar.showMessage("Configuración válida", 3000)
    
    def show_file_preview(self):
        """Mostrar vista previa de archivos a generar"""
        try:
            if not self.validation_result or self.validation_result.errors:
                QMessageBox.warning(self, "Error", "La configuración tiene errores. Corrija antes de continuar.")
                return
            
            # Simular información de archivos
            files_info = []
            column_name = self.column_combo.currentText()
            
            if column_name and column_name in self.df.columns:
                unique_values = self.df[column_name].unique()
                
                for i, value in enumerate(unique_values):
                    if pd.notna(value):
                        group_data = self.df[self.df[column_name] == value]
                        filename = self.filenames_preview.item(i).text().replace("• ", "") if i < self.filenames_preview.count() else f"archivo_{i}.xlsx"
                        
                        files_info.append({
                            'filename': filename,
                            'group': str(value),
                            'rows': len(group_data),
                            'size': f"~{len(group_data) * 0.5:.1f}KB",
                            'status': 'Listo'
                        })
            
            dialog = FilePreviewDialog(files_info, self)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error mostrando vista previa: {str(e)}")
    
    def get_configuration(self, validate: bool = True) -> Optional[ExportSeparatedConfig]:
        """Obtener configuración actual"""
        try:
            # Recopilar datos básicos
            separator_column = self.column_combo.currentText()
            template_path = getattr(self, '_template_path', '')
            start_cell = "A1"
            
            if self.start_cell_combo.currentText() == "Personalizado":
                start_cell = self.start_cell_edit.text().strip() or "A1"
            else:
                start_cell = self.start_cell_combo.currentText()
            
            sheet_name = self.sheet_combo.currentText()
            output_folder = self.dest_folder_label.text().replace("📁 ", "")
            file_template = self.filename_template_edit.text().strip()
            
            # Validar extensión de archivo de exportación
            if file_template and not file_template.lower().endswith(('.xlsx', '.xlsm')):
                self.status_bar.showMessage("Error: El nombre de archivo debe terminar en .xlsx o .xlsm", 5000)
                return None
            
            # Obtener mapeo de columnas
            column_mapping = self.mapping_widget.get_mapping()
            
            # Opciones avanzadas
            handle_duplicates = self.handle_duplicates_combo.currentText()
            chunk_size = self.chunk_size_spin.value()
            
            # Crear configuración
            config = ExportSeparatedConfig(
                separator_column=separator_column,
                template_path=template_path,
                start_cell=start_cell,
                output_folder=output_folder,
                file_template=file_template,
                column_mapping=column_mapping,
                handle_duplicates=handle_duplicates,
                enable_chunking=chunk_size > 1000,
                max_memory_mb=2048
            )
            
            # Guardar ruta de plantilla
            self._template_path = template_path
            
            if validate:
                splitter = ExcelTemplateSplitter(self.df, config)
                validation_result = splitter.validate_configuration()
                
                if not validation_result.is_valid:
                    return None
            
            return config
            
        except Exception as e:
            print(f"Error obteniendo configuración: {e}")
            return None
    
    def accept(self):
        """Aceptar diálogo y validar configuración"""
        config = self.get_configuration()
        
        if config:
            self.config = config
            super().accept()
        else:
            QMessageBox.warning(
                self, "Configuración Inválida", 
                "La configuración actual no es válida. Revise los errores marcados."
            )