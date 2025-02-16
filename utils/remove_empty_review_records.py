import json
import os

def remove_empty_review_records(filename):
    # Define the path to the reviews directory
    reviews_dir = os.path.join(os.path.dirname(__file__), '../rag/core', '..', 'data', 'reviews')

    # Define the full path to the JSON file
    file_path = os.path.join(reviews_dir, filename)

    # Load existing reviews
    with open(file_path, 'r', encoding='utf-8') as f:
        reviews_data = json.load(f)

    # Filter out records with empty reviews
    cleaned_data = [hotel for hotel in reviews_data if hotel.get('reviews')]

    # Save the cleaned data back to the JSON file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

    print(f"Cleaned data has been saved to {filename}")

# Example usage
filename = 'tehran_hotel_reviews.json'
remove_empty_review_records(filename)
