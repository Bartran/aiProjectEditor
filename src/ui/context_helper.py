import pyperclip
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox


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
        if file_info:
            context_text += f"### FILE: {file_path} (Size: {file_info['size']:.2f} MB)\n"
            context_text += "```\n" + file_info['content'] + "...\n```\n\n"
        else:
            context_text += f"### FILE: {file_path} (Size: N/A)\n"
            context_text += "```\nFile not found or unable to read\n```\n\n"
    self.context_display.setPlainText(context_text)


def copy_context(self):
    pyperclip.copy(self.context_display.toPlainText())
    QMessageBox.information(self, "Context Copied", "File contents copied to clipboard!")


def reload_selected_files(self):
    self.update_context_display()
    QMessageBox.information(self, "Files Reloaded", "Selected files have been reloaded!")
