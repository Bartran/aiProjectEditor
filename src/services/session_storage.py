import os
import json
from datetime import datetime


class SessionStorage:
    def __init__(self, storage_dir='sessions'):
        """
        Initialize session storage.

        Args:
            storage_dir (str): Directory to store session JSON files
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save_session(self, session_id, folder_path):  # Add folder_path
        """
        Save session with selected files and folder path.

        Args:
            session_id (str): Unique identifier for the session
            folder_path (str): Path of the selected folder
        """
        filename = f"{session_id}.json"
        filepath = os.path.join(self.storage_dir, filename)

        if os.path.exists(filepath):
            raise ValueError(f"Session with ID '{session_id}' already exists.")

        session_data = {
            'session_id': session_id,
            'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'folder_path': folder_path  # Store folder path
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=4)

    def get_sessions(self):
        """
        Retrieve all stored sessions.

        Returns:
            list: List of session data
        """
        sessions = {}
        for filename in sorted(os.listdir(self.storage_dir), reverse=True):
            if filename.endswith('.json'):
                filepath = os.path.join(self.storage_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    sessions[session_data['session_id']] = session_data
        return sessions
