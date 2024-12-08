import os
from PyQt5.QtWidgets import (
    QFileDialog, QTreeWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


def select_folder(self):
    folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
    if folder_path:
        self.file_tree.clear()
        self.populate_tree(folder_path, self.file_tree)


def populate_tree(self, folder_path, parent_item):
    folder_item = QTreeWidgetItem(parent_item)
    folder_item.setText(0, os.path.basename(folder_path))
    folder_item.setData(0, Qt.UserRole, folder_path)
    folder_item.setFlags(
        folder_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
    folder_item.setCheckState(0, Qt.Unchecked)
    folder_item.setIcon(0, QIcon("icons/folder.png"))  # Set folder icon

    for entry in sorted(os.listdir(folder_path)):
        full_path = os.path.join(folder_path, entry)
        if os.path.isdir(full_path):
            self.populate_tree(full_path, folder_item)
        else:
            file_item = QTreeWidgetItem(folder_item)
            file_item.setText(0, entry)
            file_item.setData(0, Qt.UserRole, full_path)
            file_item.setFlags(
                file_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled)
            file_item.setCheckState(0, Qt.Unchecked)
            file_item.setIcon(0, self.get_file_icon(entry))  # Set file icon based on extension


def get_file_icon(self, filename):
    """Returns an icon based on the file extension."""
    _, ext = os.path.splitext(filename)
    if ext == ".py":
        return QIcon("icons/py.png")
    elif ext == ".java":
        return QIcon("icons/java.png")
    elif ext == ".md":
        return QIcon("icons/md.png")
    else:
        return QIcon("icons/documents.png")  # Default file icon


def file_selection_changed(self, item):
    if item.childCount() > 0:  # Folder item
        new_state = item.checkState(0)
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, new_state)
    else:  # File item
        self.update_selected_files()
        self.update_context_display()


def clear_file_selection(self):
    for i in range(self.file_tree.topLevelItemCount()):
        self.clear_item_selection(self.file_tree.topLevelItem(i))


def clear_item_selection(self, item):
    item.setCheckState(0, Qt.Unchecked)
    for i in range(item.childCount()):
        self.clear_item_selection(item.child(i))
