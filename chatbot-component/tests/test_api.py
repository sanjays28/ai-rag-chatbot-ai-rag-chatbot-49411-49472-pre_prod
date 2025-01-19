import pytest
from io import BytesIO
from unittest.mock import patch
import json
import time

def test_home_page(client):
    """Test the home page endpoint."""
    response = client.get('/')
    assert response.status_code == 200

def test_upload_no_file(client):
    """Test upload endpoint with no file."""
    response = client.post('/upload')
    assert response.status_code == 400
    assert b'No file provided' in response.data

def test_upload_empty_filename(client):
    """Test upload endpoint with empty filename."""
    response = client.post('/upload', data={
        'file': (BytesIO(), '')
    })
    assert response.status_code == 400
    assert b'No file selected' in response.data

def test_upload_invalid_file_type(client):
    """Test upload endpoint with invalid file type."""
    response = client.post('/upload', data={
        'file': (BytesIO(b'test content'), 'test.txt')
    })
    assert response.status_code == 400
    assert b'Invalid file type' in response.data

def test_upload_valid_pdf(client, sample_pdf):
    """Test upload endpoint with valid PDF."""
    with open(sample_pdf, 'rb') as f:
        pdf_content = f.read()
    
    response = client.post('/upload', data={
        'file': (BytesIO(pdf_content), 'test.pdf')
    })
    assert response.status_code == 200
    assert b'File uploaded and processed successfully' in response.data

def test_chat_no_message(client):
    """Test chat endpoint with no message."""
    response = client.post('/chat', json={})
    assert response.status_code == 400
    assert b'No message provided' in response.data

def test_chat_no_pdf_context(client):
    """Test chat endpoint with no PDF context."""
    response = client.post('/chat', json={'message': 'test question'})
    assert response.status_code == 400
    assert b'No PDF context available' in response.data

def test_chat_valid_request(client, sample_pdf):
    """Test chat endpoint with valid request."""
    # First upload a PDF
    with open(sample_pdf, 'rb') as f:
        pdf_content = f.read()
    
    client.post('/upload', data={
        'file': (BytesIO(pdf_content), 'test.pdf')
    })
    
    # Mock OpenAI response
    mock_response = "This is a test response"
    with patch('app.ChatService.generate_response', return_value=mock_response):
        response = client.post('/chat', json={'message': 'test question'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['response'] == mock_response

def test_rate_limiting(client):
    """Test rate limiting functionality."""
    # Make multiple requests quickly to a rate-limited endpoint
    responses = []
    for _ in range(61):  # One more than the rate limit
        responses.append(client.post('/chat', json={'message': 'test'}))
        time.sleep(0.01)  # Small delay to avoid overwhelming the server
    
    # Check that the last request was rate limited
    assert responses[-1].status_code == 429
    assert b'Rate limit exceeded' in responses[-1].data
