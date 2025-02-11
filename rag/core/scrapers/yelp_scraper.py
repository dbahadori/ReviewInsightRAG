from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time


def get_review_data(review):
    # Extract the relevant information from a single review using Selenium WebDriver
    name = review.find_element(By.XPATH,
                               ".//div[contains(@class, 'text-caption') and contains(@class, 'xl:text-subtitle-2')]").text.strip()
    date = review.find_element(By.CLASS_NAME, 'text-on-surface-medium-emphasis').text.strip()
    emoji = review.find_element(By.TAG_NAME, 'img').get_attribute('src')  # URL of the emoji image

    # Extract rating
    try:
        rating = review.find_element(By.XPATH,
                                     ".//span[contains(@class, 'mini-chips_text__xuhB9') and (contains(text(), '۱') or contains(text(), '۲') or contains(text(), '۳') or contains(text(), '۴') or contains(text(), '۵'))]").text.strip()
    except:
        rating = "No rating found"

    # Extract room type
    try:
        room_type = review.find_element(By.XPATH,
                                        ".//span[contains(@class, 'mini-chips_text__xuhB9') and not(contains(text(), '۱')) and not(contains(text(), '۲')) and not(contains(text(), '۳')) and not(contains(text(), '۴')) and not(contains(text(), '۵'))]").text.strip()
    except:
        room_type = "No room type found"

    # Extract main review text
    try:
        main_text = review.find_element(By.XPATH,
                                        ".//div[@class='text-caption xl:text-body-2' and not(contains(@class, 'flex'))]").text.strip()
    except:
        main_text = "No main text found"

    # Extract positive viewpoints
    positive_viewpoints = []
    positive_elements = review.find_elements(By.XPATH,
                                             ".//div[contains(@class, 'text-caption xl:text-body-2 flex') and .//span[contains(@class, 'text-ventures-snapp')]]")
    for positive in positive_elements:
        try:
            positive_text = positive.find_element(By.XPATH, "./div[2]").text.strip()
            positive_viewpoints.append(positive_text)
        except:
            print(f"Positive viewpoint not found in: {positive.get_attribute('innerHTML')}")

    # Extract negative viewpoints
    negative_viewpoints = []
    negative_elements = review.find_elements(By.XPATH,
                                             ".//div[contains(@class, 'text-caption xl:text-body-2 flex') and .//span[contains(@class, 'text-error')]]")
    for negative in negative_elements:
        try:
            negative_text = negative.find_element(By.XPATH, "./div[2]").text.strip()
            negative_viewpoints.append(negative_text)
        except:
            print(f"Negative viewpoint not found in: {negative.get_attribute('innerHTML')}")

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



def scrape_reviews2(url):
    reviews_list = []
    # Wait for the page to load and find the first hotel article
    if hotel_article:
        hotel_link = hotel_article.find_element(By.CSS_SELECTOR, 'a[itemtype="http://schema.org/Hotel"]')
        if hotel_link:
            hotel_url = hotel_link.get_attribute('href')
            print(f"Navigating to hotel page: {hotel_url}")
            driver.get(hotel_url)

            # Wait for the span with the text "همه نظرات" to appear
            print("Looking for 'همه نظرات' span...")
            reviews_button_span = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[text()='همه نظرات']")))
            reviews_button = reviews_button_span.find_element(By.XPATH, "./ancestor::button")
            print("Found 'همه نظرات' span and its parent button")

            # Click on the parent button
            reviews_button.click()
            print("Clicked on 'All Reviews' button")

            # Wait for the parent div to load
            print("Waiting for parent div with class 'flex w-full flex-col gap-6 md:self-start' to load...")
            parent_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".flex.w-full.flex-col.gap-6.md\\:self-start")))

            # Scroll and load all reviews
            print("Scrolling and loading reviews...")
            last_review_count = 0
            while True:
                # Extract all the child divs with the specified class
                reviews = parent_div.find_elements(By.CSS_SELECTOR,
                                                   ".shadow-1.bg-dim-background.flex.w-full.flex-col.gap-4.overflow-hidden.rounded-xl.p-4.xl\\:p-6")

                # Break if no new reviews are loaded
                if len(reviews) == last_review_count:
                    break

                last_review_count = len(reviews)

                for review in reviews:
                    review_data = get_review_data(review)
                    if review_data not in reviews_list:
                        reviews_list.append(review_data)

                # Scroll to the last review element
                driver.execute_script("arguments[0].scrollIntoView();", reviews[-1])
                time.sleep(2)  # Wait for new reviews to load

    driver.quit()
    print("Scraping complete!")
    return reviews_list




def extract_popular_hotel_cities(driver, base_url):
    print("Navigating to base URL...")
    driver.get(base_url)

    # Wait for the section to load and extract popular cities information
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "section.keen-slider.size-full")))
    city_section = driver.find_element(By.CSS_SELECTOR, "section.keen-slider.size-full")

    cities = {}
    articles = city_section.find_elements(By.TAG_NAME, 'article')
    for article in articles:
        name = article.find_element(By.CLASS_NAME, 'popular-city_item-state__bBHCE').text.strip()
        link = article.find_element(By.TAG_NAME, 'a').get_attribute('href')
        cities[name] = link

    return cities


def navigate_to_city_hotels_page(driver, city_name, cities):
    if city_name in cities:
        city_url = cities[city_name]
        print(f"Navigating to city: {city_name}")
        driver.get(city_url)
    else:
        print("City not found in the list")



def extract_hotels_from_city_page(driver):
    # Wait for the section to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "section.flex.w-full.flex-col.items-center.gap-4.lg\\:gap-6")))

    # Scroll down to load all articles
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for new content to load

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Find the section again after all articles are loaded
    hotel_section = driver.find_element(By.CSS_SELECTOR, "section.flex.w-full.flex-col.items-center.gap-4.lg\\:gap-6")

    hotels = {}
    articles = hotel_section.find_elements(By.CSS_SELECTOR, "article[class='w-full']")

    for article in articles:
        try:
            span_text = article.find_element(By.CSS_SELECTOR,
                                             "span.text-overline.lg\\:text-caption.text-on-surface-medium-emphasis").text
            span_value = int(span_text.replace('(', '').replace(')', '').replace('<!-- -->', '').strip())

            if span_value > 10:
                name = article.find_element(By.CSS_SELECTOR, 'h3').text.strip()  # Targeting 'h3' for hotel name
                link = article.find_element(By.TAG_NAME, 'a').get_attribute('href')  # Extracting href from <a> tag
                hotels[name] = link
        except NoSuchElementException:
            continue
    print(len(hotels))
    return hotels



def scrape_reviews(driver, hotel_url):
    reviews_list = []

    print(f"Navigating to hotel page: {hotel_url}")
    driver.get(hotel_url)

    # Wait for the span with the text "همه نظرات" to appear
    print("Looking for 'همه نظرات' span...")
    reviews_button_span = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//span[text()='همه نظرات']")))
    reviews_button = reviews_button_span.find_element(By.XPATH, "./ancestor::button")
    print("Found 'همه نظرات' span and its parent button")

    # Click on the parent button
    reviews_button.click()
    print("Clicked on 'All Reviews' button")

    # Wait for the parent div to load
    print("Waiting for parent div with class 'flex w-full flex-col gap-6 md:self-start' to load...")
    parent_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".flex.w-full.flex-col.gap-6.md\\:self-start")))

    # Scroll and load all reviews
    print("Scrolling and loading reviews...")
    last_review_count = 0
    while True:
        # Extract all the child divs with the specified class
        reviews = parent_div.find_elements(By.CSS_SELECTOR,
                                           ".shadow-1.bg-dim-background.flex.w-full.flex-col.gap-4.overflow-hidden.rounded-xl.p-4.xl\\:p-6")

        # Break if no new reviews are loaded
        if len(reviews) == last_review_count:
            break

        last_review_count = len(reviews)

        for review in reviews:
            review_data = get_review_data(review)
            if review_data not in reviews_list:
                reviews_list.append(review_data)

        # Scroll to the last review element
        driver.execute_script("arguments[0].scrollIntoView();", reviews[-1])
        time.sleep(2)  # Wait for new reviews to load

    print("Scraping complete!")
    return reviews_list


# Main URL for the main page
main_url = "https://pwa.snapptrip.com"

# Initialize the Selenium WebDriver
options = Options()
options.headless = False  # Run in non-headless mode
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Step 1: Extract all popular hotel cities
popular_cities = extract_popular_hotel_cities(driver, main_url)
print("Extracted Popular Cities:")
print(popular_cities)

# User input to select a city (example: 'هتل های مشهد')
user_selected_city = 'هتل های مشهد'

# Step 2: Navigate to the selected city's hotels page
navigate_to_city_hotels_page(driver, user_selected_city, popular_cities)

# Step 3: Extract hotels from the city page
city_hotels = extract_hotels_from_city_page(driver)
print(f"Hotels in {user_selected_city}:")
print(city_hotels.keys())

# User input to select a hotel (example: 'هتل الماس ۲ مشهد')
user_selected_hotel = 'هتل آبان مشهد'

if user_selected_hotel in city_hotels:
    hotel_url = city_hotels[user_selected_hotel]
    # Step 4: Scrape reviews for the selected hotel
    reviews = scrape_reviews(driver, hotel_url)
    hotel_record = {
        "hotel_name": user_selected_hotel,
        "hotel_city": user_selected_city,
        "reviews" : reviews
    }
    # Print the extracted reviews
    print(hotel_record)
else:
    print("Hotel not found in the city hotel list")

# Quit the WebDriver
driver.quit()
