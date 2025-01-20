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

def test_chat_invalid_json(client):
    """Test chat endpoint with invalid JSON request format."""
    response = client.post('/chat', data='invalid json', content_type='application/json')
    assert response.status_code == 400
    assert b'Invalid request format. JSON body required' in response.data

def test_chat_missing_query(client):
    """Test chat endpoint with missing query field."""
    response = client.post('/chat', json={})
    assert response.status_code == 400
    assert b'No query provided' in response.data

def test_chat_empty_query(client):
    """Test chat endpoint with empty query string."""
    response = client.post('/chat', json={'query': ''})
    assert response.status_code == 400
    assert b'Query cannot be empty or whitespace' in response.data

def test_chat_whitespace_query(client):
    """Test chat endpoint with whitespace-only query."""
    response = client.post('/chat', json={'query': '   \n\t  '})
    assert response.status_code == 400
    assert b'Query cannot be empty or whitespace' in response.data

def test_chat_long_query(client):
    """Test chat endpoint with query exceeding length limit."""
    long_query = 'a' * 1001  # Create 1001 character string
    response = client.post('/chat', json={'query': long_query})
    assert response.status_code == 400
    assert b'Query exceeds maximum length of 1000 characters' in response.data

def test_chat_boundary_length_queries(client):
    """Test chat endpoint with boundary length queries (999, 1000, 1001 chars)."""
    # Test with 999 characters (should succeed)
    query_999 = 'a' * 999
    response = client.post('/chat', json={'query': query_999})
    assert response.status_code != 400, "999 character query should be accepted"

    # Test with 1000 characters (should succeed)
    query_1000 = 'a' * 1000
    response = client.post('/chat', json={'query': query_1000})
    assert response.status_code != 400, "1000 character query should be accepted"

    # Test with 1001 characters (should fail)
    query_1001 = 'a' * 1001
    response = client.post('/chat', json={'query': query_1001})
    assert response.status_code == 400, "1001 character query should be rejected"
    assert b'Query exceeds maximum length of 1000 characters' in response.data

def test_chat_valid_request(client, sample_pdf):
    """Test chat endpoint with valid request."""
    # First upload a PDF
    with open(sample_pdf, 'rb') as f:
        pdf_content = f.read()
    
    client.post('/upload', data={
        'file': (BytesIO(pdf_content), 'test.pdf')
    })
    
    # Mock chat service response
    mock_response = "This is a test response"
    with patch('services.chat_service.ChatService.get_response', return_value=(mock_response, None)):
        response = client.post('/chat', json={'query': 'test question'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['response'] == mock_response

def test_rate_limiting(client):
    """Test rate limiting functionality."""
    # Make multiple requests quickly to a rate-limited endpoint
    responses = []
    for _ in range(61):  # One more than the rate limit
        responses.append(client.post('/chat', json={'query': 'test'}))
        time.sleep(0.01)  # Small delay to avoid overwhelming the server
    
    # Check that the last request was rate limited
    assert responses[-1].status_code == 429
    assert b'Rate limit exceeded' in responses[-1].data
