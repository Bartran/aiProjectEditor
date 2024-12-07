import os
from openai import OpenAI
import google.generativeai as genai

from dotenv import load_dotenv  # Import load_dotenv

# Load environment variables from .env file
load_dotenv()


class AIProcessor:
    def __init__(self, openai_api_key=None, google_api_key=None):
        """
        Initialize AI processors for OpenAI and Google AI.

        Args:
            openai_api_key (str, optional): OpenAI API key
            google_api_key (str, optional): Google AI Studio API key
        """
        self.openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
        genai.configure(api_key=google_api_key) if google_api_key else None
        self.google_model = genai.GenerativeModel('gemini-1.5-flash') if google_api_key else None

    def process_with_openai(self, messages, context_files):
        """
        Process conversation using OpenAI's API.

        Args:
            messages (list): Conversation messages
            context_files (list): Files to include in context

        Returns:
            str: AI response
        """
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")

        # Append context file contents to messages
        enhanced_messages = messages.copy()
        for file in context_files:
            enhanced_messages.insert(0, {
                "role": "system",
                "content": f"Context from file {file['path']}: {file['content']}"
            })

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=enhanced_messages
        )
        return response.choices[0].message.content

    def process_with_google(self, messages, context_files):
        """
        Process conversation using Google AI Studio.

        Args:
            messages (list): Conversation messages
            context_files (list): Files to include in context

        Returns:
            str: AI response
        """
        if not self.google_model:
            raise ValueError("Google AI API key not configured")

        # Combine messages and context
        context_text = "\n".join([f"Context from {file['path']}: {file['content']}" for file in context_files])
        full_prompt = context_text + "\n" + "\n".join([msg['content'] for msg in messages])

        response = self.google_model.generate_content(full_prompt)
        return response.text
