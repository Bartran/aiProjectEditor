import uuid
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTextEdit, QLabel, QTreeWidget, QSplitter,
    QListWidget, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from src.services.file_manager import FileManager
from src.services.session_storage import SessionStorage
from src.ui.context_helper import copy_context, reload_selected_files, update_selected_files, update_context_display
from src.ui.file_tree_helper import select_folder, file_selection_changed, clear_file_selection, find_and_check_file, \
    get_file_icon, populate_tree
from src.ui.session_helper import save_current_session, load_session, load_previous_sessions


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Context Collector")
        self.resize(1200, 800)
        self.current_folder_path = None
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f0f0; }
            QTreeWidget { background-color: white; border: 1px solid #d0d0d0; }
            QTextEdit { background-color: white; border: 1px solid #d0d0d0; font-size: 14px; }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #45a049; }
            QLabel { font-size: 14px; }
            QListWidget { font-size: 14px; }
        """)

        # Initialize components
        self.file_tree = None
        self.context_display = None
        self.sessions_list = None
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
        file_layout.setContentsMargins(5, 5, 5, 5)  # Add padding
        file_layout.setSpacing(10)  # Add spacing

        select_folder_btn = QPushButton(QIcon("icons/folder.png"), " Select Folder")  # Added icon
        select_folder_btn.clicked.connect(self.select_folder)
        file_layout.addWidget(select_folder_btn)

        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderHidden(True)  # Simplified header
        self.file_tree.itemChanged.connect(self.file_selection_changed)
        self.file_tree.setDragEnabled(True)  # Enable drag and drop
        self.file_tree.setAcceptDrops(True)
        self.file_tree.setDragDropMode(QTreeWidget.InternalMove)
        file_layout.addWidget(self.file_tree)

        file_panel.setLayout(file_layout)
        splitter.addWidget(file_panel)

        # Right Panel: Context and Actions
        context_panel = QWidget()
        context_layout = QVBoxLayout()
        context_layout.setContentsMargins(5, 5, 5, 5)
        context_layout.setSpacing(10)

        # Action Buttons
        actions_layout = QHBoxLayout()
        copy_context_btn = QPushButton(QIcon("icons/copy.png"), " Copy Context")  # Added icon
        copy_context_btn.clicked.connect(self.copy_context)
        reload_context_btn = QPushButton(QIcon("icons/reload.png"), " Reload Files")  # Added icon
        reload_context_btn.clicked.connect(self.reload_selected_files)
        actions_layout.addWidget(copy_context_btn)
        actions_layout.addWidget(reload_context_btn)

        context_layout.addLayout(actions_layout)

        # Context Display
        self.context_display = QTextEdit()
        self.context_display.setReadOnly(True)
        context_layout.addWidget(self.context_display)

        # Save Session Button
        save_session_btn = QPushButton(QIcon("icons/save.png"), " Save Session")  # Added icon
        save_session_btn.clicked.connect(self.save_current_session)
        context_layout.addWidget(save_session_btn)

        # Previous Sessions List
        context_layout.addWidget(QLabel("Previous Sessions:"))
        self.sessions_list = QListWidget()
        self.sessions_list.itemDoubleClicked.connect(self.load_session)
        context_layout.addWidget(self.sessions_list)

        context_panel.setLayout(context_layout)
        splitter.addWidget(context_panel)

        splitter.setSizes([400, 600])
        main_layout.addWidget(splitter)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Load previous sessions on startup
        self.load_previous_sessions()

        # Set the application font
        app_font = QFont("Arial", 12)  # Changed font and size
        self.setFont(app_font)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.current_folder_path = folder_path
            self.file_tree.clear()
            self.populate_tree(folder_path, self.file_tree)

    def populate_tree_from_session(self, folder_path):
        """
        Populates the file tree from a given folder path (used when loading a session).
        """
        self.file_tree.clear()
        self.populate_tree(folder_path, self.file_tree)

    def get_current_folder_path(self):
        """
        Returns the path of the currently selected folder or None.
        """
        return self.current_folder_path

    # Main UI methods
    populate_tree = populate_tree
    get_file_icon = get_file_icon
    file_selection_changed = file_selection_changed
    clear_file_selection = clear_file_selection
    find_and_check_file = find_and_check_file
    copy_context = copy_context
    reload_selected_files = reload_selected_files
    update_selected_files = update_selected_files
    update_context_display = update_context_display
    save_current_session = save_current_session
    load_previous_sessions = load_previous_sessions
    load_session = load_session
