"""
Toolbar Manager for Flash View Sheet.

This module manages the main toolbar creation and coordination.
"""

from PySide6.QtWidgets import QToolBar, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from typing import TYPE_CHECKING

from app.toolbar.view_switcher import ViewSwitcher
from app.toolbar.filter_toolbar import FilterToolbar

if TYPE_CHECKING:
    from app.view_manager import ViewCoordinator
    from app.app_coordinator import AppCoordinator


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
        self.main_window = main_window
        self.tool_bar: QToolBar | None = None
        self.view_switcher: ViewSwitcher | None = None
        self.filter_toolbar: FilterToolbar | None = None
        self.view_coordinator: 'ViewCoordinator' | None = None
        self.coordinator: 'AppCoordinator' | None = None
        self.buttons_layout: QHBoxLayout | None = None

    def set_coordinators(self, view_coordinator: 'ViewCoordinator', coordinator: 'AppCoordinator') -> None:
        self.view_coordinator = view_coordinator
        self.coordinator = coordinator

    def create_toolbar(self) -> QToolBar:
        self.tool_bar = QToolBar("Herramientas")
        self.tool_bar.setMovable(False)
        self.tool_bar.setFloatable(False)
        self.tool_bar.setStyleSheet("""
            QToolBar {
                background: transparent;
                border: none;
                spacing: 6px;
            }
        """)

        ribbon_wrapper = QWidget()
        ribbon_layout = QHBoxLayout(ribbon_wrapper)
        ribbon_layout.setContentsMargins(0, 0, 0, 0)
        ribbon_layout.setSpacing(8)

        ribbon_layout.addWidget(self._create_herramientas_section())
        ribbon_layout.addWidget(self._create_filtros_section())

        self.tool_bar.addWidget(ribbon_wrapper)
        return self.tool_bar

    def _create_section_frame(self, title: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("RibbonSection")
        frame.setStyleSheet("""
            QFrame#RibbonSection {
                background-color: #f5f6f7;
                border: 1px solid #c0c2c4;
                border-bottom: 2px solid #a8a8a8;
                border-radius: 3px;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(3)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #2b579a;
            font-family: Arial, sans-serif;
            font-size: 11px;
            font-weight: bold;
            border: none;
        """)
        layout.addWidget(title_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)  # type: ignore[attr-defined]
        separator.setStyleSheet("background-color: #d4d4d4; max-height: 1px; border: none;")
        layout.addWidget(separator)

        return frame

    def _create_herramientas_section(self) -> QFrame:
        section = self._create_section_frame("Herramientas")

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setContentsMargins(0, 2, 0, 0)
        self.buttons_layout.setSpacing(6)

        self._create_view_switcher()

        self.buttons_layout.addStretch()
        section_layout = section.layout()
        assert section_layout is not None
        section_layout.addLayout(self.buttons_layout)  # type: ignore[attr-defined]

        return section

    def _create_filtros_section(self) -> QFrame:
        section = self._create_section_frame("Filtros")

        self.filter_toolbar = FilterToolbar()
        self.filter_toolbar.set_layout_margins(0, 3, 0, 0)

        if self.coordinator is not None:
            self.filter_toolbar.filter_applied.connect(self.coordinator.on_filter_applied)
            self.filter_toolbar.filter_cleared.connect(self.coordinator.on_filter_cleared)

        section_layout = section.layout()
        assert section_layout is not None
        section_layout.addWidget(self.filter_toolbar)
        return section

    def _create_view_switcher(self) -> None:
        self.view_switcher = ViewSwitcher(self.main_window)

        self.view_switcher.view_main.connect(lambda: self._on_view_switch(0))
        self.view_switcher.view_data.connect(lambda: self._on_view_switch(1))
        self.view_switcher.view_info.connect(self._on_info_requested)
        self.view_switcher.view_graphics.connect(lambda: self._on_view_switch(2))
        self.view_switcher.view_joined.connect(lambda: self._on_view_switch(3))

        if self.buttons_layout is not None:
            self.buttons_layout.addWidget(self.view_switcher)

    def _on_view_switch(self, index: int) -> None:
        if self.view_coordinator:
            self.view_coordinator.switch_to(index)

    def _on_info_requested(self) -> None:
        if self.coordinator:
            self.coordinator.mostrar_info()

    def set_view_buttons_enabled(self, enabled: bool) -> None:
        if self.view_switcher:
            self.view_switcher.set_joined_enabled(enabled)

    def on_datos_disponibles(self, has_data: bool) -> None:
        self.set_view_buttons_enabled(has_data)

    def populate_filter_combo(self, columns: list[str]) -> None:
        if self.filter_toolbar:
            self.filter_toolbar.populate_columns(columns)

    def clear_filters(self) -> None:
        if self.filter_toolbar:
            self.filter_toolbar.clear()

    def get_toolbar(self) -> QToolBar | None:
        return self.tool_bar
