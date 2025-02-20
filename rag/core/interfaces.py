from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any

from langchain_core.retrievers import BaseRetriever
from pydantic import BaseModel


class DocumentType(Enum):
    HOTEL_INFO = "hotel_info"
    HOTEL_REVIEW = "hotel_review"


from enum import Enum

class DocumentStoreType(Enum):
    FAISS = "faiss"
    PINECONE = "pinecone"
    ELASTICSEARCH = "elasticsearch"
    MILVUS = "milvus"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"
    OPENSEARCH = "opensearch"

class HashStoreType(Enum):
    SQLITE = "sqlite"


class RetrieverFrameworkType(Enum):
    LANGCHAIN = "langchain"
    HAYSTACK = "haystack"

@dataclass
class Document:
    content: str
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


class IScraper(ABC):
    @abstractmethod
    def scrape(self, url: str) -> List[str]:
        pass

    def run(self) -> List[str]:
        pass

    def get_data(self, from_file: str, file_name: str) -> List[str]:
        pass

class IRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str) -> List[Document]:
        pass

class ILLM(ABC):
    @abstractmethod
    def generate(self, query: str, context: List[Document]) -> str:
        pass

class IDocumentStore(ABC):
    @abstractmethod
    def add_documents(self, documents: List[Document], doc_type: DocumentType) -> None:
        """Add a list of Document objects to the store."""
        pass


    @abstractmethod
    def clear(self, doc_type: DocumentType) -> None:
        """Clear the FAISS index (in-memory and disk)."""
        pass

    @abstractmethod
    def search(self, query: str, k: int = 5, doc_type: DocumentType = DocumentType.HOTEL_INFO) -> List[Document]:
        pass

    @abstractmethod
    def get_retriever(self, doc_type: DocumentType) -> BaseRetriever:
        pass

    @abstractmethod
    def get_type(self) -> DocumentStoreType:
        pass


class IDocumentChunker(ABC):
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Document]:
        pass


class IQueryProcess(ABC):
    def process(self, query: str) -> str:
        pass


class IHashStore(ABC):
    @abstractmethod
    def save_hash(self, id: str, hash: str) -> None:
        pass

    @abstractmethod
    def load_hash(self, id: str) -> Optional[str]:
        pass
