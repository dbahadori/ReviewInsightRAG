from typing import List

from rag.core.factories.document_store_factory import DocumentStoreFactory
from rag.core.interfaces import IDocumentStore, Document

# Factory for document store


class DocumentStore(IDocumentStore):
    def __init__(self, config: dict):
        store_type = config["document_store"]["type"]
        self.store = DocumentStoreFactory.create_store(config)

    def add_documents(self, docs: List[str]):
        # Add documents to the store
        self.store.add_documents(docs)

    def search(self, query: str) -> List[Document]:
        # Search for documents using the vector store
        return self.store.search(query)
