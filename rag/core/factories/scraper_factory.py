from rag.core.interfaces import IScraper
from rag.core.scrapers.iranHotel.iran_hotel_online_scraper import IranHotelOnlineScraper
from rag.core.scrapers.snap.snapp_hotel_scraper import SnappTripScraper

class ScraperFactory:
    @staticmethod
    def create_scraper(config) -> IScraper:
        scraper_type = config.type  # Accessing attribute directly
        if scraper_type == "iranhotelonline":
            return IranHotelOnlineScraper()
        elif scraper_type == "snapptrip":
            return SnappTripScraper()
        else:
            raise ValueError(f"Unsupported scraper type: {scraper_type}")


# SnappTripScraper(api_key=config.get("scraper", {}).get("api_key"))