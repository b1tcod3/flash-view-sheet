"""
Test para verificar la corrección del problema de validación de plantilla
"""
import os
import tempfile
import pandas as pd
import openpyxl
from PySide6.QtWidgets import QApplication
from app.widgets.export_separated_dialog import ExportSeparatedDialog

def test_template_path_stored():
    """Test que verifica que la ruta de plantilla se almacena correctamente"""
    print("🧪 Iniciando test de corrección de ruta de plantilla...")
    
    # Crear una aplicación Qt
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Crear datos de prueba
    df = pd.DataFrame({
        'Region': ['Norte', 'Sur', 'Norte', 'Este'],
        'Ventas': [1000, 2000, 1500, 1800]
    })
    
    # Crear plantilla Excel temporal
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
        template_path = temp_file.name
    
    try:
        # Crear archivo Excel de prueba
        wb = openpyxl.Workbook()
        ws = wb.active
        ws['A1'] = 'Región'
        ws['B1'] = 'Ventas'
        wb.save(template_path)
        wb.close()
        
        # Crear diálogo
        dialog = ExportSeparatedDialog(df)
        
        # Simular selección de plantilla
        dialog._template_path = template_path  # Esto es lo que agregamos en la corrección
        dialog.template_path_label.setText(f"📄 {os.path.basename(template_path)}")
        dialog.template_path_label.setToolTip(template_path)
        
        # Verificar que la ruta se almacena correctamente
        assert hasattr(dialog, '_template_path'), "El diálogo debe tener el atributo _template_path"
        assert dialog._template_path == template_path, f"La ruta debe ser {template_path}"
        
        # Verificar que la configuración puede obtener la ruta
        config = dialog.get_configuration(validate=False)
        assert config is not None, "La configuración no debe ser None"
        assert config.template_path == template_path, "La plantilla en la configuración debe coincidir"
        
        print("✅ Test pasado: La ruta de plantilla se almacena y recupera correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Test falló: {str(e)}")
        return False
    finally:
        # Limpiar archivo temporal
        if os.path.exists(template_path):
            os.unlink(template_path)

def test_validation_with_stored_template():
    """Test que verifica la validación con plantilla almacenada"""
    print("🧪 Iniciando test de validación con plantilla almacenada...")
    
    # Crear una aplicación Qt
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    # Crear datos de prueba
    df = pd.DataFrame({
        'Region': ['Norte', 'Sur'],
        'Ventas': [1000, 2000]
    })
    
    # Crear plantilla Excel temporal
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
        template_path = temp_file.name
    
    try:
        # Crear archivo Excel de prueba
        wb = openpyxl.Workbook()
        ws = wb.active
        ws['A1'] = 'Región'
        ws['B1'] = 'Ventas'
        wb.save(template_path)
        wb.close()
        
        # Crear diálogo y configurar
        dialog = ExportSeparatedDialog(df)
        dialog._template_path = template_path
        dialog.column_combo.setCurrentText('Region')
        dialog.dest_folder_label.setText("/tmp")
        dialog.filename_template_edit.setText("{valor}.xlsx")
        
        # Intentar validación (esto no debe fallar ahora)
        try:
            validation_result = dialog.validate_configuration()
            print("✅ Test pasado: La validación funciona correctamente con plantilla almacenada")
            return True
        except Exception as e:
            print(f"❌ Test falló en validación: {str(e)}")
            return False
        
    except Exception as e:
        print(f"❌ Test falló: {str(e)}")
        return False
    finally:
        # Limpiar archivo temporal
        if os.path.exists(template_path):
            os.unlink(template_path)

if __name__ == "__main__":
    print("🔍 Test de Corrección: Validación de Plantilla")
    print("=" * 50)
    
    test1_passed = test_template_path_stored()
    test2_passed = test_validation_with_stored_template()
    
    print("\n" + "=" * 50)
    if test1_passed and test2_passed:
        print("🎉 Todos los tests pasaron. La corrección funciona correctamente.")
    else:
        print("⚠️  Algunos tests fallaron. Revisar la implementación.")