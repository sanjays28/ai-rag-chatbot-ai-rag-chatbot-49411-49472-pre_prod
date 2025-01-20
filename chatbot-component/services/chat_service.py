"""Chat service for handling AI-powered responses."""
import os
from typing import Optional
import time
from datetime import datetime, timedelta
import openai
from config import Config

class ChatService:
    """Handles chat interactions using OpenAI API."""
    
    def __init__(self):
        """Initialize the chat service with OpenAI API key."""
        openai.api_key = Config.OPENAI_API_KEY
        self.context = ""
        self.request_timestamps = []
        self.rate_limit = 10  # requests per minute
    
    # PUBLIC_INTERFACE
    def set_context(self, text: str) -> None:
        """
        Set the context for chat responses from PDF content.
        
        Args:
            text: The extracted text from PDF to use as context
        """
        self.context = text
    
    # PUBLIC_INTERFACE
    def check_rate_limit(self) -> bool:
        """
        Check if the request is within rate limits.
        
        Returns:
            bool: True if request is allowed, False if rate limit exceeded
        """
        now = datetime.now()
        # Remove timestamps older than 1 minute
        self.request_timestamps = [ts for ts in self.request_timestamps 
                                 if ts > now - timedelta(minutes=1)]
        
        if len(self.request_timestamps) >= self.rate_limit:
            return False
        
        self.request_timestamps.append(now)
        return True

    # PUBLIC_INTERFACE
    def generate_response(self, query: str, context: str) -> str:
        """
        Generate a response using OpenAI's API.
        
        Args:
            query: The user's question
            context: The context from PDF
            
        Returns:
            str: The generated response
            
        Raises:
            Exception: If there's an error in generating the response
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Context from PDF: {context}"},
                {"role": "user", "content": query}
            ]
        )
        return response.choices[0].message.content

    # PUBLIC_INTERFACE
    def get_response(self, query: str) -> tuple[str, Optional[str]]:
        """
        Generate a response to user query based on PDF context.
        
        Args:
            query: The user's question
            
        Returns:
            tuple: (response, error_message)
            - response: The AI-generated response
            - error_message: Error message if any, None otherwise
        """
        try:
            if not self.context:
                return "", "No context available. Please upload a PDF first."
            
            if not self.check_rate_limit():
                return "", "Rate limit exceeded. Please try again later."
            
            response = self.generate_response(query, self.context)
            return response, None
        except Exception as e:
            return "", f"Error generating response: {str(e)}"
    
    # PUBLIC_INTERFACE
    def save_feedback(self, feedback: str) -> tuple[bool, Optional[str]]:
        """
        Save user feedback for improving the service.
        
        Args:
            feedback: User's feedback text
            
        Returns:
            tuple: (success, error_message)
            - success: True if feedback was saved successfully
            - error_message: Error message if any, None otherwise
        """
        try:
            # TODO: Implement feedback storage mechanism
            # For now, just log the feedback
            print(f"Received feedback: {feedback}")
            return True, None
        except Exception as e:
            return False, f"Error saving feedback: {str(e)}"
