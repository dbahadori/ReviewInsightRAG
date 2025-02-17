import json
import logging
import os
from typing import List

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

from rag.core.interfaces import IScraper

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SnappTripScraper(IScraper):

    def __init__(self):
        self.driver = self._init_webdriver()
        self.all_reviews = []

    def _init_webdriver(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Run browser in headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def _get_review_data(self, review):
        """Extracts the relevant information from a single review."""
        try:
            name = review.find_element(By.XPATH,
                                       ".//div[contains(@class, 'text-caption') and contains(@class, 'xl:text-subtitle-2')]").content.strip()
            date = review.find_element(By.CLASS_NAME, 'text-on-surface-medium-emphasis').content.strip()
            emoji = review.find_element(By.TAG_NAME, 'img').get_attribute('src')  # URL of the emoji image

            try:
                rating = review.find_element(By.XPATH,
                                             ".//span[contains(@class, 'mini-chips_text__xuhB9') and (contains(text(), '۱') or contains(text(), '۲') or contains(text(), '۳') or contains(text(), '۴') or contains(text(), '۵'))]").content.strip()
            except:
                rating = "No rating found"

            try:
                room_type = review.find_element(By.XPATH,
                                                ".//span[contains(@class, 'mini-chips_text__xuhB9') and not(contains(text(), '۱')) and not(contains(text(), '۲')) and not(contains(text(), '۳')) and not(contains(text(), '۴')) and not(contains(text(), '۵'))]").content.strip()
            except:
                room_type = "No room type found"

            try:
                main_text = review.find_element(By.XPATH,
                                                ".//div[@class='text-caption xl:text-body-2' and not(contains(@class, 'flex'))]").content.strip()
            except:
                main_text = "No main text found"

            positive_viewpoints = [
                p.find_element(By.XPATH, "./div[2]").content.strip()
                for p in review.find_elements(By.XPATH,
                                              ".//div[contains(@class, 'text-caption xl:text-body-2 flex') and .//span[contains(@class, 'text-ventures-snapp')]]")
            ]

            negative_viewpoints = [
                n.find_element(By.XPATH, "./div[2]").content.strip()
                for n in review.find_elements(By.XPATH,
                                              ".//div[contains(@class, 'text-caption xl:text-body-2 flex') and .//span[contains(@class, 'text-error')]]")
            ]

            return {
                "name": name,
                "date": date,
                "emoji": emoji,
                "rating": rating,
                "room_type": room_type,
                "main_text": main_text,
                "positive_viewpoints": positive_viewpoints,
                "negative_viewpoints": negative_viewpoints
            }
        except Exception as e:
            logging.error(f"Error extracting review data: {e}")
            return {}

    def _extract_popular_hotel_cities(self):
        """Extracts popular hotel cities from the base URL."""
        logging.info("Navigating to base URL...")
        self.driver.get(self.base_url)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "section.popular-cities_list__HtD_z section.keen-slider.size-full"))
        )
        city_section = self.driver.find_element(By.CSS_SELECTOR,
                                                "section.popular-cities_list__HtD_z section.keen-slider.size-full")

        cities = {}
        articles = city_section.find_elements(By.TAG_NAME, 'article')
        print(f"article numbers : {len(articles)}")
        for article in articles:
            name = article.find_element(By.CLASS_NAME, 'popular-city_item-state__bBHCE').text.strip()
            link = article.find_element(By.TAG_NAME, 'a').get_attribute('href')
            cities[name] = link

        return cities

    def _navigate_to_city_hotels_page(self, city_name, cities):
        """Navigates to the selected city's hotels page."""
        if city_name in cities:
            city_url = cities[city_name]
            logging.info(f"Navigating to city: {city_name}")
            self.driver.get(city_url)
        else:
            raise ValueError(f"City {city_name} not found in the list.")

    def _extract_hotels_from_city_page(self):
        """Extracts hotels from the city page."""
        logging.info(f"Extracting hotels from city page...")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "section.flex.w-full.flex-col.items-center.gap-4.lg\\:gap-6"))
        )

        hotel_section = self.driver.find_element(By.CSS_SELECTOR,
                                                 "section.flex.w-full.flex-col.items-center.gap-4.lg\\:gap-6")
        hotels = {}
        articles = hotel_section.find_elements(By.CSS_SELECTOR, "article[class='w-full']")
        for article in articles:
            try:
                span_text = article.find_element(By.CSS_SELECTOR,
                                                 "span.text-overline.lg\\:text-caption.text-on-surface-medium-emphasis").text
                span_value = int(span_text.replace('(', '').replace(')', '').replace('<!-- -->', '').strip())

                if span_value > 10:
                    name = article.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                    link = article.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    hotels[name] = link
                    logging.info(f"Extracted hotel: {name} with link: {link}")
            except NoSuchElementException:
                logging.warning("Rating span not found, skipping article.")
                continue

        return hotels

    def scrape(self, base_url):
        """Main method to scrape reviews."""
        self.base_url = base_url
        self.user_selected_city = "هتل های تهران"

        try:
            cities = self._extract_popular_hotel_cities()
            self._navigate_to_city_hotels_page(self.user_selected_city, cities)

            self._scroll_to_load_all()  # Scroll to load all hotels

            hotels = self._extract_hotels_from_city_page()
            hotels = self.remove_saved_hotels(filename='tehran_hotel_reviews.json', hotels=hotels)
            for hotel_name, hotel_url in hotels.items():
                logging.info(f"Scraping reviews for hotel: {hotel_name}")
                self.driver.get(hotel_url)

                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//span[text()='همه نظرات']"))
                ).find_element(By.XPATH, "./ancestor::button").click()

                logging.info(f"Clicked on all reviews button for hotel: {hotel_name}")
                time.sleep(3)
                parent_div = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".flex.w-full.flex-col.gap-6.md\\:self-start"))
                )

                reviews_list = []
                last_review_count = 0
                while True:
                    reviews = parent_div.find_elements(By.CSS_SELECTOR,
                                                       ".shadow-1.bg-dim-background.flex.w-full.flex-col.gap-4.overflow-hidden.rounded-xl.p-4.xl\\:p-6")

                    if len(reviews) == last_review_count:
                        break

                    last_review_count = len(reviews)

                    for review in reviews:
                        review_data = self._get_review_data(review)
                        if review_data not in reviews_list:
                            reviews_list.append(review_data)
                            logging.info(f"Extracted review: {review_data}")

                    self.driver.execute_script("arguments[0].scrollIntoView();", reviews[-1])
                    logging.info(f"Scroll down for hotel: {hotel_name}")
                    time.sleep(3)

                hotel_record = {
                    "hotel_name": hotel_name,
                    "hotel_city": self.user_selected_city,
                    "reviews": reviews_list
                }
                self.all_reviews.append(hotel_record)

            return self.all_reviews

        finally:
            logging.info("Closing WebDriver.")
            self.driver.quit()

    def save_reviews(self, filename='tehran_hotel_reviews.json'):
        logging.info(f"Saving reviews to {filename}...")
        # Define the path to the reviews directory
        reviews_dir = os.path.join(os.path.dirname(__file__), '../..', '..', 'data', 'reviews')

        # Ensure the reviews directory exists
        os.makedirs(reviews_dir, exist_ok=True)

        # Define the full path to the JSON file
        file_path = os.path.join(reviews_dir, filename)

        # Load existing reviews if the file exists
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_reviews = json.load(f)
        else:
            existing_reviews = []

        # Append the new reviews to the existing ones
        existing_reviews.extend(self.all_reviews)

        # Save the combined reviews to the JSON file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_reviews, f, ensure_ascii=False, indent=4)
            logging.info("Reviews saved successfully.")

    def _scroll_to_load_all(self, container_selector="body"):
        """Scrolls down to load all items within a specific container on the page."""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        logging.info("Finished scrolling to load all items.")

    def remove_saved_hotels(self, filename, hotels):
        # Define the path to the reviews directory
        reviews_dir = os.path.join(os.path.dirname(__file__), '../..', '..', 'data', 'reviews')

        # Define the full path to the JSON file
        file_path = os.path.join(reviews_dir, filename)

        # Load existing reviews if the file exists
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_reviews = json.load(f)

            # Extract hotel names from existing reviews
            existing_hotel_names = {hotel['hotel_name'] for hotel in existing_reviews}

            # Remove hotels from the hotels dictionary if they are already saved
            hotels = {name: url for name, url in hotels.items() if name not in existing_hotel_names}

        return hotels

# Example usage
if __name__ == "__main__":
    import sys
    import threading

    # Create a stop flag
    stop_flag = threading.Event()

    # Create scraper instance
    scraper = SnappTripScraper()


    def start_scraping():
        # Start scraping reviews for all hotels in the selected city
        while not stop_flag.is_set():
            scraper.scrape("https://pwa.snapptrip.com")
            print("Scraping iteration completed.")


    # Run scraping in a separate thread
    thread = threading.Thread(target=start_scraping)
    thread.start()

    print("Scraping is running in a separate thread. You can type 'stop' to end the process and save reviews.")

    # Wait for user input to stop the process
    while True:
        user_input = input("Type 'stop' to end scraping and save reviews: ")
        if user_input.strip().lower() == 'stop':
            stop_flag.set()
            break

    print("Stopping the scraping process...")
    # Wait for the thread to finish
    thread.join()

    # Save the reviews
    scraper.save_reviews()

    print("Scraping stopped. Reviews have been saved.")
    sys.exit()
