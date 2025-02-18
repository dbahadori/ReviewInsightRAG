import logging
from typing import Dict, Any, List
from rag.core.interfaces import IRetriever, Document

class CombinedRetriever(IRetriever):
    def __init__(self, hotel_retriever: IRetriever, review_retriever: IRetriever):
        self.hotel_retriever = hotel_retriever
        self.review_retriever = review_retriever

    def retrieve(self, query: str) -> List[Document]:
        logging.info(f"Retrieving documents for query: {query}")

        hotel_docs = self.hotel_retriever.retrieve(query)
        logging.info(f"Retrieved {len(hotel_docs)} hotel documents")
        for hotel in hotel_docs:
            hotel_id = hotel.metadata.get('hotel_source_id')
            hotel_name = hotel.metadata.get('hotel_name')
            hotel_city = hotel.metadata.get('city_name')
            logging.info(f"Hotel Document - ID: {hotel_id}, Name: {hotel_name}, City: {hotel_city}")

        review_docs = self.review_retriever.retrieve(query)
        logging.info(f"Retrieved {len(review_docs)} review documents")
        for review in review_docs:
            review_id = review.metadata.get('hotel_source_id')
            logging.info(f"Review Document - ID: {review_id}")

        grouped_reviews = {}
        for doc in review_docs:
            hotel_id = doc.metadata.get("hotel_source_id")
            if hotel_id:
                grouped_reviews.setdefault(hotel_id, []).append(doc.content)

        logging.info("Grouped reviews by hotel_source_id")

        combined_docs = []
        for hotel in hotel_docs:
            hotel_id = hotel.metadata.get("hotel_source_id")
            hotel_name = hotel.metadata.get('hotel_name')
            hotel_city = hotel.metadata.get('city_name')
            reviews = grouped_reviews.get(hotel_id, [])
            combined_text = hotel.content
            if reviews:
                combined_text += "\n\nReviews:\n" + "\n".join(reviews)
            combined_doc = Document(content=combined_text, metadata=hotel.metadata)
            combined_docs.append(combined_doc)
            logging.info(f"Combined Document - ID: {hotel_id}, Name: {hotel_name}, City: {hotel_city}, Reviews Count: {len(reviews)}")

        logging.info(f"Created {len(combined_docs)} combined documents")

        return combined_docs
