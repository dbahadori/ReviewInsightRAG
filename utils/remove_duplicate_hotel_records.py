import json
import os

def remove_duplicate_hotel_records(filename):
    # Define the path to the reviews directory
    reviews_dir = os.path.join(os.path.dirname(__file__), '../rag/core', '..', 'data', 'reviews')

    # Define the full path to the JSON file
    file_path = os.path.join(reviews_dir, filename)

    # Load existing reviews
    with open(file_path, 'r', encoding='utf-8') as f:
        reviews_data = json.load(f)

    # Create a set to track seen hotel names
    seen_hotels = set()
    unique_reviews = []

    # Filter out duplicate hotel records
    for hotel in reviews_data:
        hotel_name = hotel.get('hotel_name')
        if hotel_name not in seen_hotels:
            seen_hotels.add(hotel_name)
            unique_reviews.append(hotel)

    # Save the unique data back to the JSON file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(unique_reviews, f, ensure_ascii=False, indent=4)

    print(f"Cleaned data has been saved to {filename}")

# Example usage
filename = 'tehran_hotel_reviews.json'
remove_duplicate_hotel_records(filename)
