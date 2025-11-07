"""
Diálogo de Configuración de Tabla Pivote para Flash View Sheet
Proporciona interfaz detallada para configurar parámetros de pivoteo
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QGroupBox, QTabWidget, QListWidget, QListWidgetItem,
                               QPushButton, QComboBox, QLineEdit, QCheckBox,
                               QSpinBox, QDoubleSpinBox, QTextEdit, QFormLayout,
                               QDialogButtonBox, QSplitter, QFrame, QMessageBox, QWidget)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import pandas as pd
from typing import Dict, List, Any, Optional


class PivotConfigDialog(QDialog):
    """
    Diálogo para configuración avanzada de tabla pivote
    Permite configurar todos los parámetros de manera detallada
    """
    
    # Señales
    configuration_applied = Signal(dict)  # Parámetros configurados
    preview_requested = Signal(dict)      # Solicitud de preview
    
    def __init__(self, df_original=None, parent=None):
        super().__init__(parent)
        self.df_original = df_original
        self.current_config = {}
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Configurar la interfaz del diálogo"""
        self.setWindowTitle("Configuración Avanzada - Tabla Pivote")
        self.resize(800, 600)
        self.setModal(True)
        
        main_layout = QVBoxLayout(self)
        
        # Título del diálogo
        title_label = QLabel("Configuración Detallada de Tabla Pivote")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
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
        
        # Crear tabs para diferentes configuraciones
        self.config_tabs = QTabWidget()
        
        # Tab: Configuración Básica
        self.create_basic_config_tab()
        
        # Tab: Filtros Avanzados
        self.create_filters_config_tab()
        
        # Tab: Agregaciones
        self.create_aggregations_config_tab()
        
        # Tab: Opciones Avanzadas
        self.create_advanced_options_tab()
        
        # Tab: Vista Previa
        self.create_preview_tab()
        
        main_layout.addWidget(self.config_tabs)
        
        # Panel de botones
        self.create_button_panel(main_layout)
        
    def create_basic_config_tab(self):
        """Crear tab de configuración básica"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Crear splitter para índices/columnas y valores
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo: Índices y Columnas
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Grupo: Configuración de Índices
        index_group = QGroupBox("Columnas para Índices (Filas)")
        index_layout = QVBoxLayout(index_group)
        
        self.index_columns_list = QListWidget()
        self.index_columns_list.setSelectionMode(QListWidget.MultiSelection)
        self.index_columns_list.setMaximumHeight(150)
        index_layout.addWidget(QLabel("Seleccionar columnas que将成为n las filas del pivote:"))
        index_layout.addWidget(self.index_columns_list)
        
        left_layout.addWidget(index_group)
        
        # Grupo: Configuración de Columnas del Pivote
        columns_group = QGroupBox("Columnas para Columnas del Pivote")
        columns_layout = QVBoxLayout(columns_group)
        
        self.pivot_columns_list = QListWidget()
        self.pivot_columns_list.setSelectionMode(QListWidget.MultiSelection)
        self.pivot_columns_list.setMaximumHeight(150)
        columns_layout.addWidget(QLabel("Seleccionar columnas que se convertirán en columnas del pivote:"))
        columns_layout.addWidget(self.pivot_columns_list)
        
        left_layout.addWidget(columns_group)
        
        splitter.addWidget(left_panel)
        
        # Panel derecho: Valores
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Grupo: Configuración de Valores
        values_group = QGroupBox("Columnas para Valores")
        values_layout = QVBoxLayout(values_group)
        
        self.values_columns_list = QListWidget()
        self.values_columns_list.setSelectionMode(QListWidget.MultiSelection)
        self.values_columns_list.setMaximumHeight(200)
        values_layout.addWidget(QLabel("Seleccionar columnas que contengan los valores a agregar:"))
        values_layout.addWidget(self.values_columns_list)
        
        right_layout.addWidget(values_group)
        
        # Información de columnas
        info_group = QGroupBox("Información del Dataset")
        info_layout = QVBoxLayout(info_group)
        
        self.dataset_info_text = QTextEdit()
        self.dataset_info_text.setMaximumHeight(100)
        self.dataset_info_text.setReadOnly(True)
        info_layout.addWidget(self.dataset_info_text)
        
        right_layout.addWidget(info_group)
        
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 400])
        
        layout.addWidget(splitter)
        
        self.config_tabs.addTab(tab, "Configuración Básica")
        
    def create_filters_config_tab(self):
        """Crear tab de configuración de filtros"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Título de filtros
        filters_title = QLabel("Filtros Avanzados")
        filters_title.setFont(QFont("Arial", 12, QFont.Bold))
        filters_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(filters_title)
        
        # Descripción
        description = QLabel(
            "Los filtros se aplican antes del pivoteo. Puedes crear múltiples condiciones "
            "con operadores lógicos AND/OR."
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #7f8c8d; font-style: italic; margin-bottom: 10px;")
        layout.addWidget(description)
        
        # Lista de filtros activos
        filters_group = QGroupBox("Filtros Activos")
        filters_layout = QVBoxLayout(filters_group)
        
        self.filters_list = QListWidget()
        self.filters_list.setMaximumHeight(200)
        filters_layout.addWidget(self.filters_list)
        
        # Botones para gestión de filtros
        filter_buttons_layout = QHBoxLayout()
        
        add_filter_btn = QPushButton("Agregar Filtro")
        add_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        add_filter_btn.clicked.connect(self.add_filter)
        filter_buttons_layout.addWidget(add_filter_btn)
        
        edit_filter_btn = QPushButton("Editar Filtro")
        edit_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        edit_filter_btn.clicked.connect(self.edit_filter)
        filter_buttons_layout.addWidget(edit_filter_btn)
        
        remove_filter_btn = QPushButton("Eliminar Filtro")
        remove_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        remove_filter_btn.clicked.connect(self.remove_filter)
        filter_buttons_layout.addWidget(remove_filter_btn)
        
        filter_buttons_layout.addStretch()
        filters_layout.addLayout(filter_buttons_layout)
        
        layout.addWidget(filters_group)
        
        # Panel de operadores lógicos
        logic_group = QGroupBox("Operadores Lógicos")
        logic_layout = QHBoxLayout(logic_group)
        
        self.logic_operator_combo = QComboBox()
        self.logic_operator_combo.addItems(["AND", "OR"])
        logic_layout.addWidget(QLabel("Operador para combinar filtros:"))
        logic_layout.addWidget(self.logic_operator_combo)
        logic_layout.addStretch()
        
        layout.addWidget(logic_group)
        
        self.config_tabs.addTab(tab, "Filtros Avanzados")
        
    def create_aggregations_config_tab(self):
        """Crear tab de configuración de agregaciones"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Título
        agg_title = QLabel("Configuración de Agregaciones")
        agg_title.setFont(QFont("Arial", 12, QFont.Bold))
        agg_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(agg_title)
        
        # Modo de agregación
        mode_group = QGroupBox("Modo de Agregación")
        mode_layout = QVBoxLayout(mode_group)
        
        self.agg_mode_combo = QComboBox()
        self.agg_mode_combo.addItems([
            "Una función para todos los valores",
            "Función específica por valor",
            "Múltiples funciones por valor"
        ])
        self.agg_mode_combo.currentTextChanged.connect(self.on_agg_mode_changed)
        mode_layout.addWidget(QLabel("Seleccionar cómo aplicar las funciones de agregación:"))
        mode_layout.addWidget(self.agg_mode_combo)
        
        layout.addWidget(mode_group)
        
        # Configuración de funciones
        functions_group = QGroupBox("Funciones de Agregación")
        functions_layout = QVBoxLayout(functions_group)
        
        # Tabla de configuración de funciones
        self.functions_table = QListWidget()
        self.functions_table.setMaximumHeight(200)
        functions_layout.addWidget(QLabel("Configurar funciones de agregación:"))
        functions_layout.addWidget(self.functions_table)
        
        # Botones para gestión de funciones
        func_buttons_layout = QHBoxLayout()
        
        add_func_btn = QPushButton("Agregar Función")
        add_func_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        add_func_btn.clicked.connect(self.add_aggregation_function)
        func_buttons_layout.addWidget(add_func_btn)
        
        remove_func_btn = QPushButton("Eliminar Función")
        remove_func_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        remove_func_btn.clicked.connect(self.remove_aggregation_function)
        func_buttons_layout.addWidget(remove_func_btn)
        
        func_buttons_layout.addStretch()
        functions_layout.addLayout(func_buttons_layout)
        
        layout.addWidget(functions_group)
        
        # Funciones disponibles
        available_group = QGroupBox("Funciones Disponibles")
        available_layout = QVBoxLayout(available_group)
        
        self.available_functions_list = QListWidget()
        self.available_functions_list.setMaximumHeight(120)
        
        # Agregar funciones disponibles
        available_functions = [
            "sum - Suma de valores",
            "mean - Promedio",
            "median - Mediana", 
            "count - Conteo de valores",
            "min - Valor mínimo",
            "max - Valor máximo",
            "std - Desviación estándar",
            "var - Varianza",
            "first - Primer valor",
            "last - Último valor",
            "size - Tamaño del grupo",
            "nunique - Número de valores únicos"
        ]
        
        for func in available_functions:
            self.available_functions_list.addItem(func)
            
        available_layout.addWidget(QLabel("Funciones de agregación disponibles:"))
        available_layout.addWidget(self.available_functions_list)
        
        layout.addWidget(available_group)
        
        self.config_tabs.addTab(tab, "Agregaciones")
        
    def create_advanced_options_tab(self):
        """Crear tab de opciones avanzadas"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Opciones de márgenes
        margins_group = QGroupBox("Opciones de Totales (Margins)")
        margins_layout = QFormLayout(margins_group)
        
        self.show_margins_check = QCheckBox("Mostrar filas y columnas de totales")
        self.show_margins_check.setChecked(False)
        margins_layout.addRow("", self.show_margins_check)
        
        margins_name_layout = QHBoxLayout()
        self.margins_name_edit = QLineEdit("Total")
        margins_name_layout.addWidget(QLabel("Nombre para totales:"))
        margins_name_layout.addWidget(self.margins_name_edit)
        margins_layout.addRow("", margins_name_layout)
        
        layout.addWidget(margins_group)
        
        # Opciones de valores faltantes
        missing_group = QGroupBox("Manejo de Valores Faltantes")
        missing_layout = QFormLayout(missing_group)
        
        self.dropna_check = QCheckBox("Eliminar filas con todos los valores NaN")
        self.dropna_check.setChecked(True)
        missing_layout.addRow("", self.dropna_check)
        
        fill_value_layout = QHBoxLayout()
        self.fill_value_edit = QLineEdit()
        self.fill_value_edit.setPlaceholderText("Dejar vacío para no rellenar")
        fill_value_layout.addWidget(QLabel("Valor de relleno:"))
        fill_value_layout.addWidget(self.fill_value_edit)
        missing_layout.addRow("", fill_value_layout)
        
        layout.addWidget(missing_group)
        
        # Opciones de rendimiento
        performance_group = QGroupBox("Opciones de Rendimiento")
        performance_layout = QFormLayout(performance_group)
        
        self.use_cache_check = QCheckBox("Usar cache para operaciones repetidas")
        self.use_cache_check.setChecked(True)
        performance_layout.addRow("", self.use_cache_check)
        
        max_rows_layout = QHBoxLayout()
        self.max_rows_spin = QSpinBox()
        self.max_rows_spin.setRange(1000, 1000000)
        self.max_rows_spin.setValue(100000)
        self.max_rows_spin.setSuffix(" filas")
        max_rows_layout.addWidget(QLabel("Máximo de filas a procesar:"))
        max_rows_layout.addWidget(self.max_rows_spin)
        performance_layout.addRow("", max_rows_layout)
        
        layout.addWidget(performance_group)
        
        self.config_tabs.addTab(tab, "Opciones Avanzadas")
        
    def create_preview_tab(self):
        """Crear tab de vista previa"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Título
        preview_title = QLabel("Vista Previa de Configuración")
        preview_title.setFont(QFont("Arial", 12, QFont.Bold))
        preview_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(preview_title)
        
        # Texto de configuración
        config_group = QGroupBox("Configuración Actual")
        config_layout = QVBoxLayout(config_group)
        
        self.config_preview_text = QTextEdit()
        self.config_preview_text.setReadOnly(True)
        self.config_preview_text.setMaximumHeight(200)
        config_layout.addWidget(self.config_preview_text)
        
        layout.addWidget(config_group)
        
        # Botones de acción
        preview_buttons_layout = QHBoxLayout()
        
        self.update_preview_btn = QPushButton("Actualizar Vista Previa")
        self.update_preview_btn.setStyleSheet("""
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
        self.update_preview_btn.clicked.connect(self.update_configuration_preview)
        preview_buttons_layout.addWidget(self.update_preview_btn)
        
        self.test_config_btn = QPushButton("Probar Configuración")
        self.test_config_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        self.test_config_btn.clicked.connect(self.test_configuration)
        preview_buttons_layout.addWidget(self.test_config_btn)
        
        preview_buttons_layout.addStretch()
        layout.addLayout(preview_buttons_layout)
        
        self.config_tabs.addTab(tab, "Vista Previa")
        
    def create_button_panel(self, main_layout):
        """Crear panel de botones del diálogo"""
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                border-top: 1px solid #bdc3c7;
                padding: 10px;
                background-color: #f8f9fa;
            }
        """)
        button_layout = QHBoxLayout(button_frame)
        
        # Botón Vista Previa
        preview_btn = QPushButton("Vista Previa")
        preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        preview_btn.clicked.connect(self.preview_configuration)
        button_layout.addWidget(preview_btn)
        
        button_layout.addStretch()
        
        # Botones estándar del diálogo
        self.dialog_buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        
        self.dialog_buttons.accepted.connect(self.accept_configuration)
        self.dialog_buttons.rejected.connect(self.reject)
        self.dialog_buttons.button(QDialogButtonBox.Apply).clicked.connect(self.apply_configuration)
        
        button_layout.addWidget(self.dialog_buttons)
        
        main_layout.addWidget(button_frame)
        
    def setup_connections(self):
        """Configurar conexiones de señales"""
        # Actualizar preview cuando cambien los tabs
        self.config_tabs.currentChanged.connect(self.on_tab_changed)
        
        # Actualizar cuando cambien selecciones
        lists_to_connect = [
            self.index_columns_list,
            self.pivot_columns_list,
            self.values_columns_list
        ]
        
        for list_widget in lists_to_connect:
            list_widget.itemSelectionChanged.connect(self.update_configuration_preview)
            
    def set_data(self, df):
        """Establecer datos para configurar"""
        self.df_original = df
        
        if df is not None:
            # Actualizar listas de columnas
            columns = df.columns.tolist()
            
            lists_to_update = [
                self.index_columns_list,
                self.pivot_columns_list, 
                self.values_columns_list
            ]
            
            for list_widget in lists_to_update:
                list_widget.clear()
                for col in columns:
                    item = QListWidgetItem(col)
                    list_widget.addItem(item)
                    
            # Actualizar información del dataset
            self.update_dataset_info()
            
    def update_dataset_info(self):
        """Actualizar información del dataset"""
        if self.df_original is not None:
            info_text = f"""
Dataset: {self.df_original.shape[0]} filas, {self.df_original.shape[1]} columnas

Tipos de datos:
{self.df_original.dtypes.to_string()}

Primeras 3 filas:
{self.df_original.head(3).to_string()}
            """
            self.dataset_info_text.setPlainText(info_text)
            
    def on_agg_mode_changed(self, text):
        """Manejar cambio de modo de agregación"""
        if "específica" in text:
            # Mostrar configuración específica por valor
            self.functions_table.clear()
            if self.values_columns_list.count() > 0:
                for i in range(self.values_columns_list.count()):
                    item = self.values_columns_list.item(i)
                    if item.isSelected():
                        func_item = QListWidgetItem(f"{item.text()}: mean")
                        self.functions_table.addItem(func_item)
                        
        elif "múltiples" in text:
            # Mostrar configuración con múltiples funciones
            self.functions_table.clear()
            if self.values_columns_list.count() > 0:
                for i in range(self.values_columns_list.count()):
                    item = self.values_columns_list.item(i)
                    if item.isSelected():
                        for func in ['sum', 'mean', 'count']:
                            func_item = QListWidgetItem(f"{item.text()}: {func}")
                            self.functions_table.addItem(func_item)
                            
    def on_tab_changed(self, index):
        """Manejar cambio de tabs"""
        if index == 4:  # Tab de preview
            self.update_configuration_preview()
            
    def update_configuration_preview(self):
        """Actualizar vista previa de configuración"""
        config = self.get_current_configuration()
        
        preview_text = f"""
CONFIGURACIÓN DE TABLA PIVOTE
{'=' * 40}

TIPO DE PIVOTEO: {config.get('pivot_type', 'No seleccionado')}

ÍNDICES (FILAS): {', '.join(config.get('index', [])) or 'Ninguno'}

COLUMNAS DEL PIVOTE: {', '.join(config.get('columns', [])) or 'Ninguno'}

VALORES: {', '.join(config.get('values', [])) or 'Ninguno'}

FUNCIONES DE AGREGACIÓN: {', '.join(config.get('aggfuncs', [])) or 'Ninguno'}

FILTROS: {len(config.get('filters', []))} filtro(s) configurado(s)

OPCIONES AVANZADAS:
- Mostrar márgenes: {config.get('margins', False)}
- Dropna: {config.get('dropna', True)}
- Fill value: {config.get('fill_value', 'Ninguno')}

OPERADOR LÓGICO: {config.get('logic_operator', 'AND')}
        """
        
        self.config_preview_text.setPlainText(preview_text)
        
    def get_current_configuration(self):
        """Obtener configuración actual"""
        config = {}
        
        # Índices seleccionados
        index_columns = []
        for i in range(self.index_columns_list.count()):
            item = self.index_columns_list.item(i)
            if item.isSelected():
                index_columns.append(item.text())
        config['index'] = index_columns
        
        # Columnas del pivote seleccionadas
        pivot_columns = []
        for i in range(self.pivot_columns_list.count()):
            item = self.pivot_columns_list.item(i)
            if item.isSelected():
                pivot_columns.append(item.text())
        config['columns'] = pivot_columns
        
        # Valores seleccionados
        values_columns = []
        for i in range(self.values_columns_list.count()):
            item = self.values_columns_list.item(i)
            if item.isSelected():
                values_columns.append(item.text())
        config['values'] = values_columns
        
        # Funciones de agregación
        agg_functions = []
        for i in range(self.functions_table.count()):
            item = self.functions_table.item(i)
            text = item.text()
            if ':' in text:
                func = text.split(':')[-1].strip()
                agg_functions.append(func)
            else:
                agg_functions.append(text)
        config['aggfuncs'] = agg_functions or ['mean']
        
        # Tipo de pivoteo basado en la configuración
        if (len(index_columns) <= 1 and len(pivot_columns) <= 1 and 
            len(values_columns) <= 1 and len(agg_functions) <= 1):
            config['pivot_type'] = 'Simple'
        else:
            config['pivot_type'] = 'Combinado'
            
        # Opciones avanzadas
        config['margins'] = self.show_margins_check.isChecked()
        config['margins_name'] = self.margins_name_edit.text()
        config['dropna'] = self.dropna_check.isChecked()
        config['fill_value'] = self.fill_value_edit.text() or None
        config['logic_operator'] = self.logic_operator_combo.currentText()
        
        return config
        
    def get_config(self):
        """Obtener configuración en formato compatible con las funciones de pivote"""
        config = self.get_current_configuration()
        
        # Convertir a formato compatible con SimplePivotTable y CombinedPivotTable
        if config.get('pivot_type') == 'Simple':
            # Formato simple: una sola columna para cada parámetro
            if config.get('index'):
                config['index'] = config['index'][0] if isinstance(config['index'], list) else config['index']
            if config.get('columns'):
                config['columns'] = config['columns'][0] if isinstance(config['columns'], list) else config['columns']
            if config.get('values'):
                config['values'] = config['values'][0] if isinstance(config['values'], list) else config['values']
            if config.get('aggfuncs'):
                config['aggfunc'] = config['aggfuncs'][0] if isinstance(config['aggfuncs'], list) else config['aggfuncs']
                # Remover aggfuncs ya que se usa aggfunc para simple
                config.pop('aggfuncs', None)
        else:
            # Formato combinado: listas para múltiples parámetros
            if not isinstance(config.get('index'), list):
                config['index'] = config.get('index', []) if config.get('index') else []
            if not isinstance(config.get('columns'), list):
                config['columns'] = config.get('columns', []) if config.get('columns') else []
            if not isinstance(config.get('values'), list):
                config['values'] = config.get('values', []) if config.get('values') else []
            if not isinstance(config.get('aggfuncs'), list):
                config['aggfuncs'] = config.get('aggfuncs', []) if config.get('aggfuncs') else ['mean']
        
        return config
        
    def add_filter(self):
        """Agregar nuevo filtro"""
        # TODO: Implementar diálogo de filtro
        pass
        
    def edit_filter(self):
        """Editar filtro seleccionado"""
        # TODO: Implementar edición de filtro
        pass
        
    def remove_filter(self):
        """Eliminar filtro seleccionado"""
        current_row = self.filters_list.currentRow()
        if current_row >= 0:
            self.filters_list.takeItem(current_row)
            
    def add_aggregation_function(self):
        """Agregar función de agregación"""
        current_item = self.available_functions_list.currentItem()
        if current_item:
            func_text = current_item.text()
            func_name = func_text.split(' - ')[0]
            self.functions_table.addItem(func_name)
            
    def remove_aggregation_function(self):
        """Eliminar función de agregación"""
        current_row = self.functions_table.currentRow()
        if current_row >= 0:
            self.functions_table.takeItem(current_row)
            
    def preview_configuration(self):
        """Vista previa de la configuración"""
        config = self.get_current_configuration()
        self.preview_requested.emit(config)
        
    def test_configuration(self):
        """Probar configuración actual"""
        config = self.get_current_configuration()
        # TODO: Implementar prueba de configuración
        QMessageBox.information(self, "Prueba", "Funcionalidad de prueba en desarrollo.")
        
    def apply_configuration(self):
        """Aplicar configuración"""
        config = self.get_current_configuration()
        self.configuration_applied.emit(config)
        QMessageBox.information(self, "Éxito", "Configuración aplicada exitosamente.")
        
    def accept_configuration(self):
        """Aceptar configuración y cerrar"""
        config = self.get_current_configuration()
        self.configuration_applied.emit(config)
        self.accept()