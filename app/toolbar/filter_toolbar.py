"""
Filter Toolbar for Flash View Sheet.

This module provides filter controls for the toolbar.
Note: Filter functionality is now integrated in DataView,
but this module is kept for potential future use or advanced filtering.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QComboBox, QLineEdit, QPushButton
from PySide6.QtCore import Signal


class FilterToolbar(QWidget):
    """
    Widget containing filter controls.
    
    Provides:
    - Column selection combo box
    - Search input field
    - Apply filter button
    - Clear filter button
    """
    
    # Signals
    filter_applied = Signal(str, str)  # column, term
    filter_cleared = Signal()
    
    def __init__(self, parent=None):
        """
        Initialize the filter toolbar.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # UI elements
        self.filter_combo = None
        self.filter_input = None
        self.apply_filter_btn = None
        self.clear_filter_btn = None
        
        # Create UI
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Main layout
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        # ComboBox for column selection
        self.filter_combo = QComboBox()
        self.filter_combo.setFixedWidth(150)
        self.filter_combo.setPlaceholderText("Seleccionar columna")
        self.layout.addWidget(self.filter_combo)
        
        # LineEdit for search term
        self.filter_input = QLineEdit()
        self.filter_input.setFixedWidth(200)
        self.filter_input.setPlaceholderText("Término de búsqueda")
        self.layout.addWidget(self.filter_input)
        
        # Apply filter button
        self.apply_filter_btn = QPushButton("Aplicar Filtro")
        self.layout.addWidget(self.apply_filter_btn)
        
        # Clear filter button
        self.clear_filter_btn = QPushButton("Limpiar Filtro")
        self.layout.addWidget(self.clear_filter_btn)
    
    def _connect_signals(self):
        """Connect button signals to slots."""
        self.apply_filter_btn.clicked.connect(self._on_apply_filter)
        self.clear_filter_btn.clicked.connect(self._on_clear_filter)
        
        # Allow pressing Enter in filter input
        self.filter_input.returnPressed.connect(self._on_apply_filter)
    
    def _on_apply_filter(self):
        """Handle apply filter button click."""
        column = self.filter_combo.currentText()
        term = self.filter_input.text().strip()
        
        if column and term:
            self.filter_applied.emit(column, term)
    
    def _on_clear_filter(self):
        """Handle clear filter button click."""
        self.clear()
        self.filter_cleared.emit()
    
    def populate_columns(self, columns):
        """
        Populate the column combo box.
        
        Args:
            columns: List of column names
        """
        self.filter_combo.clear()
        self.filter_combo.addItems(columns)
    
    def clear(self):
        """Clear filter controls."""
        self.filter_input.clear()
        self.filter_combo.setCurrentIndex(-1)
    
    def get_current_column(self):
        """
        Get the currently selected column.
        
        Returns:
            str: Selected column name or empty string
        """
        return self.filter_combo.currentText()
    
    def get_current_term(self):
        """
        Get the current search term.
        
        Returns:
            str: Search term
        """
        return self.filter_input.text().strip()
    
    def set_enabled(self, enabled):
        """
        Enable or disable all filter controls.
        
        Args:
            enabled: True to enable, False to disable
        """
        self.filter_combo.setEnabled(enabled)
        self.filter_input.setEnabled(enabled)
        self.apply_filter_btn.setEnabled(enabled)
        self.clear_filter_btn.setEnabled(enabled)
