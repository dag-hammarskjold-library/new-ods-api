"""
AI Module for ODS Actions

This module provides access to the extracted PDF documentation
and chatbot functionality for use by AI bots and other programs.
"""

from .pdf_extractor import (
    extract_pdf_content,
    get_documentation_text,
    get_documentation,
    load_documentation,
    DOCUMENTATION_TEXT,
    DOCUMENTATION_DATA
)

# Import chatbot functions if available
try:
    from .chatbot import (
        initialize_gemini,
        get_chatbot_model,
        chat_with_gemini,
        simple_chat,
        create_system_prompt
    )
    CHATBOT_AVAILABLE = True
except ImportError:
    CHATBOT_AVAILABLE = False
    # Define placeholder functions
    def initialize_gemini():
        return False
    def get_chatbot_model():
        return None
    def chat_with_gemini(*args, **kwargs):
        return {'success': False, 'error': 'Chatbot not available'}
    def simple_chat(*args, **kwargs):
        return {'success': False, 'error': 'Chatbot not available'}
    def create_system_prompt():
        return ""

__all__ = [
    'extract_pdf_content',
    'get_documentation_text',
    'get_documentation',
    'load_documentation',
    'DOCUMENTATION_TEXT',
    'DOCUMENTATION_DATA',
    'initialize_gemini',
    'get_chatbot_model',
    'chat_with_gemini',
    'simple_chat',
    'create_system_prompt',
    'CHATBOT_AVAILABLE'
]
