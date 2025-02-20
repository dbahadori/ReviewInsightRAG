from typing import List

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.retrievers import BaseRetriever
from rag.core.interfaces import IRetriever, Document


class LangChainRetriever(IRetriever):
    def __init__(self, retriever: BaseRetriever, embedding_model: str = "paraphrase-multilingual-mpnet-base-v2"):
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.retriever = retriever

    def retrieve(self, query: str) -> List[Document]:
        results = self.retriever.get_relevant_documents(query)
        return [Document(content=doc.page_content, metadata=doc.metadata) for doc in results]
