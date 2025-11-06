"""
Solución simplificada para preservar formato Excel sin usar deepcopy.
Evita problemas de recursión infinita.
"""

import openpyxl
from openpyxl.utils import coordinate_to_tuple, column_index_from_string
from typing import Dict, Any, Tuple
import copy


class SimpleExcelFormatPreserver:
    """Versión simplificada para preservar formato sin problemas de recursión"""
    
    def __init__(self):
        self.saved_cell_data = {}
    
    def save_cell_format(self, cell) -> Dict[str, Any]:
        """
        Guardar formato de una celda sin usar deepcopy
        
        Args:
            cell: Celda de openpyxl
            
        Returns:
            Dict con formato de la celda
        """
        format_info = {
            'value': cell.value,
            'font': {
                'name': cell.font.name,
                'size': cell.font.size,
                'bold': cell.font.bold,
                'italic': cell.font.italic,
                'color': cell.font.color.rgb if cell.font.color else None
            },
            'fill': {
                'start_color': cell.fill.start_color.rgb if cell.fill.start_color else None,
                'fill_type': cell.fill.fill_type
            },
            'border': {
                'left': self._serialize_border(cell.border.left),
                'right': self._serialize_border(cell.border.right),
                'top': self._serialize_border(cell.border.top),
                'bottom': self._serialize_border(cell.border.bottom)
            },
            'alignment': {
                'horizontal': cell.alignment.horizontal,
                'vertical': cell.alignment.vertical,
                'wrap_text': cell.alignment.wrap_text
            },
            'number_format': cell.number_format
        }
        
        return format_info
    
    def _serialize_border(self, side) -> Dict[str, Any]:
        """Serializar border side"""
        return {
            'style': side.style,
            'color': side.color.rgb if side.color else None
        }
    
    def restore_cell_format(self, cell, format_info: Dict[str, Any]) -> None:
        """
        Restaurar formato de una celda
        
        Args:
            cell: Celda de openpyxl
            format_info: Dict con formato a restaurar
        """
        try:
            # Restaurar font
            if format_info.get('font'):
                font_info = format_info['font']
                if font_info.get('name'):
                    cell.font.name = font_info['name']
                if font_info.get('size'):
                    cell.font.size = font_info['size']
                if font_info.get('bold') is not None:
                    cell.font.bold = font_info['bold']
                if font_info.get('italic') is not None:
                    cell.font.italic = font_info['italic']
                if font_info.get('color'):
                    from openpyxl.styles import Color
                    cell.font.color = Color(rgb=font_info['color'])
            
            # Restaurar fill
            if format_info.get('fill'):
                fill_info = format_info['fill']
                if fill_info.get('start_color') and fill_info.get('fill_type'):
                    from openpyxl.styles import PatternFill
                    cell.fill = PatternFill(
                        start_color=fill_info['start_color'],
                        end_color=fill_info['start_color'],
                        fill_type=fill_info['fill_type']
                    )
            
            # Restaurar border
            if format_info.get('border'):
                border_info = format_info['border']
                from openpyxl.styles import Border, Side
                
                sides = {}
                for side_name, side_info in border_info.items():
                    if side_info and side_info.get('style'):
                        side = Side(
                            border_style=side_info['style'],
                            color=Color(rgb=side_info['color']) if side_info.get('color') else None
                        )
                        sides[side_name] = side
                
                if sides:
                    cell.border = Border(**sides)
            
            # Restaurar alignment
            if format_info.get('alignment'):
                align_info = format_info['alignment']
                from openpyxl.styles import Alignment
                alignment_kwargs = {}
                if align_info.get('horizontal'):
                    alignment_kwargs['horizontal'] = align_info['horizontal']
                if align_info.get('vertical'):
                    alignment_kwargs['vertical'] = align_info['vertical']
                if align_info.get('wrap_text') is not None:
                    alignment_kwargs['wrap_text'] = align_info['wrap_text']
                
                if alignment_kwargs:
                    cell.alignment = Alignment(**alignment_kwargs)
            
            # Restaurar number format
            if format_info.get('number_format') and format_info['number_format'] != 'General':
                cell.number_format = format_info['number_format']
        
        except Exception as e:
            print(f"Warning: No se pudo restaurar formato completo: {e}")
            # Al menos preservar el valor
            if 'value' in format_info:
                cell.value = format_info['value']
    
    def backup_area_formatting(self, worksheet, start_cell: str, area_size: Tuple[int, int]) -> Dict[str, Any]:
        """
        Backup del formato en un área específica
        
        Args:
            worksheet: Worksheet de openpyxl
            start_cell: Celda inicial (ej: 'A5')
            area_size: Tamaño del área (filas, columnas)
            
        Returns:
            Dict con formatos respaldados
        """
        start_row, start_col = coordinate_to_tuple(start_cell)
        rows, cols = area_size
        
        backup = {}
        
        # Backup de celdas
        for row_offset in range(rows):
            for col_offset in range(cols):
                cell_row = start_row + row_offset
                cell_col = start_col + col_offset
                cell = worksheet.cell(row=cell_row, column=cell_col)
                
                if cell.value is not None:
                    coord = f"{openpyxl.utils.get_column_letter(cell_col)}{cell_row}"
                    backup[coord] = self.save_cell_format(cell)
        
        return backup
    
    def insert_data_simple_preservation(self, worksheet, data: Dict[str, Any], 
                                      column_mapping: Dict[str, str], start_cell: str) -> None:
        """
        Insertar datos preservando formato de manera simple
        
        Args:
            worksheet: Worksheet de openpyxl
            data: DataFrame a insertar como dict
            column_mapping: Mapeo de columnas
            start_cell: Celda inicial
        """
        start_row, start_col = coordinate_to_tuple(start_cell)
        
        # Backup formato de área donde se insertarán datos
        max_rows = len(data)
        max_cols = len(column_mapping)
        
        area_backup = self.backup_area_formatting(worksheet, start_cell, (max_rows + 5, max_cols + 2))
        
        # Insertar datos
        for row_offset, (_, row_data) in enumerate(data.items()):
            excel_row = start_row + row_offset
            
            for df_col, excel_col_letter in column_mapping.items():
                if df_col in row_data:
                    excel_col_idx = column_index_from_string(excel_col_letter)
                    cell = worksheet.cell(row=excel_row, column=excel_col_idx)
                    
                    # Insertar valor
                    value = row_data[df_col]
                    if value is None:
                        cell.value = None
                    else:
                        cell.value = value
        
        # Restaurar formato de área (solo para celdas que tenían formato)
        for cell_coord, format_info in area_backup.items():
            try:
                cell = worksheet[cell_coord]
                self.restore_cell_format(cell, format_info)
            except Exception as e:
                # Si falla la restauración, al menos asegurar que el valor se mantenga
                if 'value' in format_info:
                    try:
                        cell = worksheet[cell_coord]
                        cell.value = format_info['value']
                    except:
                        pass


def create_excel_with_simple_format_preservation(template_path: str, output_path: str, 
                                               data: Dict[str, Any], column_mapping: Dict[str, str],
                                               start_cell: str) -> bool:
    """
    Función utilitaria simple para preservar formato Excel
    
    Args:
        template_path: Ruta de plantilla original
        output_path: Ruta de salida
        data: Data a insertar
        column_mapping: Mapeo de columnas
        start_cell: Celda inicial
        
    Returns:
        bool: True si es exitoso
    """
    try:
        # Cargar plantilla
        workbook = openpyxl.load_workbook(template_path, data_only=False)
        sheet = workbook.active
        
        # Crear preserver simple
        preserver = SimpleExcelFormatPreserver()
        
        # Insertar datos con preservación
        preserver.insert_data_simple_preservation(
            sheet, data, column_mapping, start_cell
        )
        
        # Guardar archivo
        workbook.save(output_path)
        workbook.close()
        
        return True
        
    except Exception as e:
        print(f"Error creando archivo con formato preservado: {e}")
        return False