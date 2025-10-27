"""
Panel de información y estadísticas para Flash View Sheet
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QGroupBox, QScrollArea, QFrame)
from PySide6.QtCore import Qt
import pandas as pd
from typing import Dict, Any


class InfoPanel(QWidget):
    """
    Widget para mostrar información y estadísticas del DataFrame
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.df = None
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar la interfaz del panel de información"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Grupo: Información General
        general_group = QGroupBox("Información General")
        general_layout = QVBoxLayout(general_group)
        
        # Información básica
        self.lbl_filas = QLabel("Filas: -")
        self.lbl_columnas = QLabel("Columnas: -")
        
        general_layout.addWidget(self.lbl_filas)
        general_layout.addWidget(self.lbl_columnas)
        
        # Grupo: Columnas
        columns_group = QGroupBox("Columnas")
        columns_layout = QVBoxLayout(columns_group)
        
        # Área de scroll para columnas
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.columns_layout = QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        columns_layout.addWidget(scroll_area)
        
        # Grupo: Estadísticas
        stats_group = QGroupBox("Estadísticas Descriptivas")
        stats_layout = QVBoxLayout(stats_group)
        
        # Área de scroll para estadísticas
        self.stats_scroll = QScrollArea()
        self.stats_scroll.setWidgetResizable(True)
        self.stats_widget = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_widget)
        self.stats_scroll.setWidget(self.stats_widget)
        stats_layout.addWidget(self.stats_scroll)
        
        # Añadir todos los grupos al layout principal
        main_layout.addWidget(general_group)
        main_layout.addWidget(columns_group)
        main_layout.addWidget(stats_group)
        
    def update_info(self, df: pd.DataFrame):
        """
        Actualizar la información mostrada con nuevos datos
        
        Args:
            df: DataFrame de Pandas
        """
        self.df = df
        
        # Actualizar información general
        self.lbl_filas.setText(f"Filas: {df.shape[0]}")
        self.lbl_columnas.setText(f"Columnas: {df.shape[1]}")
        
        # Limpiar layout de columnas
        for i in reversed(range(self.columns_layout.count())):
            widget = self.columns_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
                
        # Mostrar información de columnas
        for col_name in df.columns:
            col_type = str(df.dtypes[col_name])
            col_info = QLabel(f"{col_name} ({col_type})")
            self.columns_layout.addWidget(col_info)
        
        # Actualizar estadísticas
        self.update_statistics(df)
        
    def update_statistics(self, df: pd.DataFrame):
        """
        Actualizar las estadísticas mostradas
        
        Args:
            df: DataFrame de Pandas
        """
        # Limpiar layout de estadísticas
        for i in reversed(range(self.stats_layout.count())):
                widget = self.stats_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()
                
        try:
            # Obtener estadísticas descriptivas
            stats = df.describe(include='all')
            
            # Mostrar estadísticas para cada columna numérica
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            for col in numeric_cols:
                col_stats = stats[col] if col in stats.columns else None
                
                if col_stats is not None:
                    # Crear grupo para cada columna numérica
                    col_group = QGroupBox(f"Estadísticas - {col}")
                    col_layout = QVBoxLayout(col_group)
                    
                    # Mostrar estadísticas básicas
                    stats_info = [
                        f"Conteo: {col_stats.get('count', 'N/A')}",
                        f"Media: {col_stats.get('mean', 'N/A')}",
                        f"Desviación Estándar: {col_stats.get('std', 'N/A')}",
                        f"Mínimo: {col_stats.get('min', 'N/A')}",
                        f"25%: {col_stats.get('25%', 'N/A')}",
                        f"50% (Mediana): {col_stats.get('50%', 'N/A')}",
                        f"75%: {col_stats.get('75%', 'N/A')}",
                        f"Máximo: {col_stats.get('max', 'N/A')}",
                    ]
                    
                    for stat_text in stats_info:
                        stat_label = QLabel(stat_text)
                        col_layout.addWidget(stat_label)
                        
                    self.stats_layout.addWidget(col_group)
                    
        except Exception as e:
            # Mostrar mensaje de error
            error_label = QLabel(f"Error al calcular estadísticas: {str(e)}")
            self.stats_layout.addWidget(error_label)