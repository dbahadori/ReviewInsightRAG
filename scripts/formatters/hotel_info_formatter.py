class HotelInfoFormatter:
    @staticmethod
    def format_info_for_faiss(hotel_info: dict) -> str:
        """
        Converts structured hotel information into text-based format for FAISS.
        """
        text = f"Hotel Name: {hotel_info.get('hotel_name', 'نامشخص')}\n"
        text += f"Hotel ID: {hotel_info.get('hotel_id', 'نامشخص')}\n"
        text += f"Hotel Summary: {hotel_info.get('hotel_summary', 'هتل نامشخص با مشخصات نامشخص')}\n"
        text += f"About and Cafe: {hotel_info.get('about_and_cafe', '')}\n"
        text += f"Internet and Parking: {hotel_info.get('internet_and_parking', 'فاقد اینترنت و فاقد پارکینگ')}\n"
        text += f"Distance Information: {hotel_info.get('distance_information', '')}\n"
        text += f"FAQs: {hotel_info.get('faqs', 'سؤالی در مورد هتل موجود نیست')}\n"
        text += f"Policies: {hotel_info.get('policies', 'هیچ سیاست مشخصی برای هتل تعریف نشده است')}\n"
        text += f"Hotel Labels: {hotel_info.get('hotel_labels', 'برچسبی برای هتل تعریف نشده است')}\n"
        text += f"Nearby Info: {hotel_info.get('nearby_info', 'هیچ اطلاعات نزدیکی برای هتل نامشخص یافت نشد')}\n"
        text += f"Club Offers: {hotel_info.get('club_offers', 'هیچ پیشنهادی از خدمات کلوب ارائه نشده است')}\n"
        text += f"Near Streets: {hotel_info.get('near_streets', 'هیچ خیابان نزدیکی برای هتل نامشخص یافت نشد')}\n"

        return text
