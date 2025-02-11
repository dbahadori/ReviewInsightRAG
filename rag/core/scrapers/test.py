import json
import os

def count_hotels_and_reviews(filename='tehran_hotel_reviews.json'):
    # Define the path to the reviews directory
    reviews_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'reviews')

    # Define the full path to the JSON file
    file_path = os.path.join(reviews_dir, filename)

    # Load the reviews from the JSON file
    with open(file_path, 'r', encoding='utf-8') as f:
        reviews_data = json.load(f)

    # Count the number of hotels
    num_hotels = len(reviews_data)

    # Count the number of reviews for each hotel
    hotel_reviews_count = {}
    for hotel in reviews_data:
        hotel_name = hotel['hotel_name']
        num_reviews = len(hotel['reviews'])
        hotel_reviews_count[hotel_name] = num_reviews

    return num_hotels, hotel_reviews_count

# Example usage
if __name__ == "__main__":
    num_hotels, hotel_reviews_count = count_hotels_and_reviews()
    print(f"Total number of hotels: {num_hotels}")
    for hotel_name, num_reviews in hotel_reviews_count.items():
        print(f"{hotel_name}: {num_reviews} reviews")
