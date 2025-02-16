# MainQueryProcess: Processes a query by building a combined retriever and using the LLM.
from rag.core.combined_retriever import CombinedRetriever
from rag.core.container import RAGContainer
from rag.core.factories.llm_factory import LLMFactory
from rag.core.factories.retriever_factory import RetrieverFactory
from rag.core.interfaces import DocumentType, ILLM, IQueryProcess
from rag.core.processors.processor import QueryProcessor


class MainQueryProcess(IQueryProcess):
    def __init__(self, retriever_config: dict,  llm_config: dict):
        # Create basic retrievers for each document type using the generic factory.
        hotel_retriever = RetrieverFactory.create_retriever(retriever_config, DocumentType.HOTEL_INFO)
        review_retriever = RetrieverFactory.create_retriever(retriever_config, DocumentType.HOTEL_REVIEW)
        # Combine them into a domain-specific (but optional) retriever.
        self.combined_retriever = CombinedRetriever(hotel_retriever, review_retriever)
        # Use the LLM provided by the container.
        self.llm = LLMFactory.create_llm(llm_config)
        # Build a QueryProcessor that depends only on the IRetriever interface.
        self.query_processor = QueryProcessor(self.combined_retriever, self.llm)

    def process(self, query: str) -> str:
        """
        Processes the query by retrieving relevant documents and generating an answer.
        """
        return self.query_processor.process(query)
