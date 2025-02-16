from rag.configs.settings import Settings
from rag.core.container import RAGContainer
from ingestion.formatters.review_formatter import ReviewFormatter

# Load settings from the config
settings = Settings()

# Create container with loaded settings
container = RAGContainer(config=settings)

# Access components
hotel_scraper = container.scraper()
retriever = container.retriever()
llm = container.llm()
document_store = container.document_store()

# Use scraper to get documents
hotel_info = hotel_scraper.scrape()

# Convert structured reviews into text format
formatted_info = ReviewFormatter.format_reviews_for_faiss(hotel_info)

# Add to document store
document_store.add_hotel_documents(hotel_info)

# Retrieve documents
documents = retriever.retrieve("best food in city")

# Generate a response with LLM
response = llm.generate("What is the best restaurant?", documents)

print(response)
