from rag.core.combined_retriever import CombinedRetriever
from rag.core.factories.retriever_factory import RetrieverFactory
from rag.core.interfaces import IRetriever, DocumentType


def build_domain_retriever(config: dict) -> IRetriever:
    hotel_retriever = RetrieverFactory.create_retriever(config.get("retriever"), DocumentType.HOTEL_INFO)
    review_retriever = RetrieverFactory.create_retriever(config.get("retriever"), DocumentType.HOTEL_REVIEW)
    return CombinedRetriever(hotel_retriever, review_retriever)