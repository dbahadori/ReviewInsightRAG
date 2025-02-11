from typing import List
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

class FAISSStore:
    def __init__(self, config: dict):
        self.config = config
        self.vector_store = None
        self.index_file_path = config.get("index_file_path", "faiss_index")  # Default file path
        self._initialize_store()

    def _initialize_store(self):
        """Initialize the vector store, load from disk if persistent mode is enabled and index exists."""
        if self.config.get("persistent", False):
            try:
                # Load index if it exists
                self.vector_store = FAISS.load_local(self.index_file_path, HuggingFaceEmbeddings())
                print(f"FAISS index loaded from {self.index_file_path}.")
            except FileNotFoundError:
                print(f"No index found at {self.index_file_path}. Creating a new index.")
                self.vector_store = FAISS(HuggingFaceEmbeddings())
        else:
            # Memory-only mode
            self.vector_store = FAISS(HuggingFaceEmbeddings())

    def add_documents(self, docs: List[str]):
        """Add documents to the FAISS vector store."""
        self.vector_store.add_texts(docs)

        # Save index to disk if persistent mode is enabled
        if self.config.get("persistent", False):
            self._save_index()

    def _save_index(self):
        """Save the FAISS index to disk."""
        self.vector_store.save_local(self.index_file_path)
        print(f"FAISS index saved to {self.index_file_path}.")

    def search(self, query: str, k: int = 5):
        """Perform similarity search with FAISS."""
        return self.vector_store.similarity_search(query, k=k)

    def save(self):
        """Explicitly save the FAISS index to disk."""
        if self.config.get("persistent", False):
            self._save_index()
        else:
            print("Persistent mode is disabled. Enable it in the config to save the index.")

    def clear(self):
        """Clear the FAISS index (in-memory and disk)."""
        self.vector_store = FAISS(HuggingFaceEmbeddings())
        if self.config.get("persistent", False):
            import os
            if os.path.exists(self.index_file_path):
                os.remove(self.index_file_path)
                print(f"Index file {self.index_file_path} deleted.")
