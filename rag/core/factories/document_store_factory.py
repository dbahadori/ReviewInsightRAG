from rag.core.interfaces import IDocumentStore, DocumentStoreType
from rag.data.faiss_store import FAISSStore


class DocumentStoreFactory:
    @staticmethod
    def create_store(config=None, store_type: DocumentStoreType = DocumentStoreType.FAISS) -> IDocumentStore:
        """
        Creates an IDocumentStore instance based on the provided configuration or a direct argument.

        This implementation follows a configuration-driven approach:
          - If a configuration is provided, the store type is extracted from config (i.e., config.type) and overrides
            any direct store_type argument.
          - If no configuration is provided, the factory defaults to the direct argument (defaulting to FAISS).

        This ensures a consistent, predictable behavior and avoids ambiguity between direct arguments and configuration.
        """
        if config:
            store_type = DocumentStoreType(config.type)

        store_type = store_type or DocumentStoreType.FAISS

        if store_type is DocumentStoreType.FAISS:
            return FAISSStore(config)
        else:
            raise ValueError(f"Unsupported document store: {store_type}")
