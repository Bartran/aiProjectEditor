import os
import fnmatch


class FileManager:
    @staticmethod
    def get_files_recursively(directory, ignored_patterns=None):
        """
        Recursively find all files in a given directory with optional ignore patterns.

        Args:
            directory (str): Path to the root directory
            ignored_patterns (list, optional): List of patterns to ignore

        Returns:
            list: Full paths of all files found
        """
        if ignored_patterns is None:
            ignored_patterns = [
                '*.pyc', '__pycache__', '.git', '.env',
                '*.log', '*.tmp', '*.swp'
            ]

        file_list = []
        for root, _, files in os.walk(directory):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, directory)

                # Check if file matches any ignore pattern
                if not any(fnmatch.fnmatch(relative_path, pattern) for pattern in ignored_patterns):
                    file_list.append(full_path)

        return sorted(file_list)

    @staticmethod
    def read_file_content(file_path, max_size_mb=5):
        """
        Read the content of a file with size limit.

        Args:
            file_path (str): Full path to the file
            max_size_mb (int, optional): Maximum file size in MB to read

        Returns:
            dict: File information including content or error
        """
        try:
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB

            if file_size > max_size_mb:
                return {
                    'path': file_path,
                    'content': f"File too large ({file_size:.2f} MB). Max size is {max_size_mb} MB.",
                    'size': file_size,
                    'is_text': False
                }

            # Try to read as text
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                'path': file_path,
                'content': content,
                'size': file_size,
                'is_text': True
            }
        except UnicodeDecodeError:
            return {
                'path': file_path,
                'content': "Unable to read file: Not a text file.",
                'size': file_size,
                'is_text': False
            }
        except Exception as e:
            return {
                'path': file_path,
                'content': f"Error reading file: {str(e)}",
                'size': 0,
                'is_text': False
            }