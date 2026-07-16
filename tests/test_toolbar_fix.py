#!/usr/bin/env python3
"""
Test para verificar que los controladores de la barra de herramientas están corregidos
"""

def test_toolbar_indices() -> None:
    """Test para verificar los índices correctos de la barra de herramientas"""
    
    print("🔍 TEST: Verificando configuración de índices en la barra de herramientas...")
    
    # Configuración esperada de las vistas en el stacked widget
    expected_indices = {
        "Vista Principal": 0,
        "Vista de Datos": 1,
        "Vista Gráficos": 2
    }

    # Orden de creación en main.py
    created_views = [
        ("main_view", "Vista Principal"),
        ("data_view", "Vista de Datos"),
        ("graphics_view", "Vista Gráficos")
    ]
    
    print("\n📋 Configuración esperada:")
    for view_name, view_desc in created_views:
        expected_index = expected_indices[view_desc]
        print(f"   - Índice {expected_index}: {view_desc} ({view_name})")
    
    # Verificar los botones configurados
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("\n🔍 Verificando configuración de botones:")
    
    # Buscar las líneas de configuración de botones
    lines = content.split('\n')
    button_configs = []
    
    for i, line in enumerate(lines, 1):
        if 'QPushButton("Vista' in line and 'clicked.connect' in lines[i] if i < len(lines) else False:
            button_name = line.strip().split('QPushButton("')[1].split('")')[0]
            # Buscar la línea de conexión
            connection_line = lines[i] if i < len(lines) and 'clicked.connect' in lines[i] else ""
            if 'clicked.connect' in connection_line:
                # Extraer el índice del lambda
                import re
                match = re.search(r'switch_view\((\d+)\)', connection_line)
                if match:
                    index = int(match.group(1))
                    button_configs.append((button_name, index))
    
    print(f"\n📊 Botones configurados encontrados:")
    all_correct = True
    
    for button_name, configured_index in button_configs:
        # Encontrar la descripción correspondiente
        view_desc = None
        for desc in expected_indices.keys():
            if desc in button_name:
                view_desc = desc
                break
        
        if view_desc:
            expected_index = expected_indices[view_desc]
            status = "✅" if configured_index == expected_index else "❌"
            if configured_index != expected_index:
                all_correct = False
            print(f"   {status} {button_name}: Índice {configured_index} (debería ser {expected_index})")
        else:
            print(f"   ❓ {button_name}: Índice {configured_index} (descripción no encontrada)")
    
    print(f"\n{'✅ CORRECCIÓN EXITOSA' if all_correct else '❌ CORRECCIÓN INCOMPLETA'}")
    
    if all_correct:
        print("🎉 Todos los botones de la barra de herramientas están correctamente configurados!")
        print("   - Los gráficos ahora apuntan al índice 2 (correcto)")
    else:
        print("⚠️  Algunos botones aún tienen índices incorrectos")
    
    return all_correct

def test_view_mapping() -> None:
    """Test para verificar el mapeo de vistas"""
    print("\n🔍 Verificando mapeo de vistas...")
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar el orden de creación de vistas
    import re
    
    # Buscar las líneas donde se añaden widgets al stacked widget
    view_creation_pattern = r'self\.stacked_widget\.addWidget\(self\.(\w+)\)'
    matches = re.findall(view_creation_pattern, content)
    
    expected_order = ['main_view', 'data_view', 'graphics_view']
    
    print(f"📋 Orden de creación de vistas:")
    for i, view in enumerate(matches):
        expected_view = expected_order[i] if i < len(expected_order) else "N/A"
        status = "✅" if view == expected_view else "❌"
        print(f"   {status} Índice {i}: {view}")
        
    correct_order = matches == expected_order
    print(f"\n{'✅ ORDEN CORRECTO' if correct_order else '❌ ORDEN INCORRECTO'}")
    
    return correct_order

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TEST DE CORRECCIÓN DE CONTROLADORES DE TOOLBAR")
    print("=" * 60)
    
    # Ejecutar tests
    indices_ok = test_toolbar_indices()
    mapping_ok = test_view_mapping()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN FINAL:")
    print("=" * 60)
    
    if indices_ok and mapping_ok:
        print("🎉 ¡CORRECCIÓN COMPLETADA EXITOSAMENTE!")
        print("   - Los controladores de gráficos ahora funcionan correctamente")
        print("   - Los índices del stacked widget están correctamente alineados")
    else:
        print("❌ LA CORRECCIÓN TIENE PROBLEMAS:")
        if not indices_ok:
            print("   - Los índices de los botones están incorrectos")
        if not mapping_ok:
            print("   - El orden de creación de vistas está incorrecto")
    
    print("=" * 60)