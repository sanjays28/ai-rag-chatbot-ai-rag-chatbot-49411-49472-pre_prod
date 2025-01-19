"""PDF processing service for text extraction."""
import os
from typing import Optional
from PyPDF2 import PdfReader
from werkzeug.datastructures import FileStorage

class PDFProcessor:
    """Handles PDF file processing and text extraction."""
    
    # PUBLIC_INTERFACE
    def extract_text(self, file: FileStorage) -> tuple[str, Optional[str]]:
        """
        Extract text from a PDF file.
        
        Args:
            file: The uploaded PDF file
            
        Returns:
            tuple: (extracted_text, error_message)
            - extracted_text: The extracted text from the PDF
            - error_message: Error message if any, None otherwise
        """
        try:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip(), None
        except Exception as e:
            return "", f"Error extracting text from PDF: {str(e)}"
    
    # PUBLIC_INTERFACE
    def handle_encrypted_pdf(self, file: FileStorage, password: str) -> tuple[str, Optional[str]]:
        """
        Handle encrypted PDF files.
        
        Args:
            file: The encrypted PDF file
            password: Password to decrypt the PDF
            
        Returns:
            tuple: (extracted_text, error_message)
            - extracted_text: The extracted text from the PDF
            - error_message: Error message if any, None otherwise
        """
        try:
            reader = PdfReader(file)
            if reader.is_encrypted:
                reader.decrypt(password)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip(), None
        except Exception as e:
            return "", f"Error processing encrypted PDF: {str(e)}"
    
    # PUBLIC_INTERFACE
    def validate_pdf(self, file: FileStorage) -> tuple[bool, Optional[str]]:
        """
        Validate if the file is a valid PDF.
        
        Args:
            file: The file to validate
            
        Returns:
            tuple: (is_valid, error_message)
            - is_valid: True if file is a valid PDF, False otherwise
            - error_message: Error message if any, None otherwise
        """
        try:
            if not file.filename.lower().endswith('.pdf'):
                return False, "File must be a PDF"
            
            reader = PdfReader(file)
            # Reset file pointer for future reads
            file.seek(0)
            return True, None
        except Exception as e:
            return False, f"Invalid PDF file: {str(e)}"