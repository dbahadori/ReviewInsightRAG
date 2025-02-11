import json
import logging
import os
import re
from typing import List

import requests

from rag.core.interfaces import IScraper


def clean_html(raw_html):
    """Remove HTML tags from a string."""
    if not raw_html:
        return ""
    return re.sub(r'<.*?>', '', raw_html).strip()


class IranHotelOnlineScraper(IScraper):
    def __init__(self):
        self.data = None
        self.hotel_name = None
        self.descriptive_info = None
    def scrape(self, url="") -> List[str]:
        response = requests.get(
            "https://www.iranhotelonline.com/api/mvc/v1/hotelInfo/getHotelSummaryInfo"
            "?cityName=mashhad&hotelName=%D9%87%D8%AA%D9%84-%D8%A2%D8%A8%D8%A7%D9%86"
            "&date=1403/12/13&endDate=1403/12/23&nights=2"
        )
        self.data = response.json()
        self.hotel_name = self.data.get("Name", "هتل نامشخص")
        self.descriptive_info = self.extract_descriptive_info()
        self.save_info(f'{self.hotel_name}.json')
        return self.data

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
        hotel_id = self.data.get("HotelId", "")
        phone = self.data.get("SupportPhone", "")
        star_rating = self.data.get("HotelHeader", {}).get("Star", {}).get("GradeId", "")
        return f"هتل {self.hotel_name} با شناسه {hotel_id}، دارای شماره تماس {phone} و رتبه ستاره‌ای {star_rating} می‌باشد."

    def _describe_about_and_cafe(self):
        # Combine AboutHotel and HotelCafe information into one description.
        about = self.data.get("AboutHotel", {})
        brief = clean_html(about.get("BriefDescription", ""))
        full = clean_html(about.get("Description", ""))

        cafe = self.data.get("HotelCafe", {})
        cafe_desc = clean_html(cafe.get("Description", ""))
        cafe_facilities = cafe.get("HotelFacilities", [])
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

    def save_info(self, filename='hotel_info.json'):
        """
        Saves the extracted descriptive hotel information into a JSON file.
        """
        logging.info(f"Saving descriptive hotel information to {filename}...")
        reviews_dir = os.path.join(os.path.dirname(__file__), '../../data/reviews')
        os.makedirs(reviews_dir, exist_ok=True)
        file_path = os.path.join(reviews_dir, filename)


        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.descriptive_info, f, ensure_ascii=False, indent=4)
        logging.info(f"Descriptive hotel information saved to {file_path}")


