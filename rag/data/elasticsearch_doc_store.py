import logging
from typing import List
from elasticsearch import Elasticsearch

from langchain.embeddings import HuggingFaceEmbeddings
from langchain_elasticsearch import ElasticsearchStore  # Updated import
from langchain.schema import BaseRetriever

from rag.core.interfaces import DocumentType, IDocumentStore, Document, DocumentStoreType
from utils.path_util import PathUtil

class ElasticsearchDocStore(IDocumentStore):
    def __init__(self, config: dict):
        """
        Initialize an Elasticsearch-based document store.

        The config should include:
          - params.embedding_model: embedding model name.
          - params.elasticsearch_url: URL for Elasticsearch instance.
        """
        self.config = config
        self.params = config.get("params", {})
        self.embedding_model = self.params.get("embedding_model", "paraphrase-multilingual-mpnet-base-v2")
        self.elasticsearch_url = self.params.get("elasticsearch_url", "http://localhost:9200")

        # Use separate index names for each document type.
        self.index_names = {
            DocumentType.HOTEL_INFO: 'elasticsearch_hotel_info_index',
            DocumentType.HOTEL_REVIEW: 'elasticsearch_hotel_review_index'
        }
        self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        # Create an Elasticsearch store per document type.
        self.stores = {
            doc_type: self._initialize_store(self.index_names[doc_type])
            for doc_type in DocumentType
        }
        self.client = Elasticsearch([self.elasticsearch_url])

    def _initialize_store(self, index_name: str) -> ElasticsearchStore:
        """
        Initialize the Elasticsearch store.
        """
        return ElasticsearchStore(
            es_url=self.elasticsearch_url,
            index_name=index_name,
            embedding=self.embeddings
        )

    def add_documents(self, docs: List[Document], doc_type: DocumentType) -> None:
        """
        Add a list of Document objects to the Elasticsearch store for the given document type.
        """
        if docs:
            store = self.stores[doc_type]
            texts = [doc.content for doc in docs]
            metadatas = [doc.metadata for doc in docs]
            # ElasticsearchStore.add_documents will generate embeddings internally using self.embeddings.
            store.add_texts(texts, metadatas=metadatas)

    def search(self, query: str, k: int = 5, doc_type: DocumentType = DocumentType.HOTEL_INFO) -> List[Document]:
        """Search the Elasticsearch store for a query and return relevant documents."""
        store = self.stores[doc_type]
        results = store.similarity_search(query, k=k)
        return [Document(content=doc.page_content, metadata=doc.metadata) for doc in results]

    def get_retriever(self, doc_type: DocumentType) -> BaseRetriever:
        """Return a retriever instance for the specified document type."""
        store = self.stores[doc_type]
        return store.as_retriever(search_kwargs={"k": 10, "distance_metric": "cosine"})

    def clear(self, doc_type: DocumentType) -> None:
        """Clear the Elasticsearch index for the specified document type."""
        index_name = self.index_names[doc_type]
        if self.client.indices.exists(index=index_name):
            self.client.indices.delete(index=index_name)
            logging.info(f"Index {index_name} deleted.")

    def get_type(self) -> DocumentStoreType:
        return DocumentStoreType.ELASTICSEARCH