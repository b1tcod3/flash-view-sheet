"""
PaginationManager - Gestor de paginación para DataView
Maneja la lógica de paginación independiente de la interfaz de usuario
"""

import pandas as pd
from PySide6.QtCore import QObject, Signal


class PaginationManager(QObject):
    """
    Gestor de paginación que maneja datos divididos en páginas
    Proporciona una interfaz para navegar entre páginas y gestionar el tamaño de página
    """
    
    # Señales para notificar cambios
    page_changed = Signal(int)  # Página actual cambió
    page_size_changed = Signal(int)  # Tamaño de página cambió
    data_changed = Signal()  # Datos subyacentes cambiaron
    total_pages_changed = Signal(int)  # Número total de páginas cambió
    
    def __init__(self, df: pd.DataFrame = None, page_size: int = 10):
        """
        Inicializar el gestor de paginación
        
        Args:
            df: DataFrame con datos a paginar
            page_size: Número de filas por página
        """
        super().__init__()
        self.original_df = df.copy() if df is not None else pd.DataFrame()
        self.filtered_df = self.original_df.copy()
        self.current_page = 1
        self.page_size = page_size
        self._update_total_pages()
    
    def set_data(self, df: pd.DataFrame, preserve_page: bool = True):
        """
        Establecer nuevos datos
        
        Args:
            df: DataFrame con datos
            preserve_page: Si True, preservar la página actual si es posible
        """
        old_page = self.current_page  # Preservar página actual
        old_total = self.total_pages if hasattr(self, 'total_pages') else 0
        
        self.original_df = df.copy()
        self.filtered_df = df.copy()
        
        self._update_total_pages()
        
        # Solo resetear página si se especifica o si la página actual ya no es válida
        if not preserve_page or old_page > self.total_pages:
            self.current_page = 1
            # Solo emitir señales si la página cambió realmente
            if old_page != 1:
                self.page_changed.emit(self.current_page)
        else:
            # Mantener la página actual si sigue siendo válida
            self.current_page = old_page
            # Solo emitir señales si el total de páginas cambió y afecta el estado
            if old_total != self.total_pages:
                self.data_changed.emit()
                self.page_changed.emit(self.current_page)
                return
        
        self.data_changed.emit()
    
    def set_page_size(self, size: int):
        """
        Establecer tamaño de página
        
        Args:
            size: Nuevo tamaño de página
        """
        if size > 0 and size != self.page_size:
            old_page_size = self.page_size
            self.page_size = size
            
            # Recalcular página actual para mantener posición aproximada
            old_start_row = (self.current_page - 1) * old_page_size
            self.current_page = max(1, (old_start_row // self.page_size) + 1)
            
            self._update_total_pages()
            self.page_size_changed.emit(size)
    
    def get_page_size(self) -> int:
        """Obtener tamaño de página actual"""
        return self.page_size
    
    def set_current_page(self, page: int):
        """
        Establecer página actual
        
        Args:
            page: Número de página (1-indexed)
        """
        if 1 <= page <= self.total_pages:
            self.current_page = page
            self.page_changed.emit(page)
    
    def get_current_page(self) -> int:
        """Obtener página actual"""
        return self.current_page
    
    def get_total_pages(self) -> int:
        """Obtener número total de páginas"""
        return self.total_pages
    
    def get_total_rows(self) -> int:
        """Obtener número total de filas filtradas"""
        return len(self.filtered_df)
    
    def get_page_data(self) -> pd.DataFrame:
        """
        Obtener datos de la página actual
        
        Returns:
            DataFrame con datos de la página actual
        """
        if self.filtered_df.empty:
            return self.filtered_df
        
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.filtered_df))
        
        return self.filtered_df.iloc[start_idx:end_idx].copy()
    
    def next_page(self):
        """Ir a la siguiente página"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.page_changed.emit(self.current_page)
    
    def previous_page(self):
        """Ir a la página anterior"""
        if self.current_page > 1:
            self.current_page -= 1
            self.page_changed.emit(self.current_page)
    
    def first_page(self):
        """Ir a la primera página"""
        if self.current_page != 1:
            self.current_page = 1
            self.page_changed.emit(self.current_page)
    
    def last_page(self):
        """Ir a la última página"""
        if self.current_page != self.total_pages:
            self.current_page = self.total_pages
            self.page_changed.emit(self.current_page)
    
    def can_go_next(self) -> bool:
        """Verificar si se puede ir a la siguiente página"""
        return self.current_page < self.total_pages
    
    def can_go_previous(self) -> bool:
        """Verificar si se puede ir a la página anterior"""
        return self.current_page > 1
    
    def apply_filter(self, column: str, term: str):
        """
        Aplicar filtro a los datos
        
        Args:
            column: Nombre de la columna
            term: Término de búsqueda
        """
        if not term.strip():
            # Si no hay término, mostrar todos los datos
            self.filtered_df = self.original_df.copy()
        else:
            try:
                # Filtrar por coincidencia parcial (case-insensitive)
                self.filtered_df = self.original_df[
                    self.original_df[column].astype(str).str.contains(
                        term, case=False, na=False, regex=False
                    )
                ].copy()
            except Exception:
                # En caso de error, mostrar todos los datos
                self.filtered_df = self.original_df.copy()
        
        # Resetear a primera página después del filtro
        self.current_page = 1
        self._update_total_pages()
        self.data_changed.emit()
    
    def clear_filter(self):
        """Limpiar filtros y mostrar todos los datos"""
        self.filtered_df = self.original_df.copy()
        self.current_page = 1
        self._update_total_pages()
        self.data_changed.emit()
    
    def get_filter_info(self) -> dict:
        """
        Obtener información del filtro actual
        
        Returns:
            Dict con información del filtro
        """
        return {
            'original_rows': len(self.original_df),
            'filtered_rows': len(self.filtered_df),
            'filtered_out': len(self.original_df) - len(self.filtered_df),
            'is_filtered': len(self.filtered_df) != len(self.original_df)
        }
    
    def _update_total_pages(self):
        """Calcular número total de páginas"""
        if self.filtered_df.empty:
            self.total_pages = 0
        else:
            self.total_pages = (len(self.filtered_df) + self.page_size - 1) // self.page_size
        
        self.total_pages_changed.emit(self.total_pages)
        
        # Asegurar que la página actual es válida
        if self.current_page > self.total_pages and self.total_pages > 0:
            self.current_page = self.total_pages
            self.page_changed.emit(self.current_page)
    
    def get_page_info(self) -> dict:
        """
        Obtener información de la página actual
        
        Returns:
            Dict con información de la página
        """
        total_rows = len(self.filtered_df)
        
        if total_rows == 0:
            return {
                'current_page': 0,
                'total_pages': 0,
                'total_rows': 0,
                'start_row': 0,
                'end_row': 0,
                'rows_in_page': 0
            }
        
        # Calcular el rango real de la página actual
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, total_rows)
        
        return {
            'current_page': self.current_page,
            'total_pages': self.total_pages,
            'total_rows': total_rows,
            'start_row': start_idx + 1,  # +1 porque las filas empiezan en 1
            'end_row': end_idx,
            'rows_in_page': end_idx - start_idx
        }