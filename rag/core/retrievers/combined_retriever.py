# --------------------------
# CombinedRetriever: Groups results by common metadata (e.g. hotel_source_id)
# --------------------------
from typing import Dict, Any, List

from rag.core.interfaces import IRetriever, Document


class CombinedRetriever(IRetriever):
    def __init__(self, hotel_retriever: IRetriever, review_retriever: IRetriever):
        self.hotel_retriever = hotel_retriever
        self.review_retriever = review_retriever

    def retrieve(self, query: str) -> List[Document]:
        hotel_docs = self.hotel_retriever.retrieve(query)
        review_docs = self.review_retriever.retrieve(query)
        grouped_reviews = {}
        for doc in review_docs:
            hotel_id = doc.metadata.get("hotel_source_id")
            if hotel_id:
                grouped_reviews.setdefault(hotel_id, []).append(doc.content)
        combined_docs = []
        for hotel in hotel_docs:
            hotel_id = hotel.metadata.get("hotel_source_id")
            reviews = grouped_reviews.get(hotel_id, [])
            combined_text = hotel.content
            if reviews:
                combined_text += "\n\nReviews:\n" + "\n".join(reviews)
            combined_docs.append(Document(content=combined_text, metadata=hotel.metadata))
        return combined_docs
