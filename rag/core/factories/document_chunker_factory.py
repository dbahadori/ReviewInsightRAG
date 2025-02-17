from rag.core.interfaces import IDocumentChunker, DocumentType
from langchain.text_splitter import RecursiveCharacterTextSplitter

from rag.data.document_chunker import HotelChunker, ReviewChunker


class DocumentChunkerFactory:
    @staticmethod
    def create_chunker(doc_type: DocumentType = None) -> IDocumentChunker:
        if doc_type == DocumentType.HOTEL_INFO:
            # Use a Persian-friendly splitter for hotel info.
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=512,
                chunk_overlap=50,
                separators=["\n\n", "\n", "،", ".", ";", ":"]
            )
            return HotelChunker(splitter)
        elif doc_type == DocumentType.HOTEL_REVIEW:
            return ReviewChunker()
        else:
            # Default: use the hotel chunker with a default splitter.
            splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
            return HotelChunker(splitter)
