# rag/file_readers/pdf_reader.py
import PyPDF2


class PDFReader:
    @staticmethod
    def read(file_path: str) -> str:
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
