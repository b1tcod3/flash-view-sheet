"""
DataView - Widget principal para vista de datos con paginación y filtros integrados
Contiene tabla paginada, controles de paginación y filtros
"""

import pandas as pd
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableView, 
                               QComboBox, QLineEdit, QPushButton, QLabel, 
                               QGroupBox, QFrame, QMessageBox, QSpinBox,
                               QApplication)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

from .pagination_manager import PaginationManager
from app.models.pandas_model import VirtualizedPandasModel


class DataView(QWidget):
    """
    Widget principal para vista de datos con paginación y filtros
    Integra tabla, controles de paginación y filtros en una sola vista
    """
    
    # Señales para comunicación con ventana principal
    filter_applied = Signal(str, str)  # columna, término
    filter_cleared = Signal()
    data_updated = Signal()  # Datos actualizados (para actualizar gráficos, etc.)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Componentes principales
        self.pagination_manager = None
        self.pandas_model = None
        self.original_df = None
        
        # Estado de ordenamiento
        self._sorting_in_progress = False
        
        # UI Components
        self.table_view = None
        self.filter_combo = None
        self.filter_input = None
        self.apply_filter_btn = None
        self.clear_filter_btn = None
        self.page_size_spin = None
        self.page_info_label = None
        self.first_page_btn = None
        self.prev_page_btn = None
        self.next_page_btn = None
        self.last_page_btn = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 1. Sección de filtros (superior)
        filter_group = self.create_filter_section()
        main_layout.addWidget(filter_group)
        
        # 2. Tabla de datos (centro)
        table_group = self.create_table_section()
        main_layout.addWidget(table_group, 1)  # Expandir para ocupar espacio disponible
        
        # 3. Controles de paginación (inferior)
        pagination_group = self.create_pagination_section()
        main_layout.addWidget(pagination_group)
        
    def create_filter_section(self) -> QGroupBox:
        """Crear sección de filtros"""
        filter_group = QGroupBox("Filtros")
        filter_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        filter_layout = QHBoxLayout(filter_group)
        filter_layout.setSpacing(10)
        
        # ComboBox para seleccionar columna
        self.filter_combo = QComboBox()
        self.filter_combo.setMinimumWidth(150)
        self.filter_combo.setPlaceholderText("Seleccionar columna")
        filter_layout.addWidget(QLabel("Columna:"))
        filter_layout.addWidget(self.filter_combo)
        
        # LineEdit para término de búsqueda
        self.filter_input = QLineEdit()
        self.filter_input.setMinimumWidth(200)
        self.filter_input.setPlaceholderText("Término de búsqueda")
        filter_layout.addWidget(QLabel("Buscar:"))
        filter_layout.addWidget(self.filter_input)
        
        # Botón aplicar filtro
        self.apply_filter_btn = QPushButton("Aplicar Filtro")
        self.apply_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        self.apply_filter_btn.clicked.connect(self.apply_filter)
        filter_layout.addWidget(self.apply_filter_btn)
        
        # Botón limpiar filtro
        self.clear_filter_btn = QPushButton("Limpiar Filtro")
        self.clear_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.clear_filter_btn.clicked.connect(self.clear_filter)
        filter_layout.addWidget(self.clear_filter_btn)
        
        return filter_group
        
    def create_table_section(self) -> QGroupBox:
        """Crear sección de tabla"""
        table_group = QGroupBox("Datos")
        table_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        table_layout = QVBoxLayout(table_group)
        
        # Tabla principal
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSortingEnabled(True)
        
        # Configurar estilo de la tabla
        self.table_view.setStyleSheet("""
            QTableView {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #ddd;
                gridline-color: #ddd;
            }
            QTableView::item {
                padding: 5px;
                border: none;
            }
            QTableView::item:selected {
                background-color: #4a90e2;
                color: white;
            }
            QHeaderView::section {
                background-color: #f1f3f4;
                border: 1px solid #ddd;
                padding: 6px;
                font-weight: bold;
            }
        """)
        
        table_layout.addWidget(self.table_view)
        
        return table_group
        
    def create_pagination_section(self) -> QGroupBox:
        """Crear sección de paginación"""
        pagination_group = QGroupBox("Paginación")
        pagination_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        pagination_layout = QHBoxLayout(pagination_group)
        pagination_layout.setSpacing(15)
        
        # Información de página
        self.page_info_label = QLabel("Página 0 de 0 (0-0 de 0 filas)")
        self.page_info_label.setFont(QFont("Arial", 10, QFont.Bold))
        pagination_layout.addWidget(self.page_info_label)
        
        pagination_layout.addStretch()
        
        # Controles de tamaño de página
        pagination_layout.addWidget(QLabel("Filas por página:"))
        self.page_size_spin = QSpinBox()
        self.page_size_spin.setMinimum(10)
        self.page_size_spin.setMaximum(1000)
        self.page_size_spin.setValue(10)
        self.page_size_spin.setSuffix(" filas")
        self.page_size_spin.valueChanged.connect(self.change_page_size)
        pagination_layout.addWidget(self.page_size_spin)
        
        # Botones de navegación
        self.first_page_btn = QPushButton("⏮️")
        self.first_page_btn.setMaximumWidth(40)
        self.first_page_btn.setToolTip("Primera página")
        self.first_page_btn.clicked.connect(self.first_page)
        pagination_layout.addWidget(self.first_page_btn)
        
        self.prev_page_btn = QPushButton("◀️")
        self.prev_page_btn.setMaximumWidth(40)
        self.prev_page_btn.setToolTip("Página anterior")
        self.prev_page_btn.clicked.connect(self.previous_page)
        pagination_layout.addWidget(self.prev_page_btn)
        
        self.next_page_btn = QPushButton("▶️")
        self.next_page_btn.setMaximumWidth(40)
        self.next_page_btn.setToolTip("Página siguiente")
        self.next_page_btn.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_page_btn)
        
        self.last_page_btn = QPushButton("⏭️")
        self.last_page_btn.setMaximumWidth(40)
        self.last_page_btn.setToolTip("Última página")
        self.last_page_btn.clicked.connect(self.last_page)
        pagination_layout.addWidget(self.last_page_btn)
        
        return pagination_group
        
    def set_data(self, df: pd.DataFrame):
        """
        Establecer datos para mostrar
        
        Args:
            df: DataFrame con datos
        """
        self.original_df = df.copy()
        
        # Crear o actualizar PaginationManager
        if self.pagination_manager is None:
            self.pagination_manager = PaginationManager(df, self.page_size_spin.value())
            self.connect_pagination_signals()
        else:
            self.pagination_manager.set_data(df)
        
        # Poblar ComboBox de filtros con nombres de columnas
        if not df.empty:
            self.filter_combo.clear()
            self.filter_combo.addItems(df.columns.tolist())
        
        # Actualizar vista
        self.update_view()
        
    def connect_pagination_signals(self):
        """Conectar señales del PaginationManager"""
        self.pagination_manager.page_changed.connect(self.on_page_changed)
        self.pagination_manager.page_size_changed.connect(self.on_page_size_changed)
        self.pagination_manager.data_changed.connect(self.on_data_changed)
        self.pagination_manager.total_pages_changed.connect(self.on_total_pages_changed)
        
    def connect_model_signals(self):
        """Conectar señales del modelo para manejar ordenamiento"""
        if self.pandas_model is not None:
            # Conectar señal de cambio de layout (ordenamiento)
            self.pandas_model.layoutChanged.connect(self.on_model_sorted)
            
    def on_model_sorted(self):
        """Manejar cuando el modelo es ordenado"""
        if self.pandas_model is not None and self.pagination_manager is not None:
            # Prevenir re-entrada y actualizaciones duplicadas
            if hasattr(self, '_sorting_in_progress') and self._sorting_in_progress:
                return
                
            self._sorting_in_progress = True
            
            try:
                # Obtener datos ordenados del modelo
                sorted_data = self.pandas_model.get_sorted_data()
                
                # Si el modelo solo tiene datos de una página, usar el DataFrame original completo
                if len(sorted_data) < len(self.original_df):
                    # El modelo solo tiene la página actual, pero queremos todo el DataFrame ordenado
                    full_sorted_data = self.original_df.sort_values(sorted_data.columns[0], ascending=False)
                else:
                    full_sorted_data = sorted_data
                
                # Actualizar PaginationManager con datos ordenados, preservando página actual
                self.pagination_manager.set_data(full_sorted_data, preserve_page=True)
                
                # Actualizar DataFrame original
                self.original_df = full_sorted_data.copy()
                
                # NO llamar update_view() aquí para evitar pérdida de ordenamiento
                # La actualización del modelo ya contiene los datos ordenados
                
            finally:
                self._sorting_in_progress = False
        
    def update_view(self):
        """Actualizar vista con datos actuales"""
        if self.pagination_manager is None or self.original_df is None:
            return
        
        # Evitar actualización de vista durante ordenamiento para preservar datos ordenados
        if hasattr(self, '_sorting_in_progress') and self._sorting_in_progress:
            return
        
        # Obtener datos de la página actual
        current_page_data = self.pagination_manager.get_page_data()
        
        # Crear modelo virtualizado con datos de la página actual
        self.pandas_model = VirtualizedPandasModel(current_page_data)
        
        # Establecer modelo en la tabla
        self.table_view.setModel(self.pandas_model)
        
        # Conectar señales del modelo (para ordenamiento)
        self.connect_model_signals()
        
        # Actualizar información de página
        self.update_page_info()
        
        # Actualizar estado de botones
        self.update_pagination_buttons()
        
        # Emitir señal de datos actualizados
        self.data_updated.emit()
        
    def update_page_info(self):
        """Actualizar etiqueta de información de página"""
        if self.pagination_manager is None:
            self.page_info_label.setText("Sin datos")
            return
        
        page_info = self.pagination_manager.get_page_info()
        
        if page_info['total_rows'] == 0:
            text = "Sin datos para mostrar"
        else:
            text = (f"Página {page_info['current_page']} de {page_info['total_pages']} "
                   f"({page_info['start_row']}-{page_info['end_row']} de {page_info['total_rows']} filas)")
        
        self.page_info_label.setText(text)
        
    def update_pagination_buttons(self):
        """Actualizar estado de botones de paginación"""
        if self.pagination_manager is None:
            # Deshabilitar todos los botones
            for btn in [self.first_page_btn, self.prev_page_btn, self.next_page_btn, self.last_page_btn]:
                btn.setEnabled(False)
            return
        
        can_prev = self.pagination_manager.can_go_previous()
        can_next = self.pagination_manager.can_go_next()
        
        self.first_page_btn.setEnabled(can_prev and self.pagination_manager.get_current_page() > 1)
        self.prev_page_btn.setEnabled(can_prev)
        self.next_page_btn.setEnabled(can_next)
        self.last_page_btn.setEnabled(can_next and self.pagination_manager.get_current_page() < self.pagination_manager.get_total_pages())
        
    # Métodos de navegación de página
    def first_page(self):
        """Ir a la primera página"""
        if self.pagination_manager:
            self.pagination_manager.first_page()
            
    def previous_page(self):
        """Ir a la página anterior"""
        if self.pagination_manager:
            self.pagination_manager.previous_page()
            
    def next_page(self):
        """Ir a la página siguiente"""
        if self.pagination_manager:
            self.pagination_manager.next_page()
            
    def last_page(self):
        """Ir a la última página"""
        if self.pagination_manager:
            self.pagination_manager.last_page()
            
    def change_page_size(self, size: int):
        """Cambiar tamaño de página"""
        if self.pagination_manager:
            self.pagination_manager.set_page_size(size)
            
    # Métodos de filtrado
    def apply_filter(self):
        """Aplicar filtro"""
        if self.pagination_manager is None:
            return
        
        column = self.filter_combo.currentText()
        term = self.filter_input.text().strip()
        
        if not column:
            QMessageBox.warning(self, "Advertencia", "Selecciona una columna para filtrar.")
            return
        
        if not term:
            QMessageBox.warning(self, "Advertencia", "Ingresa un término de búsqueda.")
            return
        
        try:
            self.pagination_manager.apply_filter(column, term)
            
            # Emitir señal para ventana principal
            self.filter_applied.emit(column, term)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al aplicar filtro: {str(e)}")
            
    def clear_filter(self):
        """Limpiar filtro"""
        if self.pagination_manager:
            self.pagination_manager.clear_filter()
            
            # Limpiar campos de filtro
            self.filter_input.clear()
            self.filter_combo.setCurrentIndex(-1)
            
            # Emitir señal para ventana principal
            self.filter_cleared.emit()
            
    # Slots para señales del PaginationManager
    def on_page_changed(self, page: int):
        """Manejar cambio de página"""
        self.update_view()
        
    def on_page_size_changed(self, size: int):
        """Manejar cambio de tamaño de página"""
        self.page_size_spin.setValue(size)
        self.update_view()
        
    def on_data_changed(self):
        """Manejar cambio de datos"""
        self.update_view()
        
    def on_total_pages_changed(self, total_pages: int):
        """Manejar cambio en número total de páginas"""
        self.update_pagination_buttons()
        self.update_page_info()
        
    def get_current_filter_info(self) -> dict:
        """Obtener información del filtro actual"""
        if self.pagination_manager:
            return self.pagination_manager.get_filter_info()
        return {}
        
    def export_current_page(self) -> pd.DataFrame:
        """Obtener datos de la página actual para exportar"""
        if self.pagination_manager:
            return self.pagination_manager.get_page_data()
        return pd.DataFrame()