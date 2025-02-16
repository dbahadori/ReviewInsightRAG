# main.py
import logging
from rag.configs.config_loader import ConfigLoader
from rag.core.container import RAGContainer
from scripts.ingest_data import MainIngestionProcess
from ui.gradio_app import launch_gradio_ui

logging.basicConfig(level=logging.INFO)


def main():
    # Load configuration
    config_loader = ConfigLoader()  # defaults to 'rag_config.yaml'
    container = RAGContainer.create(config_loader)

    # Ingest data if available (for example, from a JSON file or scraper)
    # For demonstration, we assume an empty list (or load your records).
    ingestion = MainIngestionProcess(container)
    ingestion.ingest()

    # Launch the Gradio chat UI.
    launch_gradio_ui(container.config.retriever(), container.config.llm())


if __name__ == "__main__":
    main()
