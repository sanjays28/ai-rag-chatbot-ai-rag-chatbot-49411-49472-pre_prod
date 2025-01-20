import pytest
from io import BytesIO
from werkzeug.datastructures import FileStorage
from app import PDFProcessor
import os

def test_allowed_file():
    """Test file extension validation."""
    processor = PDFProcessor()
    
    # Test valid PDF file
    assert processor.allowed_file('test.pdf') == True
    
    # Test invalid extensions
    assert processor.allowed_file('test.txt') == False
    assert processor.allowed_file('test.doc') == False
    assert processor.allowed_file('test') == False

def test_extract_text(sample_pdf):
    """Test PDF text extraction."""
    processor = PDFProcessor()
    
    # Test with valid PDF
    with open(sample_pdf, 'rb') as f:
        file_storage = FileStorage(
            stream=BytesIO(f.read()),
            filename='test.pdf',
            content_type='application/pdf'
        )
        text, error = processor.extract_text(file_storage)
        assert error is None, f"Error occurred: {error}"
        assert isinstance(text, str)
        assert len(text) > 0
        assert "Test PDF" in text

def test_extract_text_invalid_pdf(tmp_path):
    """Test PDF text extraction with invalid PDF file."""
    processor = PDFProcessor()
    
    # Create invalid PDF file
    invalid_content = b"This is not a PDF file"
    file_storage = FileStorage(
        stream=BytesIO(invalid_content),
        filename='invalid.pdf',
        content_type='application/pdf'
    )
    
    text, error = processor.extract_text(file_storage)
    assert error is not None
    assert "Error extracting text from PDF" in error
