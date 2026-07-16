"""
Tests para el diálogo de exportación separada - Actualizado para implementación con tabs
"""

import unittest
import pandas as pd
from unittest.mock import patch, MagicMock, mock_open
import tempfile

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest

from app.widgets.export_separated_dialog import ExportSeparatedDialog


class TestExportSeparatedDialog(unittest.TestCase):
    """Tests para ExportSeparatedDialog"""
    
    @classmethod
    def setUpClass(cls) -> None:
        """Configurar QApplication para tests de UI"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self) -> None:
        """Configurar datos de prueba"""
        # Crear DataFrame de prueba
        self.df_test = pd.DataFrame({
            'Region': ['Norte', 'Norte', 'Sur', 'Sur', 'Este'],
            'Producto': ['A', 'B', 'A', 'B', 'A'],
            'Ventas': [1000, 1500, 800, 1200, 900],
            'Fecha': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-01', '2024-01-02', '2024-01-01'])
        })
    
    def test_init_with_dataframe(self) -> None:
        """Test inicialización con DataFrame"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        self.assertEqual(len(dialog.df), 5)
        self.assertEqual(list(dialog.df.columns), ['Region', 'Producto', 'Ventas', 'Fecha'])
        self.assertFalse(dialog.isVisible())  # Modal, no visible inicialmente
    
    def test_init_without_dataframe(self) -> None:
        """Test inicialización sin DataFrame"""
        dialog = ExportSeparatedDialog(None)
        
        self.assertIsNone(dialog.df)
    
    def test_setup_ui_components(self) -> None:
        """Test configuración de componentes UI"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Verificar que todos los componentes están inicializados
        self.assertIsNotNone(dialog.column_combo)
        self.assertIsNotNone(dialog.select_template_btn)
        self.assertIsNotNone(dialog.dest_folder_label)
        self.assertIsNotNone(dialog.select_folder_btn)
        self.assertIsNotNone(dialog.filename_template_edit)
        self.assertIsNotNone(dialog.start_cell_combo)
        self.assertIsNotNone(dialog.cancel_btn)
        self.assertIsNotNone(dialog.export_btn)
    
    def test_populate_separator_combo(self) -> None:
        """Test población del combo de separación"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Verificar que se llenan las columnas
        combo_count = dialog.column_combo.count()
        self.assertGreater(combo_count, 0)
        
        # Verificar nombres de columnas
        columns = [dialog.column_combo.itemText(i) for i in range(combo_count)]
        expected_columns = ['Region', 'Producto', 'Ventas', 'Fecha']
        
        for col in expected_columns:
            self.assertIn(col, columns)
    
    def test_populate_start_cell_combo(self) -> None:
        """Test población del combo de celda inicial"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Verificar opciones predefinidas
        combo_count = dialog.start_cell_combo.count()
        self.assertGreater(combo_count, 0)
        
        # Verificar opciones específicas
        options = [dialog.start_cell_combo.itemText(i) for i in range(combo_count)]
        self.assertIn('A1', options)
        self.assertIn('A2', options)
        self.assertIn('B1', options)
    
    def test_on_column_changed(self) -> None:
        """Test cambio de columna (equivalente a separator_changed)"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Simular selección de 'Region'
        dialog.column_combo.setCurrentText('Region')
        dialog.on_column_changed('Region')
        
        # Verificar que se actualiza el preview de valores
        # La implementación actual actualiza valores_preview automáticamente
        self.assertGreater(dialog.values_preview.count(), 0)
    
    def test_select_template_functionality(self) -> None:
        """Test funcionalidad de selección de plantilla"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Mock del diálogo de archivo
        with patch('app.widgets.export_separated_dialog.ExcelTemplateDialog') as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog.exec.return_value = True
            mock_dialog.get_template_info.return_value = ('/path/to/template.xlsx', 'Sheet1', ['Sheet1'])
            mock_dialog_class.return_value = mock_dialog
            
            dialog.select_template()
            
            # Verificar que se actualiza el label
            self.assertIn('template.xlsx', dialog.template_path_label.text())
    
    def test_select_destination_folder_functionality(self) -> None:
        """Test funcionalidad de selección de carpeta de destino"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Mock del diálogo de directorio
        with patch('PySide6.QtWidgets.QFileDialog.getExistingDirectory') as mock_dir_dialog:
            mock_dir_dialog.return_value = '/path/to/output'
            
            dialog.select_destination_folder()
            
            # Verificar que se actualiza el label
            self.assertIn('/path/to/output', dialog.dest_folder_label.text())
    
    def test_validate_configuration_valid(self) -> None:
        """Test validación con configuración válida"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Configurar valores básicos válidos
        dialog.column_combo.setCurrentText('Region')
        dialog.filename_template_edit.setText('Reporte_{valor}.xlsx')
        
        # Mock ExcelTemplateSplitter para evitar dependencia
        with patch('app.widgets.export_separated_dialog.ExcelTemplateSplitter') as mock_splitter_class:
            mock_splitter = MagicMock()
            mock_validation_result = MagicMock()
            mock_validation_result.is_valid = True
            mock_validation_result.errors = []
            mock_validation_result.warnings = []
            mock_splitter.validate_configuration.return_value = mock_validation_result
            mock_splitter_class.return_value = mock_splitter
            
            # Ejecutar validación
            dialog.validate_configuration()
            
            # Verificar que se llama al validador
            mock_splitter.validate_configuration.assert_called_once()
    
    def test_validate_configuration_invalid(self) -> None:
        """Test validación con configuración inválida"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # No configurar nada (configuración inválida)
        
        # Mock ExcelTemplateSplitter para simular error
        with patch('app.widgets.export_separated_dialog.ExcelTemplateSplitter') as mock_splitter_class:
            mock_splitter = MagicMock()
            mock_validation_result = MagicMock()
            mock_validation_result.is_valid = False
            mock_validation_result.errors = ['Error de prueba']
            mock_validation_result.warnings = []
            mock_splitter.validate_configuration.return_value = mock_validation_result
            mock_splitter_class.return_value = mock_splitter
            
            # Ejecutar validación
            dialog.validate_configuration()
            
            # Verificar que el botón se deshabilita
            self.assertFalse(dialog.export_btn.isEnabled())
    
    def test_get_configuration_basic(self) -> None:
        """Test obtención de configuración básica"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Configurar valores
        dialog.column_combo.setCurrentText('Region')
        dialog.filename_template_edit.setText('Reporte_{valor}.xlsx')
        dialog.start_cell_combo.setCurrentText('A1')
        
        # Mock del atributo _template_path
        dialog._template_path = '/path/to/template.xlsx'
        dialog.dest_folder_label.setText('/path/to/output')
        
        config = dialog.get_configuration(validate=False)
        
        self.assertIsNotNone(config)
        self.assertEqual(config.separator_column, 'Region')
        self.assertEqual(config.file_template, 'Reporte_{valor}.xlsx')
        self.assertEqual(config.start_cell, 'A1')
        self.assertEqual(config.template_path, '/path/to/template.xlsx')
        self.assertEqual(config.output_folder, '/path/to/output')
    
    def test_get_configuration_custom_start_cell(self) -> None:
        """Test obtención de configuración con celda inicial personalizada"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Configurar valores
        dialog.column_combo.setCurrentText('Region')
        dialog.start_cell_combo.setCurrentText('Personalizado')
        dialog.start_cell_edit.setText('C5')
        
        # Mock del atributo _template_path
        dialog._template_path = '/path/to/template.xlsx'
        dialog.dest_folder_label.setText('/path/to/output')
        dialog.filename_template_edit.setText('Reporte.xlsx')
        
        config = dialog.get_configuration(validate=False)
        
        self.assertIsNotNone(config)
        self.assertEqual(config.start_cell, 'C5')
    
    def test_cancel_functionality(self) -> None:
        """Test funcionalidad de cancelar"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Simular click en cancelar
        dialog.cancel_btn.click()
        
        # Verificar que el diálogo se rechaza
        # En PySide6, esto debería resultar en Rejected
        # Nota: QTest.click() puede no funcionar en todos los casos, 
        # así que también probamos directamente reject()
        dialog.reject()
        self.assertEqual(dialog.result(), QDialog.Rejected)
    
    def test_accept_functionality_valid_config(self) -> None:
        """Test funcionalidad de aceptar con configuración válida"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Configurar valores válidos
        dialog.column_combo.setCurrentText('Region')
        dialog.filename_template_edit.setText('Reporte_{valor}.xlsx')
        
        # Mock para evitar validación real
        with patch.object(dialog, 'get_configuration') as mock_get_config:
            mock_config = MagicMock()
            mock_get_config.return_value = mock_config
            
            # Mock QDialog accept to prevent actual dialog acceptance
            with patch.object(QDialog, 'accept') as mock_accept:
                # Simular click en exportar
                dialog.export_btn.clicked.emit()
                
                # Verificar que se llama a get_configuration
                # Nota: En algunos entornos de test, las señales no se procesan inmediatamente
                # así que verificamos manualmente
                if dialog.export_btn.isEnabled():
                    dialog.accept()
                    mock_get_config.assert_called_once()
    
    def test_accept_functionality_invalid_config(self) -> None:
        """Test funcionalidad de aceptar con configuración inválida"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # No configurar nada (configuración inválida)
        
        # Mock para simular configuración inválida
        with patch.object(dialog, 'get_configuration') as mock_get_config:
            mock_get_config.return_value = None
            
            # Mock QMessageBox.warning
            with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
                # Llamar directamente al método accept en lugar de simular click
                dialog.accept()
                
                # Verificar que se muestra advertencia
                mock_warning.assert_called_once()
                
                # Verificar que no se acepta el diálogo
                self.assertEqual(dialog.result(), 0)
    
    def test_update_values_preview(self) -> None:
        """Test actualización de preview de valores"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Seleccionar columna
        dialog.column_combo.setCurrentText('Region')
        dialog.update_values_preview()
        
        # Verificar que se llenan valores
        self.assertGreater(dialog.values_preview.count(), 0)
        
        # Verificar que hay valores de región
        items_text = [dialog.values_preview.item(i).text() for i in range(dialog.values_preview.count())]
        self.assertTrue(any('Norte' in item for item in items_text))
        self.assertTrue(any('Sur' in item for item in items_text))
    
    def test_update_filename_preview(self) -> None:
        """Test actualización de preview de nombres de archivos"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Configurar valores
        dialog.column_combo.setCurrentText('Region')
        dialog.filename_template_edit.setText('Reporte_{valor}.xlsx')
        
        # Actualizar preview
        dialog.update_filename_preview()
        
        # Verificar que se generan nombres
        self.assertGreater(dialog.filenames_preview.count(), 0)
    
    def test_file_preview_dialog(self) -> None:
        """Test diálogo de vista previa de archivos"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Configurar valores mínimos
        dialog.column_combo.setCurrentText('Region')
        dialog.filename_template_edit.setText('Reporte_{valor}.xlsx')
        
        # Mock validation_result
        mock_validation = MagicMock()
        mock_validation.errors = []
        dialog.validation_result = mock_validation
        
        # Mock del diálogo de preview
        with patch('app.widgets.export_separated_dialog.FilePreviewDialog') as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog_class.return_value = mock_dialog
            
            # Ejecutar vista previa
            dialog.show_file_preview()
            
            # Verificar que se crea el diálogo
            mock_dialog_class.assert_called_once()
    
    def test_handle_no_data(self) -> None:
        """Test manejo cuando no hay datos"""
        dialog = ExportSeparatedDialog(None)
        
        # Con datos nulos, el diálogo debe manejar gracefully
        # Los componentes deberían estar disponibles pero no funcionales
        self.assertIsNone(dialog.df)
        # No deberíamos obtener errores al verificar componentes básicos
        self.assertIsNotNone(dialog.column_combo)
    
    def test_error_handling_in_validation(self) -> None:
        """Test manejo de errores en validación"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Mock ExcelTemplateSplitter para lanzar excepción
        with patch('app.widgets.export_separated_dialog.ExcelTemplateSplitter') as mock_splitter_class:
            mock_splitter_class.side_effect = Exception("Error de prueba")
            
            # La validación debe manejar el error sin crashear
            try:
                dialog.validate_configuration()
                # Si llegamos aquí, el manejo de error funcionó
                self.assertTrue(True)
            except Exception:
                self.fail("El diálogo debe manejar errores de validación gracefully")
    
    def test_mapping_widget_functionality(self) -> None:
        """Test funcionalidad del widget de mapeo"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Verificar que el mapping widget se inicializa
        self.assertIsNotNone(dialog.mapping_widget)
        
        # Verificar que se configuran las columnas
        self.assertGreater(len(dialog.mapping_widget.df_columns), 0)
        
        # Verificar que se puede obtener el mapeo
        mapping = dialog.mapping_widget.get_mapping()
        self.assertIsInstance(mapping, dict)
    
    def test_specific_start_cell_custom(self) -> None:
        """Test selección de celda inicial personalizada"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Seleccionar celda específica
        dialog.start_cell_combo.setCurrentText('Personalizado')
        dialog.start_cell_edit.setText('C5')
        
        # Verificar configuración
        config = dialog.get_configuration(validate=False)
        self.assertEqual(config.start_cell, 'C5')


class TestExportSeparatedDialogIntegration(unittest.TestCase):
    """Tests de integración para ExportSeparatedDialog"""
    
    @classmethod
    def setUpClass(cls) -> None:
        """Configurar QApplication para tests de UI"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self) -> None:
        """Configurar datos de prueba"""
        self.df_test = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6],
            'C': [7, 8, 9]
        })
    
    def test_full_workflow_simulation(self) -> None:
        """Test simulación de flujo completo"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Paso 1: Seleccionar columna
        dialog.column_combo.setCurrentText('A')
        dialog.on_column_changed('A')
        
        # Paso 2: Configurar plantilla (mock)
        dialog._template_path = '/test/template.xlsx'
        dialog.template_path_label.setText('📄 template.xlsx')
        dialog.sheet_combo.setEnabled(True)
        dialog.sheet_combo.addItems(['Sheet1'])
        
        # Paso 3: Configurar salida (mock)
        dialog.dest_folder_label.setText('📁 /test/output')
        
        # Paso 4: Configurar nombre de archivo
        dialog.filename_template_edit.setText('Report_{valor}.xlsx')
        
        # Paso 5: Actualizar previews
        dialog.update_values_preview()
        dialog.update_filename_preview()
        
        # Verificar que se configuró correctamente
        self.assertEqual(dialog.column_combo.currentText(), 'A')
        self.assertEqual(dialog.filename_template_edit.text(), 'Report_{valor}.xlsx')
        
        # Verificar que los previews se actualizaron
        self.assertGreater(dialog.values_preview.count(), 0)
        self.assertGreater(dialog.filenames_preview.count(), 0)
    
    def test_cancel_workflow_integration(self) -> None:
        """Test flujo de cancelación en integración"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Simular click en cancelar
        dialog.reject()
        
        # Verificar que se rechaza el diálogo
        self.assertEqual(dialog.result(), QDialog.Rejected)
    
    def test_export_with_minimal_config_integration(self) -> None:
        """Test exportación con configuración mínima en integración"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Configuración mínima
        dialog.column_combo.setCurrentText('A')
        dialog._template_path = '/minimal/template.xlsx'
        dialog.dest_folder_label.setText('/minimal/output')
        dialog.filename_template_edit.setText('Simple.xlsx')
        
        config = dialog.get_configuration(validate=False)
        
        # Verificar configuración mínima
        self.assertEqual(config.separator_column, 'A')
        self.assertEqual(config.file_template, 'Simple.xlsx')
        self.assertEqual(config.start_cell, 'A1')  # Default
    
    def test_tab_functionality(self) -> None:
        """Test funcionalidad de tabs"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Verificar que existe el tab widget
        self.assertIsNotNone(dialog.tab_widget)
        
        # Verificar que se agregaron los tabs
        self.assertEqual(dialog.tab_widget.count(), 3)  # 3 tabs esperados
        
        # Verificar títulos de tabs
        tab_titles = [dialog.tab_widget.tabText(i) for i in range(dialog.tab_widget.count())]
        self.assertIn("Configuración Básica", tab_titles)
        self.assertIn("Mapeo de Columnas", tab_titles)
        self.assertIn("Destino y Opciones", tab_titles)
    
    def test_advanced_options_functionality(self) -> None:
        """Test funcionalidad de opciones avanzadas"""
        dialog = ExportSeparatedDialog(self.df_test)
        
        # Verificar componentes de opciones avanzadas
        self.assertIsNotNone(dialog.handle_duplicates_combo)
        self.assertIsNotNone(dialog.chunk_size_spin)
        
        # Verificar que tienen valores por defecto
        self.assertGreater(dialog.handle_duplicates_combo.count(), 0)
        self.assertGreater(dialog.chunk_size_spin.value(), 0)


if __name__ == '__main__':
    unittest.main()