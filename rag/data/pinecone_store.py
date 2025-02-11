from typing import List

import pinecone
from langchain_community.vectorstores import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings


class PineconeStore:
    def __init__(self, config: dict):
        pinecone.init(api_key=config["pinecone"]["api_key"], environment=config["pinecone"]["environment"])
        self.vector_store = Pinecone(HuggingFaceEmbeddings(), index_name=config["pinecone"]["index_name"])

    def add_documents(self, docs: List[str]):
        # Add documents to Pinecone vector store
        self.vector_store.add_texts(docs)

    def search(self, query: str):
        # Perform similarity search with Pinecone
        results = self.vector_store.similarity_search(query, k=5)
        return results
