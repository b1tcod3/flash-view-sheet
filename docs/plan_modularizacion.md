# Plan de Modularización de main.py

## Estado Actual (Actualizado: 2024-10-02)

**Archivo:** `main.py` (~290 líneas) ✅
**Objetivo:** <250 líneas ⏳
**Problema:** MainWindow delegó exitosamente al AppCoordinator.

---

## Análisis de Responsabilidades en MainWindow

### 1. Gestión de UI (Menu, Toolbar, StatusBar) - ~150 líneas
- `create_menu_bar()` - Creación de menús
- `create_tool_bar()` - Creación de toolbar
- `create_status_bar()` - Barra de estado
- `create_view_switcher_ui()` - Botones de cambio de vista

### 2. Gestión de Datos (Carga/Exportación) - ~200 líneas
- `abrir_archivo()`, `cargar_carpeta()` - Carga
- `mostrar_loading_indicator()` - UI de carga
- `on_datos_cargados()`, `on_error_carga()` - Callback de carga
- `exportar_a_pdf/xlsx/csv/sql/imagen()` - Exportación

### 3. Operaciones de Datos - ~250 líneas
- `aplicar_filtro()`, `limpiar_filtro()` - Filtros
- `abrir_cruzar_datos()`, `on_join_completed()` - Joins
- `abrir_pivot_simple/combinada()` - Tablas pivote
- `exportar_datos_separados()`, `procesar_exportacion_separada()` - Separación

### 4. Gestión de Vistas - ~100 líneas
- `create_views()`, `switch_view()`, `show_info_modal()`
- Conexiones de señales

### 5. Actualización de UI - ~100 líneas
- `actualizar_vista()`, `actualizar_menu_separar/pivote/datos()`

---

## Plan de Modularización Propuesto

### FASE 1: Extraer Gestor de Menús (`app/menus/`)

```
app/menus/
├── __init__.py
├── menu_builder.py        # Factory para construir menús
├── archivo_menu.py        # Menú Archivo
├── datos_menu.py          # Menú Datos
├── vista_menu.py          # Menú Vista
├── exportar_menu.py       # Submenú Exportar
└── menu_actions.py        # Acciones de menú centralizadas
```

**Responsabilidades:**
- Centralizar la creación de menús
- Separar acciones de menú de la lógica de MainWindow
- Facilitar adición/modificación de menús

---

### FASE 2: Extraer Gestor de Toolbar (`app/toolbar/`)

```
app/toolbar/
├── __init__.py
├── toolbar_manager.py     # Gestor principal del toolbar
├── view_switcher.py      # Botones de cambio de vista
└── filter_toolbar.py     # Controles de filtrado
```

**Responsabilidades:**
- Gestión del toolbar principal
- Componentes de filtrado
- Separación de UI del toolbar

---

### FASE 3: Crear Servicio de Datos (`app/services/`)

```
app/services/
├── __init__.py
├── data_service.py       # Servicio unificado de datos
├── export_service.py     # Servicios de exportación
├── filter_service.py     # Servicios de filtrado
└── pivot_service.py      # Servicios de tablas pivote
```

**Responsabilidades:**
- `DataService`: Carga, guardado, gestión de datos
- `ExportService`: Todas las exportaciones (PDF, XLSX, CSV, SQL, imagen)
- `FilterService`: Aplicación de filtros
- `PivotService`: Operaciones de tablas pivote

---

### FASE 4: Extraer Gestor de Vistas (`app/view_manager/`)

```
app/view_manager/
├── __init__.py
├── view_registry.py      # Registro de vistas disponibles
├── view_switcher.py      # Lógica de cambio de vistas
└── view_coordinator.py   # Coordinator pattern para vistas
```

**Responsabilidades:**
- Registro de vistas
- Transiciones entre vistas
- Coordinación de estado entre vistas

---

### FASE 5: Refactorizar MainWindow

**Nueva estructura de MainWindow:**

```python
class MainWindow(QMainWindow):
    def __init__(self):
        # Inicialización mínima
        self.data_service = DataService()
        self.menu_manager = MenuManager()
        self.toolbar_manager = ToolbarManager()
        self.view_manager = ViewManager()
        self.export_service = ExportService()
        
        self.setup_ui()
        self.setup_connections()
```

---

## Beneficios Logrados

| Aspecto | Antes | Después |
|---------|-------|---------|
| Líneas en MainWindow | ~950 | ~290 (69% reducción) |
| Líneas en AppCoordinator | 0 | ~200 |
| Responsabilidades MainWindow | 6+ | 1 (orquestación básica) |
| Acoplamiento | Alto | Medio-Bajo |
| Testabilidad | Difícil | Media |
| Diálogos extraídos | 0 | 2 (AboutDialog, InfoModal) |

---

## Dependencias Entre Módulos

```
MainWindow
    ├── MenuManager ──────────────┐
    ├── ToolbarManager ───────────┤
    ├── ViewManager ──────────────┤
    ├── DataService ──────────────┼──> ExportService
    │   └── FilterService ────────┤     └── PivotService
    └── ExportService ───────────┘
```

---

## Archivos a Crear/Modificar

### Nuevos archivos:
1. `app/menus/__init__.py`
2. `app/menus/menu_builder.py`
3. `app/menus/menu_actions.py`
4. `app/toolbar/__init__.py`
5. `app/toolbar/toolbar_manager.py`
6. `app/services/__init__.py`
7. `app/services/data_service.py`
8. `app/services/export_service.py`
9. `app/view_manager/__init__.py`
10. `app/view_manager/view_registry.py`

### Archivos a modificar:
1. `main.py` - Reducir significativamente
2. `app/__init__.py` - Actualizar exports
3. `config.py` - Añadir configuraciones si es necesario

---

## Estado de Implementación

### FASE 1: Extraer Gestor de Menús (`app/menus/`) ✅ COMPLETADA
- `app/menus/__init__.py`
- `app/menus/menu_builder.py`
- `app/menus/menu_actions.py`
- `app/menus/archivo_menu.py`
- `app/menus/datos_menu.py`
- `app/menus/vista_menu.py`
- `app/menus/exportar_menu.py`

### FASE 2: Extraer Gestor de Toolbar (`app/toolbar/`) ✅ COMPLETADA
- `app/toolbar/__init__.py`
- `app/toolbar/toolbar_manager.py`
- `app/toolbar/view_switcher.py`
- `app/toolbar/filter_toolbar.py`

### FASE 3: Crear Servicio de Datos (`app/services/`) ✅ COMPLETADA
- `app/services/__init__.py`
- `app/services/data_service.py`
- `app/services/export_service.py`
- `app/services/filter_service.py`
- `app/services/pivot_service.py`

### FASE 4: Extraer Gestor de Vistas (`app/view_manager/`) ✅ COMPLETADA
- `app/view_manager/__init__.py`
- `app/view_manager/view_registry.py`
- `app/view_manager/view_switcher.py`
- `app/view_manager/view_coordinator.py`

### FASE 5: Refactorizar MainWindow ✅ COMPLETADA
- `main.py` refactorizado a ~320 líneas
- `MainWindow` ahora es un orquestador simple
- Delega a servicios: DataService, ExportService, PivotService
- Delega a gestores: ToolbarManager, ViewCoordinator
- Propiedades de compatibilidad mantenidas

---

## Orden de Implementación Sugerido

1. **Semana 1:** FASE 1 + FASE 2 (Menú y Toolbar) ✅ COMPLETADO
2. **Semana 2:** FASE 3 (Servicios de Datos) ⏳ PRÓXIMO
3. **Semana 3:** FASE 4 (Gestor de Vistas)
4. **Semana 4:** FASE 5 (Refactorizar MainWindow) + Pruebas

---

## Métricas de Éxito

- [ ] MainWindow < 250 líneas
- [ ] Complejidad ciclomática de MainWindow < 15
- [ ] Cobertura de tests > 70%
- [ ] Tiempo de carga de aplicación < 2 segundos
- [ ] Sin duplicación de código (herramientas: pylint, radon)

---

## Nuevos Archivos Creados (FASE 6 - Finalización)

### Módulos Nuevos
- `app/app_coordinator.py` - ⭐ NUEVO: Orquestador central de la aplicación
- `app/widgets/about_dialog.py` - Diálogo "Acerca de" extraído de main.py

### Archivos Modificados
- `app/widgets/__init__.py` - Actualizado con nuevos exports
- `main.py` - Reducido de 575 a 489 líneas → 290 líneas (~50% reducción)
- `docs/plan_modularizacion.md` - Actualizado con métricas reales

---

## Resumen Final de Métricas

| Métrica | Inicial | Actual | Cambio |
|---------|---------|--------|--------|
| Líneas main.py | 950 | 290 | -69% |
| Archivos nuevos | 0 | 2 | +2 |
| Dialogos extraídos | 0 | 2 | +2 |

**Objetivo <250 líneas**: ⏳ Faltan ~40 líneas (ver opciones abajo)

---

## Trabajo Pendiente (Opcional)

Para alcanzar <250 líneas en main.py (~40 líneas por eliminar):

### Opción A: Eliminar propiedades de compatibilidad (~10 líneas)
- `df_original`, `df_vista_actual`, `loading_thread`
- ⚠️ Rompe compatibilidad con código existente

### Opción B: Crear DialogFactory (~30 líneas)
- Unificar diálogos en factory
- Reduce código duplicado

### Opción C: Dejar en ~290 líneas ✅ Aceptable
- Ya está dentro de rangos aceptables
- Código mantenible y testeable

---

## Notas Adicionales

- Mantener compatibilidad hacia atrás con la API existente
- Usar señales de Qt para comunicación entre módulos
- Considerar usar dependency injection para servicios
- Documentar cada módulo con docstrings siguiendo Google style
