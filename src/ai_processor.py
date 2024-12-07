import os
from openai import OpenAI
import google.generativeai as genai


class AIProcessor:
    def __init__(self, openai_api_key=None, google_api_key=None):
        """
        Initialize AI processors for OpenAI and Google AI.

        Args:
            openai_api_key (str, optional): OpenAI API key
            google_api_key (str, optional): Google AI Studio API key
        """
        # Use environment variables if not provided
        self.openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', openai_api_key))

        # Configure Google AI
        google_key = os.environ.get('GOOGLE_API_KEY', google_api_key)
        if google_key:
            genai.configure(api_key=google_key)

    def process(self, provider, model, messages, context_files):
        """
        Process conversation using the specified provider and model.

        Args:
            provider (str): AI provider (OpenAI or Google AI)
            model (str): Specific model to use
            messages (list): Conversation messages
            context_files (list): Files to include in context

        Returns:
            str: AI response
        """
        # Prepare context
        context_text = "\n".join([f"Context from {file['path']}: {file['content']}" for file in context_files])

        # Modify messages to include context
        enhanced_messages = [
                                {"role": "system", "content": context_text}
                            ] + messages

        if provider == "OpenAI":
            return self._process_openai(model, enhanced_messages)
        elif provider == "Google AI":
            return self._process_google(model, enhanced_messages)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _process_openai(self, model, messages):
        """
        Process conversation using OpenAI's API.
        """
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content

    def _process_google(self, model, messages):
        """
        Process conversation using Google AI Studio.
        """
        # Combine messages into a single prompt
        full_prompt = "\n".join([msg['content'] for msg in messages])

        # Select the appropriate Google model
        google_model = genai.GenerativeModel(model)

        response = google_model.generate_content(full_prompt)
        return response.text