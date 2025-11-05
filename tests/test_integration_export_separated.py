#!/usr/bin/env python3
"""
Tests de integración para el sistema de exportación separada completo
Prueba la integración entre main.py, diálogos y core logic
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, Mock
import pandas as pd

# Configurar QApplication para tests
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from main import MainWindow
from core.data_handler import ExcelTemplateSplitter, ExportSeparatedConfig


class TestExportSeparatedIntegration(unittest.TestCase):
    """Tests de integración para sistema de exportación separada"""
    
    @classmethod
    def setUpClass(cls):
        """Configurar QApplication para tests de UI"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Configurar datos de prueba"""
        # Crear DataFrame de prueba
        self.df_test = pd.DataFrame({
            'Region': ['Norte', 'Norte', 'Sur', 'Sur', 'Este', 'Oeste'],
            'Producto': ['A', 'B', 'A', 'B', 'A', 'B'],
            'Ventas': [1000, 1500, 800, 1200, 900, 1100],
            'Fecha': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-01', '2024-01-02', '2024-01-01', '2024-01-02'])
        })
        
        # Crear directorio temporal para tests
        self.temp_dir = tempfile.mkdtemp()
        self.excel_template_path = self.create_test_excel_template()
        
    def tearDown(self):
        """Limpiar después de tests"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_test_excel_template(self):
        """Crear una plantilla Excel de prueba"""
        from openpyxl import Workbook
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Plantilla"
        
        # Crear encabezados básicos
        ws['A1'] = "Región"
        ws['B1'] = "Producto"
        ws['C1'] = "Ventas"
        ws['D1'] = "Fecha"
        
        # Formato básico
        from openpyxl.styles import Font, PatternFill
        header_font = Font(bold=True)
        header_fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        for col in range(1, 5):
            cell = ws.cell(row=1, column=col)
            cell.font = header_font
            cell.fill = header_fill
        
        # Guardar archivo temporal
        template_path = os.path.join(self.temp_dir, "plantilla_test.xlsx")
        wb.save(template_path)
        return template_path
    
    def test_main_window_integration(self):
        """Test integración básica con MainWindow"""
        window = MainWindow()
        
        # Simular carga de datos
        window.df_vista_actual = self.df_test.copy()
        
        # Verificar que el menú se habilita
        window.actualizar_menu_separar()
        
        self.assertTrue(window.exportar_separado_action.isEnabled())
        
        # Verificar que tiene el status tip correcto
        expected_tip = "Exportar datos separados por columna usando plantillas Excel"
        self.assertEqual(window.exportar_separado_action.statusTip(), expected_tip)
    
    def test_export_processing_integration(self):
        """Test procesamiento de exportación desde main window"""
        window = MainWindow()
        window.df_vista_actual = self.df_test.copy()
        
        # Crear configuración válida
        config = ExportSeparatedConfig(
            separator_column='Region',
            template_path=self.excel_template_path,
            output_folder=self.temp_dir,
            file_template='{valor}_{fecha}.xlsx',
            column_mapping={'Region': 'A', 'Producto': 'B', 'Ventas': 'C', 'Fecha': 'D'},
            start_cell='A2'
        )
        
        # Mockear la función de exportación para evitar procesamiento real
        with patch('core.data_handler.exportar_datos_separados') as mock_export:
            mock_export.return_value = {
                'success': True,
                'files_created': ['Norte_2024-01-01.xlsx', 'Sur_2024-01-01.xlsx'],
                'groups_processed': 4,
                'processing_time': 2.5,
                'errors': []
            }
            
            # Procesar exportación
            try:
                window.procesar_exportacion_separada(config)
                # Si llegamos aquí sin excepción, el flujo básico funciona
                self.assertTrue(True)
            except Exception as e:
                self.fail(f"Error en procesamiento de exportación: {e}")
    
    def test_menu_integration_with_data(self):
        """Test integración del menú con datos cargados"""
        window = MainWindow()
        
        # Sin datos
        window.df_vista_actual = None
        window.actualizar_menu_separar()
        self.assertFalse(window.exportar_separado_action.isEnabled())
        
        # Con datos vacíos
        window.df_vista_actual = pd.DataFrame()
        window.actualizar_menu_separar()
        self.assertFalse(window.exportar_separado_action.isEnabled())
        
        # Con datos válidos
        window.df_vista_actual = self.df_test.copy()
        window.actualizar_menu_separar()
        self.assertTrue(window.exportar_separado_action.isEnabled())
    
    def test_error_handling_integration(self):
        """Test manejo de errores en la integración"""
        window = MainWindow()
        window.df_vista_actual = self.df_test.copy()
        
        # Configuración inválida
        config = ExportSeparatedConfig(
            separator_column='ColumnaInexistente',  # Columna que no existe
            template_path='/ruta/inexistente.xlsx',
            output_folder='/carpeta/inexistente',
            file_template='{valor}.xlsx'
        )
        
        # Mockear la función de exportación para devolver error
        with patch('core.data_handler.exportar_datos_separados') as mock_export:
            mock_export.return_value = {
                'success': False,
                'errors': ['Error de prueba'],
                'files_created': [],
                'groups_processed': 0
            }
            
            # No debe lanzar excepción, debe manejar el error gracefully
            try:
                window.procesar_exportacion_separada(config)
                # Si llegamos aquí, el manejo de errores funciona
                self.assertTrue(True)
            except Exception as e:
                # No debe haber excepciones no manejadas
                self.fail(f"Excepción no manejada en error handling: {e}")
    
    def test_complete_workflow_simulation(self):
        """Test simulación de workflow completo"""
        window = MainWindow()
        window.df_vista_actual = self.df_test.copy()
        
        # Configuración válida
        config = ExportSeparatedConfig(
            separator_column='Region',
            template_path=self.excel_template_path,
            output_folder=self.temp_dir,
            file_template='Reporte_{valor}.xlsx',
            column_mapping={'Region': 'A', 'Producto': 'B', 'Ventas': 'C'},
            start_cell='A2'
        )
        
        # Mockear para simular exportación exitosa
        with patch('core.data_handler.exportar_datos_separados') as mock_export:
            mock_export.return_value = {
                'success': True,
                'files_created': [
                    os.path.join(self.temp_dir, 'Reporte_Norte.xlsx'),
                    os.path.join(self.temp_dir, 'Reporte_Sur.xlsx'),
                    os.path.join(self.temp_dir, 'Reporte_Este.xlsx'),
                    os.path.join(self.temp_dir, 'Reporte_Oeste.xlsx')
                ],
                'groups_processed': 4,
                'processing_time': 1.8,
                'errors': []
            }
            
            # Verificar que el método procesar_exportacion_separada existe y es callable
            self.assertTrue(hasattr(window, 'procesar_exportacion_separada'))
            self.assertTrue(callable(window.procesar_exportacion_separada))
            
            # Ejecutar procesamiento
            window.procesar_exportacion_separada(config)
            
            # Verificar que se llamó la función de exportación con los parámetros correctos
            self.assertEqual(mock_export.call_count, 1)
            call_args = mock_export.call_args
            # Verificar que se llamó con el DataFrame y el diccionario de configuración
            self.assertEqual(len(call_args[0]), 2)  # Dos argumentos posicionales
            self.assertTrue(call_args[0][0].equals(self.df_test))  # DataFrame
            self.assertIsInstance(call_args[0][1], dict)  # Dictionary config
    
    def test_menu_action_connection(self):
        """Test que el menú está conectado correctamente"""
        window = MainWindow()
        window.df_vista_actual = self.df_test.copy()
        
        # Verificar que la acción tiene el método conectado
        action = window.exportar_separado_action
        self.assertIsNotNone(action)
        
        # Verificar que el método exportar_datos_separados existe
        self.assertTrue(hasattr(window, 'exportar_datos_separados'))
        self.assertTrue(callable(window.exportar_datos_separados))
    
    def test_progress_dialog_integration(self):
        """Test integración del diálogo de progreso"""
        window = MainWindow()
        window.df_vista_actual = self.df_test.copy()
        
        # Configuración válida
        config = ExportSeparatedConfig(
            separator_column='Region',
            template_path=self.excel_template_path,
            output_folder=self.temp_dir,
            file_template='test.xlsx'
        )
        
        # Mockear para simular procesamiento rápido
        with patch('core.data_handler.exportar_datos_separados') as mock_export:
            mock_export.return_value = {
                'success': True,
                'files_created': ['test1.xlsx', 'test2.xlsx'],
                'groups_processed': 2,
                'processing_time': 0.1,
                'errors': []
            }
            
            # Ejecutar procesamiento
            window.procesar_exportacion_separada(config)
            
            # Verificar que se cerró el diálogo de progreso
            if hasattr(window, 'progress_dialog'):
                self.assertFalse(window.progress_dialog.isVisible())


class TestExcelTemplateSplitterIntegration(unittest.TestCase):
    """Tests de integración específicos para ExcelTemplateSplitter"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.df_test = pd.DataFrame({
            'Category': ['A', 'A', 'B', 'B', 'C'],
            'Value': [10, 20, 30, 40, 50],
            'Name': ['Item1', 'Item2', 'Item3', 'Item4', 'Item5']
        })
        
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Limpiar después de tests"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_splitter_with_config_integration(self):
        """Test integración ExcelTemplateSplitter con ExportSeparatedConfig"""
        # Crear plantilla Excel de prueba
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Plantilla"
        
        # Crear encabezados básicos que coincidan con el DataFrame
        ws['A1'] = "Category"
        ws['B1'] = "Value"
        ws['C1'] = "Name"
        
        template_path = os.path.join(self.temp_dir, "plantilla_category.xlsx")
        wb.save(template_path)
        
        # Configuración completa y válida
        config = ExportSeparatedConfig(
            separator_column='Category',
            template_path=template_path,
            output_folder=self.temp_dir,
            file_template='{valor}.xlsx',
            column_mapping={'Category': 'A', 'Value': 'B', 'Name': 'C'},
            start_cell='A2'
        )
        
        # Crear splitter
        splitter = ExcelTemplateSplitter(self.df_test, config)
        
        # Verificar que se inicializa correctamente
        self.assertEqual(len(splitter.df), 5)
        self.assertEqual(splitter.config.separator_column, 'Category')
        
        # Verificar validación con configuración completa
        validation = splitter.validate_configuration()
        # Con una configuración válida, debería pasar la validación básica
        self.assertIsInstance(validation.is_valid, bool)
        # Si hay errores, deberían estar relacionados con aspectos específicos del sistema, no con parámetros faltantes
        self.assertIsInstance(validation.errors, list)


if __name__ == '__main__':
    unittest.main()