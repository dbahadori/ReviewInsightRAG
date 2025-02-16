from rag.core.interfaces import IDocumentChunker
from langchain.text_splitter import RecursiveCharacterTextSplitter

from rag.data.document_chunker import HotelChunker, ReviewChunker


class DocumentChunkerFactory:
    @staticmethod
    def get_chunker(doc_type: str) -> IDocumentChunker:
        if doc_type.lower() == "hotel":
            # Use a Persian-friendly splitter for hotel info.
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=512,
                chunk_overlap=50,
                separators=["\n\n", "\n", "،", ".", ";", ":"]
            )
            return HotelChunker(splitter)
        elif doc_type.lower() == "review":
            return ReviewChunker()
        else:
            # Default: use the hotel chunker with a default splitter.
            splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
            return HotelChunker(splitter)
