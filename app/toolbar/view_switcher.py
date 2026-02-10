"""
View Switcher for Flash View Sheet.

This module provides the view switching buttons widget.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal


class ViewSwitcher(QWidget):
    """
    Widget containing buttons for switching between views.
    
    Provides:
    - Vista Principal button
    - Vista de Datos button
    - Ver Información button
    - Vista Gráficos button
    - Cruzar Datos button
    """
    
    # Signals for each view
    view_main = Signal()
    view_data = Signal()
    view_info = Signal()
    view_graphics = Signal()
    view_joined = Signal()
    
    def __init__(self, parent=None):
        """
        Initialize the view switcher.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create UI
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Main layout
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        # Button: Vista Principal
        self.view_main_btn = QPushButton("Vista Principal")
        self.view_main_btn.setToolTip("Volver a la pantalla de carga de archivos")
        self.layout.addWidget(self.view_main_btn)
        
        # Button: Vista de Datos
        self.view_data_btn = QPushButton("Vista de Datos")
        self.view_data_btn.setToolTip("Ver datos en formato tabular")
        self.layout.addWidget(self.view_data_btn)
        
        # Button: Ver Información
        self.view_info_btn = QPushButton("Ver Información del dataset")
        self.view_info_btn.setToolTip("Ver información estadística del dataset")
        self.layout.addWidget(self.view_info_btn)
        
        # Button: Vista Gráficos
        self.view_graphics_btn = QPushButton("Vista Gráficos")
        self.view_graphics_btn.setToolTip("Ver visualizaciones de datos")
        self.layout.addWidget(self.view_graphics_btn)
        
        # Button: Cruzar Datos
        self.view_joined_btn = QPushButton("Cruzar Datos")
        self.view_joined_btn.setToolTip("Ver datos cruzados (disponible después de un join)")
        self.view_joined_btn.setEnabled(False)  # Enabled when join results exist
        self.layout.addWidget(self.view_joined_btn)
    
    def _connect_signals(self):
        """Connect button signals to slots."""
        self.view_main_btn.clicked.connect(self.view_main.emit)
        self.view_data_btn.clicked.connect(self.view_data.emit)
        self.view_info_btn.clicked.connect(self.view_info.emit)
        self.view_graphics_btn.clicked.connect(self.view_graphics.emit)
        self.view_joined_btn.clicked.connect(self.view_joined.emit)
    
    def set_joined_enabled(self, enabled):
        """
        Enable or disable the joined data view button.
        
        Args:
            enabled: True to enable, False to disable
        """
        self.view_joined_btn.setEnabled(enabled)
    
    def set_main_enabled(self, enabled):
        """
        Enable or disable the main view button.
        
        Args:
            enabled: True to enable, False to disable
        """
        self.view_main_btn.setEnabled(enabled)
    
    def set_data_enabled(self, enabled):
        """
        Enable or disable the data view button.
        
        Args:
            enabled: True to enable, False to disable
        """
        self.view_data_btn.setEnabled(enabled)
    
    def set_info_enabled(self, enabled):
        """
        Enable or disable the info view button.
        
        Args:
            enabled: True to enable, False to disable
        """
        self.view_info_btn.setEnabled(enabled)
    
    def set_graphics_enabled(self, enabled):
        """
        Enable or disable the graphics view button.
        
        Args:
            enabled: True to enable, False to disable
        """
        self.view_graphics_btn.setEnabled(enabled)
