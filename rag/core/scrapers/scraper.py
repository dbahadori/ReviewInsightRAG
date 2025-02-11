from typing import List

from bs4 import BeautifulSoup
import requests
from rag.core.interfaces import IScraper

class ReviewScraper(IScraper):
    def scrape(self, url: str) -> List[str]:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        reviews = [review.text for review in soup.find_all("div", class_="review")]
        return reviews