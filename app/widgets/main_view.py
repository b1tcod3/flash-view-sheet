"""
Vista Principal para Flash View Sheet
Muestra botón para cargar archivo, card con resumen e icono de spreadsheet
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                                QLabel, QGroupBox, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from pathlib import Path
from typing import Dict, List, Optional, Any

class MainView(QWidget):
    """
    Vista principal con elementos básicos para cargar datos
    """

    load_file_clicked = Signal()
    reload_with_options = Signal(str, int, dict, bool)
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.current_file: Optional[str] = None
        self.skip_rows: int = 0
        self.column_names: Dict[str, Any] = {}
        self.options_visible: bool = False
        self._original_columns: List[str] = []
        self.setup_ui()
        
    def setup_ui(self) -> None:
        """Configurar la interfaz de la vista principal"""
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Grupo principal
        main_group = QGroupBox("Flash View Sheet - Visor de Datos Tabulares")
        main_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #4a90e2;
                border-radius: 8px;
                padding: 15px;
                margin: 15px;
            }
        """)
        group_layout = QVBoxLayout(main_group)
        
        # Logo de la aplicación
        icon_label = QLabel()
        # Cargar el logo desde assets
        logo_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logo.png"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            # Escalar la imagen manteniendo la proporción - smaller for small screens
            scaled_pixmap = pixmap.scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
        else:
            # Fallback al emoji si el logo no existe
            icon_label.setText("📊")
            icon_label.setStyleSheet("""
                font-size: 64px;
                text-align: center;
            """)
        icon_label.setAlignment(Qt.AlignCenter)
        group_layout.addWidget(icon_label)
        
        # Card con información
        card_frame = QFrame()
        card_frame.setFrameStyle(QFrame.Box)
        card_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f9f9f9;
                padding: 10px;
            }
        """)
        card_layout = QVBoxLayout(card_frame)
        
        self.info_label = QLabel("No hay archivo cargado")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 14px; color: #666;")
        card_layout.addWidget(self.info_label)
        
        group_layout.addWidget(card_frame)
        
        # Botón para cargar archivo
        self.load_button = QPushButton("Cargar Archivo")
        self.load_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        self.load_button.clicked.connect(self.load_file)
        group_layout.addWidget(self.load_button)
        
        # Botón para opciones de carga (inicialmente oculto)
        self.options_button = QPushButton("Opciones de Carga")
        self.options_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.options_button.clicked.connect(self.show_options)
        self.options_button.hide()  # Ocultar inicialmente
        group_layout.addWidget(self.options_button)
        
        main_layout.addWidget(main_group)
        
    def load_file(self) -> None:
        """Emitir señal de intención de carga de archivo."""
        self.load_file_clicked.emit()
            
    def show_options(self) -> None:
        """Mostrar diálogo de opciones de carga"""
        from app.widgets.load_options_dialog import LoadOptionsDialog
        dialog = LoadOptionsDialog(self)

        if self._original_columns:
            dialog.set_columns(self._original_columns)

        if dialog.exec():
            skip_rows, column_names, enable_column_visibility = dialog.get_options()
            # Emitir señal para recargar con las nuevas opciones
            self.reload_with_options.emit(self.current_file, skip_rows, column_names, enable_column_visibility)
            
    def update_info(self) -> None:
        """Actualizar información en la card"""
        if self.current_file:
            filename = Path(self.current_file).name
            self.info_label.setText(f"Archivo cargado: {filename}\n\nHaz clic en 'Vista de Datos' o 'Vista de Gráficos' para explorar.")
            self.show_options_button()
        else:
            self.info_label.setText("No hay archivo cargado")
            self.hide_options_button()
            
    def set_file_info(self, filepath: str) -> None:
        """Establecer información del archivo desde fuera"""
        self.current_file = filepath
        self.update_info()
    
    def set_original_columns(self, columns: List[str]) -> None:
        """Establecer los nombres de columnas de los datos originales"""
        self._original_columns = columns

    def show_options_button(self) -> None:
        """Mostrar el botón de opciones"""
        if not self.options_visible:
            self.options_button.show()
            self.options_visible = True

    def hide_options_button(self) -> None:
        """Ocultar el botón de opciones"""
        if self.options_visible:
            self.options_button.hide()
            self.options_visible = False