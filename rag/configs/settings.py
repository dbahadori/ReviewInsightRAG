from typing import Optional

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    # LLM Configuration
    llm_api_key: str
    llm_model: str = "deepseek-chat"  # Default to DeepSeek Chat model

    # Document Store Configuration
    document_store_type: str = "faiss"
    document_store_path: str = "data/vector_store.faiss"

    # Retriever Configuration
    retriever_framework: str = "langchain"
    retriever_embedding_model: str = "sentence-transformers/all-mpnet-base-v2"

    # Scraper Configuration
    scraper_type: str = "tripadvisor"
    scraper_api_key: Optional[str] = None

    class Config:
        env_file = ".env"  # Use environment variables if needed
