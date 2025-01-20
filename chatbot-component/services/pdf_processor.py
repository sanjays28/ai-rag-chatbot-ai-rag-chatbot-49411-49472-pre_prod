"""PDF processing service for text extraction."""
import os
from typing import Optional, Set
from PyPDF2 import PdfReader
from werkzeug.datastructures import FileStorage

class PDFProcessor:
    """Handles PDF file processing and text extraction."""
    
    def __init__(self):
        """Initialize PDFProcessor with allowed extensions."""
        self._allowed_extensions: Set[str] = {'pdf'}
    
    def allowed_file(self, filename: str) -> bool:
        """
        Check if the file extension is allowed.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            bool: True if file extension is allowed, False otherwise
        """
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self._allowed_extensions
    
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
            if not self.allowed_file(file.filename):
                return "", "Invalid file type. Only PDF files are allowed."
            
            reader = PdfReader(file)
            if len(reader.pages) == 0:
                return "", "PDF file is empty"
                
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    
            if not text.strip():
                return "", "No text could be extracted from the PDF"
                
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
