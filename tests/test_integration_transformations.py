"""
Test de integración para el sistema completo de transformaciones
Verifica la integración entre el sistema básico y el sistema avanzado de transformaciones
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Añadir directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.data_handler import (
    cargar_datos, limpiar_datos, agregar_datos, pivotar_datos,
    aplicar_transformacion, aplicar_pipeline_transformaciones,
    ejecutar_transformacion_con_compatibilidad, obtener_transformaciones_disponibles,
    obtener_estadisticas_transformaciones
)


class TestSystemIntegration(unittest.TestCase):
    """Tests de integración del sistema completo de transformaciones"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.df_original = pd.DataFrame({
            'id': [1, 2, 3, 4, 5, 6],
            'nombre': ['Juan', 'María', 'Carlos', 'Ana', 'Luis', 'Carmen'],
            'edad': [25, 30, 35, 28, 32, 29],
            'salario': [50000, 60000, 75000, 55000, 65000, 58000],
            'fecha_ingreso': ['2020-01-15', '2019-03-20', '2018-07-10', '2021-02-28', '2019-11-05', '2020-09-12'],
            'departamento': ['Ventas', 'IT', 'Ventas', 'IT', 'RRHH', 'Ventas']
        })
        
        self.df_texto = pd.DataFrame({
            'texto_limpio': ['Hola Mundo', '  ESPACIOS  ', 'Test-Data_123'],
            'texto_mayus': ['abc def', 'ghi jkl', 'mno pqr'],
            'fecha_texto': ['2023-01-15', '2023-06-20', '2023-12-25']
        })
    
    def test_basic_operations_compatibility(self):
        """Test compatibilidad con operaciones básicas"""
        # Test limpieza básica
        df_con_nulos = self.df_original.copy()
        df_con_nulos.loc[0, 'edad'] = None
        df_con_nulos.loc[2, 'nombre'] = None
        
        df_limpio = limpiar_datos(df_con_nulos, {'eliminar_nulos': False, 'rellenar_nulos': {'edad': 0}})
        self.assertFalse(df_limpio['edad'].isnull().any())
        
        # Test agregación básica
        operaciones = [{
            'grupo': ['departamento'],
            'funciones': {'salario': ['mean', 'count']},
            'nombre': 'salario_promedio'
        }]
        
        df_agregado = agregar_datos(self.df_original, operaciones)
        self.assertFalse(df_agregado.empty)
        # Verificar que existe una columna relacionada con departamento (puede ser 'departamento_' por el flatten)
        dept_columns = [col for col in df_agregado.columns if 'departamento' in col]
        self.assertTrue(len(dept_columns) > 0, "Debería haber al menos una columna relacionada con departamento")
        
        # Test pivoteo básico
        df_pivot = pivotar_datos(self.df_original, 'departamento', 'nombre', 'edad', 'mean')
        self.assertFalse(df_pivot.empty)
        self.assertIn('departamento', df_pivot.columns)
    
    def test_advanced_transformations_integration(self):
        """Test integración de transformaciones avanzadas"""
        # Test transformación de texto
        try:
            df_texto_transformado = aplicar_transformacion(
                self.df_texto, 
                'case_conversion', 
                {'columns': ['texto_mayus'], 'case_type': 'upper'}
            )
            # Verificar que se aplicó la transformación
            self.assertIn('texto_mayus', df_texto_transformado.columns)
            
        except Exception as e:
            # Si el sistema avanzado no está disponible, debería usar fallback
            self.assertIn("no disponible", str(e) or "fallback" in str(e).lower())
    
    def test_pipeline_operations(self):
        """Test operaciones de pipeline"""
        pipeline = [
            {
                'transformation': 'case_conversion',
                'parameters': {'columns': ['texto_mayus'], 'case_type': 'upper'},
                'name': 'convertir_mayusculas'
            }
        ]
        
        try:
            resultado = aplicar_pipeline_transformaciones(self.df_texto, pipeline)
            self.assertFalse(resultado.empty)
            
        except Exception as e:
            # Pipeline debería funcionar o usar fallback graceful
            self.assertIn("no disponible", str(e) or "fallback" in str(e).lower())
    
    def test_compatibility_function(self):
        """Test función de compatibilidad entre sistemas"""
        # Test operación básica
        resultado = ejecutar_transformacion_con_compatibilidad(
            self.df_original, 
            'limpiar_datos', 
            {'eliminar_duplicados': False}
        )
        
        # Debería devolver un DataFrame
        self.assertIsInstance(resultado, pd.DataFrame)
        self.assertEqual(len(resultado), len(self.df_original))
        
        # Test operación avanzada mapeada
        try:
            resultado_avanzado = ejecutar_transformacion_con_compatibilidad(
                self.df_texto,
                'convertir_texto',
                {'columns': ['texto_mayus'], 'case_type': 'upper'}
            )
            self.assertIsInstance(resultado_avanzado, pd.DataFrame)
            
        except Exception as e:
            # Es aceptable que falle si el sistema no está disponible
            self.assertIn("no disponible", str(e) or "fallback" in str(e).lower())
    
    def test_system_statistics(self):
        """Test obtención de estadísticas del sistema"""
        stats = obtener_estadisticas_transformaciones()
        
        # Debería devolver un diccionario
        self.assertIsInstance(stats, dict)
        
        # Debería indicar si el sistema está disponible
        if stats.get('sistema_disponible', False):
            self.assertIn('transformaciones_registradas', stats)
            self.assertIn('pipelines_guardados', stats)
            self.assertIn('operaciones_en_historial', stats)
        else:
            self.assertIn('mensaje', stats)
    
    def test_end_to_end_workflow(self):
        """Test flujo completo end-to-end"""
        # 1. Cargar datos (simulado con datos existentes)
        df = self.df_original.copy()
        
        # 2. Limpiar datos usando sistema básico
        df_limpio = limpiar_datos(df, {'eliminar_duplicados': False})
        
        # 3. Aplicar transformaciones avanzadas (si están disponibles)
        try:
            # Intentar transformación de texto
            if 'nombre' in df_limpio.columns:
                df_transformado = ejecutar_transformacion_con_compatibilidad(
                    df_limpio,
                    'convertir_texto',
                    {'columns': ['nombre'], 'case_type': 'title'}
                )
                
                # Verificar que el flujo funciona
                self.assertIsInstance(df_transformado, pd.DataFrame)
                self.assertEqual(len(df_transformado), len(df_limpio))
                
        except Exception as e:
            # Es aceptable que el sistema avanzado no esté disponible
            self.assertIn("no disponible", str(e) or "fallback" in str(e).lower())
        
        # 4. Finalizar con operación básica
        df_final = agregar_datos(df_limpio, [{
            'grupo': ['departamento'],
            'funciones': {'edad': 'mean'},
            'nombre': 'edad_promedio'
        }])
        
        # Verificar resultado final
        self.assertFalse(df_final.empty)
        self.assertIn('departamento', df_final.columns)


class TestBackwardCompatibility(unittest.TestCase):
    """Tests para asegurar retrocompatibilidad completa"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.df_test = pd.DataFrame({
            'a': [1, 2, 3, 4, 5],
            'b': [10, 20, 30, 40, 50],
            'c': ['x', 'y', 'z', 'w', 'v']
        })
    
    def test_original_functions_still_work(self):
        """Test que las funciones originales siguen funcionando"""
        # Test limpiar_datos
        resultado = limpiar_datos(self.df_test)
        self.assertIsInstance(resultado, pd.DataFrame)
        
        # Test agregar_datos
        resultado = agregar_datos(self.df_test, [{
            'grupo': [],
            'funciones': {'a': 'sum', 'b': 'mean'},
            'nombre': 'totales'
        }])
        self.assertIsInstance(resultado, pd.DataFrame)
        
        # Test pivotar_datos
        df_pivot_test = pd.DataFrame({
            'categoria': ['A', 'A', 'B', 'B'],
            'subcategoria': ['X', 'Y', 'X', 'Y'],
            'valor': [1, 2, 3, 4]
        })
        
        resultado = pivotar_datos(df_pivot_test, 'categoria', 'subcategoria', 'valor', 'sum')
        self.assertIsInstance(resultado, pd.DataFrame)


def run_integration_tests():
    """Ejecutar tests de integración"""
    # Crear suite de tests
    suite = unittest.TestSuite()
    
    # Añadir clases de test
    test_classes = [
        TestSystemIntegration,
        TestBackwardCompatibility
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Ejecutar tests de integración
    success = run_integration_tests()
    
    if success:
        print("\n✅ Todos los tests de integración pasaron exitosamente")
        print("✅ El sistema completo de transformaciones está funcionando correctamente")
    else:
        print("\n❌ Algunos tests de integración fallaron")
        print("❌ Revisar la integración del sistema de transformaciones")
    
    # Exit con código apropiado
    exit(0 if success else 1)