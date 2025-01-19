"""Chat service for handling AI-powered responses."""
import os
from typing import Optional
import openai
from config import Config

class ChatService:
    """Handles chat interactions using OpenAI API."""
    
    def __init__(self):
        """Initialize the chat service with OpenAI API key."""
        openai.api_key = Config.OPENAI_API_KEY
        self.context = ""
    
    # PUBLIC_INTERFACE
    def set_context(self, text: str) -> None:
        """
        Set the context for chat responses from PDF content.
        
        Args:
            text: The extracted text from PDF to use as context
        """
        self.context = text
    
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
            
            # Prepare the prompt with context
            prompt = f"Context:\n{self.context}\n\nQuestion: {query}\n\nAnswer:"
            
            # Get response from OpenAI
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=150,
                temperature=0.7,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            return response.choices[0].text.strip(), None
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