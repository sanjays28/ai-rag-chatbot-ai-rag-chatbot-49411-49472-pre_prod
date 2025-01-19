import pytest
import openai
from app import ChatService
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_openai_response():
    return MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content="This is a test response"
                )
            )
        ]
    )

def test_generate_response(mock_openai_response):
    """Test chat response generation."""
    with patch('openai.ChatCompletion.create', return_value=mock_openai_response):
        response = ChatService.generate_response("Test question", "Test context")
        assert response == "This is a test response"
        
        # Verify OpenAI API was called with correct parameters
        openai.ChatCompletion.create.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Context from PDF: Test context"},
                {"role": "user", "content": "Test question"}
            ]
        )

def test_generate_response_error():
    """Test error handling in response generation."""
    with patch('openai.ChatCompletion.create', side_effect=Exception("API Error")):
        with pytest.raises(Exception) as exc_info:
            ChatService.generate_response("Test question", "Test context")
        assert "Error generating response: API Error" in str(exc_info.value)
