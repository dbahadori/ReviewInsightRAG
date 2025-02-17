from rag.core.interfaces import IHashStore
from rag.data.SQLite_hash_store import SQLiteHashStore


class HashStoreFactory:
    @staticmethod
    def create_hash_store(config=None, store_type: str ="sqlite" , **kwargs) -> IHashStore:
        if store_type == "sqlite":
            return SQLiteHashStore(**kwargs)
        else:
            raise ValueError(f"Unsupported hash store type: {store_type}")

