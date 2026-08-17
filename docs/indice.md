# Índice de Documentación — Flash View Sheet

Documentación técnica del proyecto para análisis por agentes de IA y humanos.

---

## Módulos Documentados

| Archivo | Descripción | Estado |
|---------|-------------|--------|
| [main.md](main.md) | Punto de entrada, `MainWindow`, función `main()`, orquestación de componentes | ✅ Completo |
| [app_coordinator.md](app_coordinator.md) | Orquestador central de lógica de negocio | ✅ Completo |
| [data_service.md](data_service.md) | DataService, hilos de carga, gestión de estado de datos | ✅ Completo |
| [pivot_service.md](pivot_service.md) | PivotService, tablas pivote, agregaciones, crosstab | ⚠️ Desactualizado — la API real está en [app/services.md](app/services.md) y [core/pivot.md](core/pivot.md) |
| [app/services.md](app/services.md) | Servicios: ExportService, FilterService, PivotService (nuevo), Cleaning, Pagination, RecentFiles, Join, Profiler, Visualization | ✅ Completo |
| [app/view_manager.md](app/view_manager.md) | ViewCoordinator, ViewSwitcher, ViewRegistry | ✅ Completo |
| [app/toolbar.md](app/toolbar.md) | ToolbarManager, ViewSwitcher (botones) | ✅ Completo |
| [app/menus.md](app/menus.md) | MenuBuilder, ArchivoMenu, DatosMenu, VistaMenu, ExportarMenu | ✅ Completo |
| [app/widgets.md](app/widgets.md) | Todos los widgets de la aplicación | ✅ Completo |
| [core/data_handler.md](core/data_handler.md) | Operaciones centrales de datos + exportación separada (ExcelTemplateSplitter) | ✅ Completo |
| [core/loaders.md](core/loaders.md) | Sistema de carga de archivos (Factory Pattern) | ✅ Completo |
| [core/join.md](core/join.md) | Sistema de join de datos | ✅ Completo |
| [core/pivot.md](core/pivot.md) | Tablas pivote automáticas (API refactorizada de PivotService) | ✅ Completo |
| [core/performance.md](core/performance.md) | Optimización de rendimiento | ✅ Completo |
| [core/format_preservation.md](core/format_preservation.md) | Preservación de formato Excel | ✅ Completo |
| [paginacion.md](paginacion.md) | Subsistema de paginación | ✅ Completo |
| [config.md](config.md) | Configuración global | ✅ Completo |

---

## Arquitectura del Proyecto

```
main.py (punto de entrada)
├── app/ (UI + servicios + coordinación)
│   ├── app_coordinator.py    ← Orquestador central
│   ├── services/             ← 10 servicios: Data, Export, Filter, Pivot, Cleaning, Pagination, RecentFiles, Join, Profiler, Visualization
│   ├── toolbar/              ← ToolbarManager
│   ├── view_manager/         ← ViewCoordinator
│   ├── menus/                ← MenuBuilder
│   ├── widgets/              ← 16 módulos de widgets
│   ├── models/               ← VirtualizedPandasModel
│   ├── resources.py          ← get_asset_path
│   └── types.py              ← FilePath, ColumnMapping, etc.
├── core/ (lógica de negocio)
│   ├── data_handler.py       ← Operaciones de datos + exportación separada
│   ├── data_cleaner.py       ← Limpieza de datos
│   ├── excel_format_preserver.py / simple_excel_preserver.py
│   ├── loaders/              ← 13 loaders (Factory Pattern)
│   ├── join/                 ← DataJoinManager, JoinHistory, JoinConfig
│   ├── models/               ← FileMetadata, FolderLoadConfig
│   ├── consolidation/        ← ExcelConsolidator
│   └── performance_optimizer.py
└── config.py                 ← OptimizationConfig
```

---

## Convenciones de Documentación

- Cada archivo `.md` documenta un módulo o grupo de módulos relacionados
- Incluye: imports, clases, métodos, señales, diagramas de dependencias
- Formato optimizado para análisis por agentes de IA y humanos
- Tablas estructuradas para referencia rápida
- Código inline para ejemplos concretos
