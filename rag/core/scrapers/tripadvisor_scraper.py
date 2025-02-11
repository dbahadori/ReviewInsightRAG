from typing import List
import requests

from rag.core.interfaces import IScraper


class TripAdvisorScraper(IScraper):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def scrape(self, url: str) -> List[str]:
        response = requests.get(url, headers={"Authorization": f"Bearer {self.api_key}"})
        reviews = response.json()  # Assume response is JSON containing reviews
        return [review["text"] for review in reviews]
