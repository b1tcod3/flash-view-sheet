"""
JoinedDataView: Vista especializada para mostrar resultados de cruces de datos
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QGroupBox, QTextEdit, QPushButton, QMessageBox, QFileDialog)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import pandas as pd

from paginacion.data_view import DataView
from core.join.models import JoinResult, JoinMetadata


class JoinedDataView(DataView):
    """
    Vista especializada para mostrar resultados de operaciones de cruce
    Hereda de DataView y añade información específica del join
    """

    # Señales
    new_join_requested = Signal()  # Solicitar nuevo cruce de datos

    def __init__(self, parent=None):
        super().__init__(parent)
        self.join_metadata = None
        self.left_dataset_name = ""
        self.right_dataset_name = ""

        # Añadir sección de metadatos del join
        self.add_join_metadata_section()

    def add_join_metadata_section(self):
        """Añadir sección de metadatos del join al layout principal"""
        # Insertar después del título pero antes de los filtros
        main_layout = self.layout()

        # Crear sección de metadatos
        metadata_group = self.create_join_metadata_section()
        main_layout.insertWidget(0, metadata_group)  # Insertar al inicio

        # Forzar actualización del layout después de insertar
        main_layout.update()
        self.update()

    def create_join_metadata_section(self) -> QGroupBox:
        """Crear sección de metadatos del join"""
        metadata_group = QGroupBox("📊 Metadatos del Cruce")
        metadata_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f8fff9;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #27ae60;
            }
        """)

        layout = QVBoxLayout(metadata_group)

        # Información básica del join
        self.metadata_text = QTextEdit()
        self.metadata_text.setMaximumHeight(150)
        self.metadata_text.setReadOnly(True)
        self.metadata_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 5px;
                font-family: monospace;
                font-size: 10px;
            }
        """)
        layout.addWidget(self.metadata_text)

        # Botones de acción
        buttons_layout = QHBoxLayout()

        self.export_btn = QPushButton("💾 Exportar Resultados")
        self.export_btn.clicked.connect(self.export_results)
        self.export_btn.setEnabled(False)
        buttons_layout.addWidget(self.export_btn)

        self.new_join_btn = QPushButton("🔄 Nuevo Cruce")
        self.new_join_btn.clicked.connect(self.new_join)
        buttons_layout.addWidget(self.new_join_btn)

        self.history_btn = QPushButton("📋 Historial")
        self.history_btn.clicked.connect(self.show_history)
        buttons_layout.addWidget(self.history_btn)

        self.help_btn = QPushButton("❓ Ayuda")
        self.help_btn.clicked.connect(self.show_help)
        buttons_layout.addWidget(self.help_btn)

        layout.addLayout(buttons_layout)

        return metadata_group

    def set_join_result(self, result: JoinResult, left_name: str = "", right_name: str = ""):
        """
        Establecer resultado del join y mostrar metadatos

        Args:
            result: Resultado del join
            left_name: Nombre del dataset izquierdo
            right_name: Nombre del dataset derecho
        """
        self.join_metadata = result.metadata
        self.left_dataset_name = left_name or "Dataset Izquierdo"
        self.right_dataset_name = right_name or "Dataset Derecho"

        # Establecer datos en la vista padre
        super().set_data(result.data)

        # Actualizar metadatos
        self.update_join_metadata_display()

        # Habilitar botón de exportar
        self.export_btn.setEnabled(True)

    def update_join_metadata_display(self):
        """Actualizar display de metadatos del join"""
        if self.join_metadata is None:
            self.metadata_text.setPlainText("No hay información de join disponible")
            return

        metadata = self.join_metadata

        # Formatear información del join
        info_lines = []

        # Tipo de join y datasets
        join_type_names = {
            'inner': 'Inner Join',
            'left': 'Left Join',
            'right': 'Right Join',
            'cross': 'Cross Join'
        }

        info_lines.append(f"Tipo: {join_type_names.get(metadata.join_type.value, metadata.join_type.value)}")
        info_lines.append(f"Datasets: {self.left_dataset_name} + {self.right_dataset_name}")
        info_lines.append(f"Columnas join: {', '.join(metadata.join_keys)}")
        info_lines.append(f"Resultado: {metadata.result_rows:,} filas × {len(self.original_df.columns) if self.original_df is not None else '?'} columnas")
        info_lines.append(f"Tiempo procesamiento: {metadata.processing_time_seconds:.2f} segundos")
        info_lines.append(f"Memoria usada: {metadata.memory_usage_mb:.1f} MB")
        info_lines.append("")

        # Estadísticas detalladas
        info_lines.append("Estadísticas:")
        info_lines.append(f"• Coincidencias: {metadata.matched_rows:,}")
        info_lines.append(f"• Solo izquierdo: {metadata.left_only_rows:,}")
        info_lines.append(f"• Solo derecho: {metadata.right_only_rows:,}")
        info_lines.append(f"• Total original izquierdo: {metadata.left_rows:,}")
        info_lines.append(f"• Total original derecho: {metadata.right_rows:,}")

        # Calcular porcentajes
        if metadata.left_rows > 0:
            left_match_pct = (metadata.matched_rows / metadata.left_rows) * 100
            info_lines.append(f"• Cobertura izquierdo: {left_match_pct:.1f}%")

        if metadata.right_rows > 0:
            right_match_pct = (metadata.matched_rows / metadata.right_rows) * 100
            info_lines.append(f"• Cobertura derecho: {right_match_pct:.1f}%")

        self.metadata_text.setPlainText('\n'.join(info_lines))

    def export_results(self):
        """Exportar resultados del join"""
        if self.original_df is None:
            QMessageBox.warning(self, "Error", "No hay datos para exportar")
            return

        # Crear diálogo de selección de formato
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton

        dialog = QDialog(self)
        dialog.setWindowTitle("Exportar Resultados del Cruce")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        # Selección de formato
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Formato:"))

        format_combo = QComboBox()
        format_combo.addItems(["CSV (.csv)", "Excel (.xlsx)", "PDF (.pdf)", "Imagen (.png)"])
        format_combo.setCurrentText("Excel (.xlsx)")
        format_layout.addWidget(format_combo)
        layout.addLayout(format_layout)

        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        export_btn = QPushButton("Exportar")
        export_btn.clicked.connect(dialog.accept)
        buttons_layout.addWidget(export_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

        if dialog.exec() != QDialog.Accepted:
            return

        # Obtener formato seleccionado
        format_text = format_combo.currentText()

        # Determinar extensión y función de exportación
        if "CSV" in format_text:
            extension = "csv"
            file_filter = "CSV Files (*.csv);;All Files (*)"
        elif "Excel" in format_text:
            extension = "xlsx"
            file_filter = "Excel Files (*.xlsx);;All Files (*)"
        elif "PDF" in format_text:
            extension = "pdf"
            file_filter = "PDF Files (*.pdf);;All Files (*)"
        elif "Imagen" in format_text:
            extension = "png"
            file_filter = "Image Files (*.png *.jpg *.jpeg);;All Files (*)"
        else:
            QMessageBox.warning(self, "Error", "Formato no soportado.")
            return

        # Diálogo para guardar archivo
        import pandas as pd
        default_filename = f"Cruce_Datos_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Resultados del Cruce",
            default_filename,
            file_filter
        )

        if not filepath:
            return

        # Ejecutar exportación
        try:
            from core.data_handler import exportar_a_csv, exportar_a_xlsx, exportar_a_pdf, exportar_a_imagen

            # Obtener la función correcta
            if extension == "csv":
                success = exportar_a_csv(self.original_df, filepath, delimiter=',', encoding='utf-8')
            elif extension == "xlsx":
                success = exportar_a_xlsx(self.original_df, filepath)
            elif extension == "pdf":
                success = exportar_a_pdf(self.original_df, filepath)
            elif extension == "png":
                # Para imagen necesitamos la vista de tabla
                table_view = None
                for child in self.findChildren(QWidget):
                    if hasattr(child, 'model') and hasattr(child.model(), 'rowCount'):
                        table_view = child
                        break
                if table_view:
                    success = exportar_a_imagen(table_view, filepath)
                else:
                    success = False
            else:
                success = False

            if success:
                QMessageBox.information(
                    self,
                    "Exportación Exitosa",
                    f"Resultados del cruce exportados exitosamente a:\n{filepath}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Error de Exportación",
                    "Error al exportar el archivo. Verifique los permisos y el formato."
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error durante la exportación:\n{str(e)}"
            )

    def new_join(self):
        """Iniciar nuevo cruce de datos"""
        # Emitir señal para abrir nuevo diálogo de join
        self.new_join_requested.emit()
        QMessageBox.information(self, "Nuevo Cruce", "Abriendo diálogo para nuevo cruce...")

    def show_history(self):
        """Mostrar historial de joins"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QTextEdit
        from PySide6.QtCore import Qt

        # Obtener historial del main window
        main_window = self.window()
        if not hasattr(main_window, 'join_history'):
            QMessageBox.warning(self, "Error", "Sistema de historial no disponible")
            return

        history_entries = main_window.join_history.get_entries(limit=20)

        if not history_entries:
            QMessageBox.information(self, "Historial", "No hay operaciones de cruce registradas.")
            return

        # Crear diálogo
        dialog = QDialog(self)
        dialog.setWindowTitle("Historial de Operaciones de Cruce")
        dialog.setModal(True)
        dialog.resize(700, 500)

        layout = QVBoxLayout(dialog)

        # Lista de entradas
        list_widget = QListWidget()
        layout.addWidget(list_widget)

        # Detalles de la entrada seleccionada
        details_label = QLabel("Detalles de la operación seleccionada:")
        layout.addWidget(details_label)

        details_text = QTextEdit()
        details_text.setReadOnly(True)
        details_text.setMaximumHeight(150)
        layout.addWidget(details_text)

        # Botones
        buttons_layout = QHBoxLayout()

        export_btn = QPushButton("Exportar Historial")
        export_btn.clicked.connect(lambda: self._export_history(main_window.join_history))
        buttons_layout.addWidget(export_btn)

        clear_btn = QPushButton("Limpiar Historial")
        clear_btn.clicked.connect(lambda: self._clear_history(main_window.join_history, dialog))
        buttons_layout.addWidget(clear_btn)

        buttons_layout.addStretch()

        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dialog.accept)
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

        # Poblar lista
        for entry in history_entries:
            item_text = f"{entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {entry.join_type.value} - {entry.left_dataset_name} + {entry.right_dataset_name}"
            if not entry.success:
                item_text += " (ERROR)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, entry)
            list_widget.addItem(item)

        # Conectar selección
        def on_item_selected():
            current_item = list_widget.currentItem()
            if current_item:
                entry = current_item.data(Qt.UserRole)
                self._show_entry_details(entry, details_text)

        list_widget.itemSelectionChanged.connect(on_item_selected)

        # Seleccionar primera entrada
        if list_widget.count() > 0:
            list_widget.setCurrentRow(0)

        dialog.exec()

    def _show_entry_details(self, entry, details_text):
        """Mostrar detalles de una entrada del historial"""
        details = f"""
Tipo: {entry.config.join_type.value if entry.config else 'N/A'}
Datasets: {entry.left_dataset_name} + {entry.right_dataset_name}
Columnas join: {', '.join(entry.config.left_keys + entry.config.right_keys) if entry.config else 'N/A'}
Resultado: {entry.result_metadata.get('result_rows', 'N/A')} filas
Tiempo: {entry.result_metadata.get('processing_time', 'N/A'):.2f}s
Memoria: {entry.result_metadata.get('memory_usage', 'N/A'):.1f} MB
Éxito: {'Sí' if entry.success else 'No'}
"""
        if entry.error_message:
            details += f"\nError: {entry.error_message}"

        details_text.setPlainText(details.strip())

    def _export_history(self, join_history):
        """Exportar historial a archivo"""
        from PySide6.QtWidgets import QFileDialog
        import pandas as pd

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Historial",
            f"historial_cruce_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json);;All Files (*)"
        )

        if filepath:
            try:
                join_history.export_history(filepath)
                QMessageBox.information(self, "Éxito", f"Historial exportado a {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error exportando historial: {str(e)}")

    def _clear_history(self, join_history, dialog):
        """Limpiar historial"""
        reply = QMessageBox.question(
            self, "Confirmar",
            "¿Está seguro de que desea limpiar todo el historial de operaciones de cruce?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            join_history.clear_history()
            QMessageBox.information(self, "Éxito", "Historial limpiado.")
            dialog.accept()

    def show_help(self):
        """Mostrar ayuda sobre joins"""
        help_text = """
        AYUDA: Vista de Datos Cruzados

        Esta vista muestra los resultados de una operación de cruce (join) entre dos datasets.

        TIPOS DE JOIN:
        • Inner Join: Solo filas con coincidencias en ambas tablas
        • Left Join: Todas las filas del dataset izquierdo + coincidencias del derecho
        • Right Join: Todas las filas del dataset derecho + coincidencias del izquierdo
        • Cross Join: Producto cartesiano de ambas tablas

        METADATOS MOSTRADOS:
        • Información del tipo de join realizado
        • Estadísticas de coincidencias y pérdidas
        • Tiempo y memoria utilizados
        • Cobertura de datos

        FUNCIONALIDADES:
        • Filtrado y búsqueda en resultados
        • Paginación para datasets grandes
        • Exportación de resultados
        • Historial de operaciones

        Para más información, consulte la documentación completa.
        """

        QMessageBox.information(self, "Ayuda - Datos Cruzados", help_text)

    def get_join_info(self) -> dict:
        """
        Obtener información del join actual

        Returns:
            Diccionario con información del join
        """
        if self.join_metadata is None:
            return {}

        return {
            'join_type': self.join_metadata.join_type.value,
            'left_dataset': self.left_dataset_name,
            'right_dataset': self.right_dataset_name,
            'join_keys': self.join_metadata.join_keys,
            'result_rows': self.join_metadata.result_rows,
            'matched_rows': self.join_metadata.matched_rows,
            'processing_time': self.join_metadata.processing_time_seconds,
            'memory_usage': self.join_metadata.memory_usage_mb,
            'timestamp': self.join_metadata.timestamp.isoformat()
        }
