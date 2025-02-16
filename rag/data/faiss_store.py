import os
import numpy as np
import logging
from typing import List

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import BaseRetriever

from rag.core.interfaces import DocumentType, IDocumentStore, Document


class FAISSStore(IDocumentStore):
    def __init__(self, config: dict):
        """
        Initialize a FAISS-based document store.

        The config should include:
          - params.embedding_model: embedding model name.
          - params.persistent: whether to persist the index.
          - params.hotel_index_path: path for hotel info index.
          - params.reviews_index_path: path for reviews index.
        """
        self.config = config
        self.params = config.get("params", {})
        self.embedding_model = self.params.get("embedding_model", "sentence-transformers/all-mpnet-base-v2")
        self.persistent = self.params.get("persistent", True)


        # Use separate index paths for each document type.
        self.index_paths = {
            DocumentType.HOTEL_INFO: self.params.get("hotel_index_path", "faiss_hotel_index"),
            DocumentType.HOTEL_REVIEW: self.params.get("reviews_index_path", "faiss_reviews_index")
        }
        self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        # Create a FAISS vectorstore per document type.
        self.vectorstores = {
            doc_type: self._initialize_store(self.index_paths[doc_type])
            for doc_type in DocumentType
        }

    def _initialize_store(self, index_path: str) -> FAISS:
        """
        Initialize the FAISS vector store.
        If persistent mode is enabled and an index exists at index_path, load it.
        Otherwise, create a new index using a dummy entry.
        """
        if self.persistent and index_path and os.path.exists(index_path):
            return FAISS.load_local(index_path, self.embeddings, allow_dangerous_deserialization=True)
        else:
            dummy_texts = ["dummy"]
            dummy_embeddings = self.embeddings.embed_documents(dummy_texts)
            if not dummy_embeddings:
                raise ValueError("Embedding model returned empty embeddings.")
            dummy_embeddings = np.array(dummy_embeddings)
            data_store = FAISS.from_embeddings(list(zip(dummy_texts, dummy_embeddings)), self.embeddings)
            if self.persistent and index_path:
                data_store.save_local(folder_path=index_path, index_name="index")
            return data_store

    def add_documents(self, docs: List[Document], doc_type: DocumentType) -> None:
        """
        Add a list of Document objects to the FAISS store for the given document type.
        """
        vectorstore = self.vectorstores[doc_type]
        texts = [doc.content for doc in docs]
        metadatas = [doc.metadata for doc in docs]
        # FAISS.add_texts will generate embeddings internally using self.embeddings.
        vectorstore.add_texts(texts, metadatas=metadatas)
        if self.persistent:
            self.save(doc_type)

    def save(self, doc_type: DocumentType) -> None:
        """Save the FAISS index for the specified document type to disk."""
        if self.persistent:
            index_path = self.index_paths[doc_type]
            self.vectorstores[doc_type].save_local(index_path)
        else:
            logging.info("Persistent mode disabled, not saving index.")

    def search(self, query: str, k: int = 5, doc_type: DocumentType = DocumentType.HOTEL_INFO) -> List[Document]:
        """Search the FAISS store for a query and return relevant documents."""
        vectorstore = self.vectorstores[doc_type]
        results = vectorstore.similarity_search(query, k=k)
        return [Document(content=doc.page_content, metadata=doc.metadata) for doc in results]

    def get_retriever(self, doc_type: DocumentType) -> BaseRetriever:
        """Return a retriever instance for the specified document type."""
        vectorstore = self.vectorstores[doc_type]
        return vectorstore.as_retriever()

    def clear(self, doc_type: DocumentType) -> None:
        """Clear the FAISS index for the specified document type (in-memory and on disk)."""
        index_path = self.index_paths[doc_type]
        self.vectorstores[doc_type] = FAISS.from_texts([], self.embeddings)
        if self.persistent and os.path.exists(index_path):
            os.remove(index_path)
            logging.info(f"Index file {index_path} deleted.")
