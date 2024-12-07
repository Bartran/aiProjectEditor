import os


class FileManager:
    @staticmethod
    def get_files_recursively(directory):
        """
        Recursively find all files in a given directory.

        Args:
            directory (str): Path to the root directory

        Returns:
            list: Full paths of all files found
        """
        file_list = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_list.append(os.path.join(root, file))
        return file_list

    @staticmethod
    def read_file_content(file_path):
        """
        Read the content of a file.

        Args:
            file_path (str): Full path to the file

        Returns:
            str: File content or error message
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"