import logging

from rag.configs.config_loader import ConfigLoader
from rag.core.container import RAGContainer
from rag.core.interfaces import DocumentType, DocumentStoreType
from scripts.formatters.iran_hotel_online_formatter import IranHotelOnlineFormatter
from utils.hash_util import HashUtil


class MainIngestionProcess:
    def __init__(self, container):
        self.scraper = container.scraper()
        self.hotel_hash_store = container.hash_store(table_name= DocumentType.HOTEL_INFO.value)
        self.review_hash_store = container.hash_store(table_name= DocumentType.HOTEL_REVIEW.value)
        self.document_store = container.document_store()
        # Obtain a hotel chunker using the factory.
        self.hotel_chunker = container.chunker(DocumentType.HOTEL_INFO)
        self.review_chunker = container.chunker(DocumentType.HOTEL_REVIEW)

    def ingest(self):
        # Step 1: Scrape raw hotel info records (each record is a dict)
        iran_hotel_online_raw_data = self.scraper.get_data(from_file=True)
        all_hotel_info_docs = []
        all_review_docs = []

        # Step 2: Process each hotel in the list
        for hotel in iran_hotel_online_raw_data:

            # Format hotel info
            formatted_hotel_info = IranHotelOnlineFormatter.format_hotel_info_for_faiss(hotel)

            # Compute and check hotel info hash is changed or not
            hotel_info_new_hash = HashUtil.compute_hash(formatted_hotel_info.content)
            hotel_id = formatted_hotel_info.metadata["hotel_source_id"]

            hotel_hash_id =self.generate_unique_hash_id(hotel_id, self.document_store.get_type(), DocumentType.HOTEL_INFO)
            if HashUtil.update_hash_in_store_if_needed(self.hotel_hash_store, hotel_hash_id, hotel_info_new_hash):
                hotel_info_chunks = self.hotel_chunker.chunk_text(formatted_hotel_info.content, formatted_hotel_info.metadata)
                all_hotel_info_docs.extend(hotel_info_chunks)

            # Format hotel reviews
            formatted_reviews = IranHotelOnlineFormatter.format_hotel_reviews_for_faiss(hotel)

            # Compute and check hotel review hash is changed or not
            hotel_review_new_hash = HashUtil.compute_hash(formatted_reviews.content)

            review_hash_id =self.generate_unique_hash_id(hotel_id, self.document_store.get_type(), DocumentType.HOTEL_REVIEW)
            if HashUtil.update_hash_in_store_if_needed(self.review_hash_store, review_hash_id, hotel_review_new_hash):
                review_chunks = self.hotel_chunker.chunk_text(formatted_reviews.content, formatted_reviews.metadata)
                all_review_docs.extend(review_chunks)

        # Step 3: Add all hotel info Document chunks to the document store
        self.document_store.add_documents(all_hotel_info_docs, DocumentType.HOTEL_INFO)

        # Step 4: Add all review Document chunks to the document store
        self.document_store.add_documents(all_review_docs, DocumentType.HOTEL_REVIEW)

        return all_hotel_info_docs + all_review_docs

    def generate_unique_hash_id(self, id: str, doc_store_type: DocumentStoreType, doc_type: DocumentType) -> str:
        """
        Generate a unique hash ID based on the provided ID, DocumentStoreType, and DocumentType.

        Args:
            id (str): The original ID.
            doc_store_type (DocumentStoreType): The type of document store.
            doc_type (DocumentType): The type of document.

        Returns:
            str: A unique hash ID.
        """
        return f"{id}_{doc_store_type.value}_{doc_type.value}"


# Example usage
if __name__ == "__main__":
    config_loader = ConfigLoader()
    container = RAGContainer.create(config_loader)
    ingestion_process = MainIngestionProcess(container)
    hotel_info = ingestion_process.ingest()
    print(f"the number of hotel info is:  {len(hotel_info)}")
