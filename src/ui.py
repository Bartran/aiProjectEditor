import os
import uuid
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QListWidget, QListWidgetItem, QCheckBox,
                             QPushButton, QTextEdit, QFileDialog, QLabel,
                             QComboBox)
from PyQt5.QtCore import Qt

from file_manager import FileManager
from conversation_storage import ConversationStorage
from ai_processor import AIProcessor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Context Chat")
        self.resize(1000, 800)

        # Initialize components
        self.file_manager = FileManager()
        self.conversation_storage = ConversationStorage()
        self.ai_processor = AIProcessor(
            openai_api_key=os.environ.get('OPENAI_API_KEY'),
            google_api_key=os.environ.get('GOOGLE_API_KEY')
        )

        self.selected_files = []
        self.messages = []
        self.conversation_id = str(uuid.uuid4())

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout()

        # Left panel: File Selection
        file_panel = QVBoxLayout()
        select_folder_btn = QPushButton("Select Folder")
        select_folder_btn.clicked.connect(self.select_folder)
        file_panel.addWidget(select_folder_btn)

        self.file_list = QListWidget()
        self.file_list.itemChanged.connect(self.file_selection_changed)
        file_panel.addWidget(self.file_list)

        # Right panel: Chat Interface
        chat_panel = QVBoxLayout()

        self.ai_selector = QComboBox()
        self.ai_selector.addItems(["OpenAI", "Google AI"])
        chat_panel.addWidget(self.ai_selector)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        chat_panel.addWidget(self.chat_display)

        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(100)
        chat_panel.addWidget(self.message_input)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)
        chat_panel.addWidget(send_btn)

        # Add panels to main layout
        main_layout.addLayout(file_panel, 1)
        main_layout.addLayout(chat_panel, 2)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.file_list.clear()
            files = self.file_manager.get_files_recursively(folder_path)

            for file in files:
                item = QListWidgetItem(file)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.file_list.addItem(item)

    def file_selection_changed(self, item):
        file_path = item.text()
        if item.checkState() == Qt.Checked and file_path not in [f['path'] for f in self.selected_files]:
            file_content = self.file_manager.read_file_content(file_path)
            self.selected_files.append({
                'path': file_path,
                'content': file_content
            })
        elif item.checkState() == Qt.Unchecked:
            self.selected_files = [f for f in self.selected_files if f['path'] != file_path]

    def send_message(self):
        user_message = self.message_input.toPlainText()
        if not user_message:
            return

        # Display user message
        self.chat_display.append(f"You: {user_message}")

        # Prepare message for AI
        self.messages.append({"role": "user", "content": user_message})

        try:
            # Select AI based on dropdown
            if self.ai_selector.currentText() == "OpenAI":
                ai_response = self.ai_processor.process_with_openai(self.messages, self.selected_files)
            else:
                ai_response = self.ai_processor.process_with_google(self.messages, self.selected_files)

            # Display AI response
            self.chat_display.append(f"AI: {ai_response}")

            # Store messages
            self.messages.append({"role": "assistant", "content": ai_response})

            # Save conversation
            self.conversation_storage.save_conversation(
                self.conversation_id,
                self.messages,
                [f['path'] for f in self.selected_files]
            )

            # Clear message input
            self.message_input.clear()

        except Exception as e:
            self.chat_display.append(f"Error: {str(e)}")
