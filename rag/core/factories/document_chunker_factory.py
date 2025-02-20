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
                separators=["\n\n", "؟", "!", ".", "۔"]
            )
            return HotelChunker(splitter)
        elif doc_type == DocumentType.HOTEL_REVIEW:
            return ReviewChunker()
        else:
            # Default: use the hotel chunker with a default splitter.
            splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
            return HotelChunker(splitter)

# chunker = DocumentChunkerFactory.create_chunker(DocumentType.HOTEL_INFO)
# text = """هتل اسپیناس پالاس یکی از لوکس‌ترین هتل‌های تهران است. این هتل امکانات فوق‌العاده‌ای دارد از جمله اینترنت پرسرعت، پارکینگ رایگان و رستوران‌های متنوع.
# موقعیت جغرافیایی این هتل بسیار عالی است و دسترسی خوبی به نقاط مهم شهر دارد. خدمات آن شامل اسپا، استخر، سالن ورزشی و سرویس‌دهی ۲۴ ساعته است."""
#
# metadata = {"hotel_name": "هتل اسپیناس پالاس", "city": "تهران"}
# docs= chunker.chunk_text(text, metadata)
#
# for doc in docs:
#     print(doc.content)
#     print(doc.metadata)
