from rag.core.deepSeek import DeepSeek
from rag.core.lang_chain_retriever import LangChainRetriever


class QueryProcessor:
    def __init__(self, retriever: LangChainRetriever, llm: DeepSeek):
        self.retriever = retriever
        self.llm = llm

    def process(self, query: str) -> str:
        documents = self.retriever.retrieve(query)
        response = self.llm.generate(query, documents)
        return response
