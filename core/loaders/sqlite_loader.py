"""
SQLite File Loader
Handles SQLite database files
"""

import pandas as pd
import os
from typing import Optional, Dict, Any
from .base_loader import FileLoader


class SqliteLoader(FileLoader):
    """
    File loader for SQLite database format
    """

    def get_supported_extensions(self) -> list:
        return ['.db', '.sqlite', '.sqlite3']

    def load(self, skip_rows: int = 0, column_names: Optional[Dict[str, str]] = None, table_name: str = None) -> pd.DataFrame:
        """
        Load SQLite database into DataFrame
        
        Args:
            skip_rows: Number of rows to skip at the beginning
            column_names: Dictionary for renaming columns
            table_name: Name of the table to load (if None, load first table)
            
        Returns:
            DataFrame with loaded data
        """
        try:
            # If no table name provided, get the first table
            if table_name is None:
                table_name = self._get_first_table()
            
            if table_name is None:
                raise ValueError("No tables found in the database")
            
            # Load from SQLite using SQLAlchemy
            import sqlalchemy as sa
            engine = sa.create_engine(f'sqlite:///{self.filepath}')
            
            query = f"SELECT * FROM {table_name}"
            if skip_rows > 0:
                query += f" LIMIT -1 OFFSET {skip_rows}"
            
            df = pd.read_sql(query, engine)
            
            # Apply column renaming if specified
            if column_names:
                df = df.rename(columns=column_names)
            
            return df
            
        except Exception as e:
            raise Exception(f"Error loading SQLite file {self.filepath}: {str(e)}")

    def _get_first_table(self) -> str:
        """
        Get the name of the first table in the database
        
        Returns:
            Name of the first table, or None if no tables found
        """
        try:
            import sqlalchemy as sa
            engine = sa.create_engine(f'sqlite:///{self.filepath}')
            
            # Get table names
            inspector = sa.inspect(engine)
            table_names = inspector.get_table_names()
            
            return table_names[0] if table_names else None
        except:
            return None

    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about the SQLite file
        """
        try:
            file_size = os.path.getsize(self.filepath)
            
            # Get database metadata
            try:
                import sqlalchemy as sa
                engine = sa.create_engine(f'sqlite:///{self.filepath}')
                
                inspector = sa.inspect(engine)
                table_names = inspector.get_table_names()
                
                # Get info about first table
                table_info = {}
                if table_names:
                    first_table = table_names[0]
                    columns = inspector.get_columns(first_table)
                    table_info = {
                        'first_table': first_table,
                        'column_count': len(columns),
                        'columns': [col['name'] for col in columns]
                    }
                
                return {
                    'format': 'SQLite',
                    'tables': table_names,
                    'table_count': len(table_names),
                    'file_size_bytes': file_size,
                    'file_size_mb': round(file_size / (1024 * 1024), 2),
                    'sqlalchemy_version': sa.__version__,
                    **table_info
                }
            except ImportError:
                return {
                    'format': 'SQLite',
                    'file_size_bytes': file_size,
                    'file_size_mb': round(file_size / (1024 * 1024), 2),
                    'note': 'SQLAlchemy not available for detailed metadata'
                }
                
        except Exception as e:
            return {'error': str(e)}

    def can_load_chunks(self) -> bool:
        """
        SQLite files support chunk loading
        """
        return True

    def load_in_chunks(self, chunk_size: int = 1000) -> pd.DataFrame:
        """
        Load SQLite file in chunks
        """
        try:
            import sqlalchemy as sa
            engine = sa.create_engine(f'sqlite:///{self.filepath}')
            
            # Get first table
            table_name = self._get_first_table()
            if table_name is None:
                raise ValueError("No tables found in the database")
            
            chunk_list = []
            offset = 0
            
            while True:
                query = f"SELECT * FROM {table_name} LIMIT {chunk_size} OFFSET {offset}"
                chunk_df = pd.read_sql(query, engine)
                
                if chunk_df.empty:
                    break
                
                chunk_list.append(chunk_df)
                offset += chunk_size
            
            return pd.concat(chunk_list, ignore_index=True)
            
        except Exception as e:
            raise Exception(f"Error loading SQLite file in chunks: {str(e)}")

    def get_table_names(self) -> list:
        """
        Get list of table names in the database
        
        Returns:
            List of table names
        """
        try:
            import sqlalchemy as sa
            engine = sa.create_engine(f'sqlite:///{self.filepath}')
            inspector = sa.inspect(engine)
            return inspector.get_table_names()
        except:
            return []

    def _estimate_rows(self) -> int:
        """
        Estimate number of rows in SQLite file
        """
        try:
            import sqlalchemy as sa
            engine = sa.create_engine(f'sqlite:///{self.filepath}')
            
            # Get first table
            table_name = self._get_first_table()
            if table_name is None:
                return 0
            
            # Count rows
            query = f"SELECT COUNT(*) as count FROM {table_name}"
            result = pd.read_sql(query, engine)
            return result['count'].iloc[0]
        except:
            return super()._estimate_rows()