import json
import os


class FileManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_records(self):
        # Load records from file
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    print(f"Failed to decode JSON from {self.file_path}.")
                    return []
        else:
            print(f"File {self.file_path} does not exist.")
            return []

from pathlib import Path

def get_project_root(marker: str) -> Path:
    """
    Navigate up the directory tree to find the project root by looking for a specific marker.

    :param marker: The file or directory that indicates the project root (e.g., '.git', 'setup.py').
    :return: The path to the project root.
    """
    current_path = Path(__file__).resolve().parent
    while current_path != current_path.root:
        if (current_path / marker).exists():
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError(f"Marker '{marker}' not found in any parent directories")

# Example usage
try:
    project_root = get_project_root(".git")  # Change the marker to whatever is suitable for your project
    print("Project Root:", project_root)

    # Construct the path to A/B/C
    target_path = project_root / 'A' / 'B' / 'C'
    print("Target Path:", target_path)
except FileNotFoundError as e:
    print(e)

