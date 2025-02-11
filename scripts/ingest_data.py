from rag.configs import settings
from rag.core.container import RAGContainer
from scripts.formatters.hotel_info_formatter import HotelInfoFormatter
from scripts.vectorizers.hotel_info_vectorizer import HotelInfoVectorizer


class MainIngestionProcess:
    def __init__(self, container: RAGContainer):
        self.scraper = container.scraper()
        self.document_store = container.document_store()
        embedding_model_name = container.config.retriever.params.embedding_model
        self.vectorizer = HotelInfoVectorizer(embedding_model=embedding_model_name)

    def ingest(self):
        # Step 1: Scrape data
        raw_data = self.scraper.scrape()

        # Step 2: Format data
        formatted_data = HotelInfoFormatter.format_info_for_faiss(raw_data)

        # Step 3: Vectorize data
        vectors = self.vectorizer.vectorize({"formatted_info": formatted_data})

        # Step 4: Add vectorized data to document store
        self.document_store.add_documents([vectors])

        return vectors

# Example usage
if __name__ == "__main__":
    container = RAGContainer(config=settings)
    ingestion_process = MainIngestionProcess(container)
    hotel_info = ingestion_process.ingest()
