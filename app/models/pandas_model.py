"""
Modelo personalizado para conectar DataFrames de Pandas con QTableView
"""

import pandas as pd
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex


class PandasTableModel(QAbstractTableModel):
    """
    Modelo que adapta un DataFrame de Pandas para QTableView
    """
    
    def __init__(self, df: pd.DataFrame = None):
        super().__init__()
        self.df = df if df is not None else pd.DataFrame()
        
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Retornar número de filas en el DataFrame
        
        Args:
            parent: Índice padre
            
        Returns:
            Número de filas
        """
        if parent.isValid():
            return 0
        return len(self.df)
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Retornar número de columnas en el DataFrame
        
        Args:
            parent: Índice padre
            
        Returns:
            Número de columnas
        """
        if parent.isValid():
            return 0
        return len(self.df.columns)
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        """
        Retornar datos para la celda especificada
        
        Args:
            index: Índice de la celda
            role: Rol de los datos
            
        Returns:
            Valor de la celda o None
        """
        if not index.isValid():
            return None
            
        if role == Qt.DisplayRole:
            row = index.row()
            column = index.column()
            
            # Verificar que el índice está dentro del rango
            if row < len(self.df) and column < len(self.df.columns):
                value = self.df.iloc[row, column]
                # Convertir a string para mostrar
                return str(value) if not pd.isna(value) else ""
            
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        """
        Retornar datos para los encabezados
        
        Args:
            section: Sección del encabezado
            orientation: Orientación (horizontal o vertical)
            role: Rol de los datos
            
        Returns:
            Nombre del encabezado
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                # Retornar nombre de la columna
                if section < len(self.df.columns):
                    return str(self.df.columns[section])
            elif orientation == Qt.Vertical:
                # Retornar índice de la fila
                return str(section + 1)
                
        return None
    
    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        """
        Establecer datos en la celda especificada
        
        Args:
            index: Índice de la celda
            value: Nuevo valor
            role: Rol de los datos
            
        Returns:
            True si se estableció correctamente
        """
        if not index.isValid() or role != Qt.EditRole:
            return False
            
        row = index.row()
        column = index.column()
        
        # Verificar que el índice está dentro del rango
        if row < len(self.df) and column < len(self.df.columns):
            # Actualizar el DataFrame
            self.df.iloc[row, column] = value
            
        # Emitir señal de que los datos han cambiado
        self.dataChanged.emit(index, index, [role])
        return True
    
    def update_data(self, new_df: pd.DataFrame):
        """
        Actualizar los datos del modelo
        
        Args:
            new_df: Nuevo DataFrame
        """
        self.beginResetModel()
        self.df = new_df
        self.endResetModel()