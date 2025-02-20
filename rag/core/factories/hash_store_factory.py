from rag.core.interfaces import IHashStore, HashStoreType
from rag.data.SQLite_hash_store import SQLiteHashStore


class HashStoreFactory:
    @staticmethod
    def create_hash_store(config=None, store_type: HashStoreType = HashStoreType.SQLITE, **kwargs) -> IHashStore:

        if config:
            store_type = HashStoreType(config.type)
        store_type = store_type or HashStoreType.SQLITE
        if store_type is HashStoreType.SQLITE:
            return SQLiteHashStore(**kwargs)
        else:
            raise ValueError(f"Unsupported hash store type: {store_type}")
