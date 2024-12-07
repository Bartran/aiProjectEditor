import os
import uuid
import pyperclip
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTextEdit,
    QFileDialog, QLabel, QMessageBox, QTreeWidget, QTreeWidgetItem, QSplitter,
    QListWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.file_manager import FileManager
from src.session_storage import SessionStorage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Context Collector")
        self.resize(1200, 800)
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f0f0; }
            QTreeWidget { background-color: white; border: 1px solid #d0d0d0; }
            QTextEdit { background-color: white; border: 1px solid #d0d0d0; }
            QPushButton { 
                background-color: #4CAF50; 
                color: white; 
                border: none; 
                padding: 8px; 
                border-radius: 4px; 
            }
            QPushButton:hover { background-color: #45a049; }
        """)

        # Initialize components
        self.selected_files = []
        self.session_id = str(uuid.uuid4())

        # Placeholder file manager and session storage
        self.file_manager = FileManager()
        self.session_storage = SessionStorage()

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout()

        splitter = QSplitter(Qt.Horizontal)

        # Left Panel: File Selection
        file_panel = QWidget()
        file_layout = QVBoxLayout()

        select_folder_btn = QPushButton("Select Folder")
        select_folder_btn.clicked.connect(self.select_folder)
        file_layout.addWidget(select_folder_btn)

        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("Project Files")
        self.file_tree.itemChanged.connect(self.file_selection_changed)
        file_layout.addWidget(self.file_tree)

        file_panel.setLayout(file_layout)
        splitter.addWidget(file_panel)

        # Right Panel: Context and Actions
        context_panel = QWidget()
        context_layout = QVBoxLayout()

        # Action Buttons
        actions_layout = QHBoxLayout()
        copy_context_btn = QPushButton("Copy Context")
        copy_context_btn.clicked.connect(self.copy_context)
        reload_context_btn = QPushButton("Reload Files")
        reload_context_btn.clicked.connect(self.reload_selected_files)
        actions_layout.addWidget(copy_context_btn)
        actions_layout.addWidget(reload_context_btn)

        context_layout.addLayout(actions_layout)

        # Context Display
        self.context_display = QTextEdit()
        self.context_display.setReadOnly(True)
        context_layout.addWidget(self.context_display)

        # Save Session Button
        save_session_btn = QPushButton("Save Session")
        save_session_btn.clicked.connect(self.save_current_session)
        context_layout.addWidget(save_session_btn)

        # Previous Sessions List
        self.sessions_list = QListWidget()
        self.sessions_list.itemDoubleClicked.connect(self.load_session)
        context_layout.addWidget(QLabel("Previous Sessions:"))
        context_layout.addWidget(self.sessions_list)

        context_panel.setLayout(context_layout)
        splitter.addWidget(context_panel)

        splitter.setSizes([400, 600])
        main_layout.addWidget(splitter)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Load previous sessions on startup
        self.load_previous_sessions()

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.file_tree.clear()
            self.populate_tree(folder_path, self.file_tree)

    def populate_tree(self, folder_path, parent_item):
        folder_item = QTreeWidgetItem(parent_item)
        folder_item.setText(0, os.path.basename(folder_path))
        folder_item.setData(0, Qt.UserRole, folder_path)
        folder_item.setFlags(folder_item.flags() | Qt.ItemIsUserCheckable)
        folder_item.setCheckState(0, Qt.Unchecked)

        for entry in sorted(os.listdir(folder_path)):
            full_path = os.path.join(folder_path, entry)
            if os.path.isdir(full_path):
                self.populate_tree(full_path, folder_item)
            else:
                file_item = QTreeWidgetItem(folder_item)
                file_item.setText(0, entry)
                file_item.setData(0, Qt.UserRole, full_path)
                file_item.setFlags(file_item.flags() | Qt.ItemIsUserCheckable)
                file_item.setCheckState(0, Qt.Unchecked)

    def file_selection_changed(self, item):
        if item.childCount() > 0:  # Folder item
            for i in range(item.childCount()):
                child = item.child(i)
                child.setCheckState(0, item.checkState(0))
        else:  # File item
            self.update_selected_files()
            self.update_context_display()

    def update_selected_files(self):
        self.selected_files = []

        def collect_files_recursively(item):
            if item.checkState(0) == Qt.Checked:
                file_path = item.data(0, Qt.UserRole)
                if item.childCount() == 0:  # File
                    self.selected_files.append(file_path)
            for i in range(item.childCount()):
                collect_files_recursively(item.child(i))

        for i in range(self.file_tree.topLevelItemCount()):
            collect_files_recursively(self.file_tree.topLevelItem(i))

    def update_context_display(self):
        context_text = ""
        for file_path in self.selected_files:
            file_info = self.file_manager.read_file_content(file_path)
            context_text += f"### FILE: {file_path} (Size: {file_info['size']:.2f} MB)\n"
            context_text += "```\n" + file_info['content'] + "...\n```\n\n"
        self.context_display.setPlainText(context_text)

    def copy_context(self):
        pyperclip.copy(self.context_display.toPlainText())
        QMessageBox.information(self, "Context Copied", "File contents copied to clipboard!")

    def reload_selected_files(self):
        self.update_context_display()
        QMessageBox.information(self, "Files Reloaded", "Selected files have been reloaded!")

    def save_current_session(self):
        if not self.selected_files:
            QMessageBox.warning(self, "No Files", "Please select files first.")
            return
        self.session_storage.save_session(self.session_id, self.selected_files)
        QMessageBox.information(self, "Session Saved", "Session saved successfully!")
        self.load_previous_sessions()

    def load_previous_sessions(self):
        self.sessions_list.clear()
        sessions = self.session_storage.get_sessions()
        for session in sessions:
            self.sessions_list.addItem(f"{session['timestamp']} - {len(session['selected_files'])} files")

    def load_session(self, item):
        index = self.sessions_list.row(item)
        sessions = self.session_storage.get_sessions()
        selected_session = sessions[index]
        self.clear_file_selection()
        for file_path in selected_session['selected_files']:
            self.find_and_check_file(file_path)

    def clear_file_selection(self):
        for i in range(self.file_tree.topLevelItemCount()):
            self.clear_item_selection(self.file_tree.topLevelItem(i))

    def clear_item_selection(self, item):
        item.setCheckState(0, Qt.Unchecked)
        for i in range(item.childCount()):
            self.clear_item_selection(item.child(i))

    def find_and_check_file(self, file_path):
        for i in range(self.file_tree.topLevelItemCount()):
            item = self.file_tree.topLevelItem(i)
            if self.search_file_in_item(item, file_path):
                break

    def search_file_in_item(self, item, file_path):
        if item.data(0, Qt.UserRole) == file_path:
            item.setCheckState(0, Qt.Checked)
            return True
        for i in range(item.childCount()):
            if self.search_file_in_item(item.child(i), file_path):
                return True
        return False
