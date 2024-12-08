from PyQt5.QtWidgets import QMessageBox, QInputDialog


def save_current_session(self):
    """
    Save current session with selected files and folder path
    """
    if not self.selected_files:
        QMessageBox.warning(self, "No Files", "Please select files first.")
        return

    folder_path = self.get_current_folder_path()  # Get folder path from main window

    session_name, ok = QInputDialog.getText(self, "Save Session", "Enter session name:")

    if ok and session_name:
        # Store selected_files directly as a list
        self.session_storage.save_session(session_name, folder_path)  # Corrected this line
        QMessageBox.information(self, "Session Saved", f"Session '{session_name}' saved successfully.")
        self.load_previous_sessions()


def load_previous_sessions(self):
    """
    Load previous sessions into the sessions list
    """
    self.sessions_list.clear()
    sessions = self.session_storage.get_sessions()

    for session_name, session_data in sessions.items():
        folder_path = session_data.get('folder_path', 'N/A')
        item_text = f"{session_name} - Folder: {folder_path}"
        self.sessions_list.addItem(item_text)


def load_session(self, item):
    index = self.sessions_list.row(item)
    sessions = self.session_storage.get_sessions()
    selected_session_key = list(sessions.keys())[index]
    selected_session = sessions[selected_session_key]
    self.clear_file_selection()

    folder_path = selected_session.get('folder_path')
    if folder_path:
        self.populate_tree_from_session(folder_path)
