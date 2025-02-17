# MainQueryProcess: Processes a query by building a combined retriever and using the LLM.

from rag.core.interfaces import IQueryProcess, IRetriever, ILLM
from rag.core.processors.processor import QueryProcessor
from rag.core.retrievers.combined_retriever import CombinedRetriever


class MainQueryProcess(IQueryProcess):
    def __init__(self, hotel_retriever: IRetriever, review_retriever: IRetriever,  llm: ILLM):
        # Combine them into a domain-specific (but optional) retriever.
        self.combined_retriever = CombinedRetriever(hotel_retriever, review_retriever)
        # Use the LLM provided by the container.
        self.llm = llm
        # Build a QueryProcessor that depends only on the IRetriever interface.
        self.query_processor = QueryProcessor(self.combined_retriever, self.llm)

    def process(self, query: str) -> str:
        """
        Processes the query by retrieving relevant documents and generating an answer.
        """
        return self.query_processor.process(query)
