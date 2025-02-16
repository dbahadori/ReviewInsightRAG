from typing import List

from rag.core.factories.document_store_factory import DocumentStoreFactory
from rag.core.interfaces import IDocumentStore, Document

# Factory for document store


class DocumentStore(IDocumentStore):

    def __init__(self, config: dict):
        self.store = DocumentStoreFactory.create_store(config)

    def add_hotel_documents(self, docs: List[Document]):
        # Add documents to the store
        self.store.add_hotel_documents(docs)

    def get_hotel_retriever(self, query: str) -> List[Document]:
        # Search for documents using the vector store
        return self.store.get_hotel_retriever(query)

    def clear(self) -> None:
        self.clear()
