from dependency_injector import containers, providers
from rag.core.factories.document_store_factory import DocumentStoreFactory
from rag.core.factories.llm_factory import LLMFactory
from rag.core.factories.retriever_factory import RetrieverFactory
from rag.core.factories.scraper_factory import ScraperFactory


class RAGContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Provide Document Store
    document_store = providers.Singleton(
        DocumentStoreFactory.create_store,
        config=config.document_store
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

    # Provide Scraper
    scraper = providers.Factory(
        ScraperFactory.create_scraper,
        config=config.scraper
    )
