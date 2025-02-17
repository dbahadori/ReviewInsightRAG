import json
import logging
import os
from datetime import datetime
import requests

from rag.core.interfaces import IScraper
from rag.core.scrapers.iranHotel.hotel_list_fetcher import HotelListFetcher
import re

from rag.core.scrapers.iranHotel.hotel_vote_fetcher import HotelVoteFetcher
from utils.file_manager import FileManager
from utils.path_util import PathUtil


def clean_html(raw_html):
    # Check if raw_html is a dictionary
    if isinstance(raw_html, dict):
        # Extract the relevant string content from the dictionary (example key: 'content')
        raw_html = raw_html.get('content', '')

    # Check if raw_html is None or empty
    if not raw_html:
        return ''

    if not isinstance(raw_html, (str, bytes)):
        # Log an error, raise an exception, or handle the case appropriately
        raise ValueError(f"Expected string or bytes-like object, got {type(raw_html).__name__}")

    # Perform the HTML cleaning if the input is valid
    cleaned_html = re.sub(r'<.*?>', '', raw_html).strip()
    return cleaned_html


class IranHotelOnlineScraper(IScraper):
    def __init__(self):
        self.data = None
        self.hotel_name = None
        self.descriptive_info = None
        self.reviews = None
        self.hotel_info_list = []
        self.hotel_urls = None
        self.hotel_fetcher = HotelListFetcher()
        self.fetcher = HotelVoteFetcher()  # Initialize the vote fetcher

    def run(self):
        # hotel_fetcher.run()
        self.hotel_urls = self.hotel_fetcher.generate_hotel_summary_urls(from_file=False)
        self.hotel_info_list = self.scrape(urls=self.hotel_urls)
        self.save_all_info(self.hotel_info_list)
        return self.hotel_info_list

    def scrape(self, urls: list[str]) -> list[dict]:
        """
        Scrapes hotel data from multiple URLs, checking for duplicates and saving only unique entries.
        """
        if not urls:
            logging.warning("No URLs provided for scraping.")
            return []

        hotel_info_list = []
        hotel_ids = []

        for url in urls:
            logging.info(f"Scraping hotel data from: {url}")
            response = requests.get(url)

            if response.status_code != 200:
                logging.warning(f"Failed to retrieve data from {url}. Skipping...")
                continue  # Move to the next URL

            self.data = response.json()
            self.hotel_name = self.data.get("Name", "هتل نامشخص")

            # Extract city name dynamically
            city_name = self.extract_city_name(url) or "نامشخص"

            # Create metadata for the current hotel
            metadata = {
                "url": url,
                "hotel_source_id": self.data.get("HotelId", ""),
                "hotel_name": self.hotel_name,
                "city_name": city_name,
                "scraped_at": datetime.now().isoformat()
            }

            # Check for duplicates
            if self.is_duplicate_entry(filename=f'{self.hotel_name}.json', metadata=metadata):
                logging.info(f"Duplicate hotel entry found for {self.hotel_name}. Skipping...")
                continue  # Skip this hotel and move to the next URL

            # Extract descriptive information
            self.descriptive_info = self.extract_descriptive_info()

            # Collect hotel IDs for fetching votes
            hotel_ids.append(self.data.get("HotelId", ""))

            # Combine metadata and descriptive_info for the current hotel
            hotel_info = {
                "metadata": metadata,
                "descriptive_info": self.descriptive_info,
                "reviews": []  # Initialize reviews as an empty list
            }

            # Append the hotel info to the list
            hotel_info_list.append(hotel_info)

        # Fetch votes for all hotels outside the loop
        hotel_votes = self.fetcher.run(hotel_ids)

        # Add votes to the respective hotel's reviews
        for hotel_info in hotel_info_list:
            hotel_id = hotel_info["metadata"]["hotel_source_id"]
            hotel_info["reviews"] = hotel_votes.get(hotel_id, [])

        return hotel_info_list  # Return the list of successfully scraped hotel info

    def save_all_info(self, hotel_info_list: list[dict], file_name='hotels_info.json'):
        """
        Saves the extracted descriptive hotel information for multiple hotels into a JSON file.
        Prevents duplicate entries by checking hotel_source_id or (hotel_name and city_name).
        """
        logging.info(f"Saving all descriptive hotel information to {file_name}...")
        file_path = PathUtil.construct_path(PathUtil.get_project_base_path(), 'data', 'hotel', file_name)

        # Load existing data (if any)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        # Check and append unique hotel info
        for hotel_info in hotel_info_list:
            metadata = hotel_info.get("metadata", {})
            is_duplicate = any(
                (existing_metadata.get("hotel_source_id") == metadata["hotel_source_id"] if existing_metadata.get(
                    "hotel_source_id") else False) or
                (existing_metadata.get("hotel_name") == metadata["hotel_name"] and existing_metadata.get("city_name") ==
                 metadata["city_name"])
                for existing_hotel in existing_data
                for existing_metadata in [existing_hotel.get("metadata", {})]
            )
            if not is_duplicate:
                existing_data.append(hotel_info)

        # Save the updated list to the JSON file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)

        logging.info(f"Descriptive hotel information saved to {file_path}")
        return existing_data

    def get_data(self, from_file=True, file_name='hotels_info.json'):
        if from_file:
            file_path = PathUtil.construct_path(PathUtil.get_project_base_path(), 'data', 'hotel', file_name)
            file_manager = FileManager(file_path)
            hotel_info_records = file_manager.load_records()
        else:
            if not self.hotel_info_list:
                self.run()
            hotel_info_records = self.hotel_info_list
        return hotel_info_records

    def is_duplicate_entry(self, filename, metadata) -> bool:
        """
        Checks if a record with the same hotel_source_id or (hotel_name and city_name) exists.
        """
        file_path = os.path.join(os.path.dirname(__file__), '../../data/reviews', filename)

        # If file does not exist, no duplicates
        if not os.path.exists(file_path):
            return False

        # Load existing data
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                return False  # If file is corrupted, treat it as empty

        # Check for duplicates
        for existing_hotel in existing_data:
            existing_metadata = existing_hotel.get("metadata", {})
            if (existing_metadata.get("hotel_source_id") and existing_metadata["hotel_source_id"] == metadata[
                "hotel_source_id"]) or \
                    (existing_metadata.get("hotel_name") == metadata["hotel_name"] and existing_metadata.get(
                        "city_name") == metadata["city_name"]):
                return True  # Duplicate found

        return False  # No duplicates found

    def extract_descriptive_info(self):
        """Extract and combine all hotel information into descriptive natural language texts."""
        descriptive_info = {
            "hotel_summary": self._describe_basic_info(),
            "about_and_cafe": self._describe_about_and_cafe(),
            "internet_and_parking": self._describe_internet_parking(),
            "distance_information": self._describe_distance_info(),
            "faqs": self._describe_faqs(),
            "policies": self._describe_policies(),
            "hotel_labels": self._describe_hotel_labels(),
            "nearby_info": self._describe_nearbies(),
            "club_offers": self._describe_club_offers(),
            "near_streets": self._describe_near_streets()
        }
        return descriptive_info

    def _describe_basic_info(self):
        phone = self.data.get("SupportPhone", "")

        hotel_header = self.data.get("HotelHeader")
        star_rating = ""
        if hotel_header:
            star_rating_dict = hotel_header.get("Star")
            if star_rating_dict:
                star_rating = star_rating_dict.get("GradeId", "")

        sentences = []

        if phone:
            sentences.append(f"شماره تماس هتل: {phone}")

        if star_rating:
            sentences.append(f"رتبه ستاره‌ای هتل: {star_rating}")

        if sentences:
            return f"هتل {self.hotel_name}، " + " و ".join(sentences) + " می‌باشد."
        else:
            return f"اطلاعاتی برای هتل {self.hotel_name} موجود نیست."

    def _describe_about_and_cafe(self):
        # Combine AboutHotel and HotelCafe information into one description.
        about = self.data.get("AboutHotel", {})
        if about:
            brief = clean_html(about.get("BriefDescription", ""))
            full = clean_html(about.get("Description", ""))
        else:
            brief = ""
            full = ""

        cafe = self.data.get("HotelCafe", {})
        if cafe:
            cafe_desc = clean_html(cafe.get("Description", ""))
            cafe_facilities = cafe.get("HotelFacilities", [])
        else:
            cafe_desc = ""
            cafe_facilities = ""

        facilities_list = [clean_html(fac.get("Name", "")) for fac in cafe_facilities if fac.get("Name")]
        facilities_text = ", ".join(facilities_list)

        parts = []
        if brief or full:
            parts.append(f"درباره هتل: {brief} {full}".strip())
        if cafe_desc or facilities_text:
            parts.append(
                f"کافه هتل: {cafe_desc}" + (f"؛ امکانات کافه شامل: {facilities_text}" if facilities_text else ""))
        return " ".join(parts)

    def _describe_internet_parking(self):
        # Produce a natural language sentence for the hotel internet and parking amenities.
        hip = self.data.get("HotelInternetParking", {})
        if not hip:
            return "امکانات اینترنت و پارکینگ برای هتل یافت نشد"

        has_internet = hip.get("HasInternet", False)
        has_parking = hip.get("HasParking", False)
        internet_text = "دارای اینترنت" if has_internet else "فاقد اینترنت"
        parking_text = "دارای پارکینگ" if has_parking else "فاقد پارکینگ"
        return f"امکانات اینترنت و پارکینگ هتل: {internet_text} و {parking_text} می‌باشد."

    def _describe_distance_info(self):
        # Process each item in DistanceInfo and render a sentence if applicable.
        distance_info = self.data.get("DistanceInfo", {})
        descriptions = []
        for key, value in distance_info.items():
            if isinstance(value, list):
                for item in value:
                    desc = self._describe_distance_item(item)
                    if desc:
                        descriptions.append(desc)
            elif isinstance(value, dict):
                desc = self._describe_distance_item(value)
                if desc:
                    descriptions.append(desc)
        return "؛ ".join(descriptions)

    def _describe_distance_item(self, item):
        """
        Convert an item with Name, Duration, Distance, and DistanceUnit into a natural language sentence.
        Example: "فاصله تا بلوار هفت تیر 2 دقیقه به اندازه 799 متر"
        """
        name = clean_html(item.get("Name", ""))
        duration = clean_html(item.get("Duration", ""))
        distance = item.get("Distance", "")
        unit_val = item.get("DistanceUnit", "")
        # Map unit values: 1 -> متر, 2 -> کیلومتر
        if unit_val == 1 or unit_val == "1":
            unit = "متر"
        elif unit_val == 2 or unit_val == "2":
            unit = "کیلومتر"
        else:
            unit = ""
        if name and distance:
            if duration:
                return f"فاصله تا {name} {duration} به اندازه {distance} {unit}"
            else:
                return f"فاصله تا {name} به اندازه {distance} {unit}"
        return ""

    def _describe_faqs(self):
        # Combine each FAQ's question and answer into one descriptive sentence.
        faqs = self.data.get("FAQs", [])
        if not faqs:
            return "سؤالی در مورد هتل موجود نیست."

        faq_descriptions = []
        for faq in faqs:
            question = clean_html(faq.get("Title", ""))
            answer = clean_html(faq.get("Description", ""))
            if question or answer:
                faq_descriptions.append(f"سوال: {question} - پاسخ: {answer}")
        return "؛ ".join(faq_descriptions) if faq_descriptions else "سؤالی در مورد هتل موجود نیست."

    def _describe_policies(self):
        # Build a fluent natural language description for all policies.
        policies = self.data.get("Policies", {})

        sentences = []

        # Include check-in and check-out times (if available)
        check_in = self.data.get("CheckInTime", "")
        check_out = self.data.get("CheckOutTime", "")
        if check_in or check_out:
            sentences.append(f"ساعت ورود هتل {check_in} و ساعت خروج {check_out} می‌باشد.")

        if not policies:
            sentences.append("هیچ سیاست مشخصی دیگری برای هتل تعریف نشده است.")
            return sentences

        # Process each policy group if present.
        policy_groups = policies.get("PolicyGroup")
        if policy_groups:
            if isinstance(policy_groups, list):
                for group in policy_groups:
                    group_name = clean_html(group.get("Name", ""))
                    group_policies = group.get("Policies", [])
                    if group_name and group_policies:
                        # Join all policies in the group as a comma-separated string.
                        policies_text = "، ".join([clean_html(p) for p in group_policies if p])
                        sentences.append(f"در رابطه با  {group_name}، موارد زیر ذکر شده است: {policies_text}.")
            elif isinstance(policy_groups, dict):
                group_name = clean_html(policy_groups.get("Name", ""))
                group_policies = policy_groups.get("Policies", [])
                if group_name and group_policies:
                    policies_text = "، ".join([clean_html(p) for p in group_policies if p])
                    sentences.append(f"در رابطه با  {group_name}، موارد زیر ذکر شده است: {policies_text}.")

        # Cancellation policy
        cancellation = clean_html(policies.get("PolicyHotelCancellation", ""))
        if cancellation:
            sentences.append(f"قوانین کنسلی به شرح زیر است: {cancellation}.")

        # Child policy
        child_policy = clean_html(policies.get("PolicyHotelChild", ""))
        if child_policy:
            sentences.append(f"قوانین مربوط به سن خردسال به شرح زیر است: {child_policy}.")

        # General checking policies
        checking_policy = clean_html(policies.get("PolicyHotelChecking", ""))
        if checking_policy:
            sentences.append(f"قوانین عمومی پذیرش به شرح زیر است: {checking_policy}.")

        return " ".join(sentences) if sentences else "هیچ سیاست مشخصی برای هتل تعریف نشده است."

    def _describe_hotel_labels(self):
        # Combine all hotel labels into one descriptive sentence.
        labels = self.data.get("HotelLabels", [])
        if not labels:
            return "برچسبی برای هتل تعریف نشده است."

        label_list = []
        for label in labels:
            if isinstance(label, dict):
                parts = [clean_html(str(v)) for v in label.values() if v]
                label_list.append(" ".join(parts))
            elif isinstance(label, str):
                label_list.append(clean_html(label))

        if label_list:
            return "برچسب‌های هتل: " + ", ".join(label_list)
        return "برچسبی برای هتل تعریف نشده است."

    def _describe_nearbies(self):
        # For each nearby place, create a descriptive sentence.
        nearbies = self.data.get("NearBies", [])
        if not nearbies:
            return f"هیچ اطلاعات نزدیکی برای  {self.hotel_name} یافت نشد."

        descriptions = []
        for item in nearbies:
            name = clean_html(item.get("Name", ""))
            distance = item.get("Distance", "")
            unit_val = item.get("DistanceUnit", "")
            if unit_val == 1 or unit_val == "1":
                unit = "متر"
            elif unit_val == 2 or unit_val == "2":
                unit = "کیلومتر"
            else:
                unit = ""
            if name and distance:
                descriptions.append(f"فاصله  {self.hotel_name} تا {name} به اندازه {distance} {unit}")
        return "؛ ".join(descriptions) if descriptions else f"هیچ اطلاعات نزدیکی برای  {self.hotel_name} یافت نشد."

    def _describe_club_offers(self):
        # Combine all club offers into one descriptive sentence using the given template.
        club_offers = self.data.get("ClubOffers", [])
        offers_list = []
        if not club_offers:
            return "هیچ پیشنهادی از خدمات کلوب ارائه نشده است."

        for offer in club_offers:
            if isinstance(offer, dict):
                offer_name = clean_html(offer.get("Name", ""))
                if offer_name:
                    offers_list.append(offer_name)
            elif isinstance(offer, str):
                offers_list.append(clean_html(offer))
        if offers_list:
            offers_text = ", ".join(offers_list)
            return (f"خدمات +IHO امکانی جدید از ایران هتل آنلاین می‌باشد که با رزرو هتل از این سایت "
                    f"می‌توانید خدمات زیر {offers_text} را از هتل {self.hotel_name} دریافت نمایید.")
        return "هیچ پیشنهادی از خدمات کلوب ارائه نشده است."

    def _describe_near_streets(self):
        # Process the NearStreets field, which is expected to be a list of dicts with "Text" keys.
        near_streets = self.data.get("NearStreets", [])
        if not near_streets:
            return f"هیچ خیابان نزدیکی برای  {self.hotel_name} یافت نشد."

        streets_list = []
        for item in near_streets:
            if isinstance(item, dict):
                street_text = clean_html(item.get("Text", ""))
                if street_text:
                    streets_list.append(street_text)
            elif isinstance(item, str):
                streets_list.append(clean_html(item))
        if streets_list:
            streets_text = ", ".join(streets_list)
            return f"خیابان‌های نزدیک به  {self.hotel_name} شامل خیابان‌های {streets_text} می‌باشد."
        else:
            return f"هیچ خیابان نزدیکی برای  {self.hotel_name} یافت نشد."

    def extract_city_name(self, url):
        """
        Extracts the city name from the URL or the API response.
        """
        # Extract city name from the URL (if present)
        if url:
            match = re.search(r"cityName=([^&]+)", url)
            if match:
                return match.group(1)

        # Fallback: Extract city name from the API response (if available)
        if self.data:
            return self.data.get("CityName", "نامشخص")

        return "نامشخص"  # Default fallback

