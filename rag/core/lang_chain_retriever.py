from typing import List

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma, Pinecone

from rag.core.interfaces import IRetriever, Document

class LangChainRetriever(IRetriever):
    def __init__(self, vector_store_type: str = "faiss", embedding_model: str = "sentence-transformers/all-mpnet-base-v2", **kwargs):
        """
        Initializes the LangChain retriever.

        Args:
            vector_store_type (str): Type of vector store (e.g., "faiss", "chroma", "pinecone").
            embedding_model (str): Name of the embedding model.
            **kwargs: Additional parameters for the vector store.
        """
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.vector_store = self._create_vector_store(vector_store_type, **kwargs)
        self.retriever = self.vector_store.as_retriever()

    def _create_vector_store(self, vector_store_type: str, **kwargs):
        """
        Creates a vector store based on the specified type.

        Args:
            vector_store_type (str): Type of vector store.
            **kwargs: Additional parameters for the vector store.

        Returns:
            VectorStore: An instance of the specified vector store.
        """
        if vector_store_type == "faiss":
            return FAISS(self.embeddings, **kwargs)
        elif vector_store_type == "chroma":
            return Chroma(self.embeddings, **kwargs)
        elif vector_store_type == "pinecone":
            return Pinecone(self.embeddings, **kwargs)
        else:
            raise ValueError(f"Unsupported vector store type: {vector_store_type}")

    def retrieve(self, query: str) -> List[Document]:
        """
        Retrieves relevant documents for a given query.

        Args:
            query (str): The user query.

        Returns:
            List[Document]: A list of relevant documents.
        """
        results = self.retriever.get_relevant_documents(query)
        return [Document(content=doc.page_content, metadata=doc.metadata) for doc in results]
