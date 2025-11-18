"""
Text extraction from resume files
Extracts plain text from PDF, DOCX, TXT for analysis
"""

import PyPDF2
import docx
from pathlib import Path
from typing import Optional


class TextExtractor:
    """Extract text from uploaded resume files"""

    @staticmethod
    def extract_text(file_path: str) -> Optional[str]:
        """
        Extract text from resume file

        Args:
            file_path: Path to uploaded file

        Returns:
            Extracted text or None if extraction fails
        """
        path = Path(file_path)

        if not path.exists():
            return None

        try:
            if path.suffix.lower() == ".pdf":
                return TextExtractor._extract_from_pdf(file_path)
            elif path.suffix.lower() == ".docx":
                return TextExtractor._extract_from_docx(file_path)
            elif path.suffix.lower() == ".txt":
                return TextExtractor._extract_from_txt(file_path)
            else:
                return None
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            return None

    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"PDF extraction error: {e}")
        return text.strip()

    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            print(f"DOCX extraction error: {e}")
            return ""

    @staticmethod
    def _extract_from_txt(file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            print(f"TXT extraction error: {e}")
            return ""
