from rag.configs.config_loader import ConfigLoader
from rag.core.container import RAGContainer
from rag.core.factories.document_chunker_factory import DocumentChunkerFactory
from rag.core.interfaces import DocumentType
from scripts.formatters.hotel_info_formatter import IranHotelOnlineFormatter


class MainIngestionProcess:
    def __init__(self, container):
        self.scraper = container.scraper()
        self.document_store = container.document_store()
        # Obtain a hotel chunker using the factory.
        self.hotel_chunker = DocumentChunkerFactory.get_chunker("hotel")
        self.review_chunker = DocumentChunkerFactory.get_chunker("review")

    def ingest(self):
        # Step 1: Scrape raw hotel info records (each record is a dict)
        iran_hotel_online_raw_data = self.scraper.get_data(from_file=True)

        all_hotel_info_docs = []
        all_review_docs = []

        # Step 2: Process each hotel in the list
        for hotel in iran_hotel_online_raw_data:
            # Format hotel info
            formatted_hotel_info = IranHotelOnlineFormatter.format_hotel_info_for_faiss(hotel)
            hotel_info_chunks = self.hotel_chunker.chunk_text(formatted_hotel_info.content,
                                                              formatted_hotel_info.metadata)
            all_hotel_info_docs.extend(hotel_info_chunks)

            # Format hotel reviews
            formatted_reviews = IranHotelOnlineFormatter.format_hotel_reviews_for_faiss(hotel)
            review_chunks = self.hotel_chunker.chunk_text(formatted_reviews.content, formatted_reviews.metadata)
            all_review_docs.extend(review_chunks)

        # Step 3: Add all hotel info Document chunks to the document store
        self.document_store.add_documents(all_hotel_info_docs, DocumentType.HOTEL_INFO)

        # Step 4: Add all review Document chunks to the document store
        self.document_store.add_documents(all_review_docs, DocumentType.HOTEL_REVIEW)

        return all_hotel_info_docs + all_review_docs


# Example usage
if __name__ == "__main__":
    config_loader = ConfigLoader()
    container = RAGContainer.create(config_loader)
    ingestion_process = MainIngestionProcess(container)
    hotel_info = ingestion_process.ingest()
    print(f"the number of hotel info is:  {len(hotel_info)}")
