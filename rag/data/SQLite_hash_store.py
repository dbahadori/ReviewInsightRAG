import sqlite3
from typing import Optional

from rag.core.interfaces import IHashStore
from utils.path_util import PathUtil


class SQLiteHashStore(IHashStore):
    def __init__(self, db_name: str = "hash_store.db", table_name: str = "hash_store"):
        self.db_path = PathUtil.construct_path( PathUtil.get_project_base_path(),'data','hash',db_name)
        self.table_name = table_name
        self._setup_database()

    def _setup_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id TEXT PRIMARY KEY,
                hash TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_hash(self, id: str, hash: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'''
            INSERT OR REPLACE INTO {self.table_name} (id, hash) VALUES (?, ?)
        ''', (id, hash))
        conn.commit()
        conn.close()

    def load_hash(self, id: str) -> Optional[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT hash FROM {self.table_name} WHERE id=?
        ''', (id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
