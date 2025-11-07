"""
Panel de Agregaciones para Tabla Pivote
Proporciona interfaz para seleccionar y configurar funciones de agregación
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QGroupBox, QComboBox, QPushButton, QListWidget,
                               QListWidgetItem, QTableWidget, QTableWidgetItem,
                               QCheckBox, QSpinBox, QLineEdit, QFrame, QMessageBox, QTabWidget)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import pandas as pd
from typing import Dict, List, Any, Optional
import logging

# Configurar logging
logger = logging.getLogger(__name__)


class AggregationFunctionWidget(QWidget):
    """Widget para configurar una función de agregación específica"""
    
    function_changed = Signal(dict)  # Configuración de la función
    
    def __init__(self, function_data=None, parent=None):
        super().__init__(parent)
        self.function_data = function_data or {}
        self.setup_ui()
        if function_data:
            self.load_function_data()
            
    def setup_ui(self):
        """Configurar la interfaz del widget"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Nombre de la función
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nombre descriptivo")
        self.name_edit.textChanged.connect(self.emit_function_changed)
        layout.addWidget(QLabel("Nombre:"))
        layout.addWidget(self.name_edit)
        
        # Función de agregación
        self.agg_function_combo = QComboBox()
        self.setup_aggregation_functions()
        self.agg_function_combo.currentTextChanged.connect(self.emit_function_changed)
        layout.addWidget(QLabel("Función:"))
        layout.addWidget(self.agg_function_combo)
        
        # Columna objetivo (opcional)
        self.target_column_combo = QComboBox()
        self.target_column_combo.setEditable(True)
        self.target_column_combo.setPlaceholderText("Todas las columnas de valores")
        self.target_column_combo.currentTextChanged.connect(self.emit_function_changed)
        layout.addWidget(QLabel("Columna:"))
        layout.addWidget(self.target_column_combo)
        
        # Parámetros adicionales
        self.params_edit = QLineEdit()
        self.params_edit.setPlaceholderText("Parámetros adicionales (JSON)")
        self.params_edit.textChanged.connect(self.emit_function_changed)
        layout.addWidget(QLabel("Parámetros:"))
        layout.addWidget(self.params_edit)
        
        # Checkbox para función activa
        self.active_check = QCheckBox("Activa")
        self.active_check.setChecked(True)
        self.active_check.toggled.connect(self.emit_function_changed)
        layout.addWidget(self.active_check)
        
    def setup_aggregation_functions(self):
        """Configurar funciones de agregación disponibles"""
        functions = [
            ("sum", "Suma"),
            ("mean", "Promedio"),
            ("median", "Mediana"),
            ("count", "Conteo"),
            ("min", "Mínimo"),
            ("max", "Máximo"),
            ("std", "Desviación Estándar"),
            ("var", "Varianza"),
            ("first", "Primer Valor"),
            ("last", "Último Valor"),
            ("size", "Tamaño del Grupo"),
            ("nunique", "Valores Únicos"),
            ("skew", "Asimetría"),
            ("kurtosis", "Curtosis"),
            ("quantile", "Cuantil"),
            ("mad", "Desviación Absoluta Mediana")
        ]
        
        for value, text in functions:
            self.agg_function_combo.addItem(text, value)
            
    def set_available_columns(self, columns):
        """Establecer columnas disponibles"""
        self.target_column_combo.clear()
        self.target_column_combo.addItem("Todas las columnas de valores", None)
        for col in columns:
            self.target_column_combo.addItem(col, col)
            
    def load_function_data(self):
        """Cargar datos de función existente"""
        if 'name' in self.function_data:
            self.name_edit.setText(self.function_data['name'])
        if 'function' in self.function_data:
            for i in range(self.agg_function_combo.count()):
                if self.agg_function_combo.itemData(i) == self.function_data['function']:
                    self.agg_function_combo.setCurrentIndex(i)
                    break
        if 'target_column' in self.function_data:
            for i in range(self.target_column_combo.count()):
                if self.target_column_combo.itemData(i) == self.function_data['target_column']:
                    self.target_column_combo.setCurrentIndex(i)
                    break
        if 'parameters' in self.function_data:
            self.params_edit.setText(str(self.function_data['parameters']))
        if 'active' in self.function_data:
            self.active_check.setChecked(self.function_data['active'])
            
    def emit_function_changed(self):
        """Emitir señal con datos actualizados"""
        data = self.get_function_data()
        self.function_changed.emit(data)
        
    def get_function_data(self):
        """Obtener datos de la función"""
        data = {
            'name': self.name_edit.text().strip(),
            'function': self.agg_function_combo.currentData(),
            'function_text': self.agg_function_combo.currentText(),
            'target_column': self.target_column_combo.currentData(),
            'target_column_text': self.target_column_combo.currentText(),
            'parameters': self.params_edit.text().strip(),
            'active': self.active_check.isChecked()
        }
        
        # Si el nombre está vacío, usar el nombre de la función
        if not data['name']:
            data['name'] = data['function_text']
            
        return data
        
    def is_valid(self):
        """Validar si la función está configurada correctamente"""
        return bool(self.get_function_data()['function'])


class PivotAggregationPanel(QWidget):
    """
    Panel para gestión de funciones de agregación
    Permite crear, configurar y combinar múltiples funciones de agregación
    """
    
    # Señales
    aggregations_changed = Signal(list)  # Lista de funciones de agregación
    preview_requested = Signal()         # Solicitud de preview
    
    def __init__(self, df_original=None, values_columns=None, parent=None):
        super().__init__(parent)
        self.df_original = df_original
        self.values_columns = values_columns or []
        self.aggregation_functions = []  # Lista de funciones configuradas
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Configurar la interfaz del panel"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Título del panel
        title_label = QLabel("Gestión de Agregaciones")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                background-color: #e67e22;
                color: white;
                padding: 10px;
                border-radius: 6px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # Crear tabs para diferentes aspectos
        self.agg_tabs = QTabWidget()
        
        # Tab: Configuración Manual
        self.create_manual_config_tab()
        
        # Tab: Configuración Rápida
        self.create_quick_config_tab()
        
        # Tab: Presets Predefinidos
        self.create_presets_tab()
        
        # Tab: Vista Previa
        self.create_preview_tab()
        
        main_layout.addWidget(self.agg_tabs)
        
        # Panel de información
        self.create_info_panel(main_layout)
        
    def create_manual_config_tab(self):
        """Crear tab para configuración manual de funciones"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Instrucciones
        instructions = QLabel(
            "Configure funciones de agregación manualmente. Cada función puede aplicarse "
            "a una columna específica o a todas las columnas de valores."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #7f8c8d; font-style: italic; margin-bottom: 10px;")
        layout.addWidget(instructions)
        
        # Lista de funciones configuradas
        functions_group = QGroupBox("Funciones de Agregación Configuradas")
        functions_layout = QVBoxLayout(functions_group)
        
        self.functions_list = QListWidget()
        self.functions_list.setMaximumHeight(200)
        functions_layout.addWidget(self.functions_list)
        
        # Botones de gestión
        functions_buttons_layout = QHBoxLayout()
        
        add_function_btn = QPushButton("Agregar Función")
        add_function_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        add_function_btn.clicked.connect(self.add_aggregation_function)
        functions_buttons_layout.addWidget(add_function_btn)
        
        edit_function_btn = QPushButton("Editar")
        edit_function_btn.setStyleSheet("""
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
        edit_function_btn.clicked.connect(self.edit_aggregation_function)
        functions_buttons_layout.addWidget(edit_function_btn)
        
        remove_function_btn = QPushButton("Eliminar")
        remove_function_btn.setStyleSheet("""
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
        remove_function_btn.clicked.connect(self.remove_aggregation_function)
        functions_buttons_layout.addWidget(remove_function_btn)
        
        duplicate_function_btn = QPushButton("Duplicar")
        duplicate_function_btn.setStyleSheet("""
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
        duplicate_function_btn.clicked.connect(self.duplicate_aggregation_function)
        functions_buttons_layout.addWidget(duplicate_function_btn)
        
        functions_buttons_layout.addStretch()
        functions_layout.addLayout(functions_buttons_layout)
        
        layout.addWidget(functions_group)
        
        # Panel de configuración de función
        config_group = QGroupBox("Configurar Función")
        self.config_layout = QVBoxLayout(config_group)
        
        # Widget de función (se crea dinámicamente)
        self.function_widget = None
        self.create_function_widget()
        
        layout.addWidget(config_group)
        
        self.agg_tabs.addTab(tab, "Configuración Manual")
        
    def create_quick_config_tab(self):
        """Crear tab para configuración rápida"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Título
        quick_title = QLabel("Configuración Rápida")
        quick_title.setFont(QFont("Arial", 12, QFont.Bold))
        quick_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(quick_title)
        
        # Modos predefinidos
        modes_group = QGroupBox("Modos de Configuración Rápida")
        modes_layout = QVBoxLayout(modes_group)
        
        # Modo 1: Una función para todos los valores
        mode1_layout = QVBoxLayout()
        mode1_radio = QCheckBox("Una función para todos los valores de una columna")
        mode1_layout.addWidget(mode1_radio)
        
        mode1_config_layout = QHBoxLayout()
        self.quick_mode1_function = QComboBox()
        self.quick_mode1_function.addItem("mean", "mean")
        mode1_config_layout.addWidget(QLabel("Función:"))
        mode1_config_layout.addWidget(self.quick_mode1_function)
        mode1_config_layout.addWidget(QLabel("Columna:"))
        self.quick_mode1_column = QComboBox()
        self.quick_mode1_column.setEditable(True)
        mode1_config_layout.addWidget(self.quick_mode1_column)
        mode1_layout.addLayout(mode1_config_layout)
        modes_layout.addLayout(mode1_layout)
        
        # Modo 2: Múltiples funciones para una columna
        mode2_layout = QVBoxLayout()
        mode2_radio = QCheckBox("Múltiples funciones para una columna")
        mode2_layout.addWidget(mode2_radio)
        
        self.quick_mode2_functions = QListWidget()
        self.quick_mode2_functions.setMaximumHeight(100)
        mode2_layout.addWidget(QLabel("Funciones:"))
        mode2_layout.addWidget(self.quick_mode2_functions)
        mode2_layout.addWidget(QLabel("Columna:"))
        self.quick_mode2_column = QComboBox()
        self.quick_mode2_column.setEditable(True)
        mode2_layout.addWidget(self.quick_mode2_column)
        modes_layout.addLayout(mode2_layout)
        
        # Modo 3: Una función para todas las columnas
        mode3_layout = QVBoxLayout()
        mode3_radio = QCheckBox("Una función para todas las columnas de valores")
        mode3_layout.addWidget(mode3_radio)
        
        mode3_config_layout = QHBoxLayout()
        self.quick_mode3_function = QComboBox()
        mode3_config_layout.addWidget(QLabel("Función:"))
        mode3_config_layout.addWidget(self.quick_mode3_function)
        mode3_layout.addLayout(mode3_config_layout)
        modes_layout.addLayout(mode3_layout)
        
        layout.addWidget(modes_group)
        
        # Botón aplicar configuración rápida
        apply_quick_btn = QPushButton("Aplicar Configuración Rápida")
        apply_quick_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        apply_quick_btn.clicked.connect(self.apply_quick_configuration)
        layout.addWidget(apply_quick_btn)
        
        # Configurar funciones de agregación después de que todos los widgets estén creados
        self.setup_aggregation_functions()
        
        self.agg_tabs.addTab(tab, "Configuración Rápida")
        
    def create_presets_tab(self):
        """Crear tab con presets predefinidos"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Título
        presets_title = QLabel("Configuraciones Predefinidas")
        presets_title.setFont(QFont("Arial", 12, QFont.Bold))
        presets_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(presets_title)
        
        # Presets disponibles
        presets_group = QGroupBox("Plantillas de Agregación")
        presets_layout = QVBoxLayout(presets_group)
        
        # Preset 1: Estadísticas Básicas
        preset1_layout = QVBoxLayout()
        preset1_btn = QPushButton("Estadísticas Básicas (sum, mean, count, min, max)")
        preset1_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        preset1_btn.clicked.connect(lambda: self.apply_preset("basic_stats"))
        preset1_layout.addWidget(preset1_btn)
        presets_layout.addLayout(preset1_layout)
        
        # Preset 2: Análisis Financiero
        preset2_layout = QVBoxLayout()
        preset2_btn = QPushButton("Análisis Financiero (sum, mean, std, median)")
        preset2_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        preset2_btn.clicked.connect(lambda: self.apply_preset("financial"))
        preset2_layout.addWidget(preset2_btn)
        presets_layout.addLayout(preset2_layout)
        
        # Preset 3: Análisis de Ventas
        preset3_layout = QVBoxLayout()
        preset3_btn = QPushButton("Análisis de Ventas (sum, count, mean, max)")
        preset3_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        preset3_btn.clicked.connect(lambda: self.apply_preset("sales"))
        preset3_layout.addWidget(preset3_btn)
        presets_layout.addLayout(preset3_layout)
        
        # Preset 4: Análisis Estadístico Completo
        preset4_layout = QVBoxLayout()
        preset4_btn = QPushButton("Estadística Completa (mean, std, var, skew, kurtosis, quantile)")
        preset4_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        preset4_btn.clicked.connect(lambda: self.apply_preset("complete_stats"))
        preset4_layout.addWidget(preset4_btn)
        presets_layout.addLayout(preset4_layout)
        
        layout.addWidget(presets_group)
        
        self.agg_tabs.addTab(tab, "Plantillas")
        
    def create_preview_tab(self):
        """Crear tab de vista previa"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Título
        preview_title = QLabel("Vista Previa de Configuración")
        preview_title.setFont(QFont("Arial", 12, QFont.Bold))
        preview_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(preview_title)
        
        # Configuración actual
        config_group = QGroupBox("Configuración Actual")
        config_layout = QVBoxLayout(config_group)
        
        self.config_preview_text = QListWidget()
        self.config_preview_text.setMaximumHeight(200)
        config_layout.addWidget(self.config_preview_text)
        
        layout.addWidget(config_group)
        
        # Estadísticas
        stats_group = QGroupBox("Estadísticas de Configuración")
        stats_layout = QVBoxLayout(stats_group)
        
        self.config_stats_label = QLabel("No hay funciones configuradas")
        self.config_stats_label.setStyleSheet("font-style: italic; color: #7f8c8d;")
        stats_layout.addWidget(self.config_stats_label)
        
        layout.addWidget(stats_group)
        
        # Botones
        preview_buttons_layout = QHBoxLayout()
        
        update_preview_btn = QPushButton("Actualizar Vista Previa")
        update_preview_btn.setStyleSheet("""
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
        update_preview_btn.clicked.connect(self.update_configuration_preview)
        preview_buttons_layout.addWidget(update_preview_btn)
        
        test_config_btn = QPushButton("Probar Configuración")
        test_config_btn.setStyleSheet("""
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
        test_config_btn.clicked.connect(self.test_configuration)
        preview_buttons_layout.addWidget(test_config_btn)
        
        preview_buttons_layout.addStretch()
        layout.addLayout(preview_buttons_layout)
        
        self.agg_tabs.addTab(tab, "Vista Previa")
        
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
        
        self.info_label = QLabel("Panel de agregaciones listo. Configure funciones para aplicar en el pivoteo.")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        
        main_layout.addWidget(info_frame)
        
    def create_function_widget(self):
        """Crear widget de configuración de función"""
        if self.function_widget:
            self.config_layout.removeWidget(self.function_widget)
            self.function_widget.deleteLater()
            
        self.function_widget = AggregationFunctionWidget()
        self.function_widget.function_changed.connect(self.on_function_changed)
        self.config_layout.addWidget(self.function_widget)
        
        # Establecer columnas disponibles
        if self.values_columns:
            self.function_widget.set_available_columns(self.values_columns)
            
    def setup_aggregation_functions(self):
        """Configurar funciones de agregación disponibles"""
        functions = [
            "sum", "mean", "median", "count", "min", "max", "std", "var",
            "first", "last", "size", "nunique", "skew", "kurtosis", "quantile"
        ]
        
        # Limpiar y agregar funciones a todos los combo boxes
        for combo in [self.quick_mode1_function, self.quick_mode3_function]:
            combo.clear()
            for func in functions:
                combo.addItem(func, func)
                
        # Para quick_mode2, agregar a lista
        self.quick_mode2_functions.clear()
        for func in functions:
            item = QListWidgetItem(func)
            item.setCheckState(Qt.Checked)
            self.quick_mode2_functions.addItem(item)
            
    def setup_connections(self):
        """Configurar conexiones de señales"""
        self.functions_list.itemSelectionChanged.connect(self.on_function_selection_changed)
        self.agg_tabs.currentChanged.connect(self.on_tab_changed)
        
    def set_data(self, df, values_columns=None):
        """Establecer datos y columnas de valores"""
        self.df_original = df
        if values_columns:
            self.values_columns = values_columns
            
        # Actualizar columnas disponibles en widgets
        if self.function_widget:
            self.function_widget.set_available_columns(self.values_columns)
            
        self.update_info_label()
        
    def update_info_label(self):
        """Actualizar label de información"""
        if self.values_columns:
            self.info_label.setText(
                f"Columnas de valores disponibles: {', '.join(self.values_columns)}"
            )
        else:
            self.info_label.setText("Seleccione columnas de valores para configurar agregaciones.")
            
    def on_function_changed(self, function_data):
        """Manejar cambio en función de agregación"""
        # Actualizar lista si es una función válida
        if function_data.get('function'):
            self.update_functions_list()
            
    def on_function_selection_changed(self):
        """Manejar selección de función en lista"""
        current_item = self.functions_list.currentItem()
        if current_item and self.function_widget:
            # Cargar función seleccionada en widget
            function_index = current_item.data(Qt.UserRole)
            if 0 <= function_index < len(self.aggregation_functions):
                self.function_widget.load_function_data(
                    self.aggregation_functions[function_index]
                )
                
    def on_tab_changed(self, index):
        """Manejar cambio de tabs"""
        if index == 3:  # Tab de preview
            self.update_configuration_preview()
            
    def add_aggregation_function(self):
        """Agregar nueva función de agregación"""
        if not self.values_columns:
            QMessageBox.warning(self, "Advertencia", 
                              "Debe seleccionar columnas de valores primero.")
            return
            
        # Crear función por defecto
        default_function = {
            'name': f"Función {len(self.aggregation_functions) + 1}",
            'function': 'mean',
            'function_text': 'mean',
            'target_column': None,
            'target_column_text': 'Todas las columnas de valores',
            'parameters': '',
            'active': True
        }
        
        self.aggregation_functions.append(default_function)
        self.update_functions_list()
        self.emit_aggregations_changed()
        
        self.info_label.setText(f"Función agregada: {default_function['name']}")
        
    def edit_aggregation_function(self):
        """Editar función seleccionada"""
        current_item = self.functions_list.currentItem()
        if current_item and self.function_widget:
            function_index = current_item.data(Qt.UserRole)
            if 0 <= function_index < len(self.aggregation_functions):
                # Actualizar función con datos del widget
                function_data = self.function_widget.get_function_data()
                if function_data['function']:
                    self.aggregation_functions[function_index] = function_data
                    self.update_functions_list()
                    self.emit_aggregations_changed()
                    
    def remove_aggregation_function(self):
        """Eliminar función seleccionada"""
        current_item = self.functions_list.currentItem()
        if current_item:
            function_index = current_item.data(Qt.UserRole)
            if 0 <= function_index < len(self.aggregation_functions):
                # Eliminar función
                removed_function = self.aggregation_functions.pop(function_index)
                self.update_functions_list()
                self.emit_aggregations_changed()
                
                self.info_label.setText(f"Función eliminada: {removed_function['name']}")
                
    def duplicate_aggregation_function(self):
        """Duplicar función seleccionada"""
        current_item = self.functions_list.currentItem()
        if current_item:
            function_index = current_item.data(Qt.UserRole)
            if 0 <= function_index < len(self.aggregation_functions):
                # Duplicar función
                original_function = self.aggregation_functions[function_index].copy()
                original_function['name'] = f"{original_function['name']} (Copia)"
                self.aggregation_functions.append(original_function)
                self.update_functions_list()
                self.emit_aggregations_changed()
                
    def update_functions_list(self):
        """Actualizar lista de funciones"""
        self.functions_list.clear()
        
        for i, function_data in enumerate(self.aggregation_functions):
            if function_data['active']:
                # Crear texto descriptivo
                text = f"{function_data['name']} - {function_data['function_text']}"
                if function_data['target_column_text'] != 'Todas las columnas de valores':
                    text += f" ({function_data['target_column_text']})"
                    
                item = QListWidgetItem(text)
                item.setData(Qt.UserRole, i)
                self.functions_list.addItem(item)
            else:
                # Función inactiva
                text = f"[INACTIVA] {function_data['name']} - {function_data['function_text']}"
                item = QListWidgetItem(text)
                item.setData(Qt.UserRole, i)
                item.setForeground(Qt.gray)
                self.functions_list.addItem(item)
                
    def apply_quick_configuration(self):
        """Aplicar configuración rápida"""
        # Implementar según los modos seleccionados
        QMessageBox.information(self, "Configuración Rápida", 
                              "Funcionalidad de configuración rápida en desarrollo.")
                              
    def apply_preset(self, preset_name):
        """Aplicar preset predefinido"""
        if not self.values_columns:
            QMessageBox.warning(self, "Advertencia", 
                              "Debe seleccionar columnas de valores primero.")
            return
            
        # Limpiar funciones actuales
        self.aggregation_functions.clear()
        
        # Aplicar preset según el nombre
        if preset_name == "basic_stats":
            functions = ['sum', 'mean', 'count', 'min', 'max']
        elif preset_name == "financial":
            functions = ['sum', 'mean', 'std', 'median']
        elif preset_name == "sales":
            functions = ['sum', 'count', 'mean', 'max']
        elif preset_name == "complete_stats":
            functions = ['mean', 'std', 'var', 'skew', 'kurtosis']
        else:
            functions = ['mean']
            
        # Crear funciones para cada columna de valores
        for column in self.values_columns:
            for func in functions:
                function_data = {
                    'name': f"{func.title()} de {column}",
                    'function': func,
                    'function_text': func.title(),
                    'target_column': column,
                    'target_column_text': column,
                    'parameters': '',
                    'active': True
                }
                self.aggregation_functions.append(function_data)
                
        self.update_functions_list()
        self.emit_aggregations_changed()
        
        QMessageBox.information(self, "Preset Aplicado", 
                              f"Preset '{preset_name}' aplicado con {len(self.aggregation_functions)} funciones.")
                              
    def update_configuration_preview(self):
        """Actualizar vista previa de configuración"""
        self.config_preview_text.clear()
        
        active_functions = [f for f in self.aggregation_functions if f['active']]
        
        if not active_functions:
            self.config_preview_text.addItem("No hay funciones activas")
        else:
            for i, func in enumerate(active_functions, 1):
                text = f"{i}. {func['name']} - {func['function_text']}"
                if func['target_column']:
                    text += f" para {func['target_column_text']}"
                self.config_preview_text.addItem(text)
                
        # Actualizar estadísticas
        total_functions = len(self.aggregation_functions)
        active_count = len(active_functions)
        unique_functions = len(set(f['function'] for f in active_functions))
        
        stats_text = f"Total de funciones: {total_functions} | "
        stats_text += f"Activas: {active_count} | "
        stats_text += f"Funciones únicas: {unique_functions}"
        
        self.config_stats_label.setText(stats_text)
        
    def test_configuration(self):
        """Probar configuración actual"""
        active_functions = [f for f in self.aggregation_functions if f['active']]
        
        if not active_functions:
            QMessageBox.information(self, "Prueba", "No hay funciones activas para probar.")
            return
            
        # Simular test de configuración
        test_result = f"""
Prueba de Configuración de Agregaciones
{'=' * 40}

Funciones activas: {len(active_functions)}
Columnas objetivo: {len(set(f['target_column'] for f in active_functions if f['target_column']))}

Funciones de agregación:
{chr(10).join(f"- {f['name']} ({f['function']})" for f in active_functions)}

Estimación de rendimiento: {'Buena' if len(active_functions) <= 5 else 'Regular'}
        """
        
        QMessageBox.information(self, "Resultado de Prueba", test_result.strip())
        
    def emit_aggregations_changed(self):
        """Emitir señal de cambio de agregaciones"""
        self.aggregations_changed.emit(self.aggregation_functions.copy())
        self.update_configuration_preview()
        
    def get_aggregation_functions(self):
        """Obtener funciones de agregación activas"""
        return [f for f in self.aggregation_functions if f['active']]
        
    def set_aggregation_functions(self, functions):
        """Establecer funciones de agregación"""
        self.aggregation_functions = functions.copy()
        self.update_functions_list()
        self.emit_aggregations_changed()