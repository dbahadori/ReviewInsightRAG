from rag.core.haystack_retriever import HaystackRetriever
from rag.core.interfaces import IRetriever
from rag.core.lang_chain_retriever import LangChainRetriever


class RetrieverFactory:
    @staticmethod
    def create_retriever(config: dict) -> IRetriever:
        """
        Creates a retriever instance based on the provided configuration.

        Args:
            config (dict): Configuration for the retriever (e.g., framework, parameters).

        Returns:
            IRetriever: An instance of the requested retriever.
        """
        framework = config.get("framework", "langchain")  # Default to LangChain
        params = config.get("params", {})

        if framework == "langchain":
            return LangChainRetriever(**params)
        elif framework == "haystack":
            # Assuming 'document_store' is already created and passed in config
            document_store = config.get("document_store")  # Document store passed here
            return HaystackRetriever(embedding_model=params.get("embedding_model"), document_store=document_store)
        else:
            raise ValueError(f"Unsupported retriever framework: {framework}")
