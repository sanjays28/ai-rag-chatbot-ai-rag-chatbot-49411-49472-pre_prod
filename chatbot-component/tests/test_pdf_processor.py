import pytest
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
    text = processor.extract_text(sample_pdf)
    assert text is not None
    assert isinstance(text, str)
    assert "Test PDF" in text
    
    # Test with non-existent file
    with pytest.raises(Exception) as exc_info:
        processor.extract_text('nonexistent.pdf')
    assert "Error extracting text from PDF" in str(exc_info.value)

def test_extract_text_invalid_pdf(tmp_path):
    """Test PDF text extraction with invalid PDF file."""
    processor = PDFProcessor()
    
    # Create invalid PDF file
    invalid_pdf = tmp_path / "invalid.pdf"
    invalid_pdf.write_text("This is not a PDF file")
    
    with pytest.raises(Exception) as exc_info:
        processor.extract_text(str(invalid_pdf))
    assert "Error extracting text from PDF" in str(exc_info.value)