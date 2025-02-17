import json
import logging
import os
import requests

from utils.file_manager import FileManager
from utils.path_util import PathUtil

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class HotelVoteFetcher:
    def __init__(self, base_url: str="https://www.iranhotelonline.com/api/mvc/v1/vote/GetVotes"):
        """
        Initialize the fetcher with the base URL.
        :param base_url: Base URL of the API (e.g., "https://www.iranhotelonline.com/api/mvc/v1/vote/GetVotes")
        """
        self.base_url = base_url
        self.hotel_votes = {}  # Initialize as a dictionary

    def fetch_votes(self, hotel_id, page_index, page_size):
        """
        Fetch votes for a specific hotel and page.
        :param hotel_id: ID of the hotel to fetch votes for.
        :param page_index: Page index to fetch (starting from 1).
        :param page_size: Number of items per page.
        :return: JSON response containing votes and total count.
        """
        url = f"{self.base_url}?hotelId={hotel_id}&pageIndex={page_index}&pageSize={page_size}"
        logging.info(f"Fetching votes for hotel {hotel_id}, page {page_index}")
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to fetch data for hotel {hotel_id}: {response.status_code}")
            raise Exception(f"Failed to fetch data for hotel {hotel_id}: {response.status_code}")

    def fetch_all_votes(self, hotel_id, page_size=50):
        """
        Fetch all votes for a specific hotel by paginating through all pages.
        :param hotel_id: ID of the hotel to fetch votes for.
        :param page_size: Number of items per page (default is 50, the maximum allowed).
        :return: List of all votes for the hotel, with only the specified fields.
        """
        all_votes = []
        page_index = 1

        while True:
            # Fetch votes for the current page
            data = self.fetch_votes(hotel_id, page_index, page_size)
            votes = data.get("votes", [])

            # Extract only the required fields from each vote
            filtered_votes = [
                {
                    "hotelId": vote.get("hotelId"),
                    "rate": vote.get("rate"),
                    "title": vote.get("title"),
                    "description": vote.get("description"),
                    "cityName": vote.get("cityName"),
                    "guestName": vote.get("guestName"),
                    "arrivalDate": vote.get("arrivalDate"),
                    "arrivalDatePersian": vote.get("arrivalDatePersian"),
                    "checkoutDate": vote.get("checkoutDate"),
                    "checkoutDatePersian": vote.get("checkoutDatePersian"),
                    "duration": vote.get("duration"),
                    "travelTypeTitle": vote.get("travelTypeTitle"),
                    "rateTitle": vote.get("rateTitle"),
                    "roomName": vote.get("roomName"),
                    "pictureUrl": vote.get("pictureUrl"),
                }
                for vote in votes
            ]
            all_votes.extend(filtered_votes)

            # Check if we've fetched all pages
            total_count = data.get("count", 0)
            logging.info(f"Total votes: {total_count}, Fetched votes: {len(all_votes)} for hotel {hotel_id}")
            if len(all_votes) >= total_count:
                break

            # Move to the next page
            page_index += 1

        return all_votes

    def run(self, hotel_ids, page_size=50):
        """
        Fetch all votes for a list of hotel IDs.
        :param hotel_ids: List of hotel IDs to fetch votes for.
        :param page_size: Number of items per page (default is 50).
        :return: Dictionary where keys are hotel IDs and values are lists of filtered votes.
        """
        for hotel_id in hotel_ids:
            try:
                votes = self.fetch_all_votes(hotel_id, page_size)
                self.hotel_votes[hotel_id] = votes  # Correctly populate hotel_votes dictionary
                logging.info(f"Fetched {len(votes)} votes for hotel {hotel_id}")
            except Exception as e:
                logging.error(f"Error fetching votes for hotel {hotel_id}: {e}")

        updated_fetched_date = self.save_votes()
        logging.info("Hotel votes records have been saved to 'hotel_votes.json'.")
        return updated_fetched_date

    def save_votes(self, file_name='hotel_votes.json'):
        """
        Save the fetched votes to a JSON file.
        Prevents duplicate entries by checking the arrivalDate and guestName.
        :param file_name: Name of the file to save the votes.
        """
        logging.info(f"Saving hotel votes to {file_name}...")
        file_path = PathUtil.construct_path(PathUtil.get_project_base_path(), 'data','hotel', file_name)
        # Load existing data (if any)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = {}
        else:
            existing_data = {}

        # Prepare new data to merge with existing data
        new_data = {}

        for hotel_id, votes in self.hotel_votes.items():
            if hotel_id not in existing_data:
                existing_data[hotel_id] = []

            existing_votes = existing_data[hotel_id]
            new_votes = []

            # Filter new votes to avoid duplicates based on arrivalDate and guestName
            for vote in votes:
                if not any(ev for ev in existing_votes if
                           ev["arrivalDate"] == vote["arrivalDate"] and ev["guestName"] == vote["guestName"]):
                    new_votes.append(vote)

            new_data[hotel_id] = existing_votes + new_votes

        # Save the merged data to the JSON file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=4)

        logging.info(f"Hotel votes saved to {file_path}")
        return new_data

    def get_hotel_votes(self, hotel_ids, page_size=50, from_file=True, file_name="hotel_votes.json"):
        if from_file:
            file_path = PathUtil.construct_path(PathUtil.get_project_base_path(), 'data', 'hotel', file_name)
            file_manager = FileManager(file_path)
            hotel_votes_records = file_manager.load_records()
        else:
            if not self.hotel_votes:
                self.run(hotel_ids, page_size)
            hotel_votes_records = self.hotel_votes

        return hotel_votes_records

# Example Usage
if __name__ == "__main__":
    base_url = "https://www.iranhotelonline.com/api/mvc/v1/vote/GetVotes"
    hotel_ids = [92, 130, 45]  # Example list of hotel IDs

    fetcher = HotelVoteFetcher(base_url)

    # Fetch votes for all hotels
    hotel_votes = fetcher.get_hotel_votes(hotel_ids)

    # Print the results
    for hotel_id, votes in hotel_votes.items():
        logging.info(f"Hotel {hotel_id} has {len(votes)} votes.")
