import json
import os
import requests

from utils.file_manager import FileManager


class HotelListFetcher:
    def __init__(self, base_url="https://www.iranhotelonline.com/api/mvc/hotelInfo/suggest?query=",
                 city_base_url="https://www.iranhotelonline.com/api/mvc/v1/search/filter",
                 letter_limit=30, city_limit=200):
        self.base_url = base_url
        self.city_base_url = city_base_url
        self.persian_alphabet = "ا ب پ ت ث ج چ ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ک گ ل م ن و ه ی".split()
        self.letter_limit = letter_limit
        self.city_limit = city_limit
        self.hotel_records = []

    def fetch_hotels_by_letter(self, letter):
        response = requests.get(self.base_url + letter)
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def fetch_all_hotels(self):
        all_hotels = []
        for i, letter in enumerate(self.persian_alphabet):
            if i >= self.letter_limit:
                break
            hotels = self.fetch_hotels_by_letter(letter)
            all_hotels.extend(hotels)
        return all_hotels

    @staticmethod
    def remove_duplicates(hotels):
        seen_ids = set()
        unique_hotels = []
        for hotel in hotels:
            if hotel['id'] not in seen_ids:
                unique_hotels.append(hotel)
                seen_ids.add(hotel['id'])
        return unique_hotels

    @staticmethod
    def extract_city_name(hotel):
        city_name = hotel['link'].strip('/').split('-')[0]
        hotel['city'] = city_name
        return hotel

    def fetch_hotel_details_for_cities(self, hotels):
        hotel_records = []
        for i, hotel in enumerate(hotels):
            if i >= self.city_limit:
                break
            city_name = hotel['city']
            params = {
                "ReferUrl": "home",
                "PageIndex": 0,
                "PageSize": 200,
                "isFirstRequest": "true",
                "CityName": city_name
            }
            response = requests.get(self.city_base_url, params=params)
            if response.status_code == 200:
                hotel_details = response.json()
                cards = hotel_details.get('Cards', [])
                for card in cards:
                    card_data = card.get('CardData', {})
                    record = {
                        "HotelName": card_data.get('HotelName'),
                        "hotel_url": card_data.get('HotelUrl'),
                        "CityName": card_data.get('CityName'),
                        "CityEnName": card_data.get('CityEnName'),
                        "Id": card_data.get('Id')
                    }
                    hotel_records.append(record)
            else:
                print(f"Failed to fetch details for {city_name}")
        return hotel_records

    def save_info(self, filename='hotel_records.json'):
        """
        Saves the hotel records into a JSON file.
        Prevents duplicate entries by checking the hotel ID.
        """
        print(f"Saving hotel records to {filename}...")
        data_dir = os.path.join(os.path.dirname(__file__), '../../data/reviews')
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, filename)

        # Load existing data (if any)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        # Remove duplicate entries by checking the hotel ID
        existing_ids = {hotel['Id'] for hotel in existing_data}
        unique_records = [record for record in self.hotel_records if record['Id'] not in existing_ids]

        # Append the new unique records
        existing_data.extend(unique_records)

        # Save the updated list to the JSON file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)

        print(f"Hotel records saved to {file_path}")
        return existing_data

    def run(self):
        all_hotels = self.fetch_all_hotels()
        unique_hotels = self.remove_duplicates(all_hotels)
        hotels_with_city = [self.extract_city_name(hotel) for hotel in unique_hotels]
        self.hotel_records = self.fetch_hotel_details_for_cities(hotels_with_city)
        updated_fetched_date = self.save_info()
        print("Hotel records have been saved to 'hotel_records.json'.")
        return updated_fetched_date

    def generate_hotel_summary_urls(self, from_file=False, file_name="hotel_records.json"):
        base_url = "https://www.iranhotelonline.com/api/mvc/v1/hotelInfo/getHotelSummaryInfo"
        urls = []

        if from_file:
            data_dir = os.path.join(os.path.dirname(__file__), '../../data/reviews')
            file_path = os.path.join(data_dir, file_name)
            file_manager = FileManager(file_path)
            hotel_records = file_manager.load_records()
        else:
            if not self.hotel_records:
                self.run()
            hotel_records = self.hotel_records

        for record in hotel_records:
            city_name = record.get("CityEnName", "")
            hotel_name_url = record.get("hotel_url", "").strip('/').split('/')[-1]
            if city_name and hotel_name_url:
                url = f"{base_url}?cityName={city_name}&hotelName={hotel_name_url}"
                urls.append(url)

        return urls
