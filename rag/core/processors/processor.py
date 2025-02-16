from rag.core.interfaces import IRetriever, ILLM, IQueryProcess


class QueryProcessor(IQueryProcess):
    def __init__(self, retriever: IRetriever, llm: ILLM):
        self.retriever = retriever
        self.llm = llm

    def process(self, query: str) -> str:
        documents = self.retriever.retrieve(query)
        response = self.llm.generate(query, documents)
        return response
