from rag.core.factories.document_store_factory import DocumentStoreFactory
from rag.core.interfaces import IRetriever, DocumentType
from rag.core.retrievers.lang_chain_retriever import LangChainRetriever


class RetrieverFactory:
    @staticmethod
    def create_retriever(config: dict, doc_type: DocumentType) -> IRetriever:
        """
        Creates a basic retriever (e.g. LangChainRetriever) based on the provided configuration.
        This factory is now independent of domain-specific logic.
        """
        framework = config.get("framework", "langchain").lower()
        params = config.get("params", {})
        if framework == "langchain":
            document_store = DocumentStoreFactory.create_store(config.get("document_store"))
            base_retriever = document_store.get_retriever(doc_type)
            return LangChainRetriever(base_retriever, params.get("embedding_model", "sentence-transformers/all-mpnet-base-v2"))
        elif framework == "haystack":
            raise NotImplementedError("HaystackRetriever not implemented.")
        else:
            raise ValueError(f"Unsupported retriever framework: {framework}")
