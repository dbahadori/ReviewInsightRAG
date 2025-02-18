# main.py
import logging
from rag.configs.config_loader import ConfigLoader
from rag.core.container import RAGContainer
from rag.core.interfaces import DocumentType
from scripts.ingest_data import MainIngestionProcess
from ui.gradio_app import launch_gradio_ui

# Set up logging
logging.basicConfig(level=logging.INFO)
logging = logging.getLogger(__name__)

def main():
    # Load configuration
    logging.info("Loading configuration")
    config_loader = ConfigLoader()  # defaults to 'rag_config.yaml'
    container = RAGContainer.create(config_loader)
    logging.info("Configuration loaded successfully")

    # Ingest data if available (for example, from a JSON file or scraper)
    logging.info("Starting data ingestion process")
    ingestion = MainIngestionProcess(container)
    ingestion.ingest()
    logging.info("Data ingestion process completed")

    # Launch the Gradio chat UI
    logging.info("Setting up document store")
    document_store = container.document_store()

    logging.info("Initializing hotel retriever")
    hotel_retriever = container.retriever(document_store=document_store, doc_type=DocumentType.HOTEL_INFO)
    logging.info("Hotel retriever initialized")

    logging.info("Initializing review retriever")
    review_retriever = container.retriever(document_store=document_store, doc_type=DocumentType.HOTEL_REVIEW)
    logging.info("Review retriever initialized")

    logging.info("Initializing LLM")
    llm = container.llm()
    logging.info("LLM initialized")

    logging.info("Launching Gradio UI")
    launch_gradio_ui(hotel_retriever=hotel_retriever, review_retriever=review_retriever, llm=llm)
    logging.info("Gradio UI launched successfully")

if __name__ == "__main__":
    main()
