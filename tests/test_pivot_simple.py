"""
Test Simplificado de Integración - Tabla Pivote
Prueba la funcionalidad core sin dependencias de GUI
"""

import sys
from pathlib import Path
import unittest
import pandas as pd

# Agregar ruta del proyecto
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Test básico de funcionalidad core
def test_core_functionality() -> None:
    """Test básico de funcionalidad core"""
    print("🧪 Test Básico de Funcionalidad Core")
    
    # Crear datos de prueba
    test_data = pd.DataFrame({
        'region': ['Norte', 'Sur', 'Norte', 'Sur', 'Este', 'Oeste'] * 5,
        'categoria': ['A', 'B', 'A', 'B', 'A', 'B'] * 5,
        'producto': ['X', 'Y', 'Z', 'X', 'Y', 'Z'] * 5,
        'ventas': [100, 200, 150, 300, 250, 180] * 5,
        'unidades': [10, 20, 15, 30, 25, 18] * 5,
        'vendedor': ['Juan', 'Maria', 'Carlos', 'Ana', 'Luis', 'Carmen'] * 5
    })
    
    try:
        # Test importación de clases core
        print("   📦 Probando imports...")
        from core.pivot import SimplePivotTable, CombinedPivotTable, PivotFilterManager
        from core.pivot import PivotAggregationManager
        print("   ✅ Imports - OK")
        
        # Test Simple Pivot
        print("   🔄 Probando Simple Pivot...")
        simple_pivot = SimplePivotTable()
        result = simple_pivot.execute(test_data, {
            'index': 'region',
            'columns': 'categoria',
            'values': 'ventas',
            'aggfunc': 'sum'
        })
        assert result is not None and not result.empty, "Simple pivot falló"
        assert len(result) > 0, "Simple pivot sin resultados"
        print("   ✅ Simple Pivot - OK")
        
        # Test Combined Pivot
        print("   🔄 Probando Combined Pivot...")
        combined_pivot = CombinedPivotTable()
        result = combined_pivot.execute(test_data, {
            'index': ['region', 'categoria'],
            'columns': 'producto',
            'values': ['ventas', 'unidades'],
            'aggfuncs': ['sum', 'mean']
        })
        assert result is not None and not result.empty, "Combined pivot falló"
        assert len(result) > 0, "Combined pivot sin resultados"
        print("   ✅ Combined Pivot - OK")
        
        # Test Filter Manager
        print("   🔍 Probando Filter Manager...")
        filter_manager = PivotFilterManager()
        filters = {
            'region': {'type': 'equals', 'value': 'Norte'},
            'ventas': {'type': 'greater_than', 'value': 150}
        }
        # Añadir filtros desde diccionario
        filter_manager.add_filters_from_dict(filters)
        filtered_df = filter_manager.apply_filters(test_data)
        assert filtered_df is not None, "Filter manager falló"
        assert all(filtered_df['region'] == 'Norte'), "Filtro de región falló"
        assert all(filtered_df['ventas'] > 150), "Filtro de ventas falló"
        print("   ✅ Filter Manager - OK")
        
        # Test Aggregation Manager
        print("   📊 Probando Aggregation Manager...")
        agg_manager = PivotAggregationManager()
        available_functions = agg_manager.get_valid_aggregations('numeric')
        assert 'sum' in available_functions, "Función sum no disponible"
        assert 'mean' in available_functions, "Función mean no disponible"
        assert agg_manager.predefined_aggregations is not None, "Predefined aggregations no disponible"
        print("   ✅ Aggregation Manager - OK")
        
        print("   🎉 Todos los tests core pasaron!")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en tests: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_widget_creation() -> None:
    """Test básico de creación de widgets sin GUI"""
    print("\n🧪 Test de Creación de Widgets")
    
    try:
        # Test importación de widgets
        print("   📦 Probando imports de widgets...")
        from app.widgets.pivot_table_widget import PivotTableWidget
        from app.widgets.pivot_config_dialog import PivotConfigDialog
        from app.widgets.pivot_filter_panel import PivotFilterPanel
        from app.widgets.pivot_aggregation_panel import PivotAggregationPanel
        print("   ✅ Imports de Widgets - OK")
        
        # Test imports de funcionalidad de widgets
        print("   🔧 Probando funcionalidad de widgets...")
        
        # Verificar que las clases existen
        assert hasattr(PivotTableWidget, '__init__'), "PivotTableWidget sin __init__"
        assert hasattr(PivotConfigDialog, '__init__'), "PivotConfigDialog sin __init__"
        assert hasattr(PivotFilterPanel, '__init__'), "PivotFilterPanel sin __init__"
        assert hasattr(PivotAggregationPanel, '__init__'), "PivotAggregationPanel sin __init__"
        print("   ✅ Clases de Widgets - OK")
        
        # Verificar que tienen métodos esperados
        assert hasattr(PivotTableWidget, 'get_current_parameters'), "PivotTableWidget sin get_current_parameters"
        assert hasattr(PivotTableWidget, 'validate_parameters'), "PivotTableWidget sin validate_parameters"
        print("   ✅ Métodos de Widgets - OK")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en test de widgets: {e}")
        return False

def test_main_integration() -> None:
    """Test básico de integración con main.py"""
    print("\n🧪 Test de Integración con Main")
    
    try:
        # Test importación de main
        print("   📦 Probando import de main...")
        # No ejecutamos main para evitar problemas de GUI
        import main
        print("   ✅ Import de main - OK")
        
        # Verificar que MainWindow tiene los componentes necesarios
        assert hasattr(main, 'MainWindow'), "MainWindow no encontrado en main"
        print("   ✅ MainWindow - OK")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en test de integración: {e}")
        return False

def test_file_structure() -> None:
    """Test de estructura de archivos"""
    print("\n🧪 Test de Estructura de Archivos")
    
    required_files = [
        'app/widgets/pivot_table_widget.py',
        'app/widgets/pivot_config_dialog.py',
        'app/widgets/pivot_filter_panel.py',
        'app/widgets/pivot_aggregation_panel.py',
        'app/widgets/__init__.py',
        'core/pivot/pivot_table.py',
        'core/pivot/pivot_filters.py',
        'core/pivot/pivot_aggregations.py',
        'core/pivot/__init__.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"   ❌ Archivos faltantes: {missing_files}")
        return False
    else:
        print("   ✅ Estructura de archivos - OK")
        return True

def run_simplified_tests() -> None:
    """Ejecutar tests simplificados"""
    print("=" * 60)
    print("🧪 TESTS SIMPLIFICADOS - TABLA PIVOTE")
    print("=" * 60)
    
    tests = [
        ("Funcionalidad Core", test_core_functionality),
        ("Creación de Widgets", test_widget_creation),
        ("Integración con Main", test_main_integration),
        ("Estructura de Archivos", test_file_structure)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Ejecutando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   Resultado: {status}")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append((test_name, False))
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 TODOS LOS TESTS SIMPLIFICADOS PASARON")
        print("\n📋 Estado del Sistema:")
        print("   ✅ Funcionalidad core implementada y funcional")
        print("   ✅ Widgets de UI creados y disponibles")
        print("   ✅ Integración con sistema principal completada")
        print("   ✅ Estructura de archivos completa")
        return True
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        return False

if __name__ == "__main__":
    success = run_simplified_tests()
    sys.exit(0 if success else 1)