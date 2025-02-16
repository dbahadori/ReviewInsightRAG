from rag.core.interfaces import Document


class IranHotelOnlineFormatter:
    @staticmethod
    def format_hotel_info_for_faiss(hotel_info: dict) -> Document:
        """
        Converts structured hotel information into a Document object for FAISS.

        Args:
            hotel_info (dict): A dictionary containing hotel information.

        Returns:
            Document: A Document object containing the formatted text and metadata.
        """
        # Extract metadata if available
        metadata = hotel_info.get("metadata", {})
        content = hotel_info.get("descriptive_info")
        text = f"Hotel Name: {metadata.get('hotel_name', 'نامشخص')}\n"
        text += f"Hotel Summary: {content.get('hotel_summary', 'هتل نامشخص با مشخصات نامشخص')}\n"
        text += f"About and Cafe: {content.get('about_and_cafe', '')}\n"
        text += f"Internet and Parking: {content.get('internet_and_parking', 'فاقد اینترنت و فاقد پارکینگ')}\n"
        text += f"Distance Information: {content.get('distance_information', '')}\n"
        text += f"FAQs: {content.get('faqs', 'سؤالی در مورد هتل موجود نیست')}\n"
        text += f"Policies: {content.get('policies', 'هیچ سیاست مشخصی برای هتل تعریف نشده است')}\n"
        text += f"Hotel Labels: {content.get('hotel_labels', 'برچسبی برای هتل تعریف نشده است')}\n"
        text += f"Nearby Info: {content.get('nearby_info', 'هیچ اطلاعات نزدیکی برای هتل نامشخص یافت نشد')}\n"
        text += f"Club Offers: {content.get('club_offers', 'هیچ پیشنهادی از خدمات کلوب ارائه نشده است')}\n"
        text += f"Near Streets: {content.get('near_streets', 'هیچ خیابان نزدیکی برای هتل نامشخص یافت نشد')}\n"

        # Create and return a Document object
        return Document(content=text, metadata=metadata)

    @staticmethod
    def format_hotel_reviews_for_faiss(hotel_review: dict) -> Document:
        """
        Converts structured hotel review information into a Document object for FAISS.

        Args:
            hotel_review (dict): A dictionary containing hotel review information.

        Returns:
            Document: A Document object containing the formatted text and metadata.
        """
        metadata = hotel_review.get("metadata", {})
        reviews = hotel_review.get("reviews", [])

        # Combine fields into a single text
        text = ""
        for review in reviews:
            text += f"عنوان: {review.get('title', 'بدون عنوان')}. "
            text += f"توضیحات: {review.get('description', 'بدون توضیحات')}. "
            text += f"امتیاز: {review.get('rate', 'بدون امتیاز')} ({review.get('rateTitle', 'بدون عنوان امتیاز')}). "
            text += f"مسافر: {review.get('guestName', 'نامشخص')}. "
            text += f"تاریخ ورود: {review.get('arrivalDatePersian', 'نامشخص')}. "
            text += f"تاریخ خروج: {review.get('checkoutDatePersian', 'نامشخص')}. "
            text += f"مدت اقامت: {review.get('duration', 'نامشخص')} شب. "
            text += f"نوع سفر: {review.get('travelTypeTitle', 'نامشخص')}. "
            text += f"نوع اتاق: {review.get('roomName', 'نامشخص')}.\n"

        # Create and return a Document object
        return Document(content=text.strip(), metadata=metadata)
