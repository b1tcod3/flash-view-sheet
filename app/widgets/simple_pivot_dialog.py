#!/usr/bin/env python3
"""
Diálogo Simplificado para Tabla Pivote Simple
Interfaz básica para pivote simple con selección individual de columnas
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QGroupBox, QComboBox, QPushButton, QFormLayout,
                               QDialogButtonBox, QMessageBox, QWidget, QTextEdit)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import pandas as pd


class SimplePivotDialog(QDialog):
    """
    Diálogo simplificado para tabla pivote simple
    Una sola columna para cada parámetro
    """
    
    def __init__(self, df_original=None, parent=None):
        super().__init__(parent)
        self.df_original = df_original
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Configurar la interfaz del diálogo"""
        self.setWindowTitle("Tabla Pivote Simple")
        self.resize(600, 400)
        self.setModal(True)
        
        main_layout = QVBoxLayout(self)
        
        # Título del diálogo
        title_label = QLabel("Configuración de Tabla Pivote Simple")
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
        
        # Crear grupos de configuración
        self.create_basic_config_group(main_layout)
        self.create_aggregation_config_group(main_layout)
        self.create_dataset_info_group(main_layout)
        
        # Panel de botones
        self.create_button_panel(main_layout)
        
    def create_basic_config_group(self, main_layout):
        """Crear grupo de configuración básica"""
        config_group = QGroupBox("Configuración Básica")
        config_layout = QFormLayout(config_group)
        
        # Selección de columna para índices (filas)
        self.index_combo = QComboBox()
        self.index_combo.setPlaceholderText("Seleccionar columna para las filas...")
        config_layout.addRow("Columna para Filas (Índice):", self.index_combo)
        
        # Selección de columna para columnas del pivote
        self.columns_combo = QComboBox()
        self.columns_combo.setPlaceholderText("Opcional: Seleccionar columna para las columnas del pivote...")
        self.columns_combo.addItem("")  # Opción vacía
        config_layout.addRow("Columna para Columnas (Opcional):", self.columns_combo)
        
        # Selección de columna para valores
        self.values_combo = QComboBox()
        self.values_combo.setPlaceholderText("Seleccionar columna con los valores a agregar...")
        config_layout.addRow("Columna con Valores:", self.values_combo)
        
        main_layout.addWidget(config_group)
        
    def create_aggregation_config_group(self, main_layout):
        """Crear grupo de configuración de agregación"""
        agg_group = QGroupBox("Función de Agregación")
        agg_layout = QFormLayout(agg_group)
        
        # Selección de función de agregación
        self.agg_func_combo = QComboBox()
        self.agg_func_combo.addItems([
            "sum - Suma",
            "mean - Promedio", 
            "count - Conteo",
            "nunique - Conteo Único",
            "min - Mínimo",
            "max - Máximo",
            "median - Mediana",
            "std - Desviación estándar",
            "var - Varianza"
        ])
        agg_layout.addRow("Función de Agregación:", self.agg_func_combo)
        
        main_layout.addWidget(agg_group)
        
    def create_dataset_info_group(self, main_layout):
        """Crear grupo de información del dataset"""
        info_group = QGroupBox("Información del Dataset")
        info_layout = QVBoxLayout(info_group)
        
        self.dataset_info_text = QTextEdit()
        self.dataset_info_text.setMaximumHeight(100)
        self.dataset_info_text.setReadOnly(True)
        info_layout.addWidget(self.dataset_info_text)
        
        main_layout.addWidget(info_group)
        
    def create_button_panel(self, main_layout):
        """Crear panel de botones del diálogo"""
        button_layout = QHBoxLayout()
        
        # Botón Vista Previa
        preview_btn = QPushButton("Vista Previa")
        preview_btn.clicked.connect(self.show_preview)
        preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        button_layout.addWidget(preview_btn)
        
        button_layout.addStretch()
        
        # Botones estándar del diálogo
        self.dialog_buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        
        self.dialog_buttons.accepted.connect(self.accept_configuration)
        self.dialog_buttons.rejected.connect(self.reject)
        
        button_layout.addWidget(self.dialog_buttons)
        main_layout.addLayout(button_layout)
        
    def setup_connections(self):
        """Configurar conexiones de señales"""
        # Actualizar preview cuando cambien las selecciones
        combos_to_watch = [self.index_combo, self.columns_combo, self.values_combo, self.agg_func_combo]
        
        for combo in combos_to_watch:
            combo.currentTextChanged.connect(self.update_preview)
            
    def set_data(self, df):
        """Establecer datos para configurar"""
        self.df_original = df
        
        if df is not None:
            # Poblar combos con nombres de columnas
            columns = df.columns.tolist()
            
            # Llenar combos (excluir la columna actual de cada uno)
            self.index_combo.clear()
            self.index_combo.addItems(columns)
            
            self.columns_combo.clear()
            self.columns_combo.addItem("")  # Opción vacía para pivot opcional
            self.columns_combo.addItems(columns)
            
            self.values_combo.clear()
            self.values_combo.addItems(columns)
            
            # Actualizar información del dataset
            self.update_dataset_info()
            
    def update_dataset_info(self):
        """Actualizar información del dataset"""
        if self.df_original is not None:
            info_text = f"""Dataset: {self.df_original.shape[0]} filas, {self.df_original.shape[1]} columnas

Columnas disponibles: {', '.join(self.df_original.columns.tolist())}

Tip: Para un pivote simple, selecciona una columna para las filas, una para las columnas del pivote, y una con valores numéricos para agregar."""
            self.dataset_info_text.setPlainText(info_text)
            
    def update_preview(self):
        """Actualizar vista previa de configuración"""
        index_col = self.index_combo.currentText()
        columns_col = self.columns_combo.currentText()
        values_col = self.values_combo.currentText()
        agg_func = self.agg_func_combo.currentText()
        
        preview_text = f"""CONFIGURACIÓN ACTUAL - PIVOTE SIMPLE
{'=' * 40}

Columna para Filas: {index_col or 'No seleccionada'}
Columna para Columnas: {columns_col or 'No seleccionada'}
Columna con Valores: {values_col or 'No seleccionada'}
Función de Agregación: {agg_func or 'No seleccionada'}

{'✅ Configuración completa' if all([index_col, columns_col, values_col, agg_func]) else '⚠️ Complete todos los campos'}

FILAS RESULTADO: El pivote creará una tabla con las filas basadas en '{index_col or '???'}' y las columnas basadas en '{columns_col or '???'}'."""
        
        # Actualizar información en el panel
        if hasattr(self, 'dataset_info_text'):
            current_info = self.dataset_info_text.toPlainText()
            if "CONFIGURACIÓN ACTUAL" in current_info:
                # Remover preview anterior
                lines = current_info.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith("CONFIGURACIÓN ACTUAL"):
                        current_info = '\n'.join(lines[:i])
                        break
            
            self.dataset_info_text.setPlainText(current_info + "\n\n" + preview_text)
            
    def show_preview(self):
        """Mostrar vista previa detallada"""
        config = self.get_config()
        
        preview_text = f"""VISTA PREVIA DE CONFIGURACIÓN
{'=' * 30}

TIPO: Tabla Pivote Simple

CONFIGURACIÓN:
• Columna para Filas: {config.get('index', 'No seleccionada')}
• Columna para Columnas: {config.get('columns', 'No seleccionada')}
• Columna con Valores: {config.get('values', 'No seleccionada')}
• Función de Agregación: {config.get('aggfunc', 'No seleccionada')}

RESULTADO ESPERADO:
La tabla resultante tendrá como filas los valores únicos de '{config.get('index', '??')}' y como columnas los valores únicos de '{config.get('columns', '??')}'. Cada celda mostrará la {config.get('aggfunc', 'función')} de '{config.get('values', '??')}' para esa combinación.
"""
        
        QMessageBox.information(self, "Vista Previa", preview_text)
        
    def get_config(self):
        """Obtener configuración actual"""
        config = {
            'index': self.index_combo.currentText() if self.index_combo.currentText() else None,
            'columns': self.columns_combo.currentText() if self.columns_combo.currentText() else None,
            'values': self.values_combo.currentText() if self.values_combo.currentText() else None,
            'aggfunc': self.agg_func_combo.currentText().split(' - ')[0] if self.agg_func_combo.currentText() else None,
            'is_pivot': bool(self.columns_combo.currentText())  # True si hay columna para pivot, False si es agregación simple
        }
        
        return config
        
    def validate_configuration(self):
        """Validar que la configuración esté completa"""
        config = self.get_config()
        
        missing_fields = []
        if not config.get('index'):
            missing_fields.append('Columna para Filas')
        # Columna para Columnas es OPCIONAL - solo validar si se seleccionó una
        if not config.get('values'):
            missing_fields.append('Columna con Valores')
        if not config.get('aggfunc'):
            missing_fields.append('Función de Agregación')
            
        return missing_fields
        
    def accept_configuration(self):
        """Aceptar configuración y cerrar"""
        # Validar configuración
        missing_fields = self.validate_configuration()
        
        if missing_fields:
            missing_text = "\n".join([f"• {field}" for field in missing_fields])
            QMessageBox.warning(
                self, 
                "Configuración Incompleta", 
                f"Por favor complete los siguientes campos:\n\n{missing_text}"
            )
            return
            
        # Validar que las columnas sean diferentes (solo para columnas no vacías)
        config = self.get_config()
        selected_columns = [config['index'], config['values']]
        
        # Solo agregar la columna de columnas si no está vacía
        if config['columns']:
            selected_columns.append(config['columns'])
        
        if len(set(selected_columns)) != len(selected_columns):
            QMessageBox.warning(
                self,
                "Columnas Duplicadas",
                "Las columnas seleccionadas deben ser diferentes entre sí."
            )
            return
            
        # Validar tipos de datos según la función de agregación
        if self.df_original is not None and config['values']:
            if config['values'] in self.df_original.columns:
                # Solo validar numérica para funciones que la requieren
                numeric_required_funcs = ['sum', 'mean', 'min', 'max', 'median', 'std', 'var']
                if config['aggfunc'] in numeric_required_funcs:
                    if not pd.api.types.is_numeric_dtype(self.df_original[config['values']]):
                        QMessageBox.warning(
                            self,
                            "Columna No Numérica",
                            f"La columna '{config['values']}' no contiene valores numéricos.\n\n"
                            f"Para la función '{config['aggfunc']}' se requiere una columna numérica.\n"
                            f"Seleccione una columna numérica o cambie la función de agregación."
                        )
                        return
                # Para funciones como 'count' y 'nunique', verificar que la columna tenga datos
                elif config['aggfunc'] in ['count', 'nunique']:
                    if self.df_original[config['values']].empty:
                        QMessageBox.warning(
                            self,
                            "Columna Vacía",
                            f"La columna '{config['values']}' está vacía.\n"
                            f"Seleccione una columna con datos para contar."
                        )
                        return
        
        # Todo validado, aceptar
        self.accept()
        
    def get_configuration(self):
        """Obtener configuración final (alias para compatibilidad)"""
        return self.get_config()