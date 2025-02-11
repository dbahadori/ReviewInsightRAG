from rag.data.faiss_store import FAISSStore
from rag.data.pinecone_store import PineconeStore

class DocumentStoreFactory:
    @staticmethod
    def create_store(config: dict):
        store_type = config["document_store"]["type"]
        if store_type == "faiss":
            return FAISSStore(config)
        elif store_type == "pinecone":
            return PineconeStore(config)
        else:
            raise ValueError(f"Unsupported document store: {store_type}")
