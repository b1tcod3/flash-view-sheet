"""
Toolbar Manager for Flash View Sheet.

This module manages the main toolbar creation and coordination.
"""

from PySide6.QtWidgets import QToolBar, QWidget

from app.toolbar.view_switcher import ViewSwitcher
from app.toolbar.filter_toolbar import FilterToolbar
from typing import Optional, List


class ToolbarManager:
    """
    Manages the main toolbar for the application.
    
    Responsibilities:
    - Create and configure the main toolbar
    - Manage view switcher buttons
    - Manage filter controls
    - Coordinate toolbar components
    """
    
    def __init__(self, main_window: QWidget) -> None:
        """
        Initialize the toolbar manager.
        
        Args:
            main_window: Reference to the main window
        """
        self.main_window = main_window
        self.tool_bar: Optional[QToolBar] = None
        self.view_switcher: Optional[ViewSwitcher] = None
        self.filter_toolbar: Optional[FilterToolbar] = None
        
    def create_toolbar(self) -> QToolBar:
        """
        Create and configure the main toolbar.
        
        Returns:
            QToolBar: The created toolbar
        """
        self.tool_bar = QToolBar("Herramientas")
        self.tool_bar.setMovable(False)
        self.tool_bar.setFloatable(False)
        
        # Add view switcher
        self._create_view_switcher()
        
        # Note: Filter controls are now integrated in DataView
        
        return self.tool_bar
    
    def _create_view_switcher(self) -> None:
        """Create the view switcher buttons."""
        self.view_switcher = ViewSwitcher(self.main_window)
        
        # Connect signals
        self.view_switcher.view_main.connect(lambda: self._on_view_switch(0))
        self.view_switcher.view_data.connect(lambda: self._on_view_switch(1))
        self.view_switcher.view_info.connect(self._on_info_requested)
        self.view_switcher.view_graphics.connect(lambda: self._on_view_switch(2))
        self.view_switcher.view_joined.connect(lambda: self._on_view_switch(3))
        
        # Add to toolbar
        self.tool_bar.addWidget(self.view_switcher)
    
    def _on_view_switch(self, index: int) -> None:
        """Handle view switch request."""
        if hasattr(self.main_window, 'switch_view'):
            self.main_window.switch_view(index)
    
    def _on_info_requested(self) -> None:
        """Handle info modal request."""
        if hasattr(self.main_window, 'show_info_modal'):
            self.main_window.show_info_modal()
    
    def set_view_buttons_enabled(self, enabled: bool) -> None:
        """
        Enable or disable view buttons.
        
        Args:
            enabled: True to enable, False to disable
        """
        if self.view_switcher:
            self.view_switcher.set_joined_enabled(enabled)
    
    def on_datos_disponibles(self, has_data: bool) -> None:
        """Slot para reaccionar a la disponibilidad de datos"""
        self.set_view_buttons_enabled(has_data)
    
    def populate_filter_combo(self, columns: List[str]) -> None:
        """
        Populate the filter combo box with column names.
        
        Args:
            columns: List of column names
        """
        if self.filter_toolbar:
            self.filter_toolbar.populate_columns(columns)
    
    def clear_filters(self) -> None:
        """Clear filter controls."""
        if self.filter_toolbar:
            self.filter_toolbar.clear()
    
    def get_toolbar(self) -> Optional[QToolBar]:
        """
        Get the toolbar widget.
        
        Returns:
            QToolBar: The toolbar or None if not created
        """
        return self.tool_bar
