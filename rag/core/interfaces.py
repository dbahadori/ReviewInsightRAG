from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel

class Document(BaseModel):
    content: str
    metadata: dict = {}

class IScraper(ABC):
    @abstractmethod
    def scrape(self, url: str) -> List[str]:
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
    def add_documents(self, documents: List[str]):
        pass

    @abstractmethod
    def search(self, query: str) -> List[Document]:
        pass

