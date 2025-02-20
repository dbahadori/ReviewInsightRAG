from rag.core.interfaces import IRetriever, DocumentType, RetrieverFrameworkType
from rag.core.retrievers.lang_chain_retriever import LangChainRetriever


class RetrieverFactory:
    @staticmethod
    def create_retriever(config=None, document_store=None, doc_type: DocumentType = None) -> IRetriever:
        """
        Creates a basic retriever (e.g. LangChainRetriever) based on the provided configuration.
        """
        if config is None:
            raise ValueError("Configuration must be provided to create a retriever.")
        if document_store is None:
            raise ValueError("A valid DocumentStore instance must be provided to create a retriever.")

        framework = RetrieverFrameworkType(config.framework.lower())
        params = config.params
        if framework == RetrieverFrameworkType.LANGCHAIN:
            base_retriever = document_store.get_retriever(doc_type)
            return LangChainRetriever(base_retriever,
                                      params.get("embedding_model", "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"))
        elif framework == RetrieverFrameworkType.HAYSTACK:
            raise NotImplementedError("HaystackRetriever not implemented.")
        else:
            raise ValueError(f"Unsupported retriever framework: {framework}")
