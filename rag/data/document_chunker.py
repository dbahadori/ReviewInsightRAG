from typing import Optional, Any, List, Dict

from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.core.interfaces import Document, IDocumentChunker


# Implementation for Hotel documents: use a splitter to break long descriptive text.
class HotelChunker(IDocumentChunker):
    def __init__(self, splitter: RecursiveCharacterTextSplitter):
        self.splitter = splitter

    def chunk_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        chunks = self.splitter.create_documents([text], metadatas=[metadata or {}])
        return [Document(content=doc.page_content, metadata=doc.metadata) for doc in chunks]


# Implementation for Review documents: reviews are short, so no splitting is needed.
class ReviewChunker(IDocumentChunker):
    def chunk_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        return [Document(content=text, metadata=metadata or {})]
