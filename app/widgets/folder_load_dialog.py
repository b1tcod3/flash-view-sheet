"""
Folder Load Dialog
Dialog for configuring folder loading with multiple Excel files
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QGroupBox, QDialogButtonBox,
                               QListWidget, QListWidgetItem, QCheckBox,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QFileDialog, QMessageBox, QSplitter, QFrame)
from PySide6.QtCore import Qt
from typing import List, Dict, Any
import os

from core.loaders.folder_loader import FolderLoader
from core.models.folder_load_config import FolderLoadConfig, ColumnAlignmentStrategy
from .column_alignment_preview import ColumnAlignmentPreview


class FolderLoadDialog(QDialog):
    """
    Dialog for configuring folder loading operations
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cargar Carpeta con Archivos Excel")
        self.resize(800, 600)

        self.folder_loader = None
        self.config = FolderLoadConfig(folder_path="")
        self.file_checkboxes = {}

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout(self)

        # Folder selection section
        folder_group = QGroupBox("Selección de Carpeta")
        folder_layout = QHBoxLayout(folder_group)

        self.folder_path_label = QLabel("Ninguna carpeta seleccionada")
        self.folder_path_label.setStyleSheet("border: 1px solid #ccc; padding: 5px;")

        self.select_folder_btn = QPushButton("Seleccionar Carpeta...")
        self.select_folder_btn.clicked.connect(self.select_folder)

        folder_layout.addWidget(self.folder_path_label)
        folder_layout.addWidget(self.select_folder_btn)

        main_layout.addWidget(folder_group)

        # Splitter for main content
        splitter = QSplitter(Qt.Vertical)

        # File selection section
        file_group = QGroupBox("Archivos Excel Encontrados")
        file_layout = QVBoxLayout(file_group)

        self.file_list = QListWidget()
        file_layout.addWidget(self.file_list)

        splitter.addWidget(file_group)

        # Column alignment preview section
        alignment_group = QGroupBox("Vista Previa de Alineación de Columnas")
        alignment_layout = QVBoxLayout(alignment_group)

        self.alignment_preview = ColumnAlignmentPreview()
        alignment_layout.addWidget(self.alignment_preview)

        splitter.addWidget(alignment_group)

        # Column renaming section
        rename_group = QGroupBox("Renombrar Columnas")
        rename_layout = QVBoxLayout(rename_group)

        self.rename_table = QTableWidget(0, 2)
        self.rename_table.setHorizontalHeaderLabels(["Nombre Actual", "Nuevo Nombre"])
        self.rename_table.horizontalHeader().setStretchLastSection(True)
        rename_layout.addWidget(self.rename_table)

        add_rename_btn = QPushButton("Añadir Renombrado")
        add_rename_btn.clicked.connect(self.add_rename_row)
        rename_layout.addWidget(add_rename_btn)

        splitter.addWidget(rename_group)

        splitter.setSizes([200, 300, 200])
        main_layout.addWidget(splitter)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

    def connect_signals(self):
        """Connect widget signals"""
        # File selection changes should update preview
        for checkbox in self.file_checkboxes.values():
            checkbox.stateChanged.connect(self.update_alignment_preview)

    def select_folder(self):
        """Open folder selection dialog"""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Seleccionar Carpeta", os.getcwd()
        )

        if folder_path:
            self.config.folder_path = folder_path
            self.folder_path_label.setText(folder_path)
            self.scan_folder()

    def scan_folder(self):
        """Scan the selected folder for Excel files"""
        try:
            self.folder_loader = FolderLoader(self.config.folder_path)
            self.update_file_list()
            self.update_alignment_preview()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al escanear carpeta: {str(e)}")

    def update_file_list(self):
        """Update the file list with checkboxes"""
        self.file_list.clear()
        self.file_checkboxes.clear()

        if not self.folder_loader:
            return

        for file_path in self.folder_loader.get_excel_files():
            filename = os.path.basename(file_path)

            # Create list item with checkbox
            item = QListWidgetItem(self.file_list)
            checkbox = QCheckBox(filename)
            checkbox.setChecked(True)  # Default to selected
            checkbox.stateChanged.connect(self.update_alignment_preview)
            self.file_list.setItemWidget(item, checkbox)

            self.file_checkboxes[filename] = checkbox

    def update_alignment_preview(self):
        """Update the column alignment preview"""
        if not self.folder_loader:
            return

        # Get only selected files
        selected_files = []
        for filename, checkbox in self.file_checkboxes.items():
            if checkbox.isChecked():
                # Find the full path for this filename
                for file_path in self.folder_loader.get_excel_files():
                    if os.path.basename(file_path) == filename:
                        selected_files.append(file_path)
                        break

        # Load metadata only for selected files (performance optimization)
        selected_metadata = []
        for file_path in selected_files:
            try:
                meta = self.folder_loader.get_file_metadata(file_path)
                selected_metadata.append(meta)
            except Exception as e:
                # Skip files that can't be read
                print(f"Warning: Could not read metadata for {file_path}: {e}")
                continue

        self.alignment_preview.set_file_metadata(selected_metadata)

    def add_rename_row(self):
        """Add a row to the rename table"""
        row = self.rename_table.rowCount()
        self.rename_table.insertRow(row)
        self.rename_table.setItem(row, 0, QTableWidgetItem(""))
        self.rename_table.setItem(row, 1, QTableWidgetItem(""))

    def get_config(self) -> FolderLoadConfig:
        """Get the configured FolderLoadConfig"""
        # Update included/excluded files
        included = []
        excluded = []

        for filename, checkbox in self.file_checkboxes.items():
            if checkbox.isChecked():
                included.append(filename)
            else:
                excluded.append(filename)

        self.config.included_files = included
        self.config.excluded_files = excluded

        # Update column mappings from rename table
        mappings = {}
        for row in range(self.rename_table.rowCount()):
            current_item = self.rename_table.item(row, 0)
            new_item = self.rename_table.item(row, 1)

            if current_item and new_item:
                current = current_item.text().strip()
                new = new_item.text().strip()
                if current and new:
                    mappings[current] = new

        # Merge with mappings from alignment preview
        preview_mappings = self.alignment_preview.get_column_mappings()
        mappings.update(preview_mappings)

        self.config.column_rename_mapping = mappings

        # Set included columns from preview
        included_columns = self.alignment_preview.get_included_columns()
        if included_columns:
            self.config.included_columns = included_columns

        return self.config