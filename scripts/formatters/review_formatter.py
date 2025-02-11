from typing import List


class ReviewFormatter:
    @staticmethod
    def format_reviews_for_faiss(reviews: List[dict]) -> List[str]:
        """
        Converts structured hotel reviews into text-based format for FAISS.
        """
        formatted_texts = []

        for review in reviews:
            hotel_info = f"Hotel: {review['hotel_name']} in {review['hotel_city']}\n"
            for r in review["reviews"]:
                text = f"{hotel_info}Reviewer: {r['name']} on {r['date']}\n"
                text += f"Rating: {r['rating']} - Room Type: {r['room_type']}\n"
                text += f"Review: {r['main_text']}\n"
                text += f"Positives: {', '.join(r['positive_viewpoints'])}\n"
                text += f"Negatives: {', '.join(r['negative_viewpoints'])}\n"
                formatted_texts.append(text)

        return formatted_texts

