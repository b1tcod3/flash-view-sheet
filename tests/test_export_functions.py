"""
Pruebas unitarias para funciones de exportación
"""

import unittest
import pandas as pd
import os
import tempfile
from unittest.mock import Mock, patch

# Añadir el directorio raíz al path para importar módulos
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_handler import exportar_a_pdf, exportar_a_sql, exportar_a_imagen


class TestExportFunctions(unittest.TestCase):
    """Pruebas para las funciones de exportación"""

    def setUp(self):
        """Configuración antes de cada prueba"""
        # Crear DataFrame de prueba
        self.test_df = pd.DataFrame({
            'Nombre': ['Juan', 'María', 'Pedro', 'Ana'],
            'Edad': [25, 30, 35, 28],
            'Ciudad': ['Madrid', 'Barcelona', 'Valencia', 'Sevilla'],
            'Salario': [25000.50, 30000.75, 35000.25, 28000.00]
        })

        # Crear directorio temporal para archivos de prueba
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Limpieza después de cada prueba"""
        # Limpiar archivos temporales
        for file in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        os.rmdir(self.temp_dir)

    def test_exportar_a_pdf_success(self):
        """Probar exportación a PDF exitosa"""
        filepath = os.path.join(self.temp_dir, 'test_export.pdf')

        # Ejecutar exportación
        result = exportar_a_pdf(self.test_df, filepath)

        # Verificar resultado
        self.assertTrue(result, "La exportación a PDF debería ser exitosa")
        self.assertTrue(os.path.exists(filepath), "El archivo PDF debería existir")
        self.assertGreater(os.path.getsize(filepath), 0, "El archivo PDF debería tener contenido")

    def test_exportar_a_pdf_empty_dataframe(self):
        """Probar exportación a PDF con DataFrame vacío"""
        empty_df = pd.DataFrame()
        filepath = os.path.join(self.temp_dir, 'test_empty.pdf')

        # Ejecutar exportación
        result = exportar_a_pdf(empty_df, filepath)

        # Verificar resultado
        self.assertTrue(result, "La exportación a PDF con DataFrame vacío debería ser exitosa")
        self.assertTrue(os.path.exists(filepath), "El archivo PDF debería existir")

    def test_exportar_a_pdf_invalid_path(self):
        """Probar exportación a PDF con ruta inválida"""
        invalid_path = "/invalid/path/test.pdf"

        # Ejecutar exportación
        result = exportar_a_pdf(self.test_df, invalid_path)

        # Verificar resultado
        self.assertFalse(result, "La exportación a PDF con ruta inválida debería fallar")

    def test_exportar_a_sql_success(self):
        """Probar exportación a SQL exitosa"""
        filepath = os.path.join(self.temp_dir, 'test_export.db')
        table_name = 'test_table'

        # Ejecutar exportación
        result = exportar_a_sql(self.test_df, filepath, table_name)

        # Verificar resultado
        self.assertTrue(result, "La exportación a SQL debería ser exitosa")
        self.assertTrue(os.path.exists(filepath), "El archivo de base de datos debería existir")

        # Verificar que la tabla existe en la base de datos
        import sqlite3
        conn = sqlite3.connect(filepath)
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        table_exists = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(table_exists, "La tabla debería existir en la base de datos")

    def test_exportar_a_sql_empty_dataframe(self):
        """Probar exportación a SQL con DataFrame vacío"""
        empty_df = pd.DataFrame()
        filepath = os.path.join(self.temp_dir, 'test_empty.db')
        table_name = 'empty_table'

        # Ejecutar exportación
        result = exportar_a_sql(empty_df, filepath, table_name)

        # Verificar resultado
        self.assertTrue(result, "La exportación a SQL con DataFrame vacío debería ser exitosa")
        self.assertTrue(os.path.exists(filepath), "El archivo de base de datos debería existir")

    def test_exportar_a_sql_invalid_path(self):
        """Probar exportación a SQL con ruta inválida"""
        invalid_path = "/invalid/path/test.db"
        table_name = 'test_table'

        # Ejecutar exportación
        result = exportar_a_sql(self.test_df, invalid_path, table_name)

        # Verificar resultado
        self.assertFalse(result, "La exportación a SQL con ruta inválida debería fallar")

    @patch('PySide6.QtWidgets.QApplication')
    def test_exportar_a_imagen_success(self, mock_qapp):
        """Probar exportación a imagen exitosa"""
        # Crear mock para QTableView
        mock_table_view = Mock()
        mock_pixmap = Mock()
        mock_pixmap.save.return_value = True
        mock_table_view.grab.return_value = mock_pixmap

        filepath = os.path.join(self.temp_dir, 'test_export.png')

        # Ejecutar exportación
        result = exportar_a_imagen(mock_table_view, filepath)

        # Verificar resultado
        self.assertTrue(result, "La exportación a imagen debería ser exitosa")
        mock_pixmap.save.assert_called_once_with(filepath)

    @patch('PySide6.QtWidgets.QApplication')
    def test_exportar_a_imagen_save_failure(self, mock_qapp):
        """Probar exportación a imagen cuando falla el guardado"""
        # Crear mock para QTableView
        mock_table_view = Mock()
        mock_pixmap = Mock()
        mock_pixmap.save.return_value = False  # Simular fallo en guardado
        mock_table_view.grab.return_value = mock_pixmap

        filepath = os.path.join(self.temp_dir, 'test_export.png')

        # Ejecutar exportación
        result = exportar_a_imagen(mock_table_view, filepath)

        # Verificar resultado
        self.assertFalse(result, "La exportación a imagen debería fallar cuando el guardado falla")

    def test_exportar_a_imagen_exception(self):
        """Probar exportación a imagen con excepción"""
        # Crear mock para QTableView que lanza excepción
        mock_table_view = Mock()
        mock_table_view.grab.side_effect = Exception("Test exception")

        filepath = os.path.join(self.temp_dir, 'test_export.png')

        # Ejecutar exportación
        result = exportar_a_imagen(mock_table_view, filepath)

        # Verificar resultado
        self.assertFalse(result, "La exportación a imagen debería fallar con excepción")

    def test_exportacion_con_datos_especiales(self):
        """Probar exportación con datos especiales (NaN, None, caracteres especiales)"""
        # Crear DataFrame con datos especiales
        special_df = pd.DataFrame({
            'Texto': ['Normal', 'Con acentos: áéíóú', 'Con ñ: España', None],
            'Numeros': [1.5, float('nan'), 3.14, None],
            'Fechas': pd.date_range('2023-01-01', periods=4)
        })

        # Probar exportación a PDF
        pdf_path = os.path.join(self.temp_dir, 'test_special.pdf')
        result_pdf = exportar_a_pdf(special_df, pdf_path)
        self.assertTrue(result_pdf, "La exportación a PDF con datos especiales debería ser exitosa")

        # Probar exportación a SQL
        sql_path = os.path.join(self.temp_dir, 'test_special.db')
        result_sql = exportar_a_sql(special_df, sql_path, 'special_table')
        self.assertTrue(result_sql, "La exportación a SQL con datos especiales debería ser exitosa")


if __name__ == '__main__':
    unittest.main()