"""
JoinHistory: Sistema para mantener historial de operaciones de cruce
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any
from dataclasses import dataclass, asdict
import pandas as pd

from .models import JoinConfig, JoinResult

@dataclass
class JoinHistoryEntry:
    """Entrada del historial de join"""
    id: str
    timestamp: datetime
    left_dataset_name: str
    right_dataset_name: str
    config: JoinConfig
    result_metadata: dict[str, Any]
    success: bool
    error_message: str = ""

class JoinHistory:
    """Sistema para mantener historial de operaciones de cruce"""

    def __init__(self, max_entries: int = 50) -> None:
        self.max_entries = max_entries
        self.entries: list[JoinHistoryEntry] = []
        self.history_file = Path(__file__).parent / "join_history.json"

        # Cargar historial existente
        self._load_history()

    def add_entry(self, left_name: str, right_name: str, config: JoinConfig, result: JoinResult) -> None:
        """Añadir nueva entrada al historial"""
        entry_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.entries)}"

        entry = JoinHistoryEntry(
            id=entry_id,
            timestamp=datetime.now(),
            left_dataset_name=left_name,
            right_dataset_name=right_name,
            config=config,
            result_metadata={
                'result_rows': result.metadata.result_rows,
                'join_type': result.metadata.join_type.value,
                'join_keys': result.metadata.join_keys,
                'matched_rows': result.metadata.matched_rows,
                'processing_time': result.metadata.processing_time_seconds,
                'memory_usage': result.metadata.memory_usage_mb
            },
            success=result.success,
            error_message=result.error_message
        )

        self.entries.insert(0, entry)  # Añadir al inicio

        # Mantener límite de entradas
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[:self.max_entries]

        # Guardar
        self._save_history()

    def get_entries(self, limit: int | None = None) -> list[JoinHistoryEntry]:
        """Obtener entradas del historial"""
        if limit:
            return self.entries[:limit]
        return self.entries

    def get_entry(self, entry_id: str) -> JoinHistoryEntry | None:
        """Obtener entrada específica por ID"""
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None

    def clear_history(self) -> None:
        """Limpiar todo el historial"""
        self.entries = []
        self._save_history()

    def export_history(self, filepath: str) -> None:
        """Exportar historial a archivo JSON"""
        data = {
            'exported_at': datetime.now().isoformat(),
            'entries': [self._entry_to_dict(entry) for entry in self.entries]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    def import_history(self, filepath: str) -> None:
        """Importar historial desde archivo JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            imported_entries = []
            for entry_data in data.get('entries', []):
                entry = self._dict_to_entry(entry_data)
                if entry:
                    imported_entries.append(entry)

            # Añadir al inicio
            self.entries = imported_entries + self.entries

            # Mantener límite
            if len(self.entries) > self.max_entries:
                self.entries = self.entries[:self.max_entries]

            self._save_history()

        except Exception as e:
            raise ValueError(f"Error importando historial: {str(e)}")

    def _entry_to_dict(self, entry: JoinHistoryEntry) -> dict[str, Any]:
        """Convertir entrada a diccionario para serialización"""
        return {
            'id': entry.id,
            'timestamp': entry.timestamp.isoformat(),
            'left_dataset_name': entry.left_dataset_name,
            'right_dataset_name': entry.right_dataset_name,
            'config': {
                'join_type': entry.config.join_type.value,
                'left_keys': entry.config.left_keys,
                'right_keys': entry.config.right_keys,
                'suffixes': entry.config.suffixes,
                'validate_integrity': entry.config.validate_integrity,
                'sort_results': entry.config.sort_results,
                'indicator': entry.config.indicator
            },
            'result_metadata': entry.result_metadata,
            'success': entry.success,
            'error_message': entry.error_message
        }

    def _dict_to_entry(self, data: dict[str, Any]) -> JoinHistoryEntry | None:
        """Convertir diccionario a entrada"""
        try:
            from .models import JoinType

            config_data = data['config']
            config = JoinConfig(
                join_type=JoinType(config_data['join_type']),
                left_keys=config_data.get('left_keys', []),
                right_keys=config_data.get('right_keys', []),
                suffixes=tuple(config_data.get('suffixes', ('_left', '_right'))),
                validate_integrity=config_data.get('validate_integrity', True),
                sort_results=config_data.get('sort_results', True),
                indicator=config_data.get('indicator', False)
            )

            return JoinHistoryEntry(
                id=data['id'],
                timestamp=datetime.fromisoformat(data['timestamp']),
                left_dataset_name=data['left_dataset_name'],
                right_dataset_name=data['right_dataset_name'],
                config=config,
                result_metadata=data['result_metadata'],
                success=data['success'],
                error_message=data.get('error_message', '')
            )
        except Exception:
            return None

    def _load_history(self) -> None:
        """Cargar historial desde archivo"""
        if Path(self.history_file).exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.entries = []
                for entry_data in data.get('entries', []):
                    entry = self._dict_to_entry(entry_data)
                    if entry:
                        self.entries.append(entry)

            except Exception:
                # Si hay error, empezar con historial vacío
                self.entries = []

    def _save_history(self) -> None:
        """Guardar historial a archivo"""
        try:
            data = {
                'entries': [self._entry_to_dict(entry) for entry in self.entries]
            }

            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)

        except Exception:
            # Si no se puede guardar, continuar sin error
            pass