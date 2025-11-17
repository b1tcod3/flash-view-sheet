"""
Excel Consolidator
Handles consolidation of multiple Excel DataFrames
"""

import pandas as pd
import os
from typing import List, Dict, Any, Optional, Callable


class ExcelConsolidator:
    """
    Class for consolidating multiple Excel DataFrames
    """

    def __init__(self):
        self.dataframes = []
        self.column_mappings = {}
        self.included_columns = []  # If empty, include all
        self.excluded_columns = []

    def add_dataframe(self, df: pd.DataFrame, source_name: str = ""):
        """
        Add a DataFrame to be consolidated

        Args:
            df: DataFrame to add
            source_name: Name of the source file
        """
        self.dataframes.append({
            'dataframe': df.copy(),
            'source': source_name,
            'columns': df.columns.tolist()
        })

    def set_column_mappings(self, mappings: Dict[str, str]):
        """
        Set column renaming mappings

        Args:
            mappings: Dictionary {old_name: new_name}
        """
        self.column_mappings = mappings

    def set_column_selection(self, included_columns: List[str] = None, excluded_columns: List[str] = None):
        """
        Set column selection for consolidation

        Args:
            included_columns: List of column names to include (if empty, include all except excluded)
            excluded_columns: List of column names to exclude
        """
        if included_columns is not None:
            self.included_columns = included_columns
        if excluded_columns is not None:
            self.excluded_columns = excluded_columns

    def align_by_position(self) -> pd.DataFrame:
        """
        Align DataFrames by column position

        Returns:
            Consolidated DataFrame
        """
        if not self.dataframes:
            return pd.DataFrame()

        # Find the maximum number of columns
        max_columns = max(len(df['columns']) for df in self.dataframes)

        # Create aligned DataFrames
        aligned_dfs = []
        for df_info in self.dataframes:
            df = df_info['dataframe']
            columns = df_info['columns']

            # Pad with NaN columns if necessary
            if len(columns) < max_columns:
                for i in range(len(columns), max_columns):
                    df[f'__extra_col_{i}__'] = pd.NA
                    columns.append(f'__extra_col_{i}__')

            # Reorder columns to match positions
            df_aligned = df[columns[:max_columns]]

            # Add source column if specified
            if df_info['source']:
                df_aligned = df_aligned.copy()
                df_aligned['__source__'] = df_info['source']

            aligned_dfs.append(df_aligned)

        # Concatenate all DataFrames
        consolidated = pd.concat(aligned_dfs, ignore_index=True)

        # Apply column renaming
        if self.column_mappings:
            consolidated = consolidated.rename(columns=self.column_mappings)

        # Remove temporary extra columns
        extra_cols = [col for col in consolidated.columns if col.startswith('__extra_col_')]
        consolidated = consolidated.drop(columns=extra_cols)

        # Apply column selection
        if self.included_columns or self.excluded_columns:
            columns_to_keep = []
            for col in consolidated.columns:
                if col == '__source__':  # Always keep source column if present
                    columns_to_keep.append(col)
                elif self.excluded_columns and col in self.excluded_columns:
                    continue
                elif self.included_columns and col not in self.included_columns:
                    continue
                else:
                    columns_to_keep.append(col)
            consolidated = consolidated[columns_to_keep]

        return consolidated

    def get_column_alignment_preview(self) -> List[Dict[str, Any]]:
        """
        Get preview of column alignment

        Returns:
            List of dictionaries with alignment information
        """
        if not self.dataframes:
            return []

        max_columns = max(len(df['columns']) for df in self.dataframes)

        alignment = []
        for i in range(max_columns):
            column_info = {'position': i + 1, 'sources': {}}

            for df_info in self.dataframes:
                source = df_info['source'] or f"File {len(alignment) + 1}"
                columns = df_info['columns']

                if i < len(columns):
                    column_info['sources'][source] = columns[i]
                else:
                    column_info['sources'][source] = None

            alignment.append(column_info)

        return alignment

    def consolidate(self, alignment_method: str = 'position') -> pd.DataFrame:
        """
        Consolidate all DataFrames

        Args:
            alignment_method: Method to align columns ('position' or 'name')

        Returns:
            Consolidated DataFrame
        """
        if alignment_method == 'position':
            return self.align_by_position()
        else:
            raise ValueError(f"Unsupported alignment method: {alignment_method}")

    def consolidate_chunked(self, file_paths: List[str], alignment_method: str = 'position',
                           chunk_size: int = 10, progress_callback=None) -> pd.DataFrame:
        """
        Consolidate DataFrames in chunks for better memory management

        Args:
            file_paths: List of file paths to process
            alignment_method: Method to align columns ('position' or 'name')
            chunk_size: Number of files to process per chunk
            progress_callback: Optional callback function for progress updates

        Returns:
            Consolidated DataFrame
        """
        if not file_paths:
            return pd.DataFrame()

        consolidated_chunks = []

        for i in range(0, len(file_paths), chunk_size):
            chunk_files = file_paths[i:i + chunk_size]

            # Clear previous dataframes to free memory
            self.clear()

            # Load chunk
            for file_path in chunk_files:
                try:
                    df = pd.read_excel(file_path)
                    self.add_dataframe(df, os.path.basename(file_path))
                except Exception as e:
                    # Log error but continue with other files
                    print(f"Error loading {file_path}: {e}")
                    continue

            # Consolidate chunk
            if self.dataframes:
                chunk_result = self.consolidate(alignment_method)
                consolidated_chunks.append(chunk_result)

            # Progress callback
            if progress_callback:
                progress = min((i + len(chunk_files)) / len(file_paths) * 100, 100)
                progress_callback(progress)

        # Final consolidation of all chunks
        if consolidated_chunks:
            final_result = pd.concat(consolidated_chunks, ignore_index=True)

            # Apply column mappings if set
            if self.column_mappings:
                final_result = final_result.rename(columns=self.column_mappings)

            # Apply column selection
            if self.included_columns or self.excluded_columns:
                columns_to_keep = []
                for col in final_result.columns:
                    if col == '__source__':  # Always keep source column if present
                        columns_to_keep.append(col)
                    elif self.excluded_columns and col in self.excluded_columns:
                        continue
                    elif self.included_columns and col not in self.included_columns:
                        continue
                    else:
                        columns_to_keep.append(col)
                final_result = final_result[columns_to_keep]

            return final_result
        else:
            return pd.DataFrame()

    def clear(self):
        """Clear all DataFrames"""
        self.dataframes = []
        self.column_mappings = {}
        self.included_columns = []
        self.excluded_columns = []