from PyQt5.QtWidgets import QMessageBox, QInputDialog


def save_current_session(self):
    """
    Save current session with selected files
    """
    if not self.selected_files:
        QMessageBox.warning(self, "No Files", "Please select files first.")
        return

    # Prompt for the session name
    session_name, ok = QInputDialog.getText(self, "Save Session", "Enter session name:")

    if ok and session_name:
        # Save the session with the provided name as the key
        self.session_storage.save_session(session_name, {'selected_files': self.selected_files})
        QMessageBox.information(self, "Session Saved", f"Session '{session_name}' saved successfully.")

        # Reload previous sessions
        self.load_previous_sessions()


def load_previous_sessions(self):
    """
    Load previous sessions into the sessions list
    """
    self.sessions_list.clear()
    sessions = self.session_storage.get_sessions()

    for session_name, session_data in sessions.items():
        item_text = f"{session_name} - {len(session_data['selected_files'])} files"
        self.sessions_list.addItem(item_text)


def load_session(self, item):
    index = self.sessions_list.row(item)
    sessions = self.session_storage.get_sessions()
    selected_session_key = list(sessions.keys())[index]  # Get session key by index
    selected_session = sessions[selected_session_key]  # Get session using the key
    self.clear_file_selection()

    for file_path in selected_session['selected_files']:
        self.find_and_check_file(file_path)
