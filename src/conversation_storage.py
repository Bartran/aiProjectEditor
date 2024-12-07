import os
import json
from datetime import datetime


class ConversationStorage:
    def __init__(self, storage_dir='conversations'):
        """
        Initialize conversation storage.

        Args:
            storage_dir (str): Directory to store conversation JSON files
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save_conversation(self, conversation_id, messages, context_files):
        """
        Save conversation to a JSON file.

        Args:
            conversation_id (str): Unique identifier for the conversation
            messages (list): List of message dictionaries
            context_files (list): List of files used in the context
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{conversation_id}_{timestamp}.json"
        filepath = os.path.join(self.storage_dir, filename)

        conversation_data = {
            'conversation_id': conversation_id,
            'timestamp': timestamp,
            'context_files': context_files,
            'messages': messages
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=4)

    def get_conversations(self):
        """
        Retrieve all stored conversations.

        Returns:
            list: List of conversation data
        """
        conversations = []
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.storage_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    conversations.append(json.load(f))
        return conversations