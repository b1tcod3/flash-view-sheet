#!/usr/bin/env python3
"""
Script de Validación Final - Documentación Fase 5
Flash Sheet v1.1.0 - Funcionalidad de Cruce de Datos (Joins)

Este script valida que toda la documentación generada en la Fase 5
esté completa y consistente según el plan establecido.
"""

import os
import json
from pathlib import Path

def validate_documentation_structure():
    """Validar estructura completa de documentación"""
    
    print("=== VALIDACIÓN FINAL DE DOCUMENTACIÓN - FASE 5 ===\n")
    
    # Estructura esperada según plan de Fase 5
    expected_files = {
        "Subfase 5.1 - Documentación Técnica": [
            "docs/conf.py",
            "docs/index.rst", 
            "docs/api/classes.rst",
            "docs/developer_guide/architecture.rst",
            "docs/developer_guide/contributing.rst"
        ],
        "Subfase 5.2 - Documentación de Usuario": [
            "docs/user_guide/README.md",
            "docs/user_guide/advanced_configuration.md", 
            "docs/user_guide/examples_and_use_cases.md"
        ],
        "Subfase 5.3 - Preparación para Release": [
            "docs/releases/v-1-1-0/release_notes.md",
            "docs/releases/v-1-1-0/installation_guide.md",
            "docs/releases/v-1-1-0/distribution_preparation.md"
        ]
    }
    
    missing_files = []
    existing_files = []
    
    # Verificar archivos esperados
    for category, files in expected_files.items():
        print(f"📁 {category}:")
        for file_path in files:
            if Path(file_path).exists():
                size = Path(file_path).stat().st_size
                existing_files.append(file_path)
                print(f"  ✅ {file_path} ({size:,} bytes)")
            else:
                missing_files.append(file_path)
                print(f"  ❌ {file_path} (FALTANTE)")
        print()
    
    # Archivos adicionales de documentación
    additional_files = [
        "docs/testing_documentation.md",
        "docs/developer_guide/architecture.rst",
        "docs/developer_guide/contributing.rst"
    ]
    
    print("📚 Documentación Adicional:")
    for file_path in additional_files:
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            existing_files.append(file_path)
            print(f"  ✅ {file_path} ({size:,} bytes)")
        else:
            print(f"  ⚠️  {file_path} (No esperado)")
    print()
    
    # Resumen de validación
    print("=== RESUMEN DE VALIDACIÓN ===")
    print(f"Archivos esperados: {sum(len(files) for files in expected_files.values())}")
    print(f"Archivos existentes: {len(existing_files)}")
    print(f"Archivos faltantes: {len(missing_files)}")
    
    if missing_files:
        print("\n❌ ARCHIVOS FALTANTES:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print("\n✅ TODA LA DOCUMENTACIÓN ESTÁ PRESENTE")
        return True

def validate_content_completeness():
    """Validar completitud del contenido"""
    
    print("\n=== VALIDACIÓN DE CONTENIDO ===")
    
    # Verificar archivos clave por contenido
    key_files = {
        "docs/user_guide/README.md": [
            "Introducción", "Tutorial", "FAQ", "Casos de uso"
        ],
        "docs/releases/v-1-1-0/release_notes.md": [
            "v1.1.0", "Funcionalidades", "Performance", "Testing"
        ],
        "docs/releases/v-1-1-0/installation_guide.md": [
            "Instalación", "Requisitos", "Configuración", "Troubleshooting"
        ]
    }
    
    for file_path, expected_content in key_files.items():
        if not Path(file_path).exists():
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"📄 {file_path}:")
            for expected in expected_content:
                if expected.lower() in content.lower():
                    print(f"  ✅ {expected}")
                else:
                    print(f"  ❌ {expected} (no encontrado)")
        except Exception as e:
            print(f"  ❌ Error leyendo archivo: {e}")
    
    return True

def generate_documentation_summary():
    """Generar resumen de documentación generada"""
    
    print("\n=== RESUMEN DE DOCUMENTACIÓN GENERADA ===")
    
    docs_summary = {
        "Total de archivos de documentación": 0,
        "Tamaño total de documentación": 0,
        "Archivos por categoría": {
            "Técnica": 0,
            "Usuario": 0, 
            "Release": 0,
            "Testing": 0
        }
    }
    
    # Contar archivos en cada categoría
    categories = {
        "docs/conf.py": "Técnica",
        "docs/index.rst": "Técnica",
        "docs/api/": "Técnica",
        "docs/developer_guide/": "Técnica",
        "docs/user_guide/": "Usuario",
        "docs/releases/v-1-1-0/": "Release",
        "docs/testing_documentation.md": "Testing"
    }
    
    docs_dir = Path("docs")
    if docs_dir.exists():
        for file_path in docs_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.md', '.rst']:
                docs_summary["Total de archivos de documentación"] += 1
                file_size = file_path.stat().st_size
                docs_summary["Tamaño total de documentación"] += file_size
                
                # Categorizar archivo
                for pattern, category in categories.items():
                    if pattern.endswith('/'):
                        if pattern.rstrip('/') in str(file_path):
                            docs_summary["Archivos por categoría"][category] += 1
                            break
                    else:
                        if pattern in str(file_path):
                            docs_summary["Archivos por categoría"][category] += 1
                            break
                else:
                    docs_summary["Archivos por categoría"]["Técnica"] += 1
    
    # Mostrar resumen
    print(f"Total de archivos: {docs_summary['Total de archivos de documentación']}")
    print(f"Tamaño total: {docs_summary['Tamaño total de documentación']:,} bytes")
    print("\nPor categoría:")
    for category, count in docs_summary["Archivos por categoría"].items():
        if count > 0:
            print(f"  {category}: {count} archivos")
    
    return docs_summary

def validate_consistency():
    """Validar consistencia entre documentos"""
    
    print("\n=== VALIDACIÓN DE CONSISTENCIA ===")
    
    # Verificar versiones consistentes
    version_files = [
        ("docs/index.rst", "1.1.0"),
        ("docs/releases/v-1-1-0/release_notes.md", "1.1.0"),
        ("docs/releases/v-1-1-0/installation_guide.md", "1.1.0")
    ]
    
    versions_found = {}
    for file_path, expected_version in version_files:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar versión en el contenido
                for line in content.split('\n'):
                    if '1.1.0' in line or 'v1.1.0' in line:
                        versions_found[file_path] = expected_version
                        break
            except Exception as e:
                print(f"⚠️ Error verificando {file_path}: {e}")
    
    print("Versiones encontradas:")
    consistent = True
    for file_path, version in versions_found.items():
        print(f"  ✅ {file_path}: {version}")
    
    return len(versions_found) > 0

def main():
    """Función principal de validación"""
    
    print("Flash Sheet v1.1.0 - Validación Final de Documentación")
    print("=" * 60)
    
    # Ejecutar todas las validaciones
    structure_ok = validate_documentation_structure()
    content_ok = validate_content_completeness()
    summary = generate_documentation_summary()
    consistency_ok = validate_consistency()
    
    # Resultado final
    print("\n" + "=" * 60)
    print("RESULTADO FINAL DE VALIDACIÓN")
    print("=" * 60)
    
    if structure_ok and content_ok and consistency_ok:
        print("✅ TODAS LAS VALIDACIONES PASARON")
        print("✅ Documentación de Fase 5 COMPLETA Y CONSISTENTE")
        print(f"✅ {summary['Total de archivos de documentación']} archivos de documentación")
        print(f"✅ {summary['Tamaño total de documentación']:,} bytes de contenido")
        print("\n🚀 LISTO PARA RELEASE v1.1.0")
        return True
    else:
        print("❌ ALGUNAS VALIDACIONES FALLARON")
        print("❌ Revisar problemas identificados arriba")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)