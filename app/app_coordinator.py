"""
AppCoordinator - Orquestador de la aplicación

Coordinador central que maneja la lógica de negocio y la orquestación
entre servicios, diálogos y vistas.
"""

from typing import Any, TYPE_CHECKING
from pathlib import Path

import pandas as pd
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import (QMessageBox, QFileDialog, QInputDialog,
                                QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                QComboBox, QPushButton, QApplication)

from app.services import DataService, ExportService, PivotService, CleaningService, JoinService
from app.services.recent_files_service import RecentFilesService
from app.services.data_service import DataLoaderThread, FolderLoaderThread
from app.view_manager import ViewCoordinator, ViewRegistry
from app.toolbar import ToolbarManager
from app.widgets import JoinDialog, FolderLoadDialog, CSVSeparatorDialog, ExcelSheetDialog
from core.join.models import JoinResult, JoinConfig
from core.models.folder_load_config import FolderLoadConfig
from core.join.join_history import JoinHistory

if TYPE_CHECKING:
    from PySide6.QtWidgets import QMainWindow

class AppCoordinator(QObject):
    """
    Coordinador central de la aplicación.
    
    Responsabilidades:
    - Manejar callbacks de carga de datos
    - Coordinar diálogos de operaciones (join, pivote, exportación)
    - Actualizar estado de menús
    - Gestionar transiciones de vistas
    """
    
    # Señales para comunicar con MainWindow
    status_message = Signal(str)
    # Signal(pd.DataFrame)
    datos_originales_cargados = Signal(object)
    # Signal(pd.DataFrame)
    datos_actualizados = Signal(object)
    datos_disponibles = Signal(bool)
    
    def __init__(self, parent_window: 'QMainWindow', data_service: DataService, export_service: ExportService, 
                 pivot_service: PivotService, cleaning_service: CleaningService,
                 view_coordinator: ViewCoordinator, toolbar_manager: ToolbarManager, join_history: JoinHistory,
                 recent_files_service: RecentFilesService, join_service: JoinService) -> None:
        """Inicializar el coordinador"""
        super().__init__(parent_window)
        
        self.parent_window = parent_window
        self.data_service = data_service
        self.export_service = export_service
        self.pivot_service = pivot_service
        self.cleaning_service = cleaning_service
        self.view_coordinator = view_coordinator
        self.toolbar_manager = toolbar_manager
        self.join_history = join_history
        self.recent_files_service = recent_files_service
        self.join_service = join_service
        self._loader_thread: DataLoaderThread | None = None
        self._folder_thread: FolderLoaderThread | None = None
        self._active_loaders: list[DataLoaderThread] = []
        self._pending_dfs: list[pd.DataFrame] = []
        self._pending_paths: list[str] = []
        self._completed_count: int = 0
        self._error_count: int = 0
        self._total_files: int = 0
    
    # ==================== CARGA DE ARCHIVO ====================

    def solicitar_apertura_archivo(self, filepath: str | None = None) -> None:
        """Muestra QFileDialog y arranca la carga si se selecciona uno o más archivos."""
        if filepath:
            self.iniciar_carga_archivo(filepath)
            return
        filtro = self.data_service.get_file_filter()
        filepaths, _ = QFileDialog.getOpenFileNames(
            self.parent_window, "Abrir archivos de datos", "", filtro
        )
        if len(filepaths) == 1:
            filepath = filepaths[0]
            suffix = Path(filepath).suffix.lower()
            if suffix in ('.csv', '.tsv'):
                dialog = CSVSeparatorDialog(self.parent_window)
                if dialog.exec() != QDialog.Accepted:
                    return
                self.iniciar_carga_archivo(filepath, separator=dialog.get_separator())
            elif suffix in ('.xlsx', '.xls'):
                dialog = ExcelSheetDialog(filepath, self.parent_window)
                if dialog.exec() != QDialog.Accepted:
                    return
                self.iniciar_carga_archivo(filepath, sheet_name=dialog.get_sheet_name())
            else:
                self.iniciar_carga_archivo(filepath)
        elif len(filepaths) > 1:
            self.iniciar_carga_multiple(filepaths)

    def solicitar_carga_carpeta(self) -> None:
        """Muestra FolderLoadDialog y procesa la carga si se confirma."""
        dialog = FolderLoadDialog(self.parent_window)
        if dialog.exec():
            config = dialog.get_config()
            if config and config.folder_path:
                self.procesar_carga_carpeta(config)

    def iniciar_carga_archivo(self, filepath: str, skip_rows: int = 0, column_names: dict[str, str] | None = None, enable_column_visibility: bool = True, separator: str | None = None, sheet_name: str | None = None) -> None:
        """Inicia la carga de un archivo: valida extensión, muestra progreso, crea hilo y conecta resultados."""
        path = Path(filepath)
        extensiones = self.data_service.extensiones_permitidas()
        if path.suffix.lower() not in extensiones:
            self.status_message.emit(f"Formato no soportado: {path.suffix}")
            return

        self._cancel_thread(self._loader_thread)

        progress = self.data_service.create_progress_dialog(
            "Cargando datos", "Cargando archivo..."
        )
        progress.setMinimumDuration(500)
        progress.show()

        try:
            thread = self.data_service.create_loader_thread(
                filepath, skip_rows, column_names or {}, separator, sheet_name
            )
        except Exception as e:
            progress.close()
            self._on_error_carga(str(e))
            return

        self._loader_thread = thread
        self._pending_col_vis = enable_column_visibility

        thread.data_loaded.connect(self._on_datos_cargados)
        thread.error_occurred.connect(self._on_error_carga)
        thread.finished.connect(progress.close)
        thread.finished.connect(self._on_loader_finished)
        thread.start()

    # ==================== CARGA MÚLTIPLE ====================

    def iniciar_carga_multiple(self, filepaths: list[str]) -> None:
        """Cargar múltiples archivos en paralelo y consolidar al finalizar."""
        main_view = self.view_coordinator.get_main_view()
        if main_view:
            main_view.clear_file_list()

        self._pending_dfs = []
        self._pending_paths = filepaths
        self._completed_count = 0
        self._error_count = 0
        self._total_files = len(filepaths)

        for path in filepaths:
            widget = main_view.add_file_to_list(path) if main_view else None
            try:
                thread = self.data_service.create_loader_thread(path)
            except Exception as e:
                self.status_message.emit(f"Error creando hilo para {Path(path).name}: {e}")
                if widget:
                    widget.set_error(f"Error: {e}"[:50])
                self._completed_count += 1
                if self._completed_count >= self._total_files:
                    self._finalizar_carga_multiple()
                continue
            self._active_loaders.append(thread)
            thread.progress_updated.connect(
                lambda loaded, total, w=widget: w.set_progress(loaded, total) if w else None
            )
            thread.data_loaded.connect(lambda df, p=path: self._on_single_loaded(p, df))
            thread.error_occurred.connect(lambda err, p=path: self._on_single_error(p, err))
            thread.finished.connect(lambda p=path: self._on_single_finished(p))
            thread.start()

    def _on_single_loaded(self, filepath: str, df: pd.DataFrame) -> None:
        """Callback individual cuando un archivo se carga exitosamente."""
        self._pending_dfs.append(df)
        main_view = self.view_coordinator.get_main_view()
        if main_view:
            main_view.set_file_completed(filepath)

    def _on_single_error(self, filepath: str, error: str) -> None:
        """Callback individual cuando un archivo falla al cargar."""
        self._error_count += 1
        main_view = self.view_coordinator.get_main_view()
        if main_view and filepath in main_view._file_widgets:
            main_view._file_widgets[filepath].set_error(f"Error: {error[:50]}")
        self.status_message.emit(f"Error cargando {Path(filepath).name}: {error}")

    def _on_single_finished(self, filepath: str) -> None:
        """Callback individual cuando un hilo termina."""
        self._completed_count += 1
        thread = next((t for t in self._active_loaders if t.filepath == filepath), None)
        if thread in self._active_loaders:
            self._active_loaders.remove(thread)
        if self._completed_count >= len(self._pending_paths):
            self._finalizar_carga_multiple()

    def _finalizar_carga_multiple(self) -> None:
        """Consolidar todos los DataFrames cargados y actualizar la UI."""
        if not self._pending_dfs:
            self._on_error_carga("No se pudo cargar ningún archivo")
            return

        final_df = pd.concat(self._pending_dfs, ignore_index=True)
        self.data_service.set_original_data(final_df)
        self.data_service.set_current_data(final_df)

        if self._pending_paths:
            self.view_coordinator.update_main_view(self._pending_paths[-1])

        self.datos_originales_cargados.emit(self.data_service.datos_originales)
        self.datos_actualizados.emit(self.data_service.datos_actuales)
        self.datos_disponibles.emit(True)

        self.view_coordinator.switch_to(ViewRegistry.VIEW_DATA)
        status = f"{len(self._pending_dfs)} archivos consolidados: {len(final_df)} filas"
        if self._error_count > 0:
            status += f" ({self._error_count} errores)"
        self.status_message.emit(status)

        if self._pending_paths:
            for p in self._pending_paths:
                self.recent_files_service.add(p)
            self.refresh_recent_files()

        self._pending_dfs = []
        self._pending_paths = []
        self._completed_count = 0
        self._error_count = 0
        self._total_files = 0

    # ==================== CALLBACKS DE DATOS ====================
    
    def _on_datos_cargados(self, df: pd.DataFrame) -> None:
        """Manejar datos cargados exitosamente"""
        self.data_service.set_original_data(df)
        self.data_service.set_current_data(df)
        
        # Actualizar MainView con info del archivo
        self.view_coordinator.update_main_view(self.data_service.get_filepath())
        
        # Guardar en archivos recientes
        filepath = self.data_service.get_filepath()
        if filepath:
            self.recent_files_service.add(filepath)
            self.refresh_recent_files()
        
        # Emitir señales para que las vistas reaccionen
        self.datos_originales_cargados.emit(self.data_service.datos_originales)
        self.datos_actualizados.emit(self.data_service.datos_actuales)
        self.datos_disponibles.emit(True)
        
        # Phase 6: apply pending column visibility
        if hasattr(self, '_pending_col_vis'):
            self.view_coordinator.set_column_visibility_enabled(self._pending_col_vis)
            del self._pending_col_vis
        
        # Cambiar a vista de datos
        self.view_coordinator.switch_to(ViewRegistry.VIEW_DATA)
        self.status_message.emit(f"Datos cargados: {self.data_service.get_filename()}")
    
    def _on_error_carga(self, error_message: str) -> None:
        """Manejar error de carga"""
        QMessageBox.critical(self.parent_window, "Error de carga", error_message)
        self.status_message.emit("Error al cargar archivo")
    
    # ==================== CARGA DE CARPETA ====================
    
    def procesar_carga_carpeta(self, config: FolderLoadConfig) -> None:
        """Procesar carga de carpeta en segundo plano"""
        self._cancel_thread(self._folder_thread)

        progress = self.data_service.create_progress_dialog(
            "Cargando carpeta", "Escaneando archivos Excel..."
        )
        progress.setMinimumDuration(500)
        progress.show()

        try:
            thread = self.data_service.create_folder_loader_thread(
                config.folder_path, config
            )
        except Exception as e:
            progress.close()
            self._on_error_carga(str(e))
            return

        self._folder_thread = thread
        thread.data_loaded.connect(self._on_folder_data_loaded)
        thread.error_occurred.connect(self._on_error_carga)
        thread.finished.connect(progress.close)
        thread.finished.connect(self._on_folder_finished)
        thread.progress_updated.connect(
            lambda current, total: progress.setValue(int(current / total * 100)) if total > 0 else None
        )
        thread.start()
    
    def _on_folder_data_loaded(self, df: pd.DataFrame) -> None:
        """Manejar datos de carpeta cargados exitosamente"""
        self.data_service.set_original_data(df)
        self.data_service.set_current_data(df)
        
        self.view_coordinator.switch_to(ViewRegistry.VIEW_DATA)
        
        self.datos_originales_cargados.emit(self.data_service.datos_originales)
        self.datos_actualizados.emit(self.data_service.datos_actuales)
        self.datos_disponibles.emit(True)
        
        rows, cols = df.shape
        QMessageBox.information(self.parent_window, "Éxito",
            f"Carpeta cargada exitosamente.\n\n"
            f"Filas: {rows}, Columnas: {cols}")
        
        self.status_message.emit("Carpeta cargada exitosamente")
    
    # ==================== OPERACIONES DE JOIN ====================
    
    def abrir_cruzar_datos(self) -> None:
        """Abrir diálogo para cruzar datos"""
        if not self.data_service.has_data:
            QMessageBox.warning(self.parent_window, "Advertencia", 
                              "No hay datos cargados para cruzar.")
            return
        
        dialog = JoinDialog(self.data_service.datos_actuales, self.parent_window,
                           join_service=self.join_service)
        dialog.join_completed.connect(self._on_join_completed)
        dialog.exec()
    
    def _on_join_completed(self, result: JoinResult, right_file_path: str | None) -> None:
        """Manejar resultado de join"""
        try:
            left_name = self.data_service.get_filename()
            right_name = (right_file_path and 
                        self._basename(right_file_path) or "Dataset Derecho")
            
            self.view_coordinator.set_join_result(result, left_name, right_name)
            
            if result.success and result.config:
                self.join_history.add_entry(left_name, right_name, 
                                           result.config, result)
            
            self.toolbar_manager.set_view_buttons_enabled(True)
            self.view_coordinator.switch_to(ViewRegistry.VIEW_JOIN)
            self.status_message.emit(
                f"Cruce completado: {result.metadata.result_rows} filas")
            
        except Exception as e:
            QMessageBox.critical(self.parent_window, "Error", 
                               f"Error procesando resultado del join: {str(e)}")
    
    def _basename(self, path: str) -> str:
        """Obtener nombre de archivo sin ruta"""
        return Path(path).name

    def abrir_historial(self) -> None:
        """Abrir diálogo de historial de joins"""
        entries = self.join_history.get_entries(limit=20)
        joined_view = self.view_coordinator.get_joined_data_view()
        if joined_view:
            joined_view.populate_history(entries)

    def exportar_resultado_join(self, df: pd.DataFrame) -> None:
        """Exportar resultado del join actual"""
        self.mostrar_dialogo_exportacion("Cruce_Datos")

    def limpiar_historial_joins(self) -> None:
        """Limpiar el historial de joins"""
        self.join_history.clear_history()

    # ==================== OPERACIONES DE PIVOTE ====================
    
    def auto_pivot(self) -> None:
        """Generar automáticamente tablas pivote para todas las combinaciones categórica × numérica."""
        if not self.data_service.has_data:
            QMessageBox.warning(self.parent_window, "Advertencia",
                              "No hay datos cargados.")
            return
        
        df = self.data_service.datos_actuales
        if df is None or df.empty:
            return
        
        cat_cols = self.pivot_service.detect_categorical_columns(df)
        num_cols = self.pivot_service.detect_numeric_columns(df)
        
        if not cat_cols or not num_cols:
            QMessageBox.information(self.parent_window, "Sin combinaciones",
                "No se encontraron combinaciones válidas.\n\n"
                f"Columnas categóricas: {len(cat_cols)}\n"
                f"Columnas numéricas: {len(num_cols)}")
            return
        
        combos = self.pivot_service.rank_combinations(df, cat_cols, num_cols)
        total = min(len(combos), 5)
        
        progress = self.data_service.create_progress_dialog(
            "Generando pivotes", "Calculando tablas pivote...")
        progress.setMaximum(total)
        progress.setValue(0)
        progress.show()
        QApplication.processEvents()
        
        def on_progress(current: int, total_items: int) -> None:
            progress.setValue(current)
            QApplication.processEvents()
        
        results = self.pivot_service.generate_auto_pivots(df, progress_callback=on_progress)
        
        progress.close()
        
        print(f"Resultados generados: {len(results)} pivotes")
        for name in results:
            print(f"  - {name}: {results[name].shape}")
        
        pivot_view = self.view_coordinator.get_pivot_view()
        if pivot_view:
            pivot_view.set_pivot_results(results)
        
        self.view_coordinator.switch_to(ViewRegistry.VIEW_PIVOT)
        self.status_message.emit(
            f"Pivotes generados: {len(results)} tablas "
            f"({len(cat_cols)} categ × {len(num_cols)} num)")
    
    def exportar_resultado_pivote(self) -> None:
        """Exportar resultado de pivote"""
        if not self.data_service.has_data:
            QMessageBox.warning(self.parent_window, "Advertencia",
                              "No hay datos para exportar.")
            return
        self.mostrar_dialogo_exportacion("Resultado_Pivote")
    
    # ==================== EXPORTACIÓN ====================
    
    def mostrar_info(self) -> None:
        """Mostrar el modal de información del archivo cargado"""
        df = self.data_service.datos_originales
        if df is not None:
            self.view_coordinator.show_info_modal(
                df, self.data_service.get_filename())
        else:
            QMessageBox.warning(self.parent_window, "Advertencia",
                              "No hay datos cargados.")

    def _exportar_con_dialogo(
        self,
        export_method: Any,
        df: pd.DataFrame,
        titulo: str,
        filtro: str,
        default_filename: str = "",
        pre_dialogo: Any = None,
    ) -> None:
        """Flujo genérico de exportación: diálogo de archivo, servicio, mensaje."""
        filepath, _ = QFileDialog.getSaveFileName(
            self.parent_window, titulo, default_filename, filtro
        )
        if not filepath:
            return

        extra_args: tuple[Any, ...] = ()
        if pre_dialogo:
            result = pre_dialogo()
            if result is None:
                return
            extra_args = result if isinstance(result, tuple) else (result,)

        success, message = export_method(df, filepath, *extra_args)
        if success:
            QMessageBox.information(self.parent_window, "Éxito", message)
        else:
            QMessageBox.critical(self.parent_window, "Error", message)

    def mostrar_dialogo_exportacion(self, default_prefix: str = "Exportacion") -> None:
        """Diálogo de exportación con selección de formato y nombre por defecto."""
        df = self.data_service.datos_actuales
        if df is None or df.empty:
            QMessageBox.warning(self.parent_window, "Advertencia", "No hay datos para exportar.")
            return

        dialog = QDialog(self.parent_window)
        dialog.setWindowTitle("Exportar Datos")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Formato:"))
        format_combo = QComboBox()
        format_combo.addItems(["Excel (.xlsx)", "CSV (.csv)", "PDF (.pdf)", "SQLite (.db)"])
        format_combo.setCurrentText("Excel (.xlsx)")
        format_layout.addWidget(format_combo)
        layout.addLayout(format_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        export_btn = QPushButton("Exportar")
        export_btn.clicked.connect(dialog.accept)
        buttons_layout.addWidget(export_btn)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

        if dialog.exec() != QDialog.Accepted:
            return

        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        default_filename = f"{default_prefix}_{timestamp}"
        format_text = format_combo.currentText()

        if "Excel" in format_text:
            self._exportar_con_dialogo(
                self.export_service.export_to_xlsx, df,
                "Guardar como Excel", "Archivos Excel (*.xlsx)", default_filename,
            )
        elif "CSV" in format_text:
            self._exportar_con_dialogo(
                self.export_service.export_to_csv, df,
                "Guardar como CSV", "Archivos CSV (*.csv)", default_filename,
            )
        elif "PDF" in format_text:
            self._exportar_con_dialogo(
                self.export_service.export_to_pdf, df,
                "Guardar como PDF", "Archivos PDF (*.pdf)", default_filename,
            )
        elif "SQLite" in format_text:
            def pedir_nombre_tabla() -> tuple[str] | None:
                name, ok = QInputDialog.getText(
                    self.parent_window, "Nombre de la tabla", "Ingresa el nombre de la tabla:")
                return (name,) if ok and name else None

            self._exportar_con_dialogo(
                self.export_service.export_to_sql, df,
                "Guardar como SQLite", "Bases de Datos SQLite (*.db)", default_filename,
                pre_dialogo=pedir_nombre_tabla,
            )

    def exportar_a_pdf(self) -> None:
        """Exportar a PDF"""
        df = self.data_service.datos_actuales
        if df is None or df.empty:
            QMessageBox.warning(self.parent_window, "Advertencia", "No hay datos para exportar.")
            return
        self._exportar_con_dialogo(
            self.export_service.export_to_pdf, df,
            "Guardar como PDF", "Archivos PDF (*.pdf)", "Exportacion.pdf",
        )

    def exportar_a_xlsx(self) -> None:
        """Exportar a Excel"""
        df = self.data_service.datos_actuales
        if df is None or df.empty:
            QMessageBox.warning(self.parent_window, "Advertencia", "No hay datos para exportar.")
            return
        self._exportar_con_dialogo(
            self.export_service.export_to_xlsx, df,
            "Guardar como Excel", "Archivos Excel (*.xlsx)", "Exportacion.xlsx",
        )

    def exportar_a_csv(self) -> None:
        """Exportar a CSV"""
        df = self.data_service.datos_actuales
        if df is None or df.empty:
            QMessageBox.warning(self.parent_window, "Advertencia", "No hay datos para exportar.")
            return
        self._exportar_con_dialogo(
            self.export_service.export_to_csv, df,
            "Guardar como CSV", "Archivos CSV (*.csv)", "Exportacion.csv",
        )

    def exportar_a_sql(self) -> None:
        """Exportar a SQL"""
        df = self.data_service.datos_actuales
        if df is None or df.empty:
            QMessageBox.warning(self.parent_window, "Advertencia", "No hay datos para exportar.")
            return

        def pedir_nombre_tabla() -> tuple[str] | None:
            name, ok = QInputDialog.getText(
                self.parent_window, "Nombre de la tabla", "Ingresa el nombre de la tabla:")
            return (name,) if ok and name else None

        self._exportar_con_dialogo(
            self.export_service.export_to_sql, df,
            "Guardar como Base de Datos SQL", "Bases de Datos SQLite (*.db)", "Exportacion.db",
            pre_dialogo=pedir_nombre_tabla,
        )

    def exportar_a_imagen(self) -> None:
        """Exportar a imagen — redirige al diálogo genérico hasta implementar export_to_image directa."""
        # TODO: Obtener table_widget de view_coordinator y llamar export_to_image(table_widget, filepath)
        self.mostrar_dialogo_exportacion("Exportacion_Imagen")

    def exportar_datos_separados(self) -> None:
        """Exportar datos separados por columna usando plantillas Excel."""
        if not self.data_service.has_data:
            QMessageBox.warning(self.parent_window, "Advertencia",
                              "No hay datos para exportar.")
            return

        from app.widgets.export_separated_dialog import ExportSeparatedDialog

        df = self.data_service.datos_actuales
        dialog = ExportSeparatedDialog(df, self.parent_window)
        if dialog.exec() != QDialog.Accepted:
            return

        config = dialog.get_configuration(validate=False)
        if config is None:
            return

        result = self.export_service.export_separated(df, config)

        if result.get('success'):
            files = result.get('files_created', 0)
            groups = result.get('groups_processed', 0)
            QMessageBox.information(self.parent_window, "Éxito",
                f"Exportación completada.\n\n"
                f"Archivos creados: {files}\n"
                f"Grupos procesados: {groups}")
        else:
            error = result.get('error', 'Error desconocido')
            QMessageBox.critical(self.parent_window, "Error",
                f"Error en la exportación:\n{error}")
    
    # ==================== LIMPIEZA DE DATOS ====================

    def ejecutar_limpieza_rapida(self) -> None:
        """Aplica limpieza estándar y muestra resumen."""
        df = self.data_service.datos_actuales
        try:
            limpio, resumen = self.cleaning_service.ejecutar_limpieza_rapida(df)
        except ValueError as e:
            QMessageBox.warning(self.parent_window, "Advertencia", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self.parent_window, "Error", f"Error en la limpieza: {e}")
            return

        self.data_service.set_current_data(limpio)
        self.datos_actualizados.emit(self.data_service.datos_actuales)
        self.datos_disponibles.emit(True)

        cols = resumen.get('columns_affected', [])
        cols_str = ', '.join(cols) if cols else 'ninguna'
        QMessageBox.information(
            self.parent_window, "Limpieza completada",
            f"Filas originales: {resumen['rows_original']}\n"
            f"Filas finales: {resumen['rows_final']}\n"
            f"Filas eliminadas: {resumen['rows_removed']}\n"
            f"Columnas afectadas: {cols_str}",
        )
        self.status_message.emit("Limpieza rápida aplicada")

    def ejecutar_limpieza_personalizada(self, opciones: dict[str, Any]) -> None:
        """Aplica limpieza con opciones personalizadas."""
        df = self.data_service.datos_actuales
        try:
            limpio, resumen = self.cleaning_service.ejecutar_limpieza_personalizada(df, opciones)
        except ValueError as e:
            QMessageBox.warning(self.parent_window, "Advertencia", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self.parent_window, "Error", f"Error en la limpieza: {e}")
            return

        self.data_service.set_current_data(limpio)
        self.datos_actualizados.emit(self.data_service.datos_actuales)
        self.datos_disponibles.emit(True)

        cols = resumen.get('columns_affected', [])
        cols_str = ', '.join(cols) if cols else 'ninguna'
        QMessageBox.information(
            self.parent_window, "Limpieza completada",
            f"Filas originales: {resumen['rows_original']}\n"
            f"Filas finales: {resumen['rows_final']}\n"
            f"Filas eliminadas: {resumen['rows_removed']}\n"
            f"Columnas afectadas: {cols_str}",
        )
        self.status_message.emit("Limpieza personalizada aplicada")

    # ==================== FILTROS ====================
    
    def on_filter_applied(self, column: str, term: str) -> None:
        """Manejar filtro aplicado — la vista de datos ya se actualiza vía PaginationManager.data_changed."""
        self.status_message.emit(f"Filtro aplicado en '{column}': '{term}'")

    def on_filter_cleared(self) -> None:
        """Manejar filtro limpiado — la vista de datos ya se restaura vía PaginationManager.data_changed."""
        self.status_message.emit("Filtro limpiado")

    def refresh_recent_files(self) -> None:
        """Actualizar la lista de archivos recientes en MainView"""
        main_view = self.view_coordinator.get_main_view()
        if main_view:
            entries = self.recent_files_service.get_recent()
            main_view.set_recent_files(entries)

    def on_recent_file_clicked(self, filepath: str) -> None:
        """Manejar click en un archivo reciente"""
        self.solicitar_apertura_archivo(filepath)

    def on_recent_file_remove(self, filepath: str) -> None:
        """Eliminar archivo de recientes"""
        self.recent_files_service.remove(filepath)
        self.refresh_recent_files()

    def limpiar_datos(self) -> None:
        """Limpia los datos cargados y restaura el estado inicial."""
        self.data_service.clear_data()
        self.view_coordinator.switch_to(ViewRegistry.VIEW_DATA)
        self.datos_originales_cargados.emit(pd.DataFrame())
        self.datos_actualizados.emit(pd.DataFrame())
        self.datos_disponibles.emit(False)
        self.status_message.emit("Datos limpiados")

    def mostrar_acerca_de(self) -> None:
        """Mostrar diálogo Acerca de"""
        from app.widgets.about_dialog import AboutDialog
        AboutDialog.show_about(self.parent_window)

    # ==================== THREAD CLEANUP ====================

    def _cancel_thread(self, thread: DataLoaderThread | FolderLoaderThread | None) -> None:
        """Detener un hilo de forma segura si está corriendo."""
        if thread is None or not thread.isRunning():
            return
        thread.requestInterruption()
        thread.quit()
        if not thread.wait(2000):
            thread.terminate()
            thread.wait(1000)

    def _on_loader_finished(self) -> None:
        self._loader_thread = None

    def _on_folder_finished(self) -> None:
        self._folder_thread = None

    # ==================== CLEANUP ====================

    def cleanup(self) -> None:
        """Limpieza profunda de recursos, señales e historial."""
        # 0. Detener hilos de carga activos
        self._cancel_thread(self._loader_thread)
        self._cancel_thread(self._folder_thread)
        for thread in self._active_loaders[:]:
            self._cancel_thread(thread)
        self._active_loaders.clear()
        self._loader_thread = None
        self._folder_thread = None
        self._pending_dfs.clear()
        self._pending_paths.clear()

        # 1. Desconectar señales de manera segura
        for sig in (self.status_message, self.datos_originales_cargados,
                    self.datos_actualizados, self.datos_disponibles):
            try:
                sig.disconnect()
            except RuntimeError:
                pass

        # 2. Liberar join_history
        self.join_history = None  # type: ignore[assignment]

        # 3. Liberar referencias a componentes
        self.view_coordinator = None  # type: ignore[assignment]
        self.toolbar_manager = None  # type: ignore[assignment]

        # 4. Limpiar tareas pendientes del ThreadPool global
        from PySide6.QtCore import QThreadPool
        pool = QThreadPool.globalInstance()
        if pool is not None:
            pool.clear()

# Exports
__all__ = ['AppCoordinator']
