"""
Servicio de Exportación - ExportService

Servicio centralizado para todas las operaciones de exportación de datos
en Flash View Sheet.
"""

import os
import pandas as pd
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QFileDialog, QInputDialog
from PySide6.QtCore import Qt
from core.data_handler import (
    exportar_a_pdf,
    exportar_a_xlsx,
    exportar_a_csv,
    exportar_a_sql,
    exportar_a_imagen,
    exportar_datos_separados
)


class ExportService:
    """
    Servicio unificado para operaciones de exportación.
    
    Responsabilidades:
    - Exportación a PDF, XLSX, CSV, SQL, Imagen
    - Exportación separada por columnas usando plantillas
    - Gestión de diálogos de exportación
    """
    
    def __init__(self, parent_window=None):
        """Inicializar el servicio de exportación"""
        self.parent_window = parent_window
    
    def set_parent_window(self, window):
        """Establecer ventana padre para diálogos"""
        self.parent_window = window
    
    def _ensure_extension(self, filepath, extension, valid_extensions):
        """Asegurar que el archivo tenga la extensión correcta"""
        if not any(filepath.lower().endswith(ext) for ext in valid_extensions):
            filepath += extension
        return filepath
    
    def export_to_pdf(self, df, filepath=None):
        """Exportar datos a PDF"""
        if df is None or df.empty:
            QMessageBox.warning(self.parent_window, "Advertencia", "No hay datos para exportar.")
            return False
        
        if filepath is None:
            filepath, _ = QFileDialog.getSaveFileName(
                self.parent_window,
                "Guardar como PDF",
                "",
                "Archivos PDF (*.pdf)"
            )
        
        if not filepath:
            return False
        
        filepath = self._ensure_extension(filepath, '.pdf', ['.pdf'])
        
        try:
            success = exportar_a_pdf(df, filepath)
            if success:
                QMessageBox.information(self.parent_window, "Éxito", f"Datos exportados a {filepath}")
                return True
            else:
                QMessageBox.critical(self.parent_window, "Error", "No se pudo exportar a PDF.")
                return False
        except Exception as e:
            QMessageBox.critical(self.parent_window, "Error", f"Error exportando a PDF: {str(e)}")
            return False
    
    def export_to_xlsx(self, df, filepath=None):
        """Exportar datos a Excel"""
        if df is None or df.empty:
            QMessageBox.warning(self.parent_window, "Advertencia", "No hay datos para exportar.")
            return False
        
        if filepath is None:
            filepath, _ = QFileDialog.getSaveFileName(
                self.parent_window,
                "Guardar como Excel",
                "",
                "Archivos Excel (*.xlsx)"
            )
        
        if not filepath:
            return False
        
        filepath = self._ensure_extension(filepath, '.xlsx', ['.xlsx', '.xls'])
        
        try:
            success = exportar_a_xlsx(df, filepath)
            if success:
                QMessageBox.information(self.parent_window, "Éxito", f"Datos exportados a {filepath}")
                return True
            else:
                QMessageBox.critical(self.parent_window, "Error", "No se pudo exportar a XLSX.")
                return False
        except Exception as e:
            QMessageBox.critical(self.parent_window, "Error", f"Error exportando a XLSX: {str(e)}")
            return False
    
    def export_to_csv(self, df, filepath=None, delimiter=','):
        """Exportar datos a CSV"""
        if df is None or df.empty:
            QMessageBox.warning(self.parent_window, "Advertencia", "No hay datos para exportar.")
            return False
        
        if filepath is None:
            filepath, _ = QFileDialog.getSaveFileName(
                self.parent_window,
                "Guardar como CSV",
                "",
                "Archivos CSV (*.csv)"
            )
        
        if not filepath:
            return False
        
        filepath = self._ensure_extension(filepath, '.csv', ['.csv'])
        
        try:
            success = exportar_a_csv(df, filepath, delimiter=delimiter, encoding='utf-8')
            if success:
                QMessageBox.information(self.parent_window, "Éxito", f"Datos exportados a {filepath}")
                return True
            else:
                QMessageBox.critical(self.parent_window, "Error", "No se pudo exportar a CSV.")
                return False
        except Exception as e:
            QMessageBox.critical(self.parent_window, "Error", f"Error exportando a CSV: {str(e)}")
            return False
    
    def export_to_sql(self, df, filepath=None, table_name=None):
        """Exportar datos a SQL"""
        if df is None or df.empty:
            QMessageBox.warning(self.parent_window, "Advertencia", "No hay datos para exportar.")
            return False
        
        if filepath is None:
            filepath, _ = QFileDialog.getSaveFileName(
                self.parent_window,
                "Guardar como Base de Datos SQL",
                "",
                "Bases de Datos SQLite (*.db)"
            )
        
        if not filepath:
            return False
        
        filepath = self._ensure_extension(filepath, '.db', ['.db', '.sqlite', '.sqlite3'])
        
        if table_name is None:
            table_name, ok = self._get_text_input("Nombre de la Tabla", "Ingresa el nombre de la tabla:")
            if not ok or not table_name:
                return False
        
        try:
            success = exportar_a_sql(df, filepath, table_name)
            if success:
                QMessageBox.information(
                    self.parent_window, 
                    "Éxito", 
                    f"Datos exportados a {filepath} en tabla '{table_name}'"
                )
                return True
            else:
                QMessageBox.critical(self.parent_window, "Error", "No se pudo exportar a SQL.")
                return False
        except Exception as e:
            QMessageBox.critical(self.parent_window, "Error", f"Error exportando a SQL: {str(e)}")
            return False
    
    def export_to_image(self, table_widget, filepath=None):
        """Exportar vista de tabla a imagen"""
        if table_widget is None:
            QMessageBox.warning(self.parent_window, "Advertencia", "No hay tabla para exportar.")
            return False
        
        if filepath is None:
            filepath, _ = QFileDialog.getSaveFileName(
                self.parent_window,
                "Guardar como Imagen",
                "",
                "Archivos de Imagen (*.png *.jpg *.jpeg)"
            )
        
        if not filepath:
            return False
        
        valid_image_exts = ['.png', '.jpg', '.jpeg']
        filepath = self._ensure_extension(filepath, '.png', valid_image_exts)
        
        try:
            success = exportar_a_imagen(table_widget, filepath)
            if success:
                QMessageBox.information(self.parent_window, "Éxito", f"Imagen exportada a {filepath}")
                return True
            else:
                QMessageBox.critical(self.parent_window, "Error", "No se pudo exportar a imagen.")
                return False
        except Exception as e:
            QMessageBox.critical(self.parent_window, "Error", f"Error exportando a imagen: {str(e)}")
            return False
    
    def export_separated(self, df, config):
        """
        Exportar datos separados por columna usando plantillas Excel.
        
        Args:
            df: DataFrame a exportar
            config: Configuración de exportación (dict o objeto con atributos)
        
        Returns:
            Dict con resultado de la exportación
        """
        if df is None or df.empty:
            QMessageBox.warning(self.parent_window, "Advertencia", "No hay datos para exportar.")
            return {'success': False, 'error': 'No hay datos'}
        
        try:
            # Convertir config a dict si es necesario
            config_dict = config.__dict__ if hasattr(config, '__dict__') else dict(config)
            
            resultado = exportar_datos_separados(df, config_dict)
            
            if resultado.get('success', False):
                archivos_generados = resultado.get('files_created', [])
                grupos_procesados = resultado.get('groups_processed', 0)
                tiempo_procesamiento = resultado.get('processing_time', 0)
                
                mensaje = f"Exportación completada exitosamente:\n\n"
                mensaje += f"• {grupos_procesados} grupos procesados\n"
                mensaje += f"• {len(archivos_generados)} archivos generados\n"
                mensaje += f"• Tiempo: {tiempo_procesamiento:.1f} segundos\n"
                mensaje += f"• Carpeta: {config_dict.get('output_folder', 'N/A')}"
                
                if len(archivos_generados) <= 10 and archivos_generados:
                    mensaje += f"\n\nArchivos creados:\n" + "\n".join([f"• {archivo}" for archivo in archivos_generados])
                elif len(archivos_generados) > 10:
                    mensaje += f"\n\nPrimeros 10 archivos:\n" + "\n".join([f"• {archivo}" for archivo in archivos_generados[:10]])
                    mensaje += f"\n... y {len(archivos_generados) - 10} archivos más"
                
                QMessageBox.information(self.parent_window, "Éxito", mensaje)
                return resultado
            else:
                errores = resultado.get('errors', [])
                if errores:
                    QMessageBox.critical(self.parent_window, "Error en Exportación", 
                                       f"No se pudo completar la exportación:\n\n{chr(10).join(errores)}")
                return resultado
                
        except Exception as e:
            error_msg = self._format_export_error(str(e))
            QMessageBox.critical(self.parent_window, "Error", error_msg)
            return {'success': False, 'error': str(e)}
    
    def show_export_dialog(self, df, default_prefix="Exportacion"):
        """
        Mostrar diálogo genérico de exportación con selección de formato.
        
        Args:
            df: DataFrame a exportar
            default_prefix: Prefijo para el nombre del archivo
        
        Returns:
            True si se completó la exportación, False en caso contrario
        """
        if df is None or df.empty:
            QMessageBox.warning(self.parent_window, "Advertencia", "No hay datos para exportar.")
            return False
        
        dialog = QDialog(self.parent_window)
        dialog.setWindowTitle("Exportar Datos")
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        # Selección de formato
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Formato:"))
        format_combo = QComboBox()
        format_combo.addItems(["Excel (.xlsx)", "CSV (.csv)", "PDF (.pdf)", "SQLite (.db)"])
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
            return False
        
        # Generar nombre de archivo por defecto
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        default_filename = f"{default_prefix}_{timestamp}"
        
        format_text = format_combo.currentText()
        
        if "Excel" in format_text:
            return self.export_to_xlsx(df)
        elif "CSV" in format_text:
            return self.export_to_csv(df)
        elif "PDF" in format_text:
            return self.export_to_pdf(df)
        elif "SQLite" in format_text:
            return self.export_to_sql(df)
        else:
            QMessageBox.warning(self.parent_window, "Error", "Formato no soportado.")
            return False
    
    def _get_text_input(self, title, label):
        """Obtener entrada de texto del usuario"""
        text, ok = QInputDialog.getText(self.parent_window, title, label)
        return text, ok
    
    def _format_export_error(self, error_str):
        """Formatear errores de exportación para mejor comprensión"""
        error_str = str(error_str)
        
        if "Excel" in error_str or "xlsx" in error_str or "openpyxl" in error_str:
            if "corrupt" in error_str.lower() or "formato" in error_str.lower():
                return ("Error de archivo Excel:\n\n"
                       "• El archivo de plantilla puede estar corrupto\n"
                       "• Verifica que sea un archivo .xlsx válido\n"
                       "• Asegúrate de que no esté abierto en Excel\n\n"
                       f"Detalles: {error_str}")
            elif "permission" in error_str.lower():
                return ("Error de permisos:\n\n"
                       "• No tienes permisos para escribir en la carpeta\n"
                       "• Verifica los permisos de la carpeta de destino\n"
                       "• Prueba con una carpeta diferente\n\n"
                       f"Detalles: {error_str}")
            elif "template" in error_str.lower():
                return ("Error de plantilla:\n\n"
                       "• La plantilla Excel no se puede leer\n"
                       "• Verifica que el archivo existe y es accesible\n\n"
                       f"Detalles: {error_str}")
            else:
                return ("Error relacionado con Excel:\n\n"
                       "• Verifica que los archivos Excel no estén abiertos\n"
                       "• Asegúrate de tener permisos de lectura/escritura\n\n"
                       f"Detalles: {error_str}")
        elif "template" in error_str.lower():
            return ("Error de plantilla:\n\n"
                   "• La plantilla especificada no se puede leer\n"
                   f"Detalles: {error_str}")
        elif "memoria" in error_str.lower() or "memory" in error_str.lower():
            return ("Error de memoria:\n\n"
                   "• El dataset es demasiado grande para procesarlo\n"
                   "• Prueba con un dataset más pequeño\n\n"
                   f"Detalles: {error_str}")
        else:
            return f"Error procesando exportación:\n\nDetalles: {error_str}"
