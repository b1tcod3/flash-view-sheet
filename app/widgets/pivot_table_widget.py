"""
Widget Principal de Tabla Pivote para Flash View Sheet
Proporciona interfaz para crear y configurar tablas pivote (simple y combinada)
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QGroupBox, QFrame, QComboBox, QTableView,
                               QTabWidget, QTextEdit, QProgressBar, QMessageBox,
                               QCheckBox, QSpinBox, QListWidget, QListWidgetItem, QLineEdit)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QPixmap
import pandas as pd
import traceback
from typing import Dict, List, Any, Optional
import logging

# Configurar logging
logger = logging.getLogger(__name__)


class PivotWorkerThread(QThread):
    """Hilo para ejecutar operaciones de pivoteo en segundo plano"""
    
    progress_updated = Signal(int, str)
    pivot_completed = Signal(object)  # Pandas DataFrame
    error_occurred = Signal(str)
    
    def __init__(self, df, pivot_type, parameters):
        super().__init__()
        self.df = df.copy() if df is not None else None
        self.pivot_type = pivot_type  # 'simple' o 'combined'
        self.parameters = parameters
        
    def run(self):
        """Ejecutar el pivoteo"""
        try:
            if self.df is None or self.df.empty:
                raise ValueError("No hay datos para pivotear")
                
            self.progress_updated.emit(10, "Iniciando configuración de tabla pivote...")
            
            # Importar las clases de pivoteo
            from core.pivot import SimplePivotTable, CombinedPivotTable
            
            self.progress_updated.emit(30, "Configurando parámetros...")
            
            # Seleccionar tipo de pivoteo
            if self.pivot_type == 'simple':
                pivot_table = SimplePivotTable()
            else:
                pivot_table = CombinedPivotTable()
                
            self.progress_updated.emit(50, "Ejecutando pivoteo...")
            
            # Ejecutar pivoteo
            result = pivot_table.execute(self.df, self.parameters)
            
            self.progress_updated.emit(90, "Finalizando...")
            self.pivot_completed.emit(result)
            
        except Exception as e:
            error_msg = f"Error al crear tabla pivote: {str(e)}\n{traceback.format_exc()}"
            self.error_occurred.emit(error_msg)


class PivotTableWidget(QWidget):
    """
    Widget principal para crear y configurar tablas pivote
    Soporta modos Simple y Combinado con preview en tiempo real
    """
    
    # Señales
    pivot_created = Signal(object)  # Pandas DataFrame del resultado
    data_changed = Signal(object)   # Pandas DataFrame original
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.df_original = None
        self.df_current = None
        self.worker_thread = None
        self.current_pivot_params = {}
        self.current_pivot_type = 'simple'
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Título principal
        title_label = QLabel("Tabla Pivote - Análisis Avanzado")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                background-color: #2c3e50;
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # Crear splitter principal
        from PySide6.QtWidgets import QSplitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo: Configuración
        config_panel = self.create_config_panel()
        splitter.addWidget(config_panel)
        
        # Panel derecho: Preview y resultado
        preview_panel = self.create_preview_panel()
        splitter.addWidget(preview_panel)
        
        # Configurar proporciones del splitter
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter)
        
        # Panel inferior: Botones de acción
        self.create_action_panel(main_layout)
        
    def create_config_panel(self):
        """Crear panel de configuración"""
        config_widget = QWidget()
        config_layout = QVBoxLayout(config_widget)
        
        # Grupo: Selección de tipo de pivoteo
        type_group = QGroupBox("Tipo de Pivoteo")
        type_layout = QVBoxLayout(type_group)
        
        self.pivot_type_combo = QComboBox()
        self.pivot_type_combo.addItems([
            "Pivoteo Simple",
            "Pivoteo Combinado"
        ])
        self.pivot_type_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
        """)
        type_layout.addWidget(self.pivot_type_combo)
        
        # Información del tipo seleccionado
        self.type_info_label = QLabel()
        self.type_info_label.setWordWrap(True)
        self.type_info_label.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                padding: 10px;
                border-radius: 4px;
                font-style: italic;
                color: #2c3e50;
            }
        """)
        type_layout.addWidget(self.type_info_label)
        
        config_layout.addWidget(type_group)
        
        # Tabs para diferentes configuraciones
        self.config_tabs = QTabWidget()
        
        # Tab: Configuración Básica
        self.create_basic_config_tab()
        
        # Tab: Filtros Avanzados
        self.create_filters_config_tab()
        
        # Tab: Agregaciones
        self.create_aggregations_config_tab()
        
        # Tab: Opciones Avanzadas
        self.create_advanced_options_tab()
        
        config_layout.addWidget(self.config_tabs)
        
        return config_widget
        
    def create_basic_config_tab(self):
        """Crear tab de configuración básica"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Configuración para índices
        index_group = QGroupBox("Configurar Índices (Filas)")
        index_layout = QVBoxLayout(index_group)
        
        self.index_columns_list = QListWidget()
        self.index_columns_list.setSelectionMode(QListWidget.MultiSelection)
        self.index_columns_list.setMaximumHeight(100)
        layout.addWidget(QLabel("Seleccionar columnas para índices:"))
        index_layout.addWidget(self.index_columns_list)
        
        layout.addWidget(index_group)
        
        # Configuración para columnas
        columns_group = QGroupBox("Configurar Columnas del Pivote")
        columns_layout = QVBoxLayout(columns_group)
        
        self.pivot_columns_list = QListWidget()
        self.pivot_columns_list.setSelectionMode(QListWidget.MultiSelection)
        self.pivot_columns_list.setMaximumHeight(100)
        layout.addWidget(QLabel("Seleccionar columnas para columnas del pivote:"))
        columns_layout.addWidget(self.pivot_columns_list)
        
        layout.addWidget(columns_group)
        
        # Configuración para valores
        values_group = QGroupBox("Configurar Valores")
        values_layout = QVBoxLayout(values_group)
        
        self.values_columns_list = QListWidget()
        self.values_columns_list.setSelectionMode(QListWidget.MultiSelection)
        self.values_columns_list.setMaximumHeight(100)
        layout.addWidget(QLabel("Seleccionar columnas para valores:"))
        values_layout.addWidget(self.values_columns_list)
        
        layout.addWidget(values_group)
        
        # Configuración de funciones de agregación
        agg_group = QGroupBox("Funciones de Agregación")
        agg_layout = QVBoxLayout(agg_group)
        
        self.agg_functions_combo = QComboBox()
        self.agg_functions_combo.setEditable(True)
        layout.addWidget(QLabel("Función de agregación:"))
        agg_layout.addWidget(self.agg_functions_combo)
        
        layout.addWidget(agg_group)
        
        self.config_tabs.addTab(tab, "Configuración Básica")
        
    def create_filters_config_tab(self):
        """Crear tab de configuración de filtros"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Panel de filtros avanzados
        filters_label = QLabel("Filtros Avanzados (se aplicarán antes del pivoteo)")
        filters_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(filters_label)
        
        # Integrar PivotFilterPanel
        from app.widgets.pivot_filter_panel import PivotFilterPanel
        self.filter_panel = PivotFilterPanel(self.df_original)
        layout.addWidget(self.filter_panel)
        
        self.config_tabs.addTab(tab, "Filtros")
        
    def create_aggregations_config_tab(self):
        """Crear tab de configuración de agregaciones"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Panel de agregaciones
        agg_label = QLabel("Configuración de Funciones de Agregación")
        agg_label.setStyleSheet("font-weight: bold; color: #e67e22;")
        layout.addWidget(agg_label)
        
        # Integrar PivotAggregationPanel
        from app.widgets.pivot_aggregation_panel import PivotAggregationPanel
        self.aggregation_panel = PivotAggregationPanel(self.df_original)
        layout.addWidget(self.aggregation_panel)
        
        self.config_tabs.addTab(tab, "Agregaciones")
        
    def create_advanced_options_tab(self):
        """Crear tab de opciones avanzadas"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Opciones de configuración
        options_group = QGroupBox("Opciones de Configuración")
        options_layout = QVBoxLayout(options_group)
        
        # Margins (totales)
        self.margins_check = QCheckBox("Mostrar totales (margins)")
        self.margins_check.setChecked(False)
        options_layout.addWidget(self.margins_check)
        
        # Nombre de margins
        margins_name_layout = QHBoxLayout()
        margins_name_layout.addWidget(QLabel("Nombre para totales:"))
        self.margins_name_edit = QLineEdit("Total")
        margins_name_layout.addWidget(self.margins_name_edit)
        options_layout.addLayout(margins_name_layout)
        
        # Dropna
        self.dropna_check = QCheckBox("Eliminar filas con todos los valores NaN")
        self.dropna_check.setChecked(True)
        options_layout.addWidget(self.dropna_check)
        
        # Fill value
        fill_value_layout = QHBoxLayout()
        fill_value_layout.addWidget(QLabel("Valor de relleno:"))
        self.fill_value_edit = QLineEdit()
        self.fill_value_edit.setPlaceholderText("Dejar vacío para no rellenar")
        fill_value_layout.addWidget(self.fill_value_edit)
        options_layout.addLayout(fill_value_layout)
        
        layout.addWidget(options_group)
        
        self.config_tabs.addTab(tab, "Opciones Avanzadas")
        
    def create_preview_panel(self):
        """Crear panel de preview y resultado"""
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        # Título del panel
        preview_title = QLabel("Preview y Resultado")
        preview_title.setFont(QFont("Arial", 12, QFont.Bold))
        preview_title.setAlignment(Qt.AlignCenter)
        preview_title.setStyleSheet("""
            QLabel {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        preview_layout.addWidget(preview_title)
        
        # Tabs para preview y resultado
        self.preview_tabs = QTabWidget()
        
        # Tab: Preview Original
        self.create_preview_original_tab()
        
        # Tab: Resultado Pivote
        self.create_pivot_result_tab()
        
        # Tab: Historial
        self.create_pivot_history_tab()
        
        preview_layout.addWidget(self.preview_tabs)
        
        return preview_widget
        
    def create_preview_original_tab(self):
        """Crear tab de preview de datos originales"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Información del dataset
        self.original_info_label = QLabel("No hay datos cargados")
        self.original_info_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 10px;
                border-radius: 4px;
                font-style: italic;
            }
        """)
        layout.addWidget(self.original_info_label)
        
        # Vista de tabla para datos originales
        self.original_table = QTableView()
        self.original_table.setAlternatingRowColors(True)
        self.original_table.setStyleSheet("""
            QTableView {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
            }
        """)
        layout.addWidget(self.original_table)
        
        self.preview_tabs.addTab(tab, "Datos Originales")
        
    def create_pivot_result_tab(self):
        """Crear tab de resultado del pivote"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Información del resultado
        self.result_info_label = QLabel("No hay resultado de pivoteo")
        self.result_info_label.setStyleSheet("""
            QLabel {
                background-color: #e8f5e8;
                border: 1px solid #c3e6c3;
                padding: 10px;
                border-radius: 4px;
                font-style: italic;
                color: #2d5a2d;
            }
        """)
        layout.addWidget(self.result_info_label)
        
        # Vista de tabla para resultado
        self.result_table = QTableView()
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setStyleSheet("""
            QTableView {
                background-color: white;
                alternate-background-color: #f0f8f0;
                border: 1px solid #c3e6c3;
            }
        """)
        layout.addWidget(self.result_table)
        
        self.preview_tabs.addTab(tab, "Resultado Pivote")
        
    def create_pivot_history_tab(self):
        """Crear tab de historial de pivoteos"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Lista de historial
        self.pivot_history_list = QListWidget()
        self.pivot_history_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
            }
        """)
        layout.addWidget(self.pivot_history_list)
        
        # Botones de gestión de historial
        history_buttons_layout = QHBoxLayout()
        
        clear_history_btn = QPushButton("Limpiar Historial")
        clear_history_btn.clicked.connect(self.clear_pivot_history)
        history_buttons_layout.addWidget(clear_history_btn)
        
        export_result_btn = QPushButton("Exportar Resultado")
        export_result_btn.clicked.connect(self.export_pivot_result)
        history_buttons_layout.addWidget(export_result_btn)
        
        history_buttons_layout.addStretch()
        layout.addLayout(history_buttons_layout)
        
        self.preview_tabs.addTab(tab, "Historial")
        
    def create_action_panel(self, main_layout):
        """Crear panel de botones de acción"""
        action_frame = QFrame()
        action_frame.setStyleSheet("""
            QFrame {
                border-top: 1px solid #bdc3c7;
                padding: 10px;
                background-color: #f8f9fa;
            }
        """)
        action_layout = QHBoxLayout(action_frame)
        
        # Botón Previsualizar
        self.preview_btn = QPushButton("Previsualizar Pivote")
        self.preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.preview_btn.clicked.connect(self.preview_pivot)
        action_layout.addWidget(self.preview_btn)
        
        # Botón Aplicar
        self.apply_btn = QPushButton("Aplicar Pivote")
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.apply_btn.clicked.connect(self.apply_pivot)
        action_layout.addWidget(self.apply_btn)
        
        # Botón Configurar
        self.configure_btn = QPushButton("Configuración Avanzada")
        self.configure_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.configure_btn.clicked.connect(self.open_advanced_config)
        action_layout.addWidget(self.configure_btn)
        
        # Botón Información
        info_btn = QPushButton("Información")
        info_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        info_btn.clicked.connect(self.show_info)
        action_layout.addWidget(info_btn)
        
        action_layout.addStretch()
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        action_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(action_frame)
        
    def setup_connections(self):
        """Configurar conexiones de señales"""
        # Conexión del cambio de tipo de pivoteo
        self.pivot_type_combo.currentTextChanged.connect(self.on_pivot_type_changed)
        
        # Conectar señales de los paneles
        if hasattr(self, 'filter_panel'):
            self.filter_panel.filters_changed.connect(self.on_filters_changed)
        
        if hasattr(self, 'aggregation_panel'):
            self.aggregation_panel.aggregations_changed.connect(self.on_aggregations_changed)
        
        # Inicializar estado de UI
        self.update_ui_state()
        
    def set_data(self, df):
        """Establecer datos para pivotear"""
        self.df_original = df.copy() if df is not None else None
        self.df_current = df.copy() if df is not None else None
        
        # Actualizar paneles
        if hasattr(self, 'filter_panel'):
            self.filter_panel.set_data(df)
        if hasattr(self, 'aggregation_panel'):
            values_columns = self.get_selected_values_columns()
            self.aggregation_panel.set_data(df, values_columns)
        
        # Actualizar UI
        self.update_ui_state()
        self.update_column_selections()
        self.update_original_preview()
        
    def update_ui_state(self):
        """Actualizar estado de UI basado en si hay datos"""
        has_data = self.df_original is not None and not self.df_original.empty
        
        # Habilitar/deshabilitar elementos
        widgets_to_enable = [
            self.pivot_type_combo,
            self.config_tabs,
            self.preview_btn,
            self.apply_btn
        ]
        
        for widget in widgets_to_enable:
            widget.setEnabled(has_data)
            
        if not has_data:
            self.original_info_label.setText("No hay datos cargados. Carga un archivo para comenzar.")
            self.original_table.setModel(None)
            self.result_table.setModel(None)
            
    def update_column_selections(self):
        """Actualizar selecciones de columnas"""
        if self.df_original is None:
            return
            
        columns = self.df_original.columns.tolist()
        
        # Actualizar listas de selección
        lists_to_update = [
            self.index_columns_list,
            self.pivot_columns_list,
            self.values_columns_list
        ]
        
        for list_widget in lists_to_update:
            list_widget.clear()
            for col in columns:
                item = QListWidgetItem(col)
                item.setCheckState(Qt.Unchecked)
                list_widget.addItem(item)
                
        # Actualizar funciones de agregación
        self.agg_functions_combo.clear()
        agg_functions = [
            'sum', 'mean', 'median', 'count', 'min', 'max', 'std', 'var',
            'first', 'last', 'size', 'nunique'
        ]
        self.agg_functions_combo.addItems(agg_functions)
        
        # Actualizar información del dataset
        self.original_info_label.setText(
            f"Dataset: {len(self.df_original)} filas, {len(self.df_original.columns)} columnas"
        )
        
    def update_original_preview(self):
        """Actualizar preview de datos originales"""
        if self.df_original is not None and len(self.df_original) > 0:
            from app.models.pandas_model import VirtualizedPandasModel
            
            # Mostrar solo las primeras 50 filas para preview
            preview_df = self.df_original.head(50)
            model = VirtualizedPandasModel(preview_df)
            self.original_table.setModel(model)
        else:
            self.original_table.setModel(None)
            
    def on_pivot_type_changed(self, text):
        """Manejar cambio de tipo de pivoteo"""
        if "Simple" in text:
            self.current_pivot_type = 'simple'
            self.type_info_label.setText(
                "Pivoteo Simple: Una columna para índices, una para columnas del pivote, "
                "una para valores y una función de agregación."
            )
            # Configurar para selección simple
            self.index_columns_list.setSelectionMode(QListWidget.SingleSelection)
            self.pivot_columns_list.setSelectionMode(QListWidget.SingleSelection)
            self.values_columns_list.setSelectionMode(QListWidget.SingleSelection)
        else:
            self.current_pivot_type = 'combined'
            self.type_info_label.setText(
                "Pivoteo Combinado: Múltiples columnas para índices, columnas del pivote, "
                "valores y múltiples funciones de agregación."
            )
            # Configurar para selección múltiple
            self.index_columns_list.setSelectionMode(QListWidget.MultiSelection)
            self.pivot_columns_list.setSelectionMode(QListWidget.MultiSelection)
            self.values_columns_list.setSelectionMode(QListWidget.MultiSelection)
    
    def get_selected_values_columns(self):
        """Obtener columnas de valores seleccionadas"""
        values_columns = []
        for i in range(self.values_columns_list.count()):
            item = self.values_columns_list.item(i)
            if item.checkState() == Qt.Checked:
                values_columns.append(item.text())
        return values_columns
    
    def on_filters_changed(self, filters):
        """Manejar cambios en filtros"""
        self.current_pivot_params['filters'] = filters
    
    def on_aggregations_changed(self, aggregations):
        """Manejar cambios en agregaciones"""
        # Convertir agregaciones a formato de parámetros
        if aggregations:
            aggfuncs = [agg.get('function', 'mean') for agg in aggregations if agg.get('active', True)]
            self.current_pivot_params['aggfuncs'] = aggfuncs
            
    def get_current_parameters(self):
        """Obtener parámetros actuales de configuración"""
        parameters = {}
        
        # Obtener índices seleccionados
        index_columns = []
        for i in range(self.index_columns_list.count()):
            item = self.index_columns_list.item(i)
            if item.checkState() == Qt.Checked:
                index_columns.append(item.text())
        parameters['index'] = index_columns
        
        # Obtener columnas del pivote seleccionadas
        pivot_columns = []
        for i in range(self.pivot_columns_list.count()):
            item = self.pivot_columns_list.item(i)
            if item.checkState() == Qt.Checked:
                pivot_columns.append(item.text())
        parameters['columns'] = pivot_columns
        
        # Obtener columnas de valores seleccionadas
        values_columns = []
        for i in range(self.values_columns_list.count()):
            item = self.values_columns_list.item(i)
            if item.checkState() == Qt.Checked:
                values_columns.append(item.text())
        parameters['values'] = values_columns
        
        # Obtener función de agregación
        if self.current_pivot_type == 'simple':
            parameters['aggfunc'] = self.agg_functions_combo.currentText()
        else:
            # Para combined, usar la misma función para todos los valores por ahora
            parameters['aggfuncs'] = [self.agg_functions_combo.currentText()]
            
        # Obtener opciones avanzadas
        parameters['margins'] = self.margins_check.isChecked()
        parameters['margins_name'] = self.margins_name_edit.text()
        parameters['dropna'] = self.dropna_check.isChecked()
        
        fill_value = self.fill_value_edit.text().strip()
        if fill_value:
            try:
                # Intentar convertir a número si es posible
                if fill_value.replace('.', '').replace('-', '').isdigit():
                    parameters['fill_value'] = float(fill_value)
                else:
                    parameters['fill_value'] = fill_value
            except ValueError:
                parameters['fill_value'] = fill_value
        else:
            parameters['fill_value'] = None
            
        return parameters
        
    def validate_parameters(self, parameters):
        """Validar parámetros de configuración"""
        errors = []
        
        if not parameters.get('index'):
            errors.append("Debe seleccionar al menos una columna para índices")
            
        if not parameters.get('columns'):
            errors.append("Debe seleccionar al menos una columna para columnas del pivote")
            
        if not parameters.get('values'):
            errors.append("Debe seleccionar al menos una columna para valores")
            
        # Validaciones específicas para pivoteo simple
        if self.current_pivot_type == 'simple':
            if len(parameters.get('index', [])) > 1:
                errors.append("Pivoteo simple solo permite una columna para índices")
            if len(parameters.get('columns', [])) > 1:
                errors.append("Pivoteo simple solo permite una columna para columnas del pivote")
            if len(parameters.get('values', [])) > 1:
                errors.append("Pivoteo simple solo permite una columna para valores")
                
        return errors
        
    def preview_pivot(self):
        """Previsualizar resultado del pivoteo"""
        if self.df_original is None:
            return
            
        # Obtener parámetros
        parameters = self.get_current_parameters()
        
        # Validar parámetros
        errors = self.validate_parameters(parameters)
        if errors:
            QMessageBox.warning(self, "Parámetros Inválidos", "\n".join(errors))
            return
            
        # Mostrar barra de progreso
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Ejecutar pivoteo en hilo separado
        if self.worker_thread:
            self.worker_thread.terminate()
            
        self.worker_thread = PivotWorkerThread(
            self.df_original, self.current_pivot_type, parameters
        )
        self.worker_thread.progress_updated.connect(self.update_progress)
        self.worker_thread.pivot_completed.connect(self.on_preview_completed)
        self.worker_thread.error_occurred.connect(self.on_pivot_error)
        self.worker_thread.start()
        
    def apply_pivot(self):
        """Aplicar pivoteo permanentemente"""
        if self.df_original is None:
            return
            
        # Primero hacer preview
        self.preview_pivot()
        # El worker emitirá señal y se actualizará automáticamente
        
    def update_progress(self, value, message):
        """Actualizar barra de progreso"""
        self.progress_bar.setValue(value)
        
    def on_preview_completed(self, result_df):
        """Manejar preview completado"""
        self.progress_bar.setVisible(False)
        
        if result_df is not None and not result_df.empty:
            # Actualizar vista de resultado
            self.update_result_table(result_df)
            
            # Actualizar información
            self.result_info_label.setText(
                f"Resultado: {len(result_df)} filas, {len(result_df.columns)} columnas"
            )
            
            # Cambiar a tab de resultado
            self.preview_tabs.setCurrentIndex(1)
            
            # Agregar al historial
            self.add_to_pivot_history()
            
            # Guardar parámetros actuales
            self.current_pivot_params = self.get_current_parameters()
            
        else:
            QMessageBox.warning(self, "Advertencia", "El pivoteo no produjo resultados.")
            
    def on_pivot_error(self, error_message):
        """Manejar error en pivoteo"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", error_message)
        
    def update_result_table(self, df):
        """Actualizar tabla de resultado"""
        from app.models.pandas_model import VirtualizedPandasModel
        
        if df is not None and len(df) > 0:
            model = VirtualizedPandasModel(df)
            self.result_table.setModel(model)
        else:
            self.result_table.setModel(None)
            
    def add_to_pivot_history(self):
        """Agregar operación al historial"""
        timestamp = pd.Timestamp.now().strftime("%H:%M:%S")
        
        # Crear texto descriptivo
        params = self.current_pivot_params
        history_text = f"[{timestamp}] {self.current_pivot_type.title()} - "
        history_text += f"Índices: {', '.join(params.get('index', []))} | "
        history_text += f"Columnas: {', '.join(params.get('columns', []))} | "
        history_text += f"Valores: {', '.join(params.get('values', []))}"
        
        # Agregar a la lista
        item = QListWidgetItem(history_text)
        item.setData(Qt.UserRole, self.current_pivot_params.copy())
        self.pivot_history_list.addItem(item)
        
    def clear_pivot_history(self):
        """Limpiar historial de pivoteos"""
        self.pivot_history_list.clear()
        QMessageBox.information(self, "Éxito", "Historial de pivoteos limpiado.")
        
    def export_pivot_result(self):
        """Exportar resultado del pivoteo"""
        from PySide6.QtWidgets import QFileDialog
        from core.data_handler import save_dataframe
        
        # Obtener resultado actual
        model = self.result_table.model()
        if model is None:
            QMessageBox.information(self, "Información", "No hay resultado para exportar.")
            return
            
        # Obtener DataFrame del modelo
        # Nota: esto podría mejorarse para obtener el DataFrame real
        QMessageBox.information(self, "Exportar", "Funcionalidad de exportación en desarrollo.")
        
    def open_advanced_config(self):
        """Abrir diálogo de configuración avanzada"""
        from app.widgets.pivot_config_dialog import PivotConfigDialog
        
        dialog = PivotConfigDialog(self.df_original, self)
        dialog.set_data(self.df_original)
        
        if dialog.exec():
            config = dialog.get_current_configuration()
            self.apply_configuration_from_dialog(config)
    
    def apply_configuration_from_dialog(self, config):
        """Aplicar configuración desde el diálogo"""
        # Aplicar configuración básica
        if 'index' in config:
            self.set_list_selections(self.index_columns_list, config['index'])
        if 'columns' in config:
            self.set_list_selections(self.pivot_columns_list, config['columns'])
        if 'values' in config:
            self.set_list_selections(self.values_columns_list, config['values'])
        
        # Aplicar funciones de agregación
        if 'aggfuncs' in config and config['aggfuncs']:
            self.agg_functions_combo.setCurrentText(config['aggfuncs'][0])
        
        # Aplicar opciones avanzadas
        if 'margins' in config:
            self.margins_check.setChecked(config['margins'])
        if 'margins_name' in config:
            self.margins_name_edit.setText(config['margins_name'])
        if 'dropna' in config:
            self.dropna_check.setChecked(config['dropna'])
        if 'fill_value' in config:
            self.fill_value_edit.setText(str(config['fill_value']) if config['fill_value'] else '')
        
        # Aplicar filtros
        if 'filters' in config:
            if hasattr(self, 'filter_panel'):
                self.filter_panel.set_active_filters(config['filters'])
    
    def set_list_selections(self, list_widget, selected_items):
        """Establecer selecciones en un QListWidget"""
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if item.text() in selected_items:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
        
    def show_info(self):
        """Mostrar información sobre la tabla pivote"""
        info_text = """
        <h3>Tabla Pivote - Información</h3>
        <p><strong>Pivoteo Simple:</strong></p>
        <ul>
            <li>Una columna para índices (filas)</li>
            <li>Una columna para columnas del pivote</li>
            <li>Una columna para valores</li>
            <li>Una función de agregación</li>
        </ul>
        <p><strong>Pivoteo Combinado:</strong></p>
        <ul>
            <li>Múltiples columnas para índices</li>
            <li>Múltiples columnas para columnas del pivote</li>
            <li>Múltiples columnas para valores</li>
            <li>Múltiples funciones de agregación</li>
        </ul>
        <p><strong>Funciones de Agregación Disponibles:</strong></p>
        <ul>
            <li>sum, mean, median, count, min, max</li>
            <li>std, var, first, last, size, nunique</li>
        </ul>
        """
        
        QMessageBox.about(self, "Información - Tabla Pivote", info_text)