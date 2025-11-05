"""
Vista de Transformaciones para Flash View Sheet
Proporciona interfaz para aplicar transformaciones de datos con preview en tiempo real
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                               QListWidget, QListWidgetItem, QPushButton, QLabel,
                               QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
                               QCheckBox, QLineEdit, QGroupBox, QFormLayout,
                               QTableView, QSplitter, QTreeWidget, QTreeWidgetItem,
                               QProgressBar, QMessageBox, QFrame)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon
import pandas as pd
import traceback
from typing import Dict, List, Any, Optional

class TransformationWorkerThread(QThread):
    """Hilo para aplicar transformaciones en segundo plano"""
    
    progress_updated = Signal(int, str)
    transformation_applied = Signal(object)  # Pandas DataFrame
    error_occurred = Signal(str)
    
    def __init__(self, transformation_data, df):
        super().__init__()
        self.transformation_data = transformation_data
        self.df = df.copy()
        
    def run(self):
        """Ejecutar la transformación"""
        try:
            self.progress_updated.emit(10, "Iniciando transformación...")
            
            from core.transformations.transformation_manager import TransformationManager
            
            manager = TransformationManager()
            self.progress_updated.emit(30, "Configurando transformación...")
            
            # Aplicar transformación
            result = manager.apply_transformation(
                self.df, 
                self.transformation_data['type'],
                self.transformation_data['parameters']
            )
            
            self.progress_updated.emit(90, "Finalizando...")
            self.transformation_applied.emit(result)
            
        except Exception as e:
            error_msg = f"Error al aplicar transformación: {str(e)}\n{traceback.format_exc()}"
            self.error_occurred.emit(error_msg)


class TransformationsView(QWidget):
    """Vista principal de transformaciones con herramientas y preview"""
    
    # Señales
    data_transformed = Signal(object)  # Pandas DataFrame transformado
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.df_original = None
        self.df_current = None
        self.transformation_history = []
        self.worker_thread = None
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.update_preview)
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Crear splitter principal
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo: Herramientas de transformación
        left_panel = self.create_tools_panel()
        splitter.addWidget(left_panel)
        
        # Panel central: Preview y historial
        center_panel = self.create_preview_panel()
        splitter.addWidget(center_panel)
        
        # Configurar proporciones del splitter
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter)
        
    def create_tools_panel(self):
        """Crear panel de herramientas de transformación"""
        tools_widget = QWidget()
        tools_layout = QVBoxLayout(tools_widget)
        
        # Título del panel
        title_label = QLabel("Herramientas de Transformación")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                background-color: #4a90e2;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        tools_layout.addWidget(title_label)
        
        # Crear tabs para categorías de transformaciones
        self.tools_tabs = QTabWidget()
        
        # Tab: Columnas
        self.create_column_transformations_tab()
        
        # Tab: Matemáticas
        self.create_math_transformations_tab()
        
        # Tab: Texto
        self.create_text_transformations_tab()
        
        # Tab: Fechas
        self.create_date_transformations_tab()
        
        # Tab: Codificación
        self.create_encoding_transformations_tab()
        
        # Tab: Agregaciones
        self.create_aggregation_transformations_tab()
        
        tools_layout.addWidget(self.tools_tabs)
        
        # Botones de acción
        self.create_action_buttons(tools_layout)
        
        return tools_widget
        
    def create_column_transformations_tab(self):
        """Crear tab de transformaciones de columnas"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Lista de transformaciones de columnas
        self.column_transformations_list = QListWidget()
        column_transformations = [
            "Renombrar Columnas",
            "Crear Columna Calculada", 
            "Aplicar Función",
            "Eliminar Columnas"
        ]
        
        for trans in column_transformations:
            item = QListWidgetItem(trans)
            item.setData(Qt.UserRole, "column")
            self.column_transformations_list.addItem(item)
            
        self.column_transformations_list.itemClicked.connect(self.on_transformation_selected)
        layout.addWidget(self.column_transformations_list)
        
        # Parámetros específicos
        self.column_params_panel = QGroupBox("Parámetros")
        self.column_params_layout = QFormLayout(self.column_params_panel)
        layout.addWidget(self.column_params_panel)
        
        self.tools_tabs.addTab(tab, "Columnas")
        
    def create_math_transformations_tab(self):
        """Crear tab de transformaciones matemáticas"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Lista de transformaciones matemáticas
        self.math_transformations_list = QListWidget()
        math_transformations = [
            "Transformación Logarítmica",
            "Transformación Exponencial", 
            "Escalado (Min-Max)",
            "Escalado Estándar",
            "Escalado Robusto",
            "Escalado MaxAbs",
            "Normalización L1",
            "Normalización L2",
            "Normalización Max",
            "Función Personalizada"
        ]
        
        for trans in math_transformations:
            item = QListWidgetItem(trans)
            item.setData(Qt.UserRole, "math")
            self.math_transformations_list.addItem(item)
            
        self.math_transformations_list.itemClicked.connect(self.on_transformation_selected)
        layout.addWidget(self.math_transformations_list)
        
        # Parámetros específicos
        self.math_params_panel = QGroupBox("Parámetros")
        self.math_params_layout = QFormLayout(self.math_params_panel)
        layout.addWidget(self.math_params_panel)
        
        self.tools_tabs.addTab(tab, "Matemáticas")
        
    def create_text_transformations_tab(self):
        """Crear tab de transformaciones de texto"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Lista de transformaciones de texto
        self.text_transformations_list = QListWidget()
        text_transformations = [
            "Limpiar Texto",
            "Extracción con Regex",
            "Conversión de Case",
            "Padding y Trimming"
        ]
        
        for trans in text_transformations:
            item = QListWidgetItem(trans)
            item.setData(Qt.UserRole, "text")
            self.text_transformations_list.addItem(item)
            
        self.text_transformations_list.itemClicked.connect(self.on_transformation_selected)
        layout.addWidget(self.text_transformations_list)
        
        # Parámetros específicos
        self.text_params_panel = QGroupBox("Parámetros")
        self.text_params_layout = QFormLayout(self.text_params_panel)
        layout.addWidget(self.text_params_panel)
        
        self.tools_tabs.addTab(tab, "Texto")
        
    def create_date_transformations_tab(self):
        """Crear tab de transformaciones de fecha/tiempo"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Lista de transformaciones de fecha
        self.date_transformations_list = QListWidget()
        date_transformations = [
            "Parsear Fechas",
            "Extraer Componentes",
            "Diferencia de Fechas",
            "Convertir Zona Horaria"
        ]
        
        for trans in date_transformations:
            item = QListWidgetItem(trans)
            item.setData(Qt.UserRole, "date")
            self.date_transformations_list.addItem(item)
            
        self.date_transformations_list.itemClicked.connect(self.on_transformation_selected)
        layout.addWidget(self.date_transformations_list)
        
        # Parámetros específicos
        self.date_params_panel = QGroupBox("Parámetros")
        self.date_params_layout = QFormLayout(self.date_params_panel)
        layout.addWidget(self.date_params_panel)
        
        self.tools_tabs.addTab(tab, "Fechas")
        
    def create_encoding_transformations_tab(self):
        """Crear tab de transformaciones de codificación"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Lista de transformaciones de codificación
        self.encoding_transformations_list = QListWidget()
        encoding_transformations = [
            "Label Encoding",
            "One-Hot Encoding",
            "Ordinal Encoding",
            "Target Encoding"
        ]
        
        for trans in encoding_transformations:
            item = QListWidgetItem(trans)
            item.setData(Qt.UserRole, "encoding")
            self.encoding_transformations_list.addItem(item)
            
        self.encoding_transformations_list.itemClicked.connect(self.on_transformation_selected)
        layout.addWidget(self.encoding_transformations_list)
        
        # Parámetros específicos
        self.encoding_params_panel = QGroupBox("Parámetros")
        self.encoding_params_layout = QFormLayout(self.encoding_params_panel)
        layout.addWidget(self.encoding_params_panel)
        
        self.tools_tabs.addTab(tab, "Codificación")
        
    def create_aggregation_transformations_tab(self):
        """Crear tab de transformaciones de agregación"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Lista de transformaciones de agregación
        self.aggregation_transformations_list = QListWidget()
        aggregation_transformations = [
            "Agregación Multi-función",
            "Pivoteo Avanzado",
            "Ventana Deslizante",
            "Ventana Expansiva",
            "GroupBy Transform"
        ]
        
        for trans in aggregation_transformations:
            item = QListWidgetItem(trans)
            item.setData(Qt.UserRole, "aggregation")
            self.aggregation_transformations_list.addItem(item)
            
        self.aggregation_transformations_list.itemClicked.connect(self.on_transformation_selected)
        layout.addWidget(self.aggregation_transformations_list)
        
        # Parámetros específicos
        self.aggregation_params_panel = QGroupBox("Parámetros")
        self.aggregation_params_layout = QFormLayout(self.aggregation_params_panel)
        layout.addWidget(self.aggregation_params_panel)
        
        self.tools_tabs.addTab(tab, "Agregaciones")
        
    def create_action_buttons(self, layout):
        """Crear botones de acción"""
        buttons_frame = QFrame()
        buttons_layout = QVBoxLayout(buttons_frame)
        
        # Botón Previsualizar
        self.preview_btn = QPushButton("Previsualizar")
        self.preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.preview_btn.clicked.connect(self.preview_transformation)
        buttons_layout.addWidget(self.preview_btn)
        
        # Botón Aplicar
        self.apply_btn = QPushButton("Aplicar Transformación")
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.apply_btn.clicked.connect(self.apply_transformation)
        buttons_layout.addWidget(self.apply_btn)
        
        # Botón Deshacer
        self.undo_btn = QPushButton("Deshacer")
        self.undo_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.undo_btn.clicked.connect(self.undo_last_transformation)
        buttons_layout.addWidget(self.undo_btn)
        
        layout.addWidget(buttons_frame)
        
    def create_preview_panel(self):
        """Crear panel de preview e historial"""
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        # Título del panel
        title_label = QLabel("Preview e Historial")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                background-color: #6c757d;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        preview_layout.addWidget(title_label)
        
        # Crear tabs para preview e historial
        self.preview_tabs = QTabWidget()
        
        # Tab: Preview
        self.create_preview_tab()
        
        # Tab: Historial
        self.create_history_tab()
        
        preview_layout.addWidget(self.preview_tabs)
        
        return preview_widget
        
    def create_preview_tab(self):
        """Crear tab de preview"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Información del preview
        self.preview_info_label = QLabel("Selecciona una transformación para previsualizar")
        self.preview_info_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 10px;
                border-radius: 5px;
                font-style: italic;
            }
        """)
        layout.addWidget(self.preview_info_label)
        
        # Vista de tabla para preview
        self.preview_table = QTableView()
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setStyleSheet("""
            QTableView {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
            }
        """)
        layout.addWidget(self.preview_table)
        
        # Barra de progreso para operaciones
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.preview_tabs.addTab(tab, "Preview")
        
    def create_history_tab(self):
        """Crear tab de historial"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Tree widget para historial
        self.history_tree = QTreeWidget()
        self.history_tree.setHeaderLabels(["Operaciones de Transformación", "Estado", "Timestamp"])
        self.history_tree.setAlternatingRowColors(True)
        self.history_tree.setStyleSheet("""
            QTreeWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
            }
            QTreeWidget::item {
                padding: 5px;
            }
        """)
        layout.addWidget(self.history_tree)
        
        # Botones de gestión de historial
        history_buttons_layout = QHBoxLayout()
        
        clear_history_btn = QPushButton("Limpiar Historial")
        clear_history_btn.clicked.connect(self.clear_history)
        history_buttons_layout.addWidget(clear_history_btn)
        
        export_history_btn = QPushButton("Exportar Historial")
        export_history_btn.clicked.connect(self.export_history)
        history_buttons_layout.addWidget(export_history_btn)
        
        history_buttons_layout.addStretch()
        layout.addLayout(history_buttons_layout)
        
        self.preview_tabs.addTab(tab, "Historial")
        
    def setup_connections(self):
        """Configurar conexiones de señales"""
        # Inicialmente no hay datos
        self.update_ui_state()
        
    def update_ui_state(self):
        """Actualizar estado de la UI basado en si hay datos"""
        has_data = self.df_original is not None
        
        # Habilitar/deshabilitar elementos
        widgets_to_disable = [
            self.tools_tabs,
            self.preview_btn,
            self.apply_btn
        ]
        
        for widget in widgets_to_disable:
            widget.setEnabled(has_data)
            
        if not has_data:
            self.preview_info_label.setText("Selecciona una transformación para previsualizar")
            self.preview_table.setModel(None)
            
    def set_data(self, df):
        """Establecer datos para transformar"""
        self.df_original = df.copy() if df is not None else None
        self.df_current = df.copy() if df is not None else None
        self.update_ui_state()
        
        # Actualizar lista de columnas en todos los paneles de parámetros
        self.update_column_selections()
        
    def update_column_selections(self):
        """Actualizar selecciones de columnas en todos los paneles"""
        if self.df_original is None:
            return
            
        columns = self.df_original.columns.tolist()
        
        # Aquí se actualizarían los combo boxes de selección de columnas
        # en los paneles de parámetros cuando se creen
        
    def on_transformation_selected(self, item):
        """Manejar selección de transformación"""
        transformation_name = item.text()
        category = item.data(Qt.UserRole)
        
        # Crear panel de parámetros específico para la transformación
        self.create_parameters_panel(transformation_name, category)
        
    def create_parameters_panel(self, transformation_name, category):
        """Crear panel de parámetros dinámico basado en la transformación"""
        # Determinar qué panel de parámetros usar
        if category == "column":
            params_layout = self.column_params_layout
            params_panel = self.column_params_panel
        elif category == "math":
            params_layout = self.math_params_layout
            params_panel = self.math_params_panel
        elif category == "text":
            params_layout = self.text_params_layout
            params_panel = self.text_params_panel
        elif category == "date":
            params_layout = self.date_params_layout
            params_panel = self.date_params_panel
        elif category == "encoding":
            params_layout = self.encoding_params_layout
            params_panel = self.encoding_params_panel
        elif category == "aggregation":
            params_layout = self.aggregation_params_layout
            params_panel = self.aggregation_params_panel
        else:
            return
            
        # Limpiar layout actual
        while params_layout.count():
            child = params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # Agregar selección de columnas (común para todas)
        if self.df_original is not None:
            columns = self.df_original.columns.tolist()
            
            columns_combo = QComboBox()
            columns_combo.addItems(columns)
            columns_combo.setEditable(True)
            params_layout.addRow("Columnas:", columns_combo)
            
        # Parámetros específicos por tipo de transformación
        self.add_specific_parameters(transformation_name, params_layout, category)
        
        # Actualizar título del panel
        params_panel.setTitle(f"Parámetros: {transformation_name}")
        
    def add_specific_parameters(self, transformation_name, layout, category):
        """Agregar parámetros específicos según la transformación"""
        # Implementar parámetros específicos para cada transformación
        # Este es un ejemplo básico, se expandiría según las necesidades
        
        if "Renombrar" in transformation_name:
            new_name_edit = QLineEdit()
            new_name_edit.setPlaceholderText("Nuevo nombre para la columna")
            layout.addRow("Nuevo nombre:", new_name_edit)
            
        elif "Logarítmica" in transformation_name:
            base_spin = QDoubleSpinBox()
            base_spin.setRange(0.1, 10.0)
            base_spin.setValue(10.0)
            base_spin.setSingleStep(0.1)
            layout.addRow("Base:", base_spin)
            
        elif "Escalado" in transformation_name:
            method_combo = QComboBox()
            method_combo.addItems(["min-max", "standard", "robust", "maxabs"])
            layout.addRow("Método:", method_combo)
            
        elif "Limpiar" in transformation_name:
            remove_punct_check = QCheckBox("Eliminar puntuación")
            remove_numbers_check = QCheckBox("Eliminar números")
            to_lower_check = QCheckBox("Convertir a minúsculas")
            
            layout.addRow("Opciones:", remove_punct_check)
            layout.addRow("", remove_numbers_check)
            layout.addRow("", to_lower_check)
            
        elif "Parsear" in transformation_name:
            format_edit = QLineEdit()
            format_edit.setPlaceholderText("Formato de fecha (ej: %Y-%m-%d)")
            layout.addRow("Formato:", format_edit)
            
        elif "Label" in transformation_name:
            handle_unknown_combo = QComboBox()
            handle_unknown_combo.addItems(["error", "use_encoded_value", "ignore"])
            layout.addRow("Manejar desconocido:", handle_unknown_combo)
            
        elif "Agregación" in transformation_name:
            groupby_columns_combo = QComboBox()
            if self.df_original is not None:
                groupby_columns_combo.addItems(self.df_original.columns.tolist())
            groupby_columns_combo.setEditable(True)
            layout.addRow("Agrupar por:", groupby_columns_combo)
            
            agg_func_combo = QComboBox()
            agg_func_combo.addItems(["mean", "sum", "count", "std", "min", "max"])
            layout.addRow("Función:", agg_func_combo)
            
    def get_current_parameters(self, category):
        """Obtener parámetros actuales del panel activo"""
        if category == "column":
            params_layout = self.column_params_layout
        elif category == "math":
            params_layout = self.math_params_layout
        elif category == "text":
            params_layout = self.text_params_layout
        elif category == "date":
            params_layout = self.date_params_layout
        elif category == "encoding":
            params_layout = self.encoding_params_layout
        elif category == "aggregation":
            params_layout = self.aggregation_params_layout
        else:
            return {}
            
        # Extraer parámetros del layout
        parameters = {}
        for i in range(params_layout.count()):
            item = params_layout.itemAt(i)
            if isinstance(item.widget(), QComboBox) or isinstance(item.widget(), QLineEdit) or \
               isinstance(item.widget(), QSpinBox) or isinstance(item.widget(), QDoubleSpinBox):
                label_text = params_layout.itemAt(i-1).widget().text() if i > 0 else ""
                widget = item.widget()
                if hasattr(widget, 'currentText'):
                    parameters[label_text] = widget.currentText()
                elif hasattr(widget, 'text'):
                    parameters[label_text] = widget.text()
                elif hasattr(widget, 'value'):
                    parameters[label_text] = widget.value()
                    
        return parameters
        
    def preview_transformation(self):
        """Previsualizar transformación"""
        if self.df_original is None:
            return
            
        # Obtener transformación activa
        current_tab = self.tools_tabs.currentWidget()
        if current_tab is None:
            return
            
        current_list = current_tab.findChild(QListWidget)
        current_item = current_list.currentItem()
        
        if current_item is None:
            QMessageBox.warning(self, "Advertencia", "Selecciona una transformación primero.")
            return
            
        transformation_name = current_item.text()
        category = current_item.data(Qt.UserRole)
        
        # Obtener parámetros
        parameters = self.get_current_parameters(category)
        
        # Preparar datos de transformación
        transformation_data = {
            'name': transformation_name,
            'category': category,
            'parameters': parameters
        }
        
        # Mostrar barra de progreso
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Ejecutar transformación en hilo separado
        if self.worker_thread:
            self.worker_thread.terminate()
            
        self.worker_thread = TransformationWorkerThread(transformation_data, self.df_current)
        self.worker_thread.progress_updated.connect(self.update_progress)
        self.worker_thread.transformation_applied.connect(self.on_preview_completed)
        self.worker_thread.error_occurred.connect(self.on_transformation_error)
        self.worker_thread.start()
        
    def apply_transformation(self):
        """Aplicar transformación permanentemente"""
        if self.df_original is None:
            return
            
        # Usar el mismo mecanismo que preview pero aplicar al original
        self.preview_transformation()
        # El worker emitirá señal y se aplicará la transformación
        
    def undo_last_transformation(self):
        """Deshacer última transformación"""
        if len(self.transformation_history) > 0:
            self.transformation_history.pop()  # Remover última
            # Restaurar estado anterior si es necesario
            self.update_history_display()
            QMessageBox.information(self, "Éxito", "Última transformación deshecha.")
        else:
            QMessageBox.information(self, "Información", "No hay transformaciones para deshacer.")
            
    def update_progress(self, value, message):
        """Actualizar barra de progreso"""
        self.progress_bar.setValue(value)
        self.preview_info_label.setText(message)
        
    def on_preview_completed(self, result_df):
        """Manejar preview completado"""
        self.progress_bar.setVisible(False)
        self.df_current = result_df
        
        # Actualizar vista de preview
        self.update_preview_table(result_df)
        
        # Actualizar información
        self.preview_info_label.setText(f"Preview: {len(result_df)} filas, {len(result_df.columns)} columnas")
        
    def on_transformation_error(self, error_message):
        """Manejar error en transformación"""
        self.progress_bar.setVisible(False)
        self.preview_info_label.setText("Error en transformación")
        QMessageBox.critical(self, "Error", error_message)
        
    def update_preview(self):
        """Actualizar preview con temporizador"""
        # Implementar preview en tiempo real
        pass
        
    def update_preview_table(self, df):
        """Actualizar tabla de preview"""
        from app.models.pandas_model import VirtualizedPandasModel
        
        if df is not None and len(df) > 0:
            # Mostrar solo las primeras 100 filas para preview
            preview_df = df.head(100)
            model = VirtualizedPandasModel(preview_df)
            self.preview_table.setModel(model)
        else:
            self.preview_table.setModel(None)
            
    def add_to_history(self, transformation_name, parameters, success=True):
        """Agregar transformación al historial"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        status = "✅ Éxito" if success else "❌ Error"
        
        # Crear item en el tree
        root_item = QTreeWidgetItem(self.history_tree)
        root_item.setText(0, transformation_name)
        root_item.setText(1, status)
        root_item.setText(2, timestamp)
        
        # Agregar parámetros como children
        for param, value in parameters.items():
            child_item = QTreeWidgetItem(root_item)
            child_item.setText(0, f"  {param}")
            child_item.setText(1, str(value))
            
        self.history_tree.expandAll()
        
        # Agregar al historial interno
        self.transformation_history.append({
            'name': transformation_name,
            'parameters': parameters,
            'timestamp': timestamp,
            'success': success
        })
        
    def update_history_display(self):
        """Actualizar display del historial"""
        self.history_tree.clear()
        for item in self.transformation_history:
            self.add_to_history(item['name'], item['parameters'], item['success'])
            
    def clear_history(self):
        """Limpiar historial"""
        self.transformation_history.clear()
        self.history_tree.clear()
        QMessageBox.information(self, "Éxito", "Historial limpiado.")
        
    def export_history(self):
        """Exportar historial a archivo"""
        if not self.transformation_history:
            QMessageBox.information(self, "Información", "No hay historial para exportar.")
            return
            
        from PySide6.QtWidgets import QFileDialog
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Historial de Transformaciones",
            "",
            "Archivos de Texto (*.txt);;Archivos CSV (*.csv)"
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("Historial de Transformaciones\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for item in self.transformation_history:
                        f.write(f"Transformación: {item['name']}\n")
                        f.write(f"Timestamp: {item['timestamp']}\n")
                        f.write(f"Estado: {'Éxito' if item['success'] else 'Error'}\n")
                        f.write("Parámetros:\n")
                        for param, value in item['parameters'].items():
                            f.write(f"  - {param}: {value}\n")
                        f.write("\n" + "-" * 30 + "\n\n")
                        
                QMessageBox.information(self, "Éxito", f"Historial exportado a {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo exportar el historial: {str(e)}")