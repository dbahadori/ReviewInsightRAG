from rag.core.interfaces import IDocumentStore, DocumentStoreType
from rag.data.faiss_store import FAISSStore


class DocumentStoreFactory:
    @staticmethod
    def create_store(config=None, store_type: DocumentStoreType = None) -> IDocumentStore:
        if config:
            store_type = config.type

        store_type = store_type or "faiss"

        if store_type == "faiss":
            return FAISSStore(config)
        else:
            raise ValueError(f"Unsupported document store: {store_type}")
