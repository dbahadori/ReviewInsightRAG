from dependency_injector import containers, providers

from rag.configs.config_loader import ConfigLoader
from rag.core.factories.document_chunker_factory import DocumentChunkerFactory
from rag.core.factories.document_store_factory import DocumentStoreFactory
from rag.core.factories.hash_store_factory import HashStoreFactory
from rag.core.factories.llm_factory import LLMFactory
from rag.core.factories.retriever_factory import RetrieverFactory
from rag.core.factories.scraper_factory import ScraperFactory


class RAGContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    @classmethod
    def create(cls, config_loader: ConfigLoader):
        container = cls()
        config_loader.load()
        container.config.override(config_loader.get_container_config())
        return container

    # Provide Document Store
    document_store = providers.Singleton(
        DocumentStoreFactory.create_store,
        config=config.retriever.document_store
    )

    # Provide Retriever
    retriever = providers.Factory(
        RetrieverFactory.create_retriever,
        config=config.retriever
    )

    # Provide LLM
    llm = providers.Factory(
        LLMFactory.create_llm,
        config=config.llm
    )

    #provide chunker
    chunker = providers.Singleton(
        DocumentChunkerFactory.create_chunker
    )

    #provide hash sore
    hash_store = providers.Factory(
        HashStoreFactory.create_hash_store,
        config=config.hash_store
    )
    # Provide Scraper
    scraper = providers.Factory(
        ScraperFactory.create_scraper,
        config=config.scraper
    )
