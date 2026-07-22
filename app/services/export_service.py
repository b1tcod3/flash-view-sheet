"""
Servicio de Exportación - ExportService

Servicio centralizado para todas las operaciones de exportación de datos
en Flash View Sheet.
"""

from typing import Any
import pandas as pd
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
    """

    def _ensure_extension(self, filepath: str, extension: str, valid_extensions: list[str]) -> str:
        """Asegurar que el archivo tenga la extensión correcta."""
        if not any(filepath.lower().endswith(ext) for ext in valid_extensions):
            filepath += extension
        return filepath

    def _export_dataframe(
        self,
        df: pd.DataFrame,
        filepath: str,
        extension: str,
        valid_extensions: list[str],
        export_func: Any,
        success_message: str,
        error_prefix: str,
        *args: Any,
        **kwargs: Any,
    ) -> tuple[bool, str]:
        """Método genérico para exportar un DataFrame.

        Args:
            df: DataFrame a exportar.
            filepath: Ruta de destino.
            extension: Extensión por defecto (ej. '.pdf').
            valid_extensions: Extensiones válidas para _ensure_extension.
            export_func: Función de exportación (ej. exportar_a_pdf).
            success_message: Mensaje de éxito (puede contener '{filepath}').
            error_prefix: Prefijo para mensajes de error.
            *args, **kwargs: Argumentos adicionales para export_func.

        Returns:
            Tupla (éxito, mensaje descriptivo).
        """
        if df is None or df.empty:
            return False, "No hay datos para exportar."

        filepath = self._ensure_extension(filepath, extension, valid_extensions)

        try:
            success = export_func(df, filepath, *args, **kwargs)
            if success:
                return True, success_message.format(filepath=filepath)
            return False, f"{error_prefix}: no se pudo completar la exportación."
        except Exception as e:
            return False, f"{error_prefix}: {e}"

    def export_to_pdf(self, df: pd.DataFrame, filepath: str) -> tuple[bool, str]:
        """Exportar datos a PDF."""
        return self._export_dataframe(
            df, filepath, '.pdf', ['.pdf'],
            exportar_a_pdf, "Datos exportados a {filepath}", "Error exportando a PDF",
        )

    def export_to_xlsx(self, df: pd.DataFrame, filepath: str) -> tuple[bool, str]:
        """Exportar datos a Excel."""
        return self._export_dataframe(
            df, filepath, '.xlsx', ['.xlsx', '.xls'],
            exportar_a_xlsx, "Datos exportados a {filepath}", "Error exportando a XLSX",
        )

    def export_to_csv(self, df: pd.DataFrame, filepath: str, delimiter: str = ',') -> tuple[bool, str]:
        """Exportar datos a CSV."""
        return self._export_dataframe(
            df, filepath, '.csv', ['.csv'],
            exportar_a_csv, "Datos exportados a {filepath}", "Error exportando a CSV",
            delimiter=delimiter, encoding='utf-8',
        )

    def export_to_sql(self, df: pd.DataFrame, filepath: str, table_name: str) -> tuple[bool, str]:
        """Exportar datos a SQL."""
        return self._export_dataframe(
            df, filepath, '.db', ['.db', '.sqlite', '.sqlite3'],
            exportar_a_sql,
            f"Datos exportados a {{filepath}} en tabla '{table_name}'",
            "Error exportando a SQL",
            table_name,
        )

    def export_to_image(self, table_widget: Any, filepath: str) -> tuple[bool, str]:
        """Exportar vista de tabla a imagen."""
        if table_widget is None:
            return False, "No hay tabla para exportar."

        filepath = self._ensure_extension(filepath, '.png', ['.png', '.jpg', '.jpeg'])

        try:
            success = exportar_a_imagen(table_widget, filepath)
            if success:
                return True, f"Imagen exportada a {filepath}"
            return False, "No se pudo exportar a imagen."
        except Exception as e:
            return False, f"Error exportando a imagen: {e}"

    def export_separated(self, df: pd.DataFrame, config: Any) -> dict[str, Any]:
        """Exportar datos separados por columna usando plantillas Excel."""
        if df is None or df.empty:
            return {'success': False, 'error': 'No hay datos'}

        try:
            config_dict = config.__dict__ if hasattr(config, '__dict__') else dict(config)
            return exportar_datos_separados(df, config_dict)
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _format_export_error(self, error_str: str) -> str:
        """Formatear errores de exportación para mejor comprensión."""
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
