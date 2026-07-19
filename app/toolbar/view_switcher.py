"""
View Switcher for Flash View Sheet.

This module provides the view switching buttons widget.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFrame, QApplication, QStyle
from PySide6.QtCore import Signal, Qt, QSize


def _make_vline() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.VLine)  # type: ignore[attr-defined]
    line.setStyleSheet("background-color: #c0c2c4; max-width: 1px; border: none;")
    line.setFixedWidth(4)
    return line


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

    view_main = Signal()
    view_data = Signal()
    view_info = Signal()
    view_graphics = Signal()
    view_joined = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.view_main_btn: QPushButton
        self.view_data_btn: QPushButton
        self.view_info_btn: QPushButton
        self.view_graphics_btn: QPushButton
        self.view_joined_btn: QPushButton

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        self._layout = QHBoxLayout(self)
        self._layout.setSpacing(2)
        self._layout.setContentsMargins(0, 0, 0, 0)

        style = QApplication.style()
        icon_size = QSize(20, 20)

        self.view_main_btn = self._make_button(
            style.standardIcon(QStyle.SP_DirHomeIcon),  # type: ignore[attr-defined]
            "Vista Principal",
            icon_size
        )
        self._layout.addWidget(self.view_main_btn)

        self._layout.addWidget(_make_vline())

        self.view_data_btn = self._make_button(
            style.standardIcon(QStyle.SP_FileDialogContentsView),  # type: ignore[attr-defined]
            "Vista de Datos",
            icon_size
        )
        self._layout.addWidget(self.view_data_btn)

        self._layout.addWidget(_make_vline())

        self.view_graphics_btn = self._make_button(
            style.standardIcon(QStyle.SP_ComputerIcon),  # type: ignore[attr-defined]
            "Vista Gráficos",
            icon_size
        )
        self._layout.addWidget(self.view_graphics_btn)

        self.view_joined_btn = self._make_button(
            style.standardIcon(QStyle.SP_DriveNetIcon),  # type: ignore[attr-defined]
            "Cruzar Datos",
            icon_size
        )
        self.view_joined_btn.setEnabled(False)
        self._layout.addWidget(self.view_joined_btn)

        self._layout.addWidget(_make_vline())

        self.view_info_btn = self._make_button(
            style.standardIcon(QStyle.SP_MessageBoxInformation),  # type: ignore[attr-defined]
            "Ver Información del dataset",
            icon_size
        )
        self._layout.addWidget(self.view_info_btn)

    def _make_button(self, icon, tooltip: str, icon_size: QSize) -> QPushButton:  # type: ignore[no-untyped-def]
        btn = QPushButton()
        btn.setIcon(icon)
        btn.setIconSize(icon_size)
        btn.setToolTip(tooltip)
        btn.setFlat(True)
        btn.setFixedSize(30, 28)
        btn.setStyleSheet("""
            QPushButton {
                border: 1px solid transparent;
                border-radius: 2px;
                background: transparent;
            }
            QPushButton:hover {
                background-color: #e0e4e8;
                border-color: #b0b4b8;
            }
            QPushButton:pressed {
                background-color: #cdd2d6;
            }
            QPushButton:disabled {
                border: 1px solid transparent;
            }
        """)
        return btn

    def _connect_signals(self) -> None:
        self.view_main_btn.clicked.connect(self.view_main.emit)
        self.view_data_btn.clicked.connect(self.view_data.emit)
        self.view_info_btn.clicked.connect(self.view_info.emit)
        self.view_graphics_btn.clicked.connect(self.view_graphics.emit)
        self.view_joined_btn.clicked.connect(self.view_joined.emit)

    def set_joined_enabled(self, enabled: bool) -> None:
        self.view_joined_btn.setEnabled(enabled)

    def set_main_enabled(self, enabled: bool) -> None:
        self.view_main_btn.setEnabled(enabled)

    def set_data_enabled(self, enabled: bool) -> None:
        self.view_data_btn.setEnabled(enabled)

    def set_info_enabled(self, enabled: bool) -> None:
        self.view_info_btn.setEnabled(enabled)

    def set_graphics_enabled(self, enabled: bool) -> None:
        self.view_graphics_btn.setEnabled(enabled)
