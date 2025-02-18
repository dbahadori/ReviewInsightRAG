# Load configuration
import logging

from rag.configs.config_loader import ConfigLoader
from rag.core.container import RAGContainer
from rag.core.interfaces import DocumentType

config_loader = ConfigLoader()  # defaults to 'rag_config.yaml'
container = RAGContainer.create(config_loader)
document_store = container.document_store()

hotel_retriever = container.retriever(document_store=document_store, doc_type=DocumentType.HOTEL_INFO)
query = "هتل هما "
logging.info(f"Retrieving documents for query: {query}")
hotel_docs = hotel_retriever.retrieve(query=query)
logging.info(f"Retrieved {len(hotel_docs)} hotel documents")
for hotel in hotel_docs:
    hotel_id = hotel.metadata.get('hotel_source_id')
    hotel_name = hotel.metadata.get('hotel_name')
    hotel_city = hotel.metadata.get('city_name')
    logging.info(f"Hotel Document - ID: {hotel_id}, Name: {hotel_name}, City: {hotel_city}, content: {hotel.content}")

