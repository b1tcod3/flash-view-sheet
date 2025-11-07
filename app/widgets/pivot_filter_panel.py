"""
Panel de Filtros Avanzados para Tabla Pivote
Proporciona interfaz para crear y gestionar filtros complejos antes del pivoteo
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QGroupBox, QComboBox, QLineEdit, QPushButton,
                               QListWidget, QListWidgetItem, QFrame, QCheckBox,
                               QSpinBox, QDoubleSpinBox, QDateEdit, QTableWidget,
                               QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont
import pandas as pd
from typing import Dict, List, Any, Optional
import logging

# Configurar logging
logger = logging.getLogger(__name__)


class FilterValueWidget(QWidget):
    """Widget dinámico para entrada de valores de filtro según el tipo"""
    
    value_changed = Signal(object)  # Valor del filtro
    
    def __init__(self, filter_type="equals", parent=None):
        super().__init__(parent)
        self.filter_type = filter_type
        self.value_widget = None
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interfaz según el tipo de filtro"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        if self.filter_type in ["equals", "not_equals"]:
            # Campo de texto simple
            self.value_widget = QLineEdit()
            self.value_widget.textChanged.connect(self.on_value_changed)
            layout.addWidget(self.value_widget)
            
        elif self.filter_type in ["contains", "not_contains", "starts_with", "ends_with"]:
            # Campo de texto con opciones adicionales
            text_layout = QHBoxLayout()
            self.value_widget = QLineEdit()
            self.value_widget.textChanged.connect(self.on_value_changed)
            text_layout.addWidget(self.value_widget)
            
            case_sensitive = QCheckBox("Case sensitive")
            case_sensitive.toggled.connect(self.on_value_changed)
            text_layout.addWidget(case_sensitive)
            
            layout.addLayout(text_layout)
            
        elif self.filter_type in ["greater_than", "less_than", "greater_equal", "less_equal"]:
            # Campo numérico
            self.value_widget = QDoubleSpinBox()
            self.value_widget.setRange(-999999.99, 999999.99)
            self.value_widget.setDecimals(2)
            self.value_widget.valueChanged.connect(self.on_value_changed)
            layout.addWidget(self.value_widget)
            
        elif self.filter_type == "between":
            # Rango numérico
            range_layout = QHBoxLayout()
            self.min_widget = QDoubleSpinBox()
            self.min_widget.setRange(-999999.99, 999999.99)
            self.min_widget.setDecimals(2)
            self.min_widget.setValue(0)
            self.min_widget.valueChanged.connect(self.on_value_changed)
            
            self.max_widget = QDoubleSpinBox()
            self.max_widget.setRange(-999999.99, 999999.99)
            self.max_widget.setDecimals(2)
            self.max_widget.setValue(100)
            self.max_widget.valueChanged.connect(self.on_value_changed)
            
            range_layout.addWidget(QLabel("De:"))
            range_layout.addWidget(self.min_widget)
            range_layout.addWidget(QLabel("a:"))
            range_layout.addWidget(self.max_widget)
            
            layout.addLayout(range_layout)
            
        elif self.filter_type in ["in_list", "not_in_list"]:
            # Lista de valores
            self.value_widget = QLineEdit()
            self.value_widget.setPlaceholderText("Valores separados por coma")
            self.value_widget.textChanged.connect(self.on_value_changed)
            layout.addWidget(self.value_widget)
            
        elif self.filter_type == "date_range":
            # Rango de fechas
            date_layout = QHBoxLayout()
            self.start_date = QDateEdit()
            self.start_date.setCalendarPopup(True)
            self.start_date.setDate(QDate.currentDate().addDays(-30))
            self.start_date.dateChanged.connect(self.on_value_changed)
            
            self.end_date = QDateEdit()
            self.end_date.setCalendarPopup(True)
            self.end_date.setDate(QDate.currentDate())
            self.end_date.dateChanged.connect(self.on_value_changed)
            
            date_layout.addWidget(QLabel("Desde:"))
            date_layout.addWidget(self.start_date)
            date_layout.addWidget(QLabel("Hasta:"))
            date_layout.addWidget(self.end_date)
            
            layout.addLayout(date_layout)
            
        elif self.filter_type == "regex":
            # Expresión regular
            regex_layout = QVBoxLayout()
            self.value_widget = QLineEdit()
            self.value_widget.setPlaceholderText("Patrón de expresión regular")
            self.value_widget.textChanged.connect(self.on_value_changed)
            regex_layout.addWidget(self.value_widget)
            
            self.flags_widget = QComboBox()
            self.flags_widget.addItems([
                "Sin flags",
                "Case insensitive (IGNORECASE)",
                "Multiline (MULTILINE)",
                "Dotall (DOTALL)"
            ])
            self.flags_widget.currentTextChanged.connect(self.on_value_changed)
            regex_layout.addWidget(self.flags_widget)
            
            layout.addLayout(regex_layout)
            
        else:
            # Para otros tipos, usar campo de texto
            self.value_widget = QLineEdit()
            self.value_widget.textChanged.connect(self.on_value_changed)
            layout.addWidget(self.value_widget)
            
    def on_value_changed(self):
        """Emitir señal cuando cambie el valor"""
        self.value_changed.emit(self.get_value())
        
    def get_value(self):
        """Obtener valor actual del filtro"""
        if self.filter_type == "between":
            return [self.min_widget.value(), self.max_widget.value()]
        elif self.filter_type == "date_range":
            return [self.start_date.date().toPython(), self.end_date.date().toPython()]
        elif self.filter_type == "regex":
            return {
                'pattern': self.value_widget.text(),
                'flags': self.flags_widget.currentText()
            }
        else:
            text_value = self.value_widget.text()
            if self.filter_type in ["in_list", "not_in_list"]:
                return [x.strip() for x in text_value.split(',') if x.strip()]
            return text_value
            
    def set_value(self, value):
        """Establecer valor del filtro"""
        if self.filter_type == "between" and isinstance(value, list) and len(value) >= 2:
            self.min_widget.setValue(float(value[0]))
            self.max_widget.setValue(float(value[1]))
        elif self.filter_type == "date_range" and isinstance(value, list) and len(value) >= 2:
            if isinstance(value[0], str):
                self.start_date.setDate(QDate.fromString(value[0], Qt.ISODate))
            if isinstance(value[1], str):
                self.end_date.setDate(QDate.fromString(value[1], Qt.ISODate))
        elif self.filter_type == "regex" and isinstance(value, dict):
            self.value_widget.setText(value.get('pattern', ''))
            self.flags_widget.setCurrentText(value.get('flags', 'Sin flags'))
        elif self.filter_type in ["in_list", "not_in_list"] and isinstance(value, list):
            self.value_widget.setText(', '.join(str(v) for v in value))
        else:
            self.value_widget.setText(str(value))


class PivotFilterPanel(QWidget):
    """
    Panel para gestión de filtros avanzados de tabla pivote
    Permite crear, editar y combinar filtros complejos
    """
    
    # Señales
    filters_changed = Signal(dict)  # Diccionario de filtros
    preview_requested = Signal()    # Solicitud de preview
    
    def __init__(self, df_original=None, parent=None):
        super().__init__(parent)
        self.df_original = df_original
        self.active_filters = {}  # Diccionario de filtros activos
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Configurar la interfaz del panel"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Título del panel
        title_label = QLabel("Filtros Avanzados")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                background-color: #8e44ad;
                color: white;
                padding: 10px;
                border-radius: 6px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # Crear tabs para diferentes aspectos de filtros
        self.filter_tabs = QTabWidget()
        
        # Tab: Crear Filtro
        self.create_filter_tab()
        
        # Tab: Filtros Activos
        self.create_active_filters_tab()
        
        # Tab: Combinación Lógica
        self.create_logic_combination_tab()
        
        main_layout.addWidget(self.filter_tabs)
        
        # Panel de información
        self.create_info_panel(main_layout)
        
    def create_filter_tab(self):
        """Crear tab para crear nuevos filtros"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Grupo: Configuración de Filtro
        config_group = QGroupBox("Configurar Nuevo Filtro")
        config_layout = QVBoxLayout(config_group)
        
        # Seleccionar columna
        column_layout = QHBoxLayout()
        column_layout.addWidget(QLabel("Columna:"))
        self.filter_column_combo = QComboBox()
        self.filter_column_combo.setEditable(True)
        column_layout.addWidget(self.filter_column_combo)
        config_layout.addLayout(column_layout)
        
        # Seleccionar tipo de filtro
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Tipo de filtro:"))
        self.filter_type_combo = QComboBox()
        self.setup_filter_types()
        type_layout.addWidget(self.filter_type_combo)
        config_layout.addLayout(type_layout)
        
        # Widget de valor dinámico
        self.filter_value_widget = FilterValueWidget()
        self.filter_value_widget.setVisible(False)
        config_layout.addWidget(self.filter_value_widget)
        
        layout.addWidget(config_group)
        
        # Botones de acción
        action_layout = QHBoxLayout()
        
        add_filter_btn = QPushButton("Agregar Filtro")
        add_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        add_filter_btn.clicked.connect(self.add_filter)
        action_layout.addWidget(add_filter_btn)
        
        clear_filters_btn = QPushButton("Limpiar Todos")
        clear_filters_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_filters_btn.clicked.connect(self.clear_all_filters)
        action_layout.addWidget(clear_filters_btn)
        
        preview_filter_btn = QPushButton("Vista Previa")
        preview_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        preview_filter_btn.clicked.connect(self.preview_filters)
        action_layout.addWidget(preview_filter_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        self.filter_tabs.addTab(tab, "Crear Filtro")
        
    def create_active_filters_tab(self):
        """Crear tab para ver y gestionar filtros activos"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Lista de filtros activos
        filters_group = QGroupBox("Filtros Activos")
        filters_layout = QVBoxLayout(filters_group)
        
        self.active_filters_list = QListWidget()
        self.active_filters_list.setMaximumHeight(200)
        filters_layout.addWidget(self.active_filters_list)
        
        # Botones de gestión
        filter_actions_layout = QHBoxLayout()
        
        edit_filter_btn = QPushButton("Editar")
        edit_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        edit_filter_btn.clicked.connect(self.edit_filter)
        filter_actions_layout.addWidget(edit_filter_btn)
        
        remove_filter_btn = QPushButton("Eliminar")
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
        filter_actions_layout.addWidget(remove_filter_btn)
        
        move_up_btn = QPushButton("↑")
        move_up_btn.setMaximumWidth(40)
        move_up_btn.clicked.connect(self.move_filter_up)
        filter_actions_layout.addWidget(move_up_btn)
        
        move_down_btn = QPushButton("↓")
        move_down_btn.setMaximumWidth(40)
        move_down_btn.clicked.connect(self.move_filter_down)
        filter_actions_layout.addWidget(move_down_btn)
        
        filter_actions_layout.addStretch()
        filters_layout.addLayout(filter_actions_layout)
        
        layout.addWidget(filters_group)
        
        # Estadísticas de filtros
        stats_group = QGroupBox("Estadísticas de Filtrado")
        stats_layout = QVBoxLayout(stats_group)
        
        self.filters_stats_label = QLabel("No hay filtros activos")
        self.filters_stats_label.setStyleSheet("font-style: italic; color: #7f8c8d;")
        stats_layout.addWidget(self.filters_stats_label)
        
        layout.addWidget(stats_group)
        
        self.filter_tabs.addTab(tab, "Filtros Activos")
        
    def create_logic_combination_tab(self):
        """Crear tab para combinación lógica de filtros"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Información
        info_label = QLabel(
            "Configure cómo se combinan los filtros utilizando operadores lógicos. "
            "Los filtros se aplican en el orden especificado."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #7f8c8d; font-style: italic; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # Tabla de configuración lógica
        logic_group = QGroupBox("Configuración Lógica")
        logic_layout = QVBoxLayout(logic_group)
        
        self.logic_table = QTableWidget(0, 4)
        self.logic_table.setHorizontalHeaderLabels([
            "Orden", "Filtro", "Operador", "Activo"
        ])
        self.logic_table.horizontalHeader().setStretchLastSection(True)
        self.logic_table.setMaximumHeight(200)
        logic_layout.addWidget(self.logic_table)
        
        layout.addWidget(logic_group)
        
        # Opciones de combinación
        combination_group = QGroupBox("Opciones de Combinación")
        combination_layout = QVBoxLayout(combination_group)
        
        # Modo de combinación
        mode_layout = QHBoxLayout()
        self.combination_mode_combo = QComboBox()
        self.combination_mode_combo.addItems([
            "Todos los filtros (AND)",
            "Cualquier filtro (OR)",
            "Combinación personalizada"
        ])
        mode_layout.addWidget(QLabel("Modo de combinación:"))
        mode_layout.addWidget(self.combination_mode_combo)
        mode_layout.addStretch()
        combination_layout.addLayout(mode_layout)
        
        # Orden de aplicación
        order_layout = QHBoxLayout()
        self.apply_order_combo = QComboBox()
        self.apply_order_combo.addItems([
            "Secuencial (según orden)",
            "Paralelo (todos a la vez)"
        ])
        order_layout.addWidget(QLabel("Orden de aplicación:"))
        order_layout.addWidget(self.apply_order_combo)
        order_layout.addStretch()
        combination_layout.addLayout(order_layout)
        
        # Optimización
        optimization_layout = QHBoxLayout()
        self.optimize_check = QCheckBox("Optimizar secuencia de filtros")
        self.optimize_check.setChecked(True)
        optimization_layout.addWidget(self.optimize_check)
        optimization_layout.addStretch()
        combination_layout.addLayout(optimization_layout)
        
        layout.addWidget(combination_group)
        
        self.filter_tabs.addTab(tab, "Combinación Lógica")
        
    def create_info_panel(self, main_layout):
        """Crear panel de información"""
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #f8f9fa;
                padding: 5px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        self.info_label = QLabel("Panel de filtros listo. Configure filtros para aplicarlos antes del pivoteo.")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        
        main_layout.addWidget(info_frame)
        
    def setup_connections(self):
        """Configurar conexiones de señales"""
        self.filter_type_combo.currentTextChanged.connect(self.on_filter_type_changed)
        self.filter_value_widget.value_changed.connect(self.on_filter_value_changed)
        self.active_filters_list.itemSelectionChanged.connect(self.on_filter_selection_changed)
        
    def setup_filter_types(self):
        """Configurar tipos de filtro disponibles"""
        filter_types = [
            ("equals", "Igual a"),
            ("not_equals", "Diferente de"),
            ("contains", "Contiene"),
            ("not_contains", "No contiene"),
            ("starts_with", "Comienza con"),
            ("ends_with", "Termina con"),
            ("greater_than", "Mayor que"),
            ("less_than", "Menor que"),
            ("greater_equal", "Mayor o igual"),
            ("less_equal", "Menor o igual"),
            ("between", "Entre (rango)"),
            ("in_list", "En lista"),
            ("not_in_list", "No en lista"),
            ("is_null", "Es nulo"),
            ("not_null", "No es nulo"),
            ("is_empty", "Está vacío"),
            ("not_empty", "No está vacío"),
            ("date_range", "Rango de fechas"),
            ("regex", "Expresión regular"),
            ("numeric_range", "Rango numérico")
        ]
        
        for value, text in filter_types:
            self.filter_type_combo.addItem(text, value)
            
    def set_data(self, df):
        """Establecer datos para filtrar"""
        self.df_original = df
        
        if df is not None:
            # Actualizar lista de columnas
            self.filter_column_combo.clear()
            self.filter_column_combo.addItems(df.columns.tolist())
            
    def on_filter_type_changed(self, text):
        """Manejar cambio de tipo de filtro"""
        # Obtener el valor del tipo
        filter_type = self.filter_type_combo.currentData()
        
        if filter_type:
            # Recrear widget de valor
            self.filter_value_widget.setVisible(True)
            # El widget se recrea automáticamente en el setter
        else:
            self.filter_value_widget.setVisible(False)
            
    def on_filter_value_changed(self, value):
        """Manejar cambio de valor de filtro"""
        # Actualizar información
        self.update_filter_info()
        
    def on_filter_selection_changed(self):
        """Manejar selección de filtro en lista"""
        # Actualizar botones de acción
        has_selection = self.active_filters_list.currentItem() is not None
        # Habilitar/deshabilitar botones según selección
        
    def add_filter(self):
        """Agregar nuevo filtro"""
        if self.df_original is None:
            QMessageBox.warning(self, "Advertencia", "No hay datos para filtrar.")
            return
            
        # Obtener configuración del filtro
        column = self.filter_column_combo.currentText().strip()
        filter_type = self.filter_type_combo.currentData()
        value = self.filter_value_widget.get_value()
        
        # Validar configuración
        if not column:
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar una columna.")
            return
            
        if column not in self.df_original.columns:
            QMessageBox.warning(self, "Advertencia", f"La columna '{column}' no existe.")
            return
            
        if filter_type in ["is_null", "not_null", "is_empty", "not_empty"]:
            # Estos filtros no necesitan valor
            value = None
        elif value is None or value == "":
            QMessageBox.warning(self, "Advertencia", "Debe especificar un valor para el filtro.")
            return
            
        # Crear filtro
        filter_config = {
            'type': filter_type,
            'value': value
        }
        
        # Agregar a filtros activos
        filter_id = f"{column}_{len(self.active_filters)}"
        self.active_filters[filter_id] = {
            'column': column,
            'config': filter_config
        }
        
        # Actualizar UI
        self.update_active_filters_list()
        self.update_filters_statistics()
        self.emit_filters_changed()
        
        # Mostrar información
        self.info_label.setText(f"Filtro agregado: {column} {filter_type} {value}")
        
    def remove_filter(self):
        """Eliminar filtro seleccionado"""
        current_item = self.active_filters_list.currentItem()
        if current_item:
            filter_id = current_item.data(Qt.UserRole)
            if filter_id in self.active_filters:
                del self.active_filters[filter_id]
                
                # Actualizar UI
                self.update_active_filters_list()
                self.update_filters_statistics()
                self.emit_filters_changed()
                
    def edit_filter(self):
        """Editar filtro seleccionado"""
        current_item = self.active_filters_list.currentItem()
        if current_item:
            filter_id = current_item.data(Qt.UserRole)
            if filter_id in self.active_filters:
                filter_data = self.active_filters[filter_id]
                # Cargar en el formulario de creación
                self.load_filter_to_form(filter_data)
                
    def clear_all_filters(self):
        """Limpiar todos los filtros"""
        self.active_filters.clear()
        self.update_active_filters_list()
        self.update_filters_statistics()
        self.emit_filters_changed()
        self.info_label.setText("Todos los filtros han sido eliminados.")
        
    def move_filter_up(self):
        """Mover filtro seleccionado hacia arriba"""
        # TODO: Implementar reordenamiento
        pass
        
    def move_filter_down(self):
        """Mover filtro seleccionado hacia abajo"""
        # TODO: Implementar reordenamiento
        pass
        
    def load_filter_to_form(self, filter_data):
        """Cargar filtro en el formulario para edición"""
        column = filter_data['column']
        config = filter_data['config']
        
        # Establecer columna
        index = self.filter_column_combo.findText(column)
        if index >= 0:
            self.filter_column_combo.setCurrentIndex(index)
            
        # Establecer tipo
        filter_type = config['type']
        for i in range(self.filter_type_combo.count()):
            if self.filter_type_combo.itemData(i) == filter_type:
                self.filter_type_combo.setCurrentIndex(i)
                break
                
        # Establecer valor
        value = config.get('value')
        if value is not None:
            self.filter_value_widget.set_value(value)
            
    def update_active_filters_list(self):
        """Actualizar lista de filtros activos"""
        self.active_filters_list.clear()
        
        for filter_id, filter_data in self.active_filters.items():
            column = filter_data['column']
            config = filter_data['config']
            filter_type = config['type']
            value = config.get('value', 'N/A')
            
            # Crear texto descriptivo
            if isinstance(value, list):
                value_text = ', '.join(str(v) for v in value)
            else:
                value_text = str(value)
                
            filter_text = f"{column} {filter_type} {value_text}"
            item = QListWidgetItem(filter_text)
            item.setData(Qt.UserRole, filter_id)
            
            self.active_filters_list.addItem(item)
            
    def update_filters_statistics(self):
        """Actualizar estadísticas de filtros"""
        total_filters = len(self.active_filters)
        
        if total_filters == 0:
            self.filters_stats_label.setText("No hay filtros activos")
        else:
            stats_text = f"Filtros activos: {total_filters}"
            
            # Calcular impacto estimado
            if self.df_original is not None:
                original_rows = len(self.df_original)
                # Estimación básica (en un caso real, esto sería más preciso)
                estimated_rows = max(1, original_rows * 0.8 ** total_filters)
                stats_text += f"\nFilas estimadas: {original_rows} → {int(estimated_rows)}"
                
            self.filters_stats_label.setText(stats_text)
            
    def update_filter_info(self):
        """Actualizar información del filtro actual"""
        column = self.filter_column_combo.currentText()
        filter_type = self.filter_type_combo.currentText()
        value = self.filter_value_widget.get_value()
        
        if column and filter_type:
            info_text = f"Filtro: {column} {filter_type}"
            if value is not None and value != "":
                if isinstance(value, list):
                    info_text += f" = {', '.join(str(v) for v in value)}"
                else:
                    info_text += f" = {value}"
            self.info_label.setText(info_text)
        else:
            self.info_label.setText("Configure un filtro seleccionando columna, tipo y valor.")
            
    def preview_filters(self):
        """Previsualizar resultado de filtros"""
        if not self.active_filters:
            QMessageBox.information(self, "Información", "No hay filtros para previsualizar.")
            return
            
        if self.df_original is None:
            QMessageBox.warning(self, "Advertencia", "No hay datos para filtrar.")
            return
            
        try:
            # Aplicar filtros
            filtered_df = self.apply_filters_to_dataframe(self.df_original)
            
            # Mostrar resultado
            result_info = f"""
Filtros aplicados: {len(self.active_filters)}
Filas originales: {len(self.df_original)}
Filas resultantes: {len(filtered_df)}
Reducción: {((len(self.df_original) - len(filtered_df)) / len(self.df_original) * 100):.1f}%
            """
            
            QMessageBox.information(self, "Vista Previa de Filtros", result_info.strip())
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al aplicar filtros: {str(e)}")
            
    def apply_filters_to_dataframe(self, df):
        """Aplicar filtros a un DataFrame"""
        from core.pivot import PivotFilterManager
        
        filter_manager = PivotFilterManager()
        
        # Convertir filtros al formato del manager
        filters_dict = {}
        for filter_id, filter_data in self.active_filters.items():
            column = filter_data['column']
            config = filter_data['config']
            filters_dict[column] = config
            
        return filter_manager.apply_filters(df, filters_dict)
        
    def emit_filters_changed(self):
        """Emitir señal de cambio de filtros"""
        # Convertir a formato para el sistema de pivoteo
        filters_dict = {}
        for filter_id, filter_data in self.active_filters.items():
            column = filter_data['column']
            config = filter_data['config']
            filters_dict[column] = config
            
        self.filters_changed.emit(filters_dict)
        
    def get_active_filters(self):
        """Obtener filtros activos"""
        return self.active_filters.copy()
        
    def set_active_filters(self, filters_dict):
        """Establecer filtros activos desde diccionario"""
        self.active_filters.clear()
        
        for column, config in filters_dict.items():
            filter_id = f"{column}_{len(self.active_filters)}"
            self.active_filters[filter_id] = {
                'column': column,
                'config': config
            }
            
        self.update_active_filters_list()
        self.update_filters_statistics()
        self.emit_filters_changed()