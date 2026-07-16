#!/usr/bin/env python3
"""
Ejemplo de rendimiento para carga de carpeta con Flash Sheet

Este ejemplo demuestra optimizaciones para procesar grandes volúmenes de datos:
- Procesamiento por lotes (chunked processing)
- Carga diferida de metadatos
- Monitoreo de progreso
- Gestión eficiente de memoria
"""

import sys
from pathlib import Path
import time
import pandas as pd

# Añadir el directorio raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from core.loaders.folder_loader import FolderLoader
from core.consolidation.excel_consolidator import ExcelConsolidator

def performance_comparison() -> None:
    """Comparar métodos de procesamiento para demostrar optimizaciones"""

    print("🚀 Flash Sheet - Comparativa de Rendimiento")
    print("=" * 55)

    folder_path = str(Path(__file__).parent / 'sample_data')

    try:
        # Método 1: Procesamiento tradicional (uno por uno)
        print("1️⃣ Método 1: Procesamiento tradicional")
        start_time = time.time()

        loader = FolderLoader(folder_path)
        consolidator1 = ExcelConsolidator()

        files = loader.get_excel_files()
        for file_path in files:
            df = pd.read_excel(file_path)
            consolidator1.add_dataframe(df, Path(file_path).name)

        result1 = consolidator1.consolidate()
        time1 = time.time() - start_time

        print(f"   ⏱️  Tiempo: {time1:.2f} segundos")
        print(f"   📊 Resultado: {len(result1)} filas, {len(result1.columns)} columnas")
        print()

        # Método 2: Procesamiento por lotes optimizado
        print("2️⃣ Método 2: Procesamiento por lotes (Optimizado)")
        start_time = time.time()

        consolidator2 = ExcelConsolidator()

        # Callback para mostrar progreso
        def progress_callback(progress: float) -> None:
            print(f"     Progreso: {progress:.1f}%")

        result2 = consolidator2.consolidate_chunked(
            files,
            chunk_size=2,  # Procesar de 2 en 2 archivos
            progress_callback=progress_callback
        )
        time2 = time.time() - start_time

        print(f"   ⏱️  Tiempo: {time2:.2f} segundos")
        print(f"   📊 Resultado: {len(result2)} filas, {len(result2.columns)} columnas")
        print()

        # Comparación
        print("3️⃣ Comparación de rendimiento:")
        speedup = time1 / time2 if time2 > 0 else 1
        print(f"   🚀 Aceleración: {speedup:.2f}x más rápido")
        print(f"   💾 Ahorro de tiempo: {(time1 - time2):.1f} segundos")
        print()

        # Verificar que los resultados son equivalentes
        print("4️⃣ Verificación de integridad:")
        if len(result1) == len(result2) and len(result1.columns) == len(result2.columns):
            print("   ✅ Resultados equivalentes")
        else:
            print("   ❌ Resultados diferentes - posible error")

        # Comparar algunas estadísticas
        if 'Total' in result1.columns and 'Total' in result2.columns:
            sum1 = result1['Total'].sum()
            sum2 = result2['Total'].sum()
            if abs(sum1 - sum2) < 0.01:
                print(f"   ✅ Suma total correcta: ${sum1:.2f}")
            else:
                print(f"   ❌ Diferencia en suma: ${abs(sum1 - sum2):.2f}")
        print()

    except Exception as e:
        print(f"❌ Error en comparación: {e}")
        import traceback
        traceback.print_exc()

def large_scale_simulation() -> None:
    """Simular procesamiento de un gran número de archivos"""

    print("5️⃣ Simulación de procesamiento a gran escala")
    print("=" * 50)

    # Crear archivos adicionales para simular carga mayor
    import tempfile
    import shutil

    temp_dir = tempfile.mkdtemp()
    try:
        # Copiar archivos existentes y crear más
        sample_dir = str(Path(__file__).parent / 'sample_data')

        # Copiar archivos existentes
        for filename in Path(sample_dir).iterdir():
            if filename.suffix == '.xlsx':
                shutil.copy2(
                    str(filename),
                    str(Path(temp_dir) / filename.name)
                )

        # Crear archivos adicionales (simulando más datos)
        base_df = pd.read_excel(str(Path(sample_dir) / 'ventas_q1.xlsx'))

        for i in range(6, 16):  # Crear archivos ventas_q6.xlsx hasta ventas_q15.xlsx
            # Modificar ligeramente los datos para simular diferentes períodos
            modified_df = base_df.copy()
            modified_df['Total'] = modified_df['Total'] * (0.8 + i * 0.05)  # Variación en ventas

            filename = f'ventas_q{i}.xlsx'
            modified_df.to_excel(str(Path(temp_dir) / filename), index=False)

        print(f"   📁 Creados {len(list(Path(temp_dir).iterdir()))} archivos de simulación en {temp_dir}")

        # Procesar con método optimizado
        print("   ⚡ Procesando con método optimizado...")
        start_time = time.time()

        loader = FolderLoader(temp_dir)
        consolidator = ExcelConsolidator()

        files = loader.get_excel_files()
        print(f"   📊 Procesando {len(files)} archivos...")

        processed_count = 0
        def progress_callback(progress: float) -> None:
            nonlocal processed_count
            current_count = int(progress * len(files) / 100)
            if current_count > processed_count:
                print(f"     Progreso: {current_count}/{len(files)} archivos ({progress:.1f}%)")
                processed_count = current_count

        result = consolidator.consolidate_chunked(
            files,
            chunk_size=3,  # Procesar de 3 en 3 para simular optimización
            progress_callback=progress_callback
        )

        processing_time = time.time() - start_time

        print(f"   ⏱️  Tiempo de procesamiento: {processing_time:.2f} segundos")
        print(f"   📊 Dataset final: {len(result)} filas, {len(result.columns)} columnas")
        print(f"   📈 Rendimiento: {len(result) / processing_time:.1f} filas/segundo")
        print()

    except Exception as e:
        print(f"❌ Error en simulación: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Limpiar archivos temporales
        shutil.rmtree(temp_dir, ignore_errors=True)

def memory_optimization_demo() -> None:
    """Demostrar optimizaciones de memoria"""

    print("6️⃣ Optimizaciones de memoria")
    print("=" * 35)

    folder_path = str(Path(__file__).parent / 'sample_data')
    loader = FolderLoader(folder_path)

    print("   📊 Demostrando caché de metadatos:")

    # Primera carga (sin caché)
    start_time = time.time()
    meta1 = loader.get_file_metadata(loader.get_excel_files()[0])
    time1 = time.time() - start_time

    # Segunda carga (con caché)
    start_time = time.time()
    meta2 = loader.get_file_metadata(loader.get_excel_files()[0])
    time2 = time.time() - start_time

    print(f"   📊 Primera carga (sin caché): {time1:.4f} segundos")
    print(f"   📊 Segunda carga (con caché): {time2:.4f} segundos")
    print(f"   🚀 Aceleración con caché: {time1 / time2:.1f}x más rápido")
    print()

    # Limpiar caché para demostrar
    print("   🧹 Limpiando caché...")
    loader.clear_metadata_cache()

    start_time = time.time()
    meta3 = loader.get_file_metadata(loader.get_excel_files()[0])
    time3 = time.time() - start_time

    print(f"   📊 Después de limpiar caché: {time3:.4f} segundos")
    print()

def main() -> None:
    """Función principal del ejemplo de rendimiento"""

    print("🎯 Flash Sheet - Ejemplo de Optimizaciones de Rendimiento")
    print("=" * 65)
    print()

    try:
        performance_comparison()
        large_scale_simulation()
        memory_optimization_demo()

        print("✅ ¡Todos los ejemplos de rendimiento completados!")
        print()
        print("💡 Lecciones aprendidas:")
        print("   • El procesamiento por lotes reduce el uso de memoria")
        print("   • El caché de metadatos acelera operaciones repetidas")
        print("   • Los callbacks de progreso mejoran la experiencia del usuario")
        print("   • Para datasets grandes, usa consolidate_chunked()")

    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()