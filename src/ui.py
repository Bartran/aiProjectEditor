import os
import uuid
import pyperclip
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QListWidget, QListWidgetItem,
                             QPushButton, QTextEdit, QFileDialog, QLabel,
                             QComboBox, QMessageBox, QTreeWidget, QTreeWidgetItem)
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
        self.ai_processor = AIProcessor()

        self.selected_files = []
        self.messages = []
        self.conversation_id = str(uuid.uuid4())

        self.init_ui()

    def init_ui(self):
        """
        Initialize the user interface
         """
        central_widget = QWidget()
        main_layout = QHBoxLayout()

        # Left panel: File Selection
        file_panel = QVBoxLayout()
        select_folder_btn = QPushButton("Select Folder")
        select_folder_btn.clicked.connect(self.select_folder)
        file_panel.addWidget(select_folder_btn)

        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("Files")
        self.file_tree.itemChanged.connect(self.file_selection_changed)
        file_panel.addWidget(self.file_tree)

        # Right panel: Chat Interface
        chat_panel = QVBoxLayout()

        # AI Provider Selector
        ai_provider_layout = QHBoxLayout()
        self.ai_provider_selector = QComboBox()
        self.ai_provider_selector.addItems(["OpenAI", "Google AI"])
        self.ai_provider_selector.currentTextChanged.connect(self.update_model_selector)
        ai_provider_layout.addWidget(QLabel("Provider:"))
        ai_provider_layout.addWidget(self.ai_provider_selector)

        # Model Selector
        self.model_selector = QComboBox()
        ai_provider_layout.addWidget(QLabel("Model:"))
        ai_provider_layout.addWidget(self.model_selector)

        # Add provider and model selectors to chat panel
        chat_panel.addLayout(ai_provider_layout)

        # Export Context Button
        export_context_btn = QPushButton("Export Context to Clipboard")
        export_context_btn.clicked.connect(self.export_context)
        chat_panel.addWidget(export_context_btn)

        # Paste External Response Button
        paste_response_btn = QPushButton("Paste External AI Response")
        paste_response_btn.clicked.connect(self.paste_external_response)
        chat_panel.addWidget(paste_response_btn)

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

        # Initialize model selector
        self.update_model_selector()

    def select_folder(self):
        """
        Open a folder selection dialog and populate the file tree with the folder structure
        """
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.file_tree.clear()
            self.populate_tree(folder_path, self.file_tree)

    def populate_tree(self, folder_path, parent_item):
        """
        Recursively populate the tree with subfolders at the top and files below them
        """
        folder_item = QTreeWidgetItem(parent_item)
        folder_item.setText(0, os.path.basename(folder_path))
        folder_item.setData(0, Qt.UserRole, folder_path)
        folder_item.setFlags(folder_item.flags() | Qt.ItemIsUserCheckable)
        folder_item.setCheckState(0, Qt.Unchecked)

        # Separate subfolders and files
        entries = os.listdir(folder_path)
        subfolders = [item for item in entries if os.path.isdir(os.path.join(folder_path, item))]
        files = [item for item in entries if not os.path.isdir(os.path.join(folder_path, item))]

        # Add subfolders
        for subfolder in sorted(subfolders):  # Sort alphabetically
            subfolder_path = os.path.join(folder_path, subfolder)
            self.populate_tree(subfolder_path, folder_item)

        # Add files
        for file in sorted(files):  # Sort alphabetically
            file_path = os.path.join(folder_path, file)
            file_item = QTreeWidgetItem(folder_item)
            file_item.setText(0, file)
            file_item.setData(0, Qt.UserRole, file_path)
            file_item.setFlags(file_item.flags() | Qt.ItemIsUserCheckable)
            file_item.setCheckState(0, Qt.Unchecked)

    def file_selection_changed(self, item):
        """
        Handle file selection changes in the file tree
        """
        file_path = item.data(0, Qt.UserRole)

        if item.childCount() > 0:  # It's a folder
            for i in range(item.childCount()):
                child = item.child(i)
                child.setCheckState(0, item.checkState(0))
        else:  # It's an individual file
            if item.checkState(0) == Qt.Checked and file_path not in [f['path'] for f in self.selected_files]:
                try:
                    file_content = self.file_manager.read_file_content(file_path)
                    self.selected_files.append({
                        'path': file_path,
                        'content': file_content
                    })
                except Exception as e:
                    QMessageBox.warning(self, "File Read Error", f"Could not read file {file_path}: {str(e)}")
            elif item.checkState(0) == Qt.Unchecked:
                self.selected_files = [f for f in self.selected_files if f['path'] != file_path]

    def update_model_selector(self):
        """
        Update model selector based on the selected AI provider
        """
        self.model_selector.clear()
        if self.ai_provider_selector.currentText() == "OpenAI":
            self.model_selector.addItems([
                "gpt-4o-mini",
                "gpt-4o"
            ])
        else:  # Google AI
            self.model_selector.addItems([
                "gemini-1.5-flash",
                "gemini-1.5-pro"
            ])

    def export_context(self):
        """
        Export current conversation context and selected files to clipboard
        """
        # Prepare context export
        context_export = "### Selected Files Context:\n"
        for file in self.selected_files:
            context_export += f"FILE: {file['path']}\n```\n{file['content']}\n```\n\n"

        context_export += "### Conversation History:\n"
        for msg in self.messages:
            role = msg['role'].capitalize()
            context_export += f"{role}: {msg['content']}\n\n"

        # Copy to clipboard
        pyperclip.copy(context_export)

        # Show notification
        QMessageBox.information(self, "Context Exported",
                                "Conversation context and file contents have been copied to clipboard.")

    def paste_external_response(self):
        """
        Paste an external AI response into the chat
        """
        # Get text from clipboard
        external_response = pyperclip.paste()

        if external_response:
            # Add to messages
            self.messages.append({"role": "assistant", "content": external_response})

            # Display in chat
            self.chat_display.append(f"External AI: {external_response}")

            # Save conversation
            self.conversation_storage.save_conversation(
                self.conversation_id,
                self.messages,
                [f['path'] for f in self.selected_files]
            )
        else:
            QMessageBox.warning(self, "Paste Error", "No text found in clipboard.")

    def send_message(self):
        """
        Send a message to the selected AI
        """
        user_message = self.message_input.toPlainText()
        if not user_message:
            return

        # Display user message
        self.chat_display.append(f"You: {user_message}")

        # Prepare message for AI
        self.messages.append({"role": "user", "content": user_message})

        try:
            # Select AI and model based on dropdown
            provider = self.ai_provider_selector.currentText()
            model = self.model_selector.currentText()

            # Process message
            ai_response = self.ai_processor.process(
                provider,
                model,
                self.messages,
                self.selected_files
            )

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