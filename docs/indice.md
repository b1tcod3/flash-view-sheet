# Índice de Documentación — Flash View Sheet

Documentación técnica del proyecto para análisis por agentes de IA y humanos.

---

## Módulos Documentados

| Archivo | Descripción | Estado |
|---------|-------------|--------|
| [main.md](main.md) | Punto de entrada, `MainWindow`, función `main()`, orquestación de componentes | ✅ Completo |
| [app_coordinator.md](app_coordinator.md) | Orquestador central de lógica de negocio | ✅ Completo |
| [data_service.md](data_service.md) | DataService, hilos de carga, gestión de estado de datos | ✅ Completo |

---

## Módulos Pendientes

| Archivo | Descripción | Estado |
|---------|-------------|--------|
| `app/services.md` | ExportService, FilterService, PivotService | ⏳ Pendiente |
| `app/view_manager.md` | ViewCoordinator, ViewSwitcher, ViewRegistry | ⏳ Pendiente |
| `app/toolbar.md` | ToolbarManager, ViewSwitcher, FilterToolbar | ⏳ Pendiente |
| `app/menus.md` | MenuBuilder, MenuActions, menús | ⏳ Pendiente |
| `app/widgets.md` | Todos los widgets de la aplicación | ⏳ Pendiente |
| `core/data_handler.md` | Operaciones centrales de datos | ⏳ Pendiente |
| `core/loaders.md` | Sistema de carga de archivos (Factory Pattern) | ⏳ Pendiente |
| `core/join.md` | Sistema de join de datos | ⏳ Pendiente |
| `core/pivot.md` | Tablas pivote | ⏳ Pendiente |
| `core/performance.md` | Optimización de rendimiento | ⏳ Pendiente |
| `paginacion.md` | Subsistema de paginación | ⏳ Pendiente |
| `config.md` | Configuración global | ⏳ Pendiente |

---

## Arquitectura del Proyecto

```
main.py (punto de entrada)
├── app/ (UI + servicios + coordinación)
│   ├── app_coordinator.py    ← Orquestador central
│   ├── services/             ← DataService, ExportService, FilterService, PivotService
│   ├── toolbar/              ← ToolbarManager
│   ├── view_manager/         ← ViewCoordinator
│   ├── menus/                ← MenuBuilder, MenuActions
│   ├── widgets/              ← 16+ widgets
│   └── models/               ← VirtualizedPandasModel
├── core/ (lógica de negocio)
│   ├── data_handler.py       ← Operaciones de datos
│   ├── loaders/              ← 10 loaders (Factory Pattern, 16 formatos)
│   ├── join/                 ← DataJoinManager, JoinHistory
│   ├── pivot/                ← BasePivotTable, SimplePivotTable, CombinedPivotTable
│   ├── consolidation/        ← ExcelConsolidator
│   └── performance_optimizer.py
├── paginacion/               ← DataView, PaginationManager
└── config.py                 ← OptimizationConfig
```

---

## Convenciones de Documentación

- Cada archivo `.md` documenta un módulo o grupo de módulos relacionados
- Incluye: imports, clases, métodos, señales, diagramas de dependencias
- Formato optimizado para análisis por agentes de IA y humanos
- Tablas estructuradas para referencia rápida
- Código inline para ejemplos concretos
