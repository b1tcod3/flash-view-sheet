"""
JoinDialog: Diálogo para configurar operaciones de cruce de datos
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                  QGroupBox, QComboBox, QPushButton, QFormLayout,
                                  QDialogButtonBox, QMessageBox, QWidget, QTextEdit,
                                  QRadioButton, QButtonGroup, QCheckBox, QLineEdit,
                                  QFileDialog, QProgressBar, QTableWidget, QTableWidgetItem,
                                  QHeaderView, QProgressDialog, QTabWidget, QListWidget,
                                  QListWidgetItem, QSplitter, QHBoxLayout)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import pandas as pd
import os

from core.data_handler import cargar_datos
from core.join.models import JoinConfig, JoinType
from core.join.data_join_manager import DataJoinManager
from core.join.exceptions import JoinValidationError, JoinExecutionError


class JoinDialog(QDialog):
    """
    Diálogo modal para configurar operaciones de cruce de datos
    """

    # Señales
    join_completed = Signal(object, str)  # JoinResult, right_file_path
    join_cancelled = Signal()

    def __init__(self, left_df: pd.DataFrame, parent=None):
        super().__init__(parent)
        self.left_df = left_df
        self.right_df = None
        self.right_file_path = None
        self.join_manager = None
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Configurar la interfaz del diálogo"""
        self.setWindowTitle("Configurar Cruce de Datos")
        self.resize(900, 700)
        self.setModal(True)

        main_layout = QVBoxLayout(self)

        # Título
        title_label = QLabel("Configurar Cruce de Datos")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                background-color: #27ae60;
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title_label)

        # Crear widget de pestañas
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Pestaña de configuración
        self.create_configuration_tab()

        # Pestaña de vista previa
        self.create_preview_tab()

    def create_configuration_tab(self):
        """Crear pestaña de configuración"""
        config_widget = QWidget()
        config_layout = QVBoxLayout(config_widget)

        # Dataset izquierdo (pre-cargado)
        self.create_left_dataset_group(config_layout)

        # Dataset derecho
        self.create_right_dataset_group(config_layout)

        # Configuración del join
        self.create_join_config_group(config_layout)

        # Opciones avanzadas
        self.create_advanced_options_group(config_layout)

        self.tab_widget.addTab(config_widget, "⚙️ Configuración")

    def create_preview_tab(self):
        """Crear pestaña de vista previa"""
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)

        # Selección de columnas
        self.create_column_selection_group(preview_layout)

        # Preview
        self.create_preview_group(preview_layout)

        # Botones de acción
        self.create_button_panel(preview_layout)

        self.tab_widget.addTab(preview_widget, "👁️ Vista Previa")

    def create_left_dataset_group(self, layout):
        """Crear grupo para dataset izquierdo"""
        group = QGroupBox("Dataset Izquierdo")
        group_layout = QVBoxLayout(group)

        info = f"📄 Datos principales\n{self.left_df.shape[0]} filas × {self.left_df.shape[1]} columnas"
        info_label = QLabel(info)
        info_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        group_layout.addWidget(info_label)

        layout.addWidget(group)

    def create_right_dataset_group(self, layout):
        """Crear grupo para dataset derecho"""
        group = QGroupBox("Dataset Derecho")
        group_layout = QVBoxLayout(group)

        # Botón para cargar
        load_btn = QPushButton("📁 Cargar Dataset Derecho")
        load_btn.clicked.connect(self.load_right_dataset)
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        group_layout.addWidget(load_btn)

        # Información del dataset derecho
        self.right_info_label = QLabel("No se ha cargado dataset derecho")
        self.right_info_label.setStyleSheet("color: #7f8c8d;")
        group_layout.addWidget(self.right_info_label)

        layout.addWidget(group)

    def create_join_config_group(self, layout):
        """Crear grupo de configuración del join"""
        group = QGroupBox("Configuración del Join")
        group_layout = QVBoxLayout(group)

        # Tipo de join
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Tipo de Join:"))

        self.join_type_group = QButtonGroup(self)
        join_types = [
            ("Inner Join", JoinType.INNER),
            ("Left Join", JoinType.LEFT),
            ("Right Join", JoinType.RIGHT),
            ("Cross Join", JoinType.CROSS)
        ]

        for name, join_type in join_types:
            radio = QRadioButton(name)
            radio.setProperty("join_type", join_type)
            if join_type == JoinType.LEFT:  # Default
                radio.setChecked(True)
            self.join_type_group.addButton(radio)
            type_layout.addWidget(radio)

        type_layout.addStretch()
        group_layout.addLayout(type_layout)

        # Columnas para join
        columns_group = QGroupBox("Columnas para Join")
        columns_layout = QFormLayout(columns_group)

        self.left_key_combo = QComboBox()
        self.left_key_combo.setEnabled(False)
        columns_layout.addRow("Izquierdo:", self.left_key_combo)

        self.right_key_combo = QComboBox()
        self.right_key_combo.setEnabled(False)
        columns_layout.addRow("Derecho:", self.right_key_combo)

        # Botón añadir columna
        add_btn = QPushButton("+ Añadir columna")
        add_btn.clicked.connect(self.add_join_column)
        columns_layout.addRow("", add_btn)

        group_layout.addWidget(columns_group)

        layout.addWidget(group)

    def create_advanced_options_group(self, layout):
        """Crear grupo de opciones avanzadas"""
        group = QGroupBox("Opciones Avanzadas")
        group_layout = QFormLayout(group)

        # Sufijos
        self.left_suffix_edit = QLineEdit("_left")
        self.right_suffix_edit = QLineEdit("_right")
        suffix_layout = QHBoxLayout()
        suffix_layout.addWidget(QLabel("Izquierdo:"))
        suffix_layout.addWidget(self.left_suffix_edit)
        suffix_layout.addWidget(QLabel("Derecho:"))
        suffix_layout.addWidget(self.right_suffix_edit)
        group_layout.addRow("Sufijos:", suffix_layout)

        # Checkboxes
        self.validate_check = QCheckBox("Validar integridad referencial")
        self.validate_check.setChecked(True)
        group_layout.addRow("", self.validate_check)

        self.indicator_check = QCheckBox("Añadir columna indicador (_merge)")
        group_layout.addRow("", self.indicator_check)

        self.sort_check = QCheckBox("Ordenar resultados")
        self.sort_check.setChecked(True)
        group_layout.addRow("", self.sort_check)

        layout.addWidget(group)

    def create_column_selection_group(self, layout):
        """Crear grupo de selección de columnas"""
        group = QGroupBox("Selección de Columnas (Opcional)")
        group_layout = QVBoxLayout(group)

        # Checkbox para habilitar selección de columnas
        self.select_columns_check = QCheckBox("Seleccionar columnas específicas para el resultado")
        self.select_columns_check.setChecked(False)
        self.select_columns_check.stateChanged.connect(self.on_column_selection_changed)
        group_layout.addWidget(self.select_columns_check)

        # Splitter para listas de columnas disponibles y seleccionadas
        splitter = QSplitter()

        # Lista de columnas disponibles
        available_group = QGroupBox("Columnas Disponibles")
        available_layout = QVBoxLayout(available_group)
        self.available_columns_list = QListWidget()
        self.available_columns_list.setSelectionMode(QListWidget.MultiSelection)
        available_layout.addWidget(self.available_columns_list)
        splitter.addWidget(available_group)

        # Botones de control
        buttons_layout = QVBoxLayout()
        buttons_layout.addStretch()

        self.add_column_btn = QPushButton("➡️ Añadir")
        self.add_column_btn.clicked.connect(self.add_selected_columns)
        self.add_column_btn.setEnabled(False)
        buttons_layout.addWidget(self.add_column_btn)

        self.remove_column_btn = QPushButton("⬅️ Quitar")
        self.remove_column_btn.clicked.connect(self.remove_selected_columns)
        self.remove_column_btn.setEnabled(False)
        buttons_layout.addWidget(self.remove_column_btn)

        self.select_all_btn = QPushButton("Seleccionar Todas")
        self.select_all_btn.clicked.connect(self.select_all_columns)
        self.select_all_btn.setEnabled(False)
        buttons_layout.addWidget(self.select_all_btn)

        self.clear_selection_btn = QPushButton("Limpiar Selección")
        self.clear_selection_btn.clicked.connect(self.clear_column_selection)
        self.clear_selection_btn.setEnabled(False)
        buttons_layout.addWidget(self.clear_selection_btn)

        buttons_layout.addStretch()
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        splitter.addWidget(buttons_widget)

        # Lista de columnas seleccionadas
        selected_group = QGroupBox("Columnas Seleccionadas")
        selected_layout = QVBoxLayout(selected_group)
        self.selected_columns_list = QListWidget()
        self.selected_columns_list.setSelectionMode(QListWidget.MultiSelection)
        selected_layout.addWidget(self.selected_columns_list)
        splitter.addWidget(selected_group)

        # Configurar splitter
        splitter.setSizes([200, 100, 200])

        group_layout.addWidget(splitter)

        # Inicialmente deshabilitado
        self.available_columns_list.setEnabled(False)
        self.selected_columns_list.setEnabled(False)

        layout.addWidget(group)

    def create_preview_group(self, layout):
        """Crear grupo de preview"""
        group = QGroupBox("Preview de Resultados")
        group_layout = QVBoxLayout(group)

        # Estadísticas
        self.preview_stats_label = QLabel("Cargue un dataset derecho para ver preview")
        self.preview_stats_label.setStyleSheet("color: #7f8c8d; font-weight: bold;")
        group_layout.addWidget(self.preview_stats_label)

        # Tabla preview - sin límite de altura para ocupar espacio disponible
        self.preview_table = QTableWidget()
        # self.preview_table.setMaximumHeight(200)  # Removido para ocupar espacio completo
        group_layout.addWidget(self.preview_table)

        # Botón actualizar preview
        update_btn = QPushButton("🔄 Actualizar Preview")
        update_btn.clicked.connect(self.update_preview)
        update_btn.setEnabled(False)
        self.update_preview_btn = update_btn
        group_layout.addWidget(update_btn)

        layout.addWidget(group)

    def create_button_panel(self, layout):
        """Crear panel de botones"""
        button_layout = QHBoxLayout()

        self.validate_btn = QPushButton("⚠️ Validar")
        self.validate_btn.clicked.connect(self.validate_config)
        self.validate_btn.setEnabled(False)
        button_layout.addWidget(self.validate_btn)

        button_layout.addStretch()

        self.execute_btn = QPushButton("🚀 Ejecutar Join")
        self.execute_btn.clicked.connect(self.execute_join)
        self.execute_btn.setEnabled(False)
        button_layout.addWidget(self.execute_btn)

        self.cancel_btn = QPushButton("❌ Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

    def setup_connections(self):
        """Configurar conexiones de señales"""
        # Actualizar UI cuando cambie el tipo de join
        self.join_type_group.buttonClicked.connect(self.on_join_type_changed)

        # Actualizar preview cuando cambien configuraciones
        self.left_key_combo.currentTextChanged.connect(self.update_preview)
        self.right_key_combo.currentTextChanged.connect(self.update_preview)

        # Actualizar columnas disponibles cuando se cambie a la pestaña de preview
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

    def load_right_dataset(self):
        """Cargar dataset derecho"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Dataset Derecho",
            "",
            "Archivos de datos (*.csv *.xlsx *.xls *.json *.parquet *.feather *.hdf5 *.sqlite3);;Todos los archivos (*)"
        )

        if file_path:
            try:
                self.right_df = cargar_datos(file_path)
                self.right_file_path = file_path
                self.right_info_label.setText(
                    f"📄 {os.path.basename(file_path)}\n{self.right_df.shape[0]} filas × {self.right_df.shape[1]} columnas"
                )
                self.right_info_label.setStyleSheet("color: #2c3e50; font-weight: bold;")

                # Habilitar configuración
                self.enable_join_config(True)
                self.update_column_combos()

                # Actualizar columnas disponibles si la selección está habilitada
                if self.select_columns_check.isChecked():
                    self.update_available_columns()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error cargando archivo: {str(e)}")

    def enable_join_config(self, enabled: bool):
        """Habilitar/deshabilitar configuración del join"""
        self.left_key_combo.setEnabled(enabled)
        self.right_key_combo.setEnabled(enabled)
        self.validate_btn.setEnabled(enabled)
        self.execute_btn.setEnabled(enabled)
        self.update_preview_btn.setEnabled(enabled)

    def update_column_combos(self):
        """Actualizar combos de columnas y sugerir matches automáticos"""
        if self.right_df is not None:
            # Columnas del izquierdo
            left_columns = self.left_df.columns.tolist()
            self.left_key_combo.clear()
            self.left_key_combo.addItems(left_columns)

            # Columnas del derecho
            right_columns = self.right_df.columns.tolist()
            self.right_key_combo.clear()
            self.right_key_combo.addItems(right_columns)

            # Buscar columnas con nombres similares para sugerir automáticamente
            self._suggest_matching_columns(left_columns, right_columns)

    def _suggest_matching_columns(self, left_columns, right_columns):
        """Sugerir automáticamente columnas que podrían hacer match"""
        # Buscar columnas con el mismo nombre (case insensitive)
        suggested_left = None
        suggested_right = None

        for left_col in left_columns:
            for right_col in right_columns:
                if left_col.lower() == right_col.lower():
                    suggested_left = left_col
                    suggested_right = right_col
                    break
            if suggested_left:
                break

        # Si no hay match exacto, buscar columnas con "id" o "key"
        if not suggested_left:
            id_columns_left = [col for col in left_columns if 'id' in col.lower() or 'key' in col.lower()]
            id_columns_right = [col for col in right_columns if 'id' in col.lower() or 'key' in col.lower()]

            if id_columns_left and id_columns_right:
                suggested_left = id_columns_left[0]
                suggested_right = id_columns_right[0]

        # Seleccionar las columnas sugeridas
        if suggested_left and suggested_right:
            self.left_key_combo.setCurrentText(suggested_left)
            self.right_key_combo.setCurrentText(suggested_right)

    def on_join_type_changed(self, button):
        """Manejar cambio de tipo de join"""
        join_type = button.property("join_type")

        # Para cross join, deshabilitar selección de columnas
        if join_type == JoinType.CROSS:
            self.left_key_combo.setEnabled(False)
            self.right_key_combo.setEnabled(False)
        else:
            self.left_key_combo.setEnabled(True)
            self.right_key_combo.setEnabled(True)

        self.update_preview()

    def on_column_selection_changed(self, state):
        """Manejar cambio en selección de columnas"""
        enabled = state == 2  # Qt.CheckState.Checked

        self.available_columns_list.setEnabled(enabled)
        self.selected_columns_list.setEnabled(enabled)
        self.add_column_btn.setEnabled(enabled)
        self.remove_column_btn.setEnabled(enabled)
        self.select_all_btn.setEnabled(enabled)
        self.clear_selection_btn.setEnabled(enabled)

        if enabled:
            self.update_available_columns()
        else:
            self.available_columns_list.clear()
            self.selected_columns_list.clear()

        self.update_preview()

    def on_tab_changed(self, index):
        """Manejar cambio de pestaña"""
        # Si se cambia a la pestaña de preview (índice 1) y hay dataset derecho cargado
        if index == 1 and self.right_df is not None and self.select_columns_check.isChecked():
            self.update_available_columns()

    def update_available_columns(self):
        """Actualizar lista de columnas disponibles"""
        if self.right_df is None:
            return

        # Obtener configuración actual para determinar columnas disponibles
        config = self.get_config()
        if not config:
            return

        # Crear manager temporal para obtener columnas del resultado
        manager = DataJoinManager(self.left_df, self.right_df)
        try:
            # Obtener preview para ver qué columnas estarán disponibles
            preview_df = manager.get_join_preview(config, max_rows=1)
            available_columns = preview_df.columns.tolist()
        except:
            # Si no se puede obtener preview, usar todas las columnas de ambos datasets
            available_columns = list(self.left_df.columns) + list(self.right_df.columns)

        # Limpiar y llenar lista
        self.available_columns_list.clear()
        for col in sorted(available_columns):
            item = QListWidgetItem(col)
            self.available_columns_list.addItem(item)

    def add_selected_columns(self):
        """Añadir columnas seleccionadas a la lista de seleccionadas"""
        selected_items = self.available_columns_list.selectedItems()
        for item in selected_items:
            # Verificar si ya está en la lista seleccionada
            existing_items = [self.selected_columns_list.item(i).text()
                            for i in range(self.selected_columns_list.count())]
            if item.text() not in existing_items:
                new_item = QListWidgetItem(item.text())
                self.selected_columns_list.addItem(new_item)

        self.update_preview()

    def remove_selected_columns(self):
        """Quitar columnas seleccionadas de la lista de seleccionadas"""
        selected_items = self.selected_columns_list.selectedItems()
        for item in selected_items:
            row = self.selected_columns_list.row(item)
            self.selected_columns_list.takeItem(row)

        self.update_preview()

    def select_all_columns(self):
        """Seleccionar todas las columnas disponibles"""
        self.selected_columns_list.clear()
        for i in range(self.available_columns_list.count()):
            item = self.available_columns_list.item(i)
            new_item = QListWidgetItem(item.text())
            self.selected_columns_list.addItem(new_item)

        self.update_preview()

    def clear_column_selection(self):
        """Limpiar selección de columnas"""
        self.selected_columns_list.clear()
        self.update_preview()

    def add_join_column(self):
        """Añadir columna adicional para join múltiple"""
        # TODO: Implementar joins múltiples
        QMessageBox.information(self, "Información", "Joins múltiples no implementados aún")

    def update_preview(self):
        """Actualizar preview de resultados"""
        if self.right_df is None:
            return

        try:
            config = self.get_config()
            if not config:
                return

            # Crear manager temporal para preview
            manager = DataJoinManager(self.left_df, self.right_df)
            preview_df = manager.get_join_preview(config, max_rows=10)

            # Actualizar estadísticas
            estimated_rows = len(preview_df)
            estimated_cols = len(preview_df.columns)
            self.preview_stats_label.setText(
                f"Estimación: {estimated_rows} filas × {estimated_cols} columnas"
            )

            # Actualizar tabla
            self.update_preview_table(preview_df)

        except Exception as e:
            self.preview_stats_label.setText(f"Error en preview: {str(e)}")
            self.preview_table.setRowCount(0)
            self.preview_table.setColumnCount(0)

    def update_preview_table(self, df: pd.DataFrame):
        """Actualizar tabla de preview"""
        if df.empty:
            self.preview_table.setRowCount(0)
            self.preview_table.setColumnCount(0)
            return

        self.preview_table.setRowCount(min(len(df), 10))
        self.preview_table.setColumnCount(len(df.columns))
        self.preview_table.setHorizontalHeaderLabels(df.columns.tolist())

        for row in range(min(len(df), 10)):
            for col in range(len(df.columns)):
                value = str(df.iloc[row, col])
                item = QTableWidgetItem(value)
                self.preview_table.setItem(row, col, item)

        self.preview_table.resizeColumnsToContents()

    def get_config(self) -> JoinConfig:
        """Obtener configuración actual"""
        if self.right_df is None:
            return None

        # Tipo de join
        selected_button = self.join_type_group.checkedButton()
        if not selected_button:
            return None
        join_type = selected_button.property("join_type")

        # Columnas de join
        left_keys = [self.left_key_combo.currentText()] if self.left_key_combo.currentText() else []
        right_keys = [self.right_key_combo.currentText()] if self.right_key_combo.currentText() else []

        # Para cross join, no se necesitan keys
        if join_type == JoinType.CROSS:
            left_keys = []
            right_keys = []

        # Columnas a incluir
        include_columns = []
        if self.select_columns_check.isChecked():
            include_columns = [self.selected_columns_list.item(i).text()
                             for i in range(self.selected_columns_list.count())]

        return JoinConfig(
            left_keys=left_keys,
            right_keys=right_keys,
            join_type=join_type,
            suffixes=(self.left_suffix_edit.text(), self.right_suffix_edit.text()),
            validate_integrity=self.validate_check.isChecked(),
            sort_results=self.sort_check.isChecked(),
            indicator=self.indicator_check.isChecked(),
            include_columns=include_columns
        )

    def validate_config(self):
        """Validar configuración"""
        if self.right_df is None:
            QMessageBox.warning(self, "Error", "Debe cargar un dataset derecho primero")
            return

        config = self.get_config()
        if not config:
            QMessageBox.warning(self, "Error", "Configuración incompleta")
            return

        try:
            manager = DataJoinManager(self.left_df, self.right_df)
            validation = manager.validate_join(config)

            if validation.is_valid:
                QMessageBox.information(self, "Validación Exitosa",
                                      "La configuración es válida")
            else:
                errors_text = "\n".join(validation.errors)
                warnings_text = "\n".join(validation.warnings) if validation.warnings else ""

                message = f"Errores:\n{errors_text}"
                if warnings_text:
                    message += f"\n\nAdvertencias:\n{warnings_text}"

                QMessageBox.warning(self, "Errores de Validación", message)

        except JoinValidationError as e:
            QMessageBox.critical(self, "Error de Validación", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error inesperado: {str(e)}")

    def execute_join(self):
        """Ejecutar el join"""
        if self.right_df is None:
            QMessageBox.warning(self, "Error", "Debe cargar un dataset derecho primero")
            return

        config = self.get_config()
        if not config:
            QMessageBox.warning(self, "Error", "Configuración incompleta")
            return

        # Estimar si la operación será larga
        estimated_time = self._estimate_operation_time(config)
        show_progress = estimated_time > 2.0  # Mostrar progreso si > 2 segundos

        progress_dialog = None
        if show_progress:
            progress_dialog = QProgressDialog(
                "Ejecutando operación de cruce...",
                "Cancelar",
                0, 100, self
            )
            progress_dialog.setWindowModality(2)  # ApplicationModal
            progress_dialog.setAutoClose(True)
            progress_dialog.setAutoReset(True)
            progress_dialog.setValue(10)  # Iniciar con 10%

        try:
            # Deshabilitar botón
            self.execute_btn.setEnabled(False)
            self.execute_btn.setText("Procesando...")

            manager = DataJoinManager(self.left_df, self.right_df)

            if progress_dialog:
                progress_dialog.setValue(30)
                progress_dialog.setLabelText("Validando configuración...")

            # Verificar validación antes de ejecutar
            validation = manager.validate_join(config)
            if validation.warnings:
                warning_msg = "Advertencias detectadas:\n" + "\n".join(validation.warnings)
                warning_msg += "\n\n¿Desea continuar de todos modos?"
                reply = QMessageBox.question(self, "Advertencias de Configuración",
                                           warning_msg, QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No:
                    self.execute_btn.setEnabled(True)
                    self.execute_btn.setText("🚀 Ejecutar Join")
                    if progress_dialog:
                        progress_dialog.cancel()
                    return

            result = manager.execute_join(config)

            if progress_dialog:
                progress_dialog.setValue(90)
                progress_dialog.setLabelText("Finalizando...")

            if result.success:
                if progress_dialog:
                    progress_dialog.setValue(100)

                self.join_completed.emit(result, self.right_file_path)
                QMessageBox.information(self, "Éxito",
                                      f"Join completado exitosamente\n"
                                      f"Resultado: {result.metadata.result_rows} filas × {len(result.data.columns)} columnas\n"
                                      f"Tiempo: {result.metadata.processing_time_seconds:.2f} segundos")
                self.accept()
            else:
                if progress_dialog:
                    progress_dialog.cancel()
                QMessageBox.critical(self, "Error", result.error_message)

        except JoinExecutionError as e:
            if progress_dialog:
                progress_dialog.cancel()
            QMessageBox.critical(self, "Error de Ejecución", str(e))
        except Exception as e:
            if progress_dialog:
                progress_dialog.cancel()
            QMessageBox.critical(self, "Error", f"Error inesperado: {str(e)}")
        finally:
            self.execute_btn.setEnabled(True)
            self.execute_btn.setText("🚀 Ejecutar Join")
            if progress_dialog:
                progress_dialog.close()

    def _estimate_operation_time(self, config: JoinConfig) -> float:
        """
        Estimar tiempo de ejecución de la operación

        Args:
            config: Configuración del join

        Returns:
            Tiempo estimado en segundos
        """
        if self.right_df is None:
            return 0.0

        left_rows = len(self.left_df)
        right_rows = len(self.right_df)

        # Factores base por tipo de join
        if config.join_type == JoinType.CROSS:
            # Cross join: tiempo proporcional al producto
            base_time = (left_rows * right_rows) / 1000000  # ~1 segundo por millón de operaciones
        elif config.join_type == JoinType.INNER:
            # Inner join: más rápido, depende del tamaño del resultado
            base_time = min(left_rows, right_rows) / 50000
        else:
            # Left/Right join: tiempo moderado
            base_time = left_rows / 30000

        # Factor adicional por validación de integridad
        if config.validate_integrity:
            base_time *= 1.2

        # Factor adicional por ordenamiento
        if config.sort_results:
            base_time *= 1.1

        # Mínimo 0.5 segundos, máximo 30 segundos para estimación
        return max(0.5, min(base_time, 30.0))

    def reject(self):
        """Cancelar operación"""
        self.join_cancelled.emit()
        super().reject()