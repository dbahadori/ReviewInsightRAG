from typing import List
from rag.core.interfaces import IRetriever, Document
from rag.data.document_store import DocumentStore


class HaystackRetriever(IRetriever):
    def __init__(self, embedding_model: str, document_store: DocumentStore, **kwargs):
        """
        Initializes the HaystackRetriever.

        Args:
            embedding_model (str): Name or path of the embedding model for dense retrieval.
            document_store (DocumentStore): The document store where documents are stored (e.g., FAISS, Elasticsearch).
            **kwargs: Additional parameters for retrieval (e.g., model-specific configurations).
        """
        # Assuming document_store is already initialized with the documents
        self.document_store = document_store
        # self.retriever = DenseRetriever(document_store=self.document_store, embedding_model=embedding_model)

    def retrieve(self, query: str) -> List[Document]:
        """
        Retrieves relevant documents based on a query using Haystack.

        Args:
            query (str): The user query.

        Returns:
            List[HotelInfoDocument]: A list of relevant documents retrieved by the retriever.
        """
        results = self.retriever.retrieve(query, top_k=5)  # Retrieve top 5 documents
        return [HotelInfoDocument(content=doc.content, metadata=doc.metadata) for doc in results]
